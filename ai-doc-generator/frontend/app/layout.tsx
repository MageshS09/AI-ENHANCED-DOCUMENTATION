import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Documentation Generator",
  description: "Generate professional README.md files from public GitHub repositories."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
