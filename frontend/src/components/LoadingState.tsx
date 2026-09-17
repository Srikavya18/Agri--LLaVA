import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

const MESSAGES = [
  "Checking the leaf image…",
  "Analyzing your crop…",
  "Generating disease explanation…",
];

export function LoadingState() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((i) => Math.min(i + 1, MESSAGES.length - 1));
    }, 1800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center gap-3 rounded-card border border-leaf-light bg-white p-5 text-ink-soft"
    >
      <Loader2 size={20} className="animate-spin text-leaf shrink-0" />
      <span>{MESSAGES[index]}</span>
    </div>
  );
}
