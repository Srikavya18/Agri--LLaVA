import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  messages: readonly string[];
}

export function LoadingState({ messages }: LoadingStateProps) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    setIndex(0);
    const interval = setInterval(() => {
      setIndex((i) => Math.min(i + 1, messages.length - 1));
    }, 1800);
    return () => clearInterval(interval);
  }, [messages]);

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center gap-3 rounded-card border border-leaf-light bg-white p-5 text-ink-soft"
    >
      <Loader2 size={20} className="animate-spin text-leaf shrink-0" />
      <span>{messages[index]}</span>
    </div>
  );
}
