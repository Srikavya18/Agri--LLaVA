/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        forest: "#25402B",
        leaf: "#5B8C3E",
        "leaf-light": "#EAF3E4",
        "leaf-dark": "#3E6B2A",
        soil: "#8C6239",
        paper: "#FBF9F4",
        ink: "#20241F",
        "ink-soft": "#4A4F45",
        alert: "#B3261E",
        "alert-light": "#FBEAE9",
        amber: "#9A6B00",
        "amber-light": "#FBF2DC",
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "serif"],
        body: ["Work Sans", "Segoe UI", "sans-serif"],
      },
      borderRadius: {
        card: "16px",
      },
    },
  },
  plugins: [],
};
