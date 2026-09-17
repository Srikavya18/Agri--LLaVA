interface QuestionInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function QuestionInput({ value, onChange }: QuestionInputProps) {
  return (
    <div>
      <label htmlFor="question" className="block text-sm font-medium text-ink mb-2">
        Ask a question (optional)
      </label>
      <textarea
        id="question"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Describe what you observe on the plant or ask a question..."
        rows={3}
        className="w-full rounded-card border border-leaf-light bg-white p-4 text-ink placeholder:text-ink-soft/60 focus:border-leaf focus:ring-0 resize-none"
      />
    </div>
  );
}
