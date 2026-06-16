"""Repository metadata extraction."""

import json
import re
import tomllib
from pathlib import Path

from models.repository import FileSummary, RepositoryMetadata
from parsers.file_filters import is_relevant_text_file, should_ignore_path


class RepositoryParser:
    """Extract metadata and compact summaries from a cloned repository."""

    def parse(self, root: Path, repo_url: str) -> RepositoryMetadata:
        """Parse a repository into structured metadata."""
        files = [path for path in root.rglob("*") if is_relevant_text_file(path)]
        return RepositoryMetadata(
            name=root.name,
            url=repo_url,
            directory_tree=self._build_tree(root),
            package_dependencies=self._package_dependencies(root),
            python_dependencies=self._python_dependencies(root),
            readme_content=self._readme_content(root),
            has_dockerfile=(root / "Dockerfile").exists(),
            env_example_variables=self._env_example_variables(root),
            api_endpoints=self._detect_api_endpoints(files),
            file_summaries=[self._summarize_file(path, root) for path in files[:80]],
        )

    def _build_tree(self, root: Path, max_entries: int = 220) -> str:
        """Build a concise directory tree."""
        lines: list[str] = [root.name]
        entries = 0
        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root)
            if should_ignore_path(relative):
                continue
            depth = len(relative.parts)
            if depth > 4:
                continue
            prefix = "  " * (depth - 1) + "- "
            suffix = "/" if path.is_dir() else ""
            lines.append(f"{prefix}{relative.name}{suffix}")
            entries += 1
            if entries >= max_entries:
                lines.append("- ...")
                break
        return "\n".join(lines)

    def _package_dependencies(self, root: Path) -> dict[str, str]:
        """Read dependencies from package.json."""
        package_path = root / "package.json"
        if not package_path.exists():
            return {}
        try:
            data = json.loads(package_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
        deps: dict[str, str] = {}
        for section in ("dependencies", "devDependencies"):
            values = data.get(section, {})
            if isinstance(values, dict):
                deps.update({str(key): str(value) for key, value in values.items()})
        return deps

    def _python_dependencies(self, root: Path) -> list[str]:
        """Read Python dependencies from requirements.txt and pyproject.toml."""
        dependencies: list[str] = []
        req_path = root / "requirements.txt"
        if req_path.exists():
            try:
                lines = req_path.read_text(encoding="utf-8").splitlines()
                dependencies.extend(
                    line.strip()
                    for line in lines
                    if line.strip() and not line.strip().startswith("#")
                )
            except UnicodeDecodeError:
                pass
        pyproject_path = root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
                project_deps = pyproject.get("project", {}).get("dependencies", [])
                if isinstance(project_deps, list):
                    dependencies.extend(str(dep) for dep in project_deps)
            except (tomllib.TOMLDecodeError, UnicodeDecodeError):
                pass
        return sorted(set(dependencies))

    def _readme_content(self, root: Path) -> str | None:
        """Read an existing README, if present."""
        for name in ("README.md", "Readme.md", "readme.md"):
            path = root / name
            if path.exists():
                try:
                    return path.read_text(encoding="utf-8")[:8_000]
                except UnicodeDecodeError:
                    return None
        return None

    def _env_example_variables(self, root: Path) -> list[str]:
        """Extract variable names from .env.example."""
        env_path = root / ".env.example"
        if not env_path.exists():
            return []
        try:
            content = env_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return []
        variables: list[str] = []
        for line in content.splitlines():
            if not line.strip() or line.strip().startswith("#") or "=" not in line:
                continue
            variables.append(line.split("=", 1)[0].strip())
        return variables

    def _detect_api_endpoints(self, files: list[Path]) -> list[str]:
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
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
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
                    if not route and path.name in {"route.ts", "route.tsx", "route.js", "route.jsx"}:
                        route = self._route_from_next_path(path)
                    endpoints.add(f"{method.upper()} {route}".strip())
        return sorted(endpoints)[:50]

    def _route_from_next_path(self, path: Path) -> str:
        """Infer a Next.js app route from a route handler path."""
        parts = list(path.parts)
        if "app" not in parts:
            return ""
        app_index = parts.index("app")
        route_parts = parts[app_index + 1 : -1]
        cleaned = [part for part in route_parts if not part.startswith("(")]
        return "/" + "/".join(cleaned)

    def _summarize_file(self, path: Path, root: Path) -> FileSummary:
        """Create a concise file summary from lightweight heuristics."""
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
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
