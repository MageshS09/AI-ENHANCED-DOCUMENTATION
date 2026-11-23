"""Repository metadata extraction."""

import json
import os
import re
from pathlib import Path

import tomllib

from models.repository import FileSummary, RepositoryMetadata
from parsers.file_filters import (
    IGNORED_DIRS,
    iter_relevant_files,
    safe_read_text,
)

TREE_MAX_DEPTH = 4
# Monorepos keep manifests in subfolders (e.g. backend/requirements.txt), so look a few
# levels down, nearest first, and cap how many of each kind are read.
MANIFEST_MAX_DEPTH = 3
MANIFEST_MAX_FILES = 5


class RepositoryParser:
    """Extract metadata and compact summaries from a cloned repository."""

    def parse(self, root: Path, repo_url: str) -> RepositoryMetadata:
        """Parse a repository into structured metadata."""
        files = list(iter_relevant_files(root))
        return RepositoryMetadata(
            name=root.name,
            url=repo_url,
            directory_tree=self._build_tree(root),
            package_dependencies=self._package_dependencies(root, files),
            python_dependencies=self._python_dependencies(root, files),
            readme_content=self._readme_content(root),
            has_dockerfile=bool(self._manifests(root, files, "Dockerfile")),
            env_example_variables=self._env_example_variables(root, files),
            api_endpoints=self._detect_api_endpoints(files, root),
            file_summaries=[
                summary for path in files[:80] if (summary := self._summarize_file(path, root)) is not None
            ],
        )

    def _build_tree(self, root: Path, max_entries: int = 220) -> str:
        """Build a concise directory tree, skipping ignored directories entirely."""
        lines: list[str] = [root.name]
        entries = 0

        def walk(directory: Path, depth: int) -> bool:
            """Append entries below ``directory``; return False once the entry limit is hit."""
            nonlocal entries
            try:
                children = sorted(os.scandir(directory), key=lambda entry: entry.name)
            except OSError:
                return True
            for child in children:
                is_dir = child.is_dir(follow_symlinks=False)
                if is_dir and child.name in IGNORED_DIRS:
                    continue
                lines.append(f"{'  ' * (depth - 1)}- {child.name}{'/' if is_dir else ''}")
                entries += 1
                if entries >= max_entries:
                    lines.append("- ...")
                    return False
                if is_dir and depth < TREE_MAX_DEPTH and not walk(Path(child.path), depth + 1):
                    return False
            return True

        walk(root, 1)
        return "\n".join(lines)

    def _manifests(self, root: Path, files: list[Path], name: str) -> list[Path]:
        """Return up to MANIFEST_MAX_FILES files called ``name``, shallowest first."""
        matches = [
            path
            for path in files
            if path.name == name and len(path.relative_to(root).parts) <= MANIFEST_MAX_DEPTH + 1
        ]
        matches.sort(key=lambda path: (len(path.relative_to(root).parts), path.as_posix()))
        return matches[:MANIFEST_MAX_FILES]

    def _package_dependencies(self, root: Path, files: list[Path]) -> dict[str, str]:
        """Read dependencies from every nearby package.json."""
        deps: dict[str, str] = {}
        for package_path in self._manifests(root, files, "package.json"):
            content = safe_read_text(package_path, root)
            if content is None:
                continue
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue
            for section in ("dependencies", "devDependencies"):
                values = data.get(section, {})
                if isinstance(values, dict):
                    deps.update({str(key): str(value) for key, value in values.items()})
        return deps

    def _python_dependencies(self, root: Path, files: list[Path]) -> list[str]:
        """Read Python dependencies from requirements.txt and pyproject.toml files."""
        dependencies: list[str] = []
        for req_path in self._manifests(root, files, "requirements.txt"):
            requirements = safe_read_text(req_path, root)
            if requirements is None:
                continue
            dependencies.extend(
                line.strip()
                for line in requirements.splitlines()
                if line.strip() and not line.strip().startswith(("#", "-"))
            )
        for pyproject_path in self._manifests(root, files, "pyproject.toml"):
            pyproject_text = safe_read_text(pyproject_path, root)
            if pyproject_text is None:
                continue
            try:
                pyproject = tomllib.loads(pyproject_text)
            except tomllib.TOMLDecodeError:
                continue
            project_deps = pyproject.get("project", {}).get("dependencies", [])
            if isinstance(project_deps, list):
                dependencies.extend(str(dep) for dep in project_deps)
        return sorted(set(dependencies))

    def _readme_content(self, root: Path) -> str | None:
        """Read an existing README, if present."""
        for name in ("README.md", "Readme.md", "readme.md"):
            content = safe_read_text(root / name, root, limit=8_000)
            if content is not None:
                return content
        return None

    def _env_example_variables(self, root: Path, files: list[Path]) -> list[str]:
        """Extract variable names (never values) from nearby .env.example files."""
        variables: list[str] = []
        for env_path in self._manifests(root, files, ".env.example"):
            content = safe_read_text(env_path, root)
            if content is None:
                continue
            for line in content.splitlines():
                if not line.strip() or line.strip().startswith("#") or "=" not in line:
                    continue
                name = line.split("=", 1)[0].strip()
                if name not in variables:
                    variables.append(name)
        return variables

    def _detect_api_endpoints(self, files: list[Path], root: Path) -> list[str]:
        """Detect common web API route declarations."""
        patterns = [
            r"@(?:app|router)\.(get|post|put|patch|delete)\([\"']([^\"']+)",
            r"(?:app|router)\.(get|post|put|patch|delete)\([\"']([^\"']+)",
            r"(?:app|router)\.route\([\"']([^\"']+)[\"'].*?methods=\[[\"']([A-Z]+)",
            r"Route::(get|post|put|patch|delete)\([\"']([^\"']+)",
            r"export\s+async\s+function\s+(GET|POST|PUT|PATCH|DELETE)\(",
        ]
        endpoints: set[str] = set()
        for path in files:
            text = self._read_lenient(path)
            if text is None:
                continue
            for pattern in patterns:
                for match in re.findall(pattern, text, flags=re.IGNORECASE):
                    if isinstance(match, tuple) and len(match) == 2:
                        first, second = match
                        method, route = (second, first) if first.startswith("/") else (first, second)
                    elif isinstance(match, tuple):
                        method, route = match[0], ""
                    else:
                        method, route = match, ""
                    if not route:
                        # `export async function GET()` only declares an endpoint inside a
                        # Next.js route handler file; elsewhere it is not a route.
                        if path.name not in {"route.ts", "route.tsx", "route.js", "route.jsx"}:
                            continue
                        route = self._route_from_next_path(path, root)
                    endpoints.add(f"{method.upper()} {route}".strip())
        return sorted(endpoints)[:50]

    def _route_from_next_path(self, path: Path, root: Path) -> str:
        """Infer a Next.js app route from a route handler path (relative to the repository)."""
        parts = list(path.relative_to(root).parts)
        if "app" not in parts:
            return ""
        app_index = parts.index("app")
        route_parts = parts[app_index + 1 : -1]
        cleaned = [part for part in route_parts if not part.startswith("(")]
        return "/" + "/".join(cleaned)

    def _read_lenient(self, path: Path) -> str | None:
        """Read an already-vetted file, replacing undecodable bytes."""
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return None

    def _summarize_file(self, path: Path, root: Path) -> FileSummary | None:
        """Create a concise file summary from lightweight heuristics."""
        text = self._read_lenient(path)
        if text is None:
            return None
        relative = path.relative_to(root).as_posix()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        language = path.suffix.lstrip(".") or path.name
        interesting = [
            line
            for line in lines
            if line.startswith(("def ", "class ", "export ", "function ", "const ", "interface "))
            or "@router." in line
            or "@app." in line
        ][:8]
        summary = "; ".join(interesting) if interesting else f"{len(lines)} non-empty lines"
        return FileSummary(
            path=relative,
            language=language,
            summary=summary[:700],
            content_excerpt="\n".join(lines[:80])[:4_000],
        )
