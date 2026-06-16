"""Request and response schemas."""

from pydantic import BaseModel, Field, HttpUrl


class GenerateReadmeRequest(BaseModel):
    """Request body for README generation."""

    repository_url: HttpUrl = Field(
        ...,
        description="Public GitHub repository URL.",
        examples=["https://github.com/owner/repository"],
    )


class GenerateReadmeResponse(BaseModel):
    """Response body containing generated Markdown."""

    markdown: str = Field(..., description="Generated README.md content.")
