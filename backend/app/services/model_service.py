"""
ModelInferenceService abstraction.

This is the single seam between the backend and "whatever actually predicts
crop + disease from an image". Three implementations:

  MockModelService    - DEVELOPMENT ONLY. Deterministic, clearly-labeled fake
                         predictions. Guarded so it can never run when
                         ENVIRONMENT=production (see core/config.py).

  RemoteModelService  - Calls an external GPU-hosted inference API over HTTP.
                         This is what production should use.

  LocalModelService   - Placeholder for loading the model in-process.

All implementations return a plain dict shaped like:
    {"crop": str, "disease": str, "confidence": float}
"""

import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from PIL import Image

logger = logging.getLogger(__name__)


_MOCK_OUTCOMES = [
    {"crop": "Tomato", "disease": "Early Blight", "confidence": 0.87},
    {"crop": "Tomato", "disease": "Late Blight", "confidence": 0.81},
    {"crop": "Tomato", "disease": "Healthy", "confidence": 0.93},
    {"crop": "Potato", "disease": "Early Blight", "confidence": 0.79},
    {"crop": "Potato", "disease": "Late Blight", "confidence": 0.84},
    {"crop": "Bell Pepper", "disease": "Bacterial Spot", "confidence": 0.76},
    {"crop": "Apple", "disease": "Cedar Apple Rust", "confidence": 0.72},
    {"crop": "Corn (Maize)", "disease": "Common Rust", "confidence": 0.80},
]


class ModelInferenceError(Exception):
    """Raised when inference fails."""


class ModelInferenceService(ABC):

    @abstractmethod
    async def predict(
        self,
        image: Image.Image,
        text: Optional[str],
        language: str
    ) -> dict:
        """Returns crop, disease and confidence."""
        raise NotImplementedError


class MockModelService(ModelInferenceService):
    """
    DEVELOPMENT ONLY.

    Deterministically picks an outcome based on a hash of the image bytes.
    This is NOT a real prediction.
    """

    async def predict(
        self,
        image: Image.Image,
        text: Optional[str],
        language: str
    ) -> dict:

        logger.warning(
            "Using MockModelService — DEVELOPMENT ONLY, not a real prediction."
        )

        pixel_bytes = image.tobytes()

        digest = hashlib.sha256(pixel_bytes).hexdigest()

        index = int(digest, 16) % len(_MOCK_OUTCOMES)

        outcome = dict(_MOCK_OUTCOMES[index])

        return outcome


class RemoteModelService(ModelInferenceService):
    """
    Calls an external GPU-hosted inference service.
    """

    def __init__(
        self,
        api_url: str,
        api_key: str = "",
        timeout_seconds: float = 60.0
    ):
        if not api_url:
            raise ModelInferenceError(
                "MODEL_API_URL is not set. RemoteModelService requires "
                "a deployed GPU inference endpoint."
            )

        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    async def predict(
        self,
        image: Image.Image,
        text: Optional[str],
        language: str
    ) -> dict:

        import io

        buffer = io.BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=90
        )

        buffer.seek(0)

        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        files = {
            "image": (
                "image.jpg",
                buffer,
                "image/jpeg"
            )
        }

        data = {
            "text": text or "",
            "language": language
        }

        try:

            async with httpx.AsyncClient(
                timeout=self.timeout_seconds
            ) as client:

                response = await client.post(
                    f"{self.api_url}/predict",
                    headers=headers,
                    files=files,
                    data=data
                )

                response.raise_for_status()

                return response.json()

        except httpx.TimeoutException:

            raise ModelInferenceError(
                "Inference request to the model service timed out."
            )

        except httpx.HTTPStatusError as e:

            raise ModelInferenceError(
                f"Model service returned an error: "
                f"{e.response.status_code}"
            )

        except httpx.RequestError as e:

            raise ModelInferenceError(
                f"Could not reach the model service: {e}"
            )


class LocalModelService(ModelInferenceService):
    """
    NOT YET IMPLEMENTED.

    Will load Qwen2.5-VL-7B-Instruct + LoRA adapter directly
    once ml/inference is implemented and a GPU is available.
    """

    def __init__(self, lora_adapter_path: str):

        raise ModelInferenceError(
            "LocalModelService is not implemented yet. "
            "It depends on ml/inference/, which is built in a later phase, "
            "and requires LORA_ADAPTER_PATH to point at your trained adapter. "
            "Use INFERENCE_MODE=mock for local development or "
            "INFERENCE_MODE=remote once you have a deployed GPU inference service."
        )

    async def predict(
        self,
        image: Image.Image,
        text: Optional[str],
        language: str
    ) -> dict:

        raise NotImplementedError


def get_model_service(
    inference_mode: str,
    model_api_url: str = "",
    model_api_key: str = "",
    lora_adapter_path: str = "",
) -> ModelInferenceService:

    """Factory: builds the correct ModelInferenceService."""

    if inference_mode == "mock":
        return MockModelService()

    if inference_mode == "remote":
        return RemoteModelService(
            api_url=model_api_url,
            api_key=model_api_key
        )

    if inference_mode == "local":
        return LocalModelService(
            lora_adapter_path=lora_adapter_path
        )

    raise ValueError(
        f"Unknown INFERENCE_MODE '{inference_mode}'. "
        "Must be mock, remote, or local."
    )