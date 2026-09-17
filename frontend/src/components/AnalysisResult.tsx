import { useState } from "react";
import { Volume2, VolumeX, Copy, Check, RotateCcw } from "lucide-react";
import type { AnalysisResponse } from "../types/analysis";
import { SPEECH_LANG_CODES } from "../utils/languageCodes";
import { useSpeechSynthesis } from "../hooks/useSpeechSynthesis";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { DiseaseInformation } from "./DiseaseInformation";
import { TreatmentSection } from "./TreatmentSection";

interface AnalysisResultProps {
  result: AnalysisResponse;
  onNewAnalysis: () => void;
}

function buildSpokenSummary(result: AnalysisResponse): string {
  const parts = [
    `${result.crop}. ${result.disease}.`,
    result.symptoms.length ? `Symptoms: ${result.symptoms.join(". ")}.` : "",
    result.prevention.length ? `Prevention: ${result.prevention.join(". ")}.` : "",
    result.recommendation,
  ];
  return parts.filter(Boolean).join(" ");
}

export function AnalysisResult({ result, onNewAnalysis }: AnalysisResultProps) {
  const { isSupported: ttsSupported, isSpeaking, speak, stop } = useSpeechSynthesis();
  const [copied, setCopied] = useState(false);

  const handleSpeak = () => {
    if (isSpeaking) {
      stop();
      return;
    }
    speak(buildSpokenSummary(result), SPEECH_LANG_CODES[result.language]);
  };

  const handleCopy = async () => {
    const text = [
      `Crop: ${result.crop}`,
      `Disease: ${result.disease}`,
      `Confidence: ${Math.round(result.confidence * 100)}%`,
      result.symptoms.length ? `Symptoms: ${result.symptoms.join(", ")}` : "",
      result.causes.length ? `Causes: ${result.causes.join(", ")}` : "",
      result.prevention.length ? `Prevention: ${result.prevention.join(", ")}` : "",
      result.organic_treatment.length ? `Organic treatment: ${result.organic_treatment.join(", ")}` : "",
      result.chemical_treatment.length ? `Chemical treatment: ${result.chemical_treatment.join(", ")}` : "",
      `Recommendation: ${result.recommendation}`,
    ]
      .filter(Boolean)
      .join("\n");

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API can fail on insecure contexts; fail silently, button just won't confirm.
    }
  };

  return (
    <section className="rounded-card border border-leaf-light bg-white p-6 space-y-6">
      {result.is_mock && (
        <div className="rounded-card bg-amber-light border border-amber/30 px-4 py-2 text-xs text-amber">
          Development preview — this result comes from the mock inference service, not the
          trained model.
        </div>
      )}

      {result.is_fallback && (
        <div className="rounded-card bg-alert-light border border-alert/30 px-4 py-2 text-xs text-alert">
          We couldn't generate a confident result for this image. Try a clearer photo of the
          affected leaf.
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm text-ink-soft">{result.crop}</p>
          <h2 className="text-2xl font-display font-semibold text-forest">{result.disease}</h2>
        </div>
        <ConfidenceBadge confidence={result.confidence} />
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <DiseaseInformation title="Symptoms" items={result.symptoms} />
        <DiseaseInformation title="Causes" items={result.causes} />
      </div>

      <DiseaseInformation title="Prevention" items={result.prevention} />

      <div className="grid gap-4 sm:grid-cols-2">
        <TreatmentSection title="Organic Treatment" items={result.organic_treatment} variant="organic" />
        <TreatmentSection title="Chemical Treatment" items={result.chemical_treatment} variant="chemical" />
      </div>

      <div className="rounded-card bg-leaf-light px-4 py-3 text-sm text-forest">
        {result.recommendation}
      </div>

      <div className="flex flex-wrap gap-3 pt-2 border-t border-leaf-light">
        {ttsSupported ? (
          <button
            type="button"
            onClick={handleSpeak}
            className="flex items-center gap-2 rounded-full border border-leaf-light px-4 py-2 text-sm text-forest hover:bg-leaf-light transition-colors"
          >
            {isSpeaking ? <VolumeX size={16} /> : <Volume2 size={16} />}
            {isSpeaking ? "Stop" : "Speak Response"}
          </button>
        ) : (
          <span className="text-xs text-ink-soft self-center">
            Text-to-speech is not supported in this browser.
          </span>
        )}

        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-2 rounded-full border border-leaf-light px-4 py-2 text-sm text-forest hover:bg-leaf-light transition-colors"
        >
          {copied ? <Check size={16} /> : <Copy size={16} />}
          {copied ? "Copied" : "Copy"}
        </button>

        <button
          type="button"
          onClick={onNewAnalysis}
          className="flex items-center gap-2 rounded-full bg-forest text-paper px-4 py-2 text-sm hover:bg-leaf-dark transition-colors ml-auto"
        >
          <RotateCcw size={16} />
          Analyze Another Image
        </button>
      </div>
    </section>
  );
}
