"""
Image validation and preprocessing.

Security rules (see docs/architecture.md #security):
- Never trust the client-supplied filename or Content-Type header alone.
- Verify the file is actually a decodable image before use.
- Enforce a maximum size limit.
- Only allow JPEG, PNG, WEBP.
"""
import io
import logging

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


class ImageValidationError(Exception):
    """Raised when an uploaded file fails validation. Message is safe to show to the user."""


async def validate_and_load_image(file: UploadFile, max_size_bytes: int) -> Image.Image:
    """
    Reads, validates, and returns a PIL Image.

    Raises ImageValidationError with a user-safe message on any failure.
    """
    if file is None:
        raise ImageValidationError("No image was provided.")

    # Content-Type header is client-supplied and not trustworthy on its own,
    # but reject obviously wrong types early for a fast, clear error.
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ImageValidationError(
            "Unsupported file type. Please upload a JPEG, PNG, or WEBP image."
        )

    raw_bytes = await file.read()

    if not raw_bytes:
        raise ImageValidationError("The uploaded image is empty.")

    if len(raw_bytes) > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise ImageValidationError(f"Image is too large. Maximum allowed size is {max_mb:.0f} MB.")

    # This is the real check: does PIL consider this actual, decodable image data?
    try:
        img = Image.open(io.BytesIO(raw_bytes))
        img.verify()  # verify() checks integrity but leaves the image unusable afterward
        # Re-open because verify() invalidates the file pointer/object
        img = Image.open(io.BytesIO(raw_bytes))
        img.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ImageValidationError(
            "The uploaded file could not be read as a valid image. It may be corrupted or unsupported."
        )

    if img.format not in ALLOWED_FORMATS:
        raise ImageValidationError(
            "Unsupported image format. Please upload a JPEG, PNG, or WEBP image."
        )

    # Normalize to RGB for consistent downstream processing (handles PNG with alpha, etc.)
    if img.mode != "RGB":
        img = img.convert("RGB")

    logger.info("Image validated: format=%s size=%s bytes=%d", img.format, img.size, len(raw_bytes))
    return img


def resize_for_model(img: Image.Image, max_dimension: int = 1024) -> Image.Image:
    """Resize large images down for consistent, efficient model input. Keeps aspect ratio."""
    width, height = img.size
    if max(width, height) <= max_dimension:
        return img

    scale = max_dimension / max(width, height)
    new_size = (int(width * scale), int(height * scale))
    return img.resize(new_size, Image.LANCZOS)
