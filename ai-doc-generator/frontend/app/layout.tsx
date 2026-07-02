import type { Metadata } from "next";
import { Inter, Sora, Playfair_Display } from "next/font/google";
import "./globals.css";

const sans = Inter({ subsets: ["latin"], variable: "--font-sans" });
const display = Sora({ subsets: ["latin"], variable: "--font-display" });
const serif = Playfair_Display({ subsets: ["latin"], variable: "--font-serif" });

export const metadata: Metadata = {
  title: "AI Documentation Generator — Instant README.md from any GitHub repo",
  description:
    "Generate professional, production-ready README.md files from public GitHub repositories in seconds, powered by AI.",
  keywords: ["README generator", "AI documentation", "GitHub", "developer tools"],
  openGraph: {
    title: "AI Documentation Generator",
    description: "Generate professional README.md files from public GitHub repositories in seconds.",
    type: "website"
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${sans.variable} ${display.variable} ${serif.variable}`}>
      <body>{children}</body>
    </html>
  );
}
