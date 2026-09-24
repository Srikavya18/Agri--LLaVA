import { Search, Loader2 } from "lucide-react";

interface AnalyzeButtonProps {
  disabled: boolean;
  loading: boolean;
  onClick: () => void;
  label: string;
  loadingLabel: string;
}

export function AnalyzeButton({ disabled, loading, onClick, label, loadingLabel }: AnalyzeButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      className="w-full flex items-center justify-center gap-2 rounded-full bg-forest text-paper px-6 py-3.5 font-medium text-base hover:bg-leaf-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {loading ? <Loader2 size={18} className="animate-spin" /> : <Search size={18} />}
      {loading ? loadingLabel : label}
    </button>
  );
}
