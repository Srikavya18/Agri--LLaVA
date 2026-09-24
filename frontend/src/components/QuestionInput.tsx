interface QuestionInputProps {
  value: string;
  onChange: (value: string) => void;
  label: string;
  placeholder: string;
}

export function QuestionInput({ value, onChange, label, placeholder }: QuestionInputProps) {
  return (
    <div>
      <label htmlFor="question" className="block text-sm font-medium text-ink mb-2">
        {label}
      </label>
      <textarea
        id="question"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={3}
        className="w-full rounded-card border border-leaf-light bg-white p-4 text-ink placeholder:text-ink-soft/60 focus:border-leaf focus:ring-0 resize-none"
      />
    </div>
  );
}
