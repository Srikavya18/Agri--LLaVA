import type { Language } from "../types/analysis";

// BCP-47 language tags for the Web Speech API (recognition + synthesis).
// India-localized variants per the project spec.
export const SPEECH_LANG_CODES: Record<Language, string> = {
  en: "en-IN",
  hi: "hi-IN",
  te: "te-IN",
};
