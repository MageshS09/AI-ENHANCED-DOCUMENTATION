"""FastAPI entrypoint for the AI Documentation Generator backend."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import router
from utils.config import get_settings
from utils.logging import configure_logging, get_logger
from utils.rate_limit import InMemoryRateLimitMiddleware

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Configure startup and shutdown hooks."""
    logger.info("backend_started")
    yield
    logger.info("backend_stopped")


app = FastAPI(
    title="AI Documentation Generator API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    InMemoryRateLimitMiddleware,
    requests_per_window=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a structured JSON error for unexpected exceptions."""
    logger.exception(
        "unhandled_exception",
        extra={"path": request.url.path, "method": request.method},
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected server error. Please try again."},
    )


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return a lightweight health response."""
    return {"status": "ok"}


app.include_router(router, prefix="/api")
