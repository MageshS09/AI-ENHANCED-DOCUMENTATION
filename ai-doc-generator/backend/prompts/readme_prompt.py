"""Prompt builder for README generation."""

import json

from models.repository import FileSummary, RepositoryMetadata


def build_readme_prompt(metadata: RepositoryMetadata, context: list[FileSummary]) -> str:
    """Build a grounded prompt for README.md generation."""
    context_payload = [
        {
            "path": item.path,
            "language": item.language,
            "summary": item.summary,
            "excerpt": item.content_excerpt[:1_500],
        }
        for item in context
    ]
    metadata_payload = metadata.model_dump(exclude={"file_summaries"})
    return f"""
Generate a professional README.md for this repository.

Rules:
- Return only Markdown.
- Be accurate and do not invent commands or endpoints.
- Include sections: Project overview, Features, Tech stack, Installation,
  Configuration, Usage, Folder structure, API endpoints if detected, Contributing.
- Keep it concise but useful.
- Use fenced code blocks for commands and environment variables.

Repository metadata:
{json.dumps(metadata_payload, indent=2)}

Relevant file context:
{json.dumps(context_payload, indent=2)}
""".strip()
