"""
Pydantic schemas for the Agri-LLaVA API.

These are the contract between backend and frontend (see frontend/src/types/analysis.ts,
which must be kept in sync with AnalysisResponse below).
"""
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

SUPPORTED_LANGUAGES = {"en", "hi", "te"}


class HealthResponse(BaseModel):
    status: str = "ok"


class AnalysisResponse(BaseModel):
    crop: str
    disease: str
    confidence: float = Field(ge=0.0, le=1.0)
    symptoms: List[str] = Field(default_factory=list)
    causes: List[str] = Field(default_factory=list)
    prevention: List[str] = Field(default_factory=list)
    organic_treatment: List[str] = Field(default_factory=list)
    chemical_treatment: List[str] = Field(default_factory=list)
    recommendation: str
    language: str

    # Transparency flags — never hidden from the frontend/dev.
    # is_mock=True means this came from the DEVELOPMENT ONLY mock inference service,
    # not the real Qwen2.5-VL + LoRA model.
    is_mock: bool = False
    is_fallback: bool = False  # True if the real model's output failed validation and a safe fallback was used

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language '{v}'. Supported: {sorted(SUPPORTED_LANGUAGES)}")
        return v


class DiseaseListItem(BaseModel):
    key: str
    crop: str
    disease: str


class FeedbackRequest(BaseModel):
    crop: Optional[str] = None
    disease: Optional[str] = None
    helpful: bool
    comment: Optional[str] = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    status: str = "received"


class ErrorResponse(BaseModel):
    detail: str
