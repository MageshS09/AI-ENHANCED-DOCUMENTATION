"""Repository analysis domain models."""

from pydantic import BaseModel, Field


class FileSummary(BaseModel):
    """Compact summary of a source file."""

    path: str
    language: str
    summary: str
    content_excerpt: str


class RepositoryMetadata(BaseModel):
    """Structured metadata extracted from a repository."""

    name: str
    url: str
    directory_tree: str
    package_dependencies: dict[str, str] = Field(default_factory=dict)
    python_dependencies: list[str] = Field(default_factory=list)
    readme_content: str | None = None
    has_dockerfile: bool = False
    env_example_variables: list[str] = Field(default_factory=list)
    api_endpoints: list[str] = Field(default_factory=list)
    file_summaries: list[FileSummary] = Field(default_factory=list)
