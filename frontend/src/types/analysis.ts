// Keep in sync with backend/app/models/schemas.py — this is the frontend/backend contract.

export type Language = "en" | "hi" | "te";

export interface AnalysisResponse {
  crop: string;
  disease: string;
  confidence: number; // 0.0 - 1.0
  symptoms: string[];
  causes: string[];
  prevention: string[];
  organic_treatment: string[];
  chemical_treatment: string[];
  recommendation: string;
  language: Language;
  is_mock: boolean;
  is_fallback: boolean;
}

export interface DiseaseListItem {
  key: string;
  crop: string;
  disease: string;
}

export const LANGUAGE_LABELS: Record<Language, string> = {
  en: "English",
  hi: "हिंदी",
  te: "తెలుగు",
};
