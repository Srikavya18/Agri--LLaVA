interface ConfidenceBadgeProps {
  confidence: number;
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const pct = Math.round(confidence * 100);

  let classes = "bg-leaf-light text-leaf-dark border-leaf/30";
  if (confidence < 0.5) {
    classes = "bg-alert-light text-alert border-alert/30";
  } else if (confidence < 0.75) {
    classes = "bg-amber-light text-amber border-amber/30";
  }

  return (
    <span className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium ${classes}`}>
      {pct}% confidence
    </span>
  );
}
