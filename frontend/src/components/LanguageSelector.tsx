import type { Language } from "../types/analysis";
import { LANGUAGE_LABELS } from "../types/analysis";

interface LanguageSelectorProps {
  value: Language;
  onChange: (language: Language) => void;
}

const LANGUAGES: Language[] = ["en", "hi", "te"];

export function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
  return (
    <div>
      <label htmlFor="language" className="block text-sm font-medium text-ink mb-2">
        Language
      </label>
      <select
        id="language"
        value={value}
        onChange={(e) => onChange(e.target.value as Language)}
        className="rounded-full border border-leaf-light bg-white px-4 py-2 text-sm text-ink focus:border-leaf focus:ring-0"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang} value={lang}>
            {LANGUAGE_LABELS[lang]}
          </option>
        ))}
      </select>
    </div>
  );
}
