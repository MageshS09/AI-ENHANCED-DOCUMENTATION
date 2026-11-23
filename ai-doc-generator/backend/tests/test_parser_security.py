"""Security and robustness tests for repository parsing (cloned repos are untrusted)."""

import os
from pathlib import Path

import pytest

from parsers import file_filters
from parsers.repository_parser import RepositoryParser

SECRET = "GROQ_API_KEY=sk-super-secret-value\n"


@pytest.fixture
def secret_file(tmp_path: Path) -> Path:
    outside = tmp_path / "outside"
    outside.mkdir()
    path = outside / "server.env"
    path.write_text(SECRET, encoding="utf-8")
    return path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    return root


def _symlink(target: Path, link: Path) -> None:
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported on this platform")


def test_symlinked_readme_is_not_read(repo: Path, secret_file: Path) -> None:
    # Regression: a malicious repo could point README.md at a server file such as .env.
    _symlink(secret_file, repo / "README.md")
    assert RepositoryParser().parse(repo, "u").readme_content is None


def test_symlinked_env_example_is_not_read(repo: Path, secret_file: Path) -> None:
    _symlink(secret_file, repo / ".env.example")
    assert RepositoryParser().parse(repo, "u").env_example_variables == []


def test_symlinked_manifests_are_not_read(repo: Path, secret_file: Path) -> None:
    _symlink(secret_file, repo / "requirements.txt")
    _symlink(secret_file, repo / "package.json")
    _symlink(secret_file, repo / "pyproject.toml")
    metadata = RepositoryParser().parse(repo, "u")
    assert metadata.python_dependencies == []
    assert metadata.package_dependencies == {}


def test_symlinked_source_file_is_not_summarized(repo: Path, secret_file: Path) -> None:
    _symlink(secret_file, repo / "stolen.py")
    metadata = RepositoryParser().parse(repo, "u")
    assert metadata.file_summaries == []
    assert "sk-super-secret-value" not in metadata.model_dump_json()


def test_files_in_symlinked_directory_are_not_read(repo: Path, secret_file: Path) -> None:
    _symlink(secret_file.parent, repo / "linked")
    metadata = RepositoryParser().parse(repo, "u")
    assert "sk-super-secret-value" not in metadata.model_dump_json()


def test_symlinked_dockerfile_does_not_count(repo: Path, secret_file: Path) -> None:
    _symlink(secret_file, repo / "Dockerfile")
    assert RepositoryParser().parse(repo, "u").has_dockerfile is False


def test_safe_read_text_rejects_paths_outside_root(repo: Path, secret_file: Path) -> None:
    assert file_filters.safe_read_text(secret_file, repo) is None


def test_safe_read_text_reads_regular_files_and_applies_limit(repo: Path) -> None:
    (repo / "a.txt").write_text("abcdef", encoding="utf-8")
    assert file_filters.safe_read_text(repo / "a.txt", repo) == "abcdef"
    assert file_filters.safe_read_text(repo / "a.txt", repo, limit=3) == "abc"
    assert file_filters.safe_read_text(repo / "missing.txt", repo) is None


def test_non_utf8_file_is_skipped_not_fatal(repo: Path) -> None:
    (repo / "README.md").write_bytes(b"\xff\xfe\x00bad")
    assert RepositoryParser().parse(repo, "u").readme_content is None


@pytest.mark.parametrize("name", ["build", "dist", "venv", "coverage"])
def test_repository_named_like_an_ignored_dir_is_still_parsed(tmp_path: Path, name: str) -> None:
    # Regression: ignore rules were applied to the absolute path, so a root named
    # "build" (or a temp dir containing such a segment) made every file invisible.
    root = tmp_path / name
    root.mkdir()
    (root / "main.py").write_text("def run():\n    pass\n", encoding="utf-8")
    assert [s.path for s in RepositoryParser().parse(root, "u").file_summaries] == ["main.py"]


def test_ignored_directories_are_skipped_in_files_and_tree(repo: Path) -> None:
    (repo / "node_modules" / "pkg").mkdir(parents=True)
    (repo / "node_modules" / "pkg" / "index.js").write_text("module.exports = 1", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("def f():\n    pass\n", encoding="utf-8")
    metadata = RepositoryParser().parse(repo, "u")
    assert [s.path for s in metadata.file_summaries] == ["src/app.py"]
    assert "node_modules" not in metadata.directory_tree


def test_file_order_is_deterministic(repo: Path) -> None:
    for name in ("b.py", "a.py", "c.py"):
        (repo / name).write_text("x = 1\n", encoding="utf-8")
    paths = [s.path for s in RepositoryParser().parse(repo, "u").file_summaries]
    assert paths == ["a.py", "b.py", "c.py"]


def test_oversized_files_are_skipped(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(file_filters, "MAX_FILE_SIZE_BYTES", 10)
    (repo / "big.py").write_text("x = 1\n" * 10, encoding="utf-8")
    (repo / "small.py").write_text("x=1", encoding="utf-8")
    assert [s.path for s in RepositoryParser().parse(repo, "u").file_summaries] == ["small.py"]


def test_number_of_scanned_files_is_capped(repo: Path) -> None:
    for index in range(15):
        (repo / f"f{index:02}.py").write_text("x = 1\n", encoding="utf-8")
    assert len(list(file_filters.iter_relevant_files(repo, limit=5))) == 5


def test_directory_tree_is_depth_limited_and_entry_limited(repo: Path) -> None:
    deep = repo / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    (deep / "too_deep.py").write_text("x = 1", encoding="utf-8")
    tree = RepositoryParser()._build_tree(repo)
    assert "d/" in tree and "e/" not in tree
    for index in range(30):
        (repo / f"file{index:02}.txt").write_text("x", encoding="utf-8")
    limited = RepositoryParser()._build_tree(repo, max_entries=10)
    assert limited.splitlines()[-1] == "- ..."


def test_invalid_manifests_do_not_crash(repo: Path) -> None:
    (repo / "package.json").write_text("[1, 2, 3]", encoding="utf-8")
    (repo / "pyproject.toml").write_text("not = valid = toml", encoding="utf-8")
    metadata = RepositoryParser().parse(repo, "u")
    assert metadata.package_dependencies == {}
    assert metadata.python_dependencies == []


def test_requirements_comments_and_blank_lines_are_ignored(repo: Path) -> None:
    (repo / "requirements.txt").write_text("# comment\n\nflask==3.0\n", encoding="utf-8")
    assert RepositoryParser().parse(repo, "u").python_dependencies == ["flask==3.0"]


def test_env_example_comments_and_values_are_not_leaked(repo: Path) -> None:
    (repo / ".env.example").write_text("# note\nAPI_KEY=abc\n\nPORT = 8000\nNOEQUALS\n", encoding="utf-8")
    assert RepositoryParser().parse(repo, "u").env_example_variables == ["API_KEY", "PORT"]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('@router.post("/items")\ndef f(): pass\n', "POST /items"),
        ('@app.route("/old", methods=["PUT"])\ndef f(): pass\n', "PUT /old"),
    ],
)
def test_api_endpoint_detection(repo: Path, source: str, expected: str) -> None:
    (repo / "routes.py").write_text(source, encoding="utf-8")
    assert expected in RepositoryParser().parse(repo, "u").api_endpoints


def test_next_route_handler_path_is_inferred(repo: Path) -> None:
    handler = repo / "app" / "api" / "users" / "route.ts"
    handler.parent.mkdir(parents=True)
    handler.write_text("export async function GET() {}\n", encoding="utf-8")
    assert "GET /api/users" in RepositoryParser().parse(repo, "u").api_endpoints


def test_bare_http_method_function_outside_route_file_is_not_an_endpoint(repo: Path) -> None:
    # Regression: any file mentioning `export async function GET(` produced a path-less "GET".
    (repo / "notes.ts").write_text("export async function GET() {}\n", encoding="utf-8")
    assert RepositoryParser().parse(repo, "u").api_endpoints == []


def test_next_route_inference_ignores_app_directories_above_the_repo(tmp_path: Path) -> None:
    root = tmp_path / "app" / "checkout"
    handler = root / "app" / "api" / "items" / "route.ts"
    handler.parent.mkdir(parents=True)
    handler.write_text("export async function POST() {}\n", encoding="utf-8")
    assert RepositoryParser().parse(root, "u").api_endpoints == ["POST /api/items"]


def test_manifests_in_monorepo_subfolders_are_found(repo: Path) -> None:
    (repo / "backend").mkdir()
    (repo / "frontend").mkdir()
    (repo / "backend" / "requirements.txt").write_text("fastapi==0.1\n-r base.txt\n--index-url https://x\n", encoding="utf-8")
    (repo / "backend" / ".env.example").write_text("GROQ_API_KEY=\nLOG_LEVEL=INFO\n", encoding="utf-8")
    (repo / "backend" / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
    (repo / "frontend" / "package.json").write_text('{"dependencies":{"next":"15"}}', encoding="utf-8")
    metadata = RepositoryParser().parse(repo, "u")
    assert metadata.python_dependencies == ["fastapi==0.1"]
    assert metadata.env_example_variables == ["GROQ_API_KEY", "LOG_LEVEL"]
    assert metadata.has_dockerfile is True
    assert metadata.package_dependencies == {"next": "15"}


def test_deeply_nested_and_ignored_manifests_are_not_used(repo: Path) -> None:
    deep = repo / "a" / "b" / "c" / "d"
    deep.mkdir(parents=True)
    (deep / "requirements.txt").write_text("too-deep==1\n", encoding="utf-8")
    vendored = repo / "node_modules" / "pkg"
    vendored.mkdir(parents=True)
    (vendored / "package.json").write_text('{"dependencies":{"vendored":"1"}}', encoding="utf-8")
    metadata = RepositoryParser().parse(repo, "u")
    assert metadata.python_dependencies == []
    assert metadata.package_dependencies == {}


def test_root_manifests_take_priority_and_count_is_capped(repo: Path) -> None:
    for index in range(8):
        sub = repo / f"svc{index}"
        sub.mkdir()
        (sub / "requirements.txt").write_text(f"pkg{index}==1\n", encoding="utf-8")
    (repo / "requirements.txt").write_text("rootpkg==1\n", encoding="utf-8")
    deps = RepositoryParser().parse(repo, "u").python_dependencies
    assert "rootpkg==1" in deps
    assert len(deps) == 5  # root + the four nearest-by-name subfolders
