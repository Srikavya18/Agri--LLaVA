interface DiseaseInformationProps {
  title: string;
  items: string[];
}

export function DiseaseInformation({ title, items }: DiseaseInformationProps) {
  if (items.length === 0) return null;

  return (
    <div>
      <h3 className="text-base font-display font-semibold text-forest mb-2">{title}</h3>
      <ul className="space-y-1.5">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2 text-sm text-ink">
            <span className="text-leaf mt-1.5 block h-1 w-1 rounded-full bg-leaf shrink-0" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
