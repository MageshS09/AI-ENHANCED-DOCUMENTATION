"""HTTP routes for README generation."""

from fastapi import APIRouter, HTTPException, status

from models.schemas import GenerateReadmeRequest, GenerateReadmeResponse
from services.documentation_service import DocumentationService
from utils.exceptions import AppError
from utils.logging import get_logger

router = APIRouter(tags=["documentation"])
logger = get_logger(__name__)


@router.post("/generate", response_model=GenerateReadmeResponse)
async def generate_readme(
    payload: GenerateReadmeRequest,
) -> GenerateReadmeResponse:
    """Generate a README.md for a public GitHub repository."""
    try:
        service = DocumentationService()
        markdown = await service.generate(str(payload.repository_url))
        return GenerateReadmeResponse(markdown=markdown)
    except AppError as exc:
        logger.warning("expected_generation_error", extra={"error": str(exc)})
        raise HTTPException(status_code=exc.status_code, detail=exc.public_message) from exc
    except ValueError as exc:
        logger.warning("invalid_generation_request", extra={"error": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
