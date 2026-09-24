"""
API routes.

Endpoints:
  GET  /health                -> liveness check
  POST /api/v1/analyze        -> main analysis endpoint (image + optional text + language)
  POST /api/v1/predict        -> alias of /analyze, kept for spec compatibility
  GET  /api/v1/diseases       -> lists all known crop/disease entries in the knowledge base
  POST /api/v1/feedback       -> accepts user feedback on a result (logged only, no DB per spec)
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File

from app.core.config import Settings, get_settings
from app.models.schemas import (
    AnalysisResponse,
    DiseaseListItem,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    SUPPORTED_LANGUAGES,
)
from app.rag.knowledge_loader import KnowledgeBaseError, load_knowledge_base
from app.rag.retriever import retrieve
from app.services.image_service import ImageValidationError, resize_for_model, validate_and_load_image
from app.services.model_service import ModelInferenceError, get_model_service
from app.utils.response_builder import build_analysis_response, build_safe_fallback

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


async def _run_analysis(
    image: UploadFile,
    text: Optional[str],
    language: str,
    settings: Settings,
) -> AnalysisResponse:
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{language}'. Supported: {sorted(SUPPORTED_LANGUAGES)}",
        )

    # 1. Validate + load image
    try:
        pil_image = await validate_and_load_image(image, settings.max_image_size_bytes)
    except ImageValidationError as e:
        logger.info("Image validation failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    pil_image = resize_for_model(pil_image)

    # 2. Run model inference
    is_mock = settings.inference_mode == "mock"
    try:
        model_service = get_model_service(
            inference_mode=settings.inference_mode,
            model_api_url=settings.model_api_url,
            model_api_key=settings.model_api_key,
            lora_adapter_path=settings.lora_adapter_path,
        )
        prediction = await model_service.predict(pil_image, text, language)
    except ModelInferenceError as e:
        logger.error("Model inference failed: %s", e)
        # Never show raw backend errors to the user (spec section 9/27).
        raise HTTPException(
            status_code=503,
            detail="Unable to analyze the image right now. Please try again.",
        )
    except Exception:
        logger.exception("Unexpected error during model inference")
        raise HTTPException(
            status_code=500,
            detail="Unable to analyze the image right now. Please try again.",
        )

    # 3. RAG: ground the prediction in real agricultural knowledge
    try:
        kb = load_knowledge_base(settings.knowledge_base_path)
        knowledge_entry = retrieve(
            kb, prediction.get("crop", ""), prediction.get("disease", ""), language
        )
    except KnowledgeBaseError as e:
        logger.error("Knowledge base failed to load: %s", e)
        return build_safe_fallback(language)

    # 4. Build + validate the final structured response (safe fallback on failure)
    return build_analysis_response(
        model_prediction=prediction,
        knowledge_entry=knowledge_entry,
        language=language,
        is_mock=is_mock,
    )


@router.post("/api/v1/analyze", response_model=AnalysisResponse, tags=["analysis"])
async def analyze(
    image: UploadFile = File(...),
    text: Optional[str] = Form(None),
    language: str = Form("en"),
    settings: Settings = Depends(get_settings),
) -> AnalysisResponse:
    return await _run_analysis(image, text, language, settings)


@router.post("/api/v1/predict", response_model=AnalysisResponse, tags=["analysis"])
async def predict(
    image: UploadFile = File(...),
    text: Optional[str] = Form(None),
    language: str = Form("en"),
    settings: Settings = Depends(get_settings),
) -> AnalysisResponse:
    """Alias of /api/v1/analyze — kept because the spec references both names."""
    return await _run_analysis(image, text, language, settings)


@router.get("/api/v1/diseases", response_model=list[DiseaseListItem], tags=["knowledge"])
async def list_diseases(settings: Settings = Depends(get_settings)) -> list[DiseaseListItem]:
    try:
        kb = load_knowledge_base(settings.knowledge_base_path)
    except KnowledgeBaseError as e:
        logger.error("Knowledge base failed to load: %s", e)
        raise HTTPException(status_code=503, detail="Knowledge base is currently unavailable.")

    return [
        DiseaseListItem(key=key, crop=entry.get("crop", ""), disease=entry.get("disease", ""))
        for key, entry in kb.items()
    ]


@router.post("/api/v1/feedback", response_model=FeedbackResponse, tags=["feedback"])
async def feedback(payload: FeedbackRequest) -> FeedbackResponse:
    # No database per spec (avoid unnecessary infra) — logged for now.
    logger.info(
        "Feedback received: crop=%s disease=%s helpful=%s",
        payload.crop, payload.disease, payload.helpful,
    )
    return FeedbackResponse(status="received")
