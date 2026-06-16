"use client";

import { Clipboard, Download, FileText, Loader2, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useMemo, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const canGenerate = useMemo(() => repositoryUrl.trim().length > 0 && !loading, [repositoryUrl, loading]);

  async function handleGenerate() {
    setLoading(true);
    setError("");
    setMarkdown("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repository_url: repositoryUrl.trim() })
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail ?? "Unable to generate README.md.");
      }
      setMarkdown(data.markdown);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected error.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!markdown) return;
    await navigator.clipboard.writeText(markdown);
  }

  function handleDownload() {
    if (!markdown) return;
    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "README.md";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main className="min-h-screen">
      <section className="border-b border-ink/10 bg-paper">
        <div className="mx-auto flex min-h-[92vh] max-w-7xl flex-col gap-8 px-5 py-6 sm:px-8 lg:px-10">
          <header className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="grid h-10 w-10 place-items-center rounded-md bg-ink text-paper">
                <FileText size={20} aria-hidden="true" />
              </div>
              <span className="text-lg font-semibold tracking-normal">AI Documentation Generator</span>
            </div>
          </header>

          <div className="grid flex-1 gap-6 lg:grid-cols-[420px_1fr]">
            <aside className="flex flex-col justify-center gap-5">
              <div>
                <h1 className="max-w-3xl text-4xl font-semibold tracking-normal text-ink sm:text-5xl">
                  Generate a professional README.md from a GitHub repository.
                </h1>
                <p className="mt-4 max-w-xl text-base leading-7 text-ink/70">
                  Paste a public repository URL, analyze its structure, dependencies, configuration, and routes, then produce clean Markdown ready for your project.
                </p>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium text-ink" htmlFor="repo-url">
                  Repository URL
                </label>
                <input
                  id="repo-url"
                  value={repositoryUrl}
                  onChange={(event) => setRepositoryUrl(event.target.value)}
                  placeholder="https://github.com/owner/repository"
                  className="h-12 w-full rounded-md border border-ink/15 bg-white px-4 text-sm outline-none transition focus:border-steel focus:ring-4 focus:ring-steel/15"
                />
                <button
                  type="button"
                  disabled={!canGenerate}
                  onClick={handleGenerate}
                  className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-md bg-coral px-4 text-sm font-semibold text-white transition hover:bg-coral/90 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? <Loader2 className="animate-spin" size={18} aria-hidden="true" /> : <Sparkles size={18} aria-hidden="true" />}
                  Generate
                </button>
                {error ? <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
              </div>
            </aside>

            <section className="flex min-h-[560px] flex-col overflow-hidden rounded-md border border-ink/10 bg-white shadow-sm">
              <div className="flex items-center justify-between gap-3 border-b border-ink/10 px-4 py-3">
                <span className="text-sm font-semibold text-ink">Markdown preview</span>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleCopy}
                    disabled={!markdown}
                    title="Copy Markdown"
                    className="grid h-9 w-9 place-items-center rounded-md border border-ink/10 text-ink transition hover:bg-mint disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <Clipboard size={17} aria-hidden="true" />
                  </button>
                  <button
                    type="button"
                    onClick={handleDownload}
                    disabled={!markdown}
                    title="Download README.md"
                    className="grid h-9 w-9 place-items-center rounded-md border border-ink/10 text-ink transition hover:bg-mint disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <Download size={17} aria-hidden="true" />
                  </button>
                </div>
              </div>
              <div className="flex-1 overflow-auto p-5">
                {loading ? (
                  <div className="flex h-full items-center justify-center text-sm text-ink/60">Analyzing repository and drafting README.md...</div>
                ) : markdown ? (
                  <article className="prose max-w-none prose-headings:text-ink prose-a:text-steel prose-pre:bg-ink">
                    <ReactMarkdown>{markdown}</ReactMarkdown>
                  </article>
                ) : (
                  <div className="flex h-full items-center justify-center text-center text-sm text-ink/55">
                    Generated Markdown will appear here.
                  </div>
                )}
              </div>
            </section>
          </div>
        </div>
      </section>
    </main>
  );
}
