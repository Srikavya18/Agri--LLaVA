import { Leaf } from "lucide-react";

export function Header() {
  return (
    <header className="border-b border-leaf-light bg-paper/95 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto max-w-3xl px-6 py-4 flex items-center justify-between">
        <a href="#top" className="flex items-center gap-2 text-forest">
          <Leaf size={22} strokeWidth={2.2} />
          <span className="font-display text-lg font-semibold tracking-tight">Agri-LLaVA</span>
        </a>
        <nav className="flex items-center gap-6 text-sm font-body text-ink-soft">
          <a href="#top" className="hover:text-forest transition-colors">
            Home
          </a>
          <a href="#how-it-works" className="hover:text-forest transition-colors">
            How It Works
          </a>
          <a href="#about" className="hover:text-forest transition-colors">
            About
          </a>
        </nav>
      </div>
    </header>
  );
}
