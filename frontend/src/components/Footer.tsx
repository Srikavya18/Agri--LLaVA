import type { Language } from "../types/analysis";
import { useUIStrings } from "../utils/uiStrings";

interface FooterProps {
  language: Language;
}

export function Footer({ language }: FooterProps) {
  const strings = useUIStrings(language);

  return (
    <footer className="border-t border-leaf-light mt-16">
      <div className="mx-auto max-w-3xl px-6 py-8 text-sm text-ink-soft font-body space-y-2">
        <p>{strings.footerDisclaimer}</p>
        <p className="text-ink-soft/70">Built as a portfolio project · Agri-LLaVA</p>
      </div>
    </footer>
  );
}
