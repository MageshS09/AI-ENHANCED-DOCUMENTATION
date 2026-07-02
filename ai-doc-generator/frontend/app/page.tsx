"use client";

import {
  Copy,
  CircleCheck,
  ArrowDownToLine,
  ScrollText,
  Github,
  Loader2,
  Wand2,
  BrainCircuit,
  Zap,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useEffect, useMemo, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function Home() {
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [error, setError] = useState("");
  const [configError, setConfigError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!API_BASE_URL) {
      setConfigError(
        "Backend URL is not configured. Set NEXT_PUBLIC_API_BASE_URL in your deployment environment."
      );
    }
  }, []);

  const canGenerate = useMemo(
    () => repositoryUrl.trim().length > 0 && !loading && !configError,
    [repositoryUrl, loading, configError]
  );

  async function handleGenerate() {
    setLoading(true);
    setError("");
    setMarkdown("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repository_url: repositoryUrl.trim() }),
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
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
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
    <main className="min-h-screen overflow-x-hidden">
      {/* Ambient depth layers */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden="true">
        <div className="absolute -top-48 left-1/2 h-[640px] w-[900px] -translate-x-1/2 rounded-full bg-gold/[0.07] blur-[130px]" />
        <div className="absolute left-0 top-1/3 h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-violet/[0.08] blur-[110px]" />
        <div className="absolute bottom-0 right-0 h-[320px] w-[320px] translate-x-1/3 rounded-full bg-violet/[0.06] blur-[90px]" />
      </div>

      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col gap-12 px-5 py-8 sm:px-8 lg:px-10">

        {/* ── Header ── */}
        <header className="flex items-center justify-between gap-4 animate-fade-up">
          <div className="flex items-center gap-3.5">
            <div className="logo-icon grid h-11 w-11 place-items-center rounded-2xl text-gold">
              <BrainCircuit size={22} aria-hidden="true" />
            </div>
            <div className="flex items-baseline gap-0.5">
              <span className="font-serif text-xl font-bold tracking-tight text-cream">
                DocForge
              </span>
              <span className="font-serif text-xl font-bold text-gold">.</span>
            </div>
          </div>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="hidden items-center gap-2 rounded-full border border-gold/18 px-4 py-2 text-sm text-cream/55 transition hover:border-gold/38 hover:text-cream/90 sm:flex"
          >
            <Github size={15} aria-hidden="true" />
            Star on GitHub
          </a>
        </header>

        {/* ── Main Grid ── */}
        <section className="grid flex-1 items-start gap-10 lg:grid-cols-[460px_1fr]">

          {/* Left — controls */}
          <aside className="flex flex-col gap-7 animate-fade-up">

            {/* AI badge */}
            <div className="badge-3d inline-flex w-fit items-center gap-2 rounded-full px-3.5 py-1.5 text-[11px] font-semibold uppercase tracking-widest">
              <Zap size={11} className="text-gold" aria-hidden="true" />
              <span className="text-gold/80">Powered by Groq · Llama 3.3 70B</span>
            </div>

            {/* Hero heading */}
            <div>
              <h1 className="font-serif text-[2.6rem] font-bold leading-[1.13] tracking-tight text-cream sm:text-[3.1rem]">
                Turn any repo into a{" "}
                <span className="text-shimmer">polished README</span>
                {" "}in seconds.
              </h1>

              {/* Classic ornament divider */}
              <div className="ornament-divider my-5">
                <span />
                <span className="text-[9px] text-gold/35 select-none">◆</span>
                <span />
              </div>

              <p className="max-w-xl text-base leading-7 text-cream/52">
                Paste a public GitHub repository URL. We analyze its structure,
                dependencies, configuration, and routes, then draft clean,
                accurate Markdown — ready to ship.
              </p>
            </div>

            {/* Form card */}
            <div className="panel-3d space-y-4 rounded-3xl p-6">
              {configError ? (
                <div className="rounded-xl border border-red-400/25 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {configError}
                </div>
              ) : null}

              <div className="space-y-2">
                <label
                  htmlFor="repo-url"
                  className="block text-[11px] font-semibold uppercase tracking-widest text-cream/45"
                >
                  Repository URL
                </label>
                <input
                  id="repo-url"
                  value={repositoryUrl}
                  onChange={(e) => setRepositoryUrl(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && canGenerate) handleGenerate();
                  }}
                  placeholder="https://github.com/owner/repository"
                  className="input-3d h-12 w-full rounded-xl px-4 text-sm text-cream outline-none placeholder:text-cream/25"
                />
              </div>

              <button
                type="button"
                disabled={!canGenerate}
                onClick={handleGenerate}
                className="btn-generate inline-flex h-12 w-full items-center justify-center gap-2.5 rounded-xl text-sm font-bold tracking-wide disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={17} aria-hidden="true" />
                ) : (
                  <Wand2 size={17} aria-hidden="true" />
                )}
                {loading ? "Generating..." : "Generate README"}
              </button>

              {error ? (
                <p className="rounded-xl border border-red-400/25 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {error}
                </p>
              ) : null}
            </div>

            {/* Stats */}
            <dl className="grid grid-cols-3 gap-3 text-center">
              {[
                ["Free", "to use"],
                ["~10s", "avg. generation"],
                ["Public", "repos only"],
              ].map(([value, label]) => (
                <div key={value} className="stat-card rounded-2xl px-2 py-4">
                  <dt className="font-serif text-lg font-bold text-gold">{value}</dt>
                  <dd className="mt-0.5 text-[11px] text-cream/38">{label}</dd>
                </div>
              ))}
            </dl>
          </aside>

          {/* Right — output panel */}
          <section className="output-panel flex min-h-[620px] flex-col overflow-hidden rounded-3xl animate-fade-up-delay">

            {/* Panel toolbar */}
            <div className="flex items-center justify-between gap-3 border-b border-white/[0.06] px-6 py-4">
              <div className="flex items-center gap-2.5">
                <span className="h-2.5 w-2.5 rounded-full bg-red-400/75" />
                <span className="h-2.5 w-2.5 rounded-full bg-yellow-400/75" />
                <span className="h-2.5 w-2.5 rounded-full bg-green-400/75" />
                <div className="ml-3 flex items-center gap-1.5 text-sm font-medium text-cream/38">
                  <ScrollText size={13} aria-hidden="true" />
                  README.md
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleCopy}
                  disabled={!markdown}
                  title="Copy Markdown"
                  className="icon-btn grid h-9 w-9 place-items-center rounded-lg"
                >
                  {copied ? (
                    <CircleCheck size={15} aria-hidden="true" className="text-green-400" />
                  ) : (
                    <Copy size={15} aria-hidden="true" />
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleDownload}
                  disabled={!markdown}
                  title="Download README.md"
                  className="icon-btn grid h-9 w-9 place-items-center rounded-lg"
                >
                  <ArrowDownToLine size={15} aria-hidden="true" />
                </button>
              </div>
            </div>

            {/* Panel body */}
            <div className="scrollbar-thin flex-1 overflow-auto p-7">
              {loading ? (
                <div className="flex h-full flex-col items-center justify-center gap-4 text-sm text-cream/40">
                  <Loader2 className="animate-spin text-gold" size={30} aria-hidden="true" />
                  <span className="tracking-wider">Analyzing repository and drafting README...</span>
                </div>
              ) : markdown ? (
                <article className="prose prose-invert max-w-none prose-headings:font-serif prose-headings:text-cream prose-a:text-gold prose-strong:text-cream prose-code:text-gold prose-pre:bg-black/40 prose-pre:border prose-pre:border-white/10">
                  <ReactMarkdown>{markdown}</ReactMarkdown>
                </article>
              ) : (
                <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
                  <div className="empty-icon-box grid h-14 w-14 place-items-center rounded-2xl">
                    <ScrollText size={24} aria-hidden="true" className="text-gold/45" />
                  </div>
                  <p className="text-sm text-cream/30">Generated Markdown will appear here.</p>
                </div>
              )}
            </div>
          </section>
        </section>

        {/* ── Footer ── */}
        <footer className="flex flex-col items-center justify-between gap-2 border-t border-gold/[0.10] py-6 text-xs text-cream/28 sm:flex-row">
          <span className="font-serif italic">
            Built for developers who&rsquo;d rather ship than write docs.
          </span>
          <div className="flex items-center gap-3">
            <span className="tracking-widest uppercase text-gold/38">
              AI Documentation Generator
            </span>
            <span className="text-gold/20">·</span>
            <span className="text-cream/35">
              Created by <span className="font-semibold text-gold/60">Magesh S</span>
            </span>
          </div>
        </footer>
      </div>
    </main>
  );
}
