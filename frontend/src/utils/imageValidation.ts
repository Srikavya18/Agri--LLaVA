const ALLOWED_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
const MAX_SIZE_MB = 10;

export interface ImageValidationResult {
  valid: boolean;
  error?: string;
}

/**
 * Fast client-side check so users get instant feedback instead of waiting
 * for a round-trip to the backend. This is a UX convenience only — the
 * backend re-validates everything server-side and is the real security
 * boundary (see backend/app/services/image_service.py).
 */
export function validateImageFile(file: File): ImageValidationResult {
  if (!ALLOWED_TYPES.includes(file.type)) {
    return {
      valid: false,
      error: "Unsupported file type. Please choose a JPEG, PNG, or WEBP image.",
    };
  }

  const maxBytes = MAX_SIZE_MB * 1024 * 1024;
  if (file.size > maxBytes) {
    return {
      valid: false,
      error: `Image is too large. Maximum allowed size is ${MAX_SIZE_MB} MB.`,
    };
  }

  if (file.size === 0) {
    return { valid: false, error: "The selected image is empty." };
  }

  return { valid: true };
}
