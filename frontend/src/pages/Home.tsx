import { useState } from "react";
import { ImageUploader } from "../components/ImageUploader";
import { QuestionInput } from "../components/QuestionInput";
import { VoiceInput } from "../components/VoiceInput";
import { LanguageSelector } from "../components/LanguageSelector";
import { AnalyzeButton } from "../components/AnalyzeButton";
import { LoadingState } from "../components/LoadingState";
import { ErrorMessage } from "../components/ErrorMessage";
import { AnalysisResult } from "../components/AnalysisResult";
import { analyzeCrop, ApiError } from "../services/api";
import { SPEECH_LANG_CODES } from "../utils/languageCodes";
import type { AnalysisResponse, Language } from "../types/analysis";

export function Home() {
  const [image, setImage] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState<Language>("en");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const handleAnalyze = async () => {
    if (!image) return;
    setLoading(true);
    setError(null);
    try {
      const response = await analyzeCrop(image, question, language);
      setResult(response);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Unable to analyze the image right now. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleNewAnalysis = () => {
    setImage(null);
    setQuestion("");
    setResult(null);
    setError(null);
  };

  return (
    <div id="top" className="mx-auto max-w-3xl px-6 py-12 space-y-14">
      <section className="space-y-4">
        <h1 className="text-4xl sm:text-5xl font-display font-semibold leading-tight max-w-xl">
          Know what's wrong with your crop, today
        </h1>
        <p className="text-lg text-ink-soft max-w-xl">
          Upload a crop leaf image and get an AI-powered explanation of possible diseases,
          causes, prevention, and treatment.
        </p>
      </section>

      <section className="space-y-5">
        <ImageUploader
          image={image}
          onImageSelected={(file) => {
            setImage(file);
            setResult(null);
            setError(null);
          }}
          onImageRemoved={() => {
            setImage(null);
            setResult(null);
          }}
          onValidationError={(message) => setError(message)}
        />

        <QuestionInput value={question} onChange={setQuestion} />

        <div className="flex flex-wrap items-center justify-between gap-4">
          <VoiceInput
            langCode={SPEECH_LANG_CODES[language]}
            onTranscript={(text) => setQuestion(text)}
          />
          <LanguageSelector value={language} onChange={setLanguage} />
        </div>

        <AnalyzeButton disabled={!image} loading={loading} onClick={handleAnalyze} />

        {loading && <LoadingState />}
        {error && !loading && <ErrorMessage message={error} />}
      </section>

      {result && !loading && (
        <section>
          <AnalysisResult result={result} onNewAnalysis={handleNewAnalysis} />
        </section>
      )}

      <section id="how-it-works" className="space-y-6 pt-6 border-t border-leaf-light">
        <h2 className="text-2xl font-display font-semibold">How it works</h2>
        <ol className="grid gap-6 sm:grid-cols-3">
          <li className="space-y-1">
            <span className="text-sm font-medium text-leaf">1. Upload</span>
            <p className="text-sm text-ink-soft">
              Take or choose a clear photo of the affected leaf.
            </p>
          </li>
          <li className="space-y-1">
            <span className="text-sm font-medium text-leaf">2. Analyze</span>
            <p className="text-sm text-ink-soft">
              The system checks the image against known crop diseases.
            </p>
          </li>
          <li className="space-y-1">
            <span className="text-sm font-medium text-leaf">3. Get guidance</span>
            <p className="text-sm text-ink-soft">
              Read or listen to symptoms, causes, and treatment steps.
            </p>
          </li>
        </ol>
      </section>

      <section id="about" className="space-y-3 pt-6 border-t border-leaf-light">
        <h2 className="text-2xl font-display font-semibold">About</h2>
        <p className="text-sm text-ink-soft max-w-xl">
          Agri-LLaVA combines computer vision and a vision-language model with a grounded
          agricultural knowledge base, so explanations stay tied to real, documented disease
          information rather than invented facts.
        </p>
      </section>
    </div>
  );
}
