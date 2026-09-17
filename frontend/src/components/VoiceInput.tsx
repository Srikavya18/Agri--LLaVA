import { useEffect } from "react";
import { Mic, MicOff } from "lucide-react";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";

interface VoiceInputProps {
  langCode: string;
  onTranscript: (text: string) => void;
}

export function VoiceInput({ langCode, onTranscript }: VoiceInputProps) {
  const { isSupported, isListening, transcript, error, start, stop } =
    useSpeechRecognition(langCode);

  useEffect(() => {
    if (transcript) {
      onTranscript(transcript);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [transcript]);

  if (!isSupported) {
    return (
      <p className="text-xs text-ink-soft">
        Voice input isn't supported in this browser. You can type your question instead.
      </p>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={isListening ? stop : start}
        aria-pressed={isListening}
        aria-label={isListening ? "Stop recording" : "Start voice input"}
        className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors border ${
          isListening
            ? "bg-alert-light text-alert border-alert/30"
            : "bg-white text-forest border-leaf-light hover:bg-leaf-light"
        }`}
      >
        {isListening ? <MicOff size={16} /> : <Mic size={16} />}
        {isListening ? "Listening… Stop Recording" : "Voice Input"}
      </button>
      {error && <span className="text-xs text-alert">{error}</span>}
    </div>
  );
}
