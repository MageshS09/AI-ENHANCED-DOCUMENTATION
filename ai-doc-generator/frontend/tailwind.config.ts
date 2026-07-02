import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18212f",
        paper: "#f7f8f5",
        mint: "#d7f5df",
        coral: "#f06f5f",
        steel: "#3c6e71",
        midnight: "#07080e",
        surface: "#0c0d18",
        panel: "#0f1020",
        gold: "#c9a227",
        "gold-light": "#e8c84a",
        "gold-dim": "#7a6118",
        violet: "#6c47ff",
        cream: "#f0ebe0",
        bronze: "#cd7f32",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui"],
        display: ["var(--font-display)", "ui-sans-serif", "system-ui"],
        serif: ["var(--font-serif)", "Georgia", "ui-serif"],
      },
      boxShadow: {
        glow: "0 0 60px -10px rgba(201, 162, 39, 0.45)",
        "glow-violet": "0 0 60px -10px rgba(108, 71, 255, 0.45)",
        premium: "0 24px 60px -20px rgba(0,0,0,0.7)",
        depth: "0 2px 2px rgba(0,0,0,0.14), 0 4px 4px rgba(0,0,0,0.14), 0 8px 8px rgba(0,0,0,0.14), 0 16px 16px rgba(0,0,0,0.12), 0 32px 32px rgba(0,0,0,0.10)",
      },
      backgroundImage: {
        "grid-faint":
          "linear-gradient(to right, rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px)",
      },
    }
  },
  plugins: [require("@tailwindcss/typography")]
};

export default config;
