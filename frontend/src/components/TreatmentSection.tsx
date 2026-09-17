interface TreatmentSectionProps {
  title: string;
  items: string[];
  variant: "organic" | "chemical";
}

export function TreatmentSection({ title, items, variant }: TreatmentSectionProps) {
  if (items.length === 0) return null;

  const badgeClasses =
    variant === "organic"
      ? "bg-leaf-light text-leaf-dark"
      : "bg-soil/10 text-soil";

  return (
    <div className="rounded-card border border-leaf-light bg-white p-4">
      <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium mb-2 ${badgeClasses}`}>
        {title}
      </span>
      <ul className="space-y-1.5">
        {items.map((item, i) => (
          <li key={i} className="text-sm text-ink">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
