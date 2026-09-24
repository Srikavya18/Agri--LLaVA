import { useState } from "react";
import { Header } from "./components/Header";
import { Footer } from "./components/Footer";
import { Home } from "./pages/Home";
import type { Language } from "./types/analysis";

function App() {
  const [language, setLanguage] = useState<Language>("en");

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Home language={language} onLanguageChange={setLanguage} />
      </main>
      <Footer language={language} />
    </div>
  );
}

export default App;
