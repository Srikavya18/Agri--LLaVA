"""
Agri-LLaVA backend entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000

See backend/.env.example for required environment variables.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.rag.knowledge_loader import KnowledgeBaseError, load_knowledge_base

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Agri-LLaVA backend | environment=%s inference_mode=%s",
                settings.environment, settings.inference_mode)

    if settings.inference_mode == "mock":
        logger.warning(
            "INFERENCE_MODE=mock — using DEVELOPMENT ONLY fake predictions. "
            "This is guarded against running when ENVIRONMENT=production."
        )

    # Fail fast if the knowledge base is missing/broken rather than on the first request.
    try:
        load_knowledge_base(settings.knowledge_base_path)
    except KnowledgeBaseError as e:
        logger.error("Startup check failed: %s", e)
        raise

    yield  # app runs here

    logger.info("Shutting down Agri-LLaVA backend")


app = FastAPI(
    title="Agri-LLaVA API",
    description="Multimodal AI backend for crop disease detection.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.info("Request validation failed: %s", exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request. Please check the image, text, and language fields."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again."},
    )
