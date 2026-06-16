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
        steel: "#3c6e71"
      }
    }
  },
  plugins: [require("@tailwindcss/typography")]
};

export default config;
