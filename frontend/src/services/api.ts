import type { AnalysisResponse, Language } from "../types/analysis";

const API_URL = import.meta.env.VITE_API_URL as string | undefined;

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function getBaseUrl(): string {
  if (!API_URL) {
    // Fails loudly in dev rather than silently hitting a relative path that
    // would 404 in a confusing way. See frontend/.env.example.
    throw new ApiError(
      "The app is not configured with a backend URL (VITE_API_URL is missing).",
      0,
    );
  }
  return API_URL.replace(/\/$/, "");
}

export async function analyzeCrop(
  image: File,
  text: string,
  language: Language,
  signal?: AbortSignal,
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("image", image);
  if (text.trim()) {
    formData.append("text", text.trim());
  }
  formData.append("language", language);

  let response: Response;
  try {
    response = await fetch(`${getBaseUrl()}/api/v1/analyze`, {
      method: "POST",
      body: formData,
      signal,
    });
  } catch {
    // Network-level failure (backend down, CORS, offline, etc.)
    throw new ApiError(
      "Unable to reach the analysis service. Please check your connection and try again.",
      0,
    );
  }

  if (!response.ok) {
    let detail = "Unable to analyze the image right now. Please try again.";
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // Response wasn't JSON — keep the generic message. Never surface raw HTML/text errors.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as AnalysisResponse;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${getBaseUrl()}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
