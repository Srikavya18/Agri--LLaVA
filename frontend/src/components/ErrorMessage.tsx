import { AlertTriangle } from "lucide-react";

interface ErrorMessageProps {
  message: string;
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-card border border-alert/30 bg-alert-light p-4 text-alert"
    >
      <AlertTriangle size={18} className="shrink-0 mt-0.5" />
      <span className="text-sm">{message}</span>
    </div>
  );
}
