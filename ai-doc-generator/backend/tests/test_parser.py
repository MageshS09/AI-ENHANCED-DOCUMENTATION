from pathlib import Path

from parsers.repository_parser import RepositoryParser


def test_parser_extracts_metadata(tmp_path: Path) -> None:
    """It extracts dependency, env, docker, and endpoint metadata."""
    (tmp_path / "package.json").write_text(
        '{"dependencies":{"next":"15.0.0"},"devDependencies":{"typescript":"5.0.0"}}',
        encoding="utf-8",
    )
    (tmp_path / "requirements.txt").write_text("fastapi==0.1\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["pydantic==2.0.0"]\n',
        encoding="utf-8",
    )
    (tmp_path / ".env.example").write_text("OPENAI_API_KEY=\n", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    (tmp_path / "main.py").write_text(
        'from fastapi import FastAPI\napp=FastAPI()\n@app.get("/health")\ndef health(): pass\n',
        encoding="utf-8",
    )

    metadata = RepositoryParser().parse(tmp_path, "https://github.com/a/b")

    assert metadata.package_dependencies["next"] == "15.0.0"
    assert "fastapi==0.1" in metadata.python_dependencies
    assert "pydantic==2.0.0" in metadata.python_dependencies
    assert metadata.has_dockerfile is True
    assert "OPENAI_API_KEY" in metadata.env_example_variables
    assert "GET /health" in metadata.api_endpoints
