"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Loader2, ScanLine } from "lucide-react";
import {
  classify, CATS, EXAMPLES, catColor, catName, type Prediction,
} from "@/lib/api";
import { ActionPanel } from "@/components/site/action-panel";

function useCountUp(target: number, run: boolean, ms = 750) {
  const [v, setV] = useState(0);
  useEffect(() => {
    if (!run) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) { setV(target); return; }
    const start = performance.now();
    let raf = 0;
    const step = (now: number) => {
      const p = Math.min(1, (now - start) / ms);
      setV(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, run, ms]);
  return v;
}

export function Classifier() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Prediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);

  async function run() {
    if (!text.trim()) { taRef.current?.focus(); return; }
    setLoading(true); setError(null);
    try { setResult(await classify(text)); }
    catch (e) { setError(e instanceof Error ? e.message : "request failed"); setResult(null); }
    finally { setLoading(false); }
  }

  const top = result?.predicted_category;
  const conf = useCountUp(Math.round((result?.confidence ?? 0) * 100), !!result);
  const entries = result ? Object.entries(result.scores).sort((a, b) => b[1] - a[1]) : [];

  return (
    <div className="flex flex-col gap-5">
      <div className="grid gap-5 md:grid-cols-2">
      {/* INPUT */}
      <div className="glass-card relative overflow-hidden rounded-2xl p-6 md:p-7">
        <p className="text-xs uppercase tracking-[0.26em] text-slate-500">Intercept</p>
        <h2 className="font-display mt-2 text-2xl font-bold">Paste a message</h2>

        <textarea
          ref={taRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => { if ((e.metaKey || e.ctrlKey) && e.key === "Enter") run(); }}
          spellCheck={false}
          rows={5}
          aria-label="Message to classify"
          placeholder="e.g. URGENT! Your number won a 2000 prize — call 09061790121 to claim."
          className="mt-5 w-full resize-y rounded-xl border border-slate-200 bg-slate-50 p-4 font-mono text-sm leading-relaxed text-slate-800 outline-none transition focus:border-[var(--brand)] focus:ring-2 focus:ring-[var(--brand)]/25"
        />

        <div className="mt-4 flex flex-wrap gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex.label}
              type="button"
              onClick={() => { setText(ex.text); taRef.current?.focus(); }}
              className="group inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-900/5 px-3 py-1.5 text-xs text-slate-600 transition hover:border-slate-200 hover:text-slate-900"
            >
              <span className="h-1.5 w-1.5 rounded-full" style={{ background: catColor(ex.cat) }} />
              {ex.label}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={run}
          disabled={loading}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--brand-ink)] py-3.5 font-semibold text-white transition hover:-translate-y-0.5 disabled:opacity-60"
          style={{ boxShadow: "0 14px 32px -12px rgba(34,211,238,.7), inset 0 1px 0 rgba(255,255,255,.5)" }}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          {loading ? "Analysing" : "Classify"}
        </button>
        {loading && (
          <motion.div
            className="pointer-events-none absolute inset-x-0 top-0 h-1/3"
            style={{ background: "linear-gradient(180deg,transparent,rgba(34,211,238,.16),transparent)" }}
            animate={{ y: ["-60%", "320%"] }}
            transition={{ duration: 1.1, repeat: Infinity, ease: "easeInOut" }}
          />
        )}
      </div>

      {/* OUTPUT */}
      <div className="glass-card rounded-2xl p-6 md:p-7">
        <p className="text-xs uppercase tracking-[0.26em] text-slate-500">Verdict</p>

        <AnimatePresence mode="wait">
          {!result && !error && (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="mt-6 flex max-w-[36ch] flex-col gap-4 text-slate-500"
            >
              <ScanLine className="h-9 w-9 text-slate-300" />
              <p className="text-sm leading-relaxed">
                No result yet. Classify a message to see its predicted category and the
                score for each class.
              </p>
            </motion.div>
          )}

          {error && (
            <motion.div key="err" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="mt-6 rounded-xl border border-[var(--c-phishing)]/30 bg-[var(--c-phishing)]/10 p-4 text-sm text-[var(--c-phishing)]">
              <b>Could not reach the classifier.</b> {error}.<br />
              The API sleeps on the free tier — the first request can take 30–50s to wake up.
            </motion.div>
          )}

          {result && (
            <motion.div key="res" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }} className="mt-5">
              <div className="flex items-baseline gap-3">
                <span className="font-display text-6xl font-extrabold tabular-nums" style={{ color: catColor(top!) }}>
                  {conf}%
                </span>
                <span className="text-[11px] uppercase tracking-[0.24em] text-slate-500">confidence</span>
              </div>
              <div className="font-display mt-1 text-2xl font-bold" style={{ color: catColor(top!) }}>
                {catName(top!)}
              </div>
              <p className="mt-1 text-sm text-slate-500">
                {(CATS as Record<string, { note: string }>)[top!]?.note}
              </p>

              <div className="mt-7 flex flex-col gap-4">
                {entries.map(([cat, score], i) => (
                  <div key={cat} className="grid grid-cols-[1fr_auto] items-center gap-y-1.5">
                    <div className={`flex items-center gap-2 text-sm ${cat === top ? "font-semibold text-slate-900" : "text-slate-700"}`}>
                      <span className="h-2 w-2 rounded-[3px]" style={{ background: catColor(cat) }} />
                      {catName(cat)}
                    </div>
                    <div className="font-mono text-xs tabular-nums text-slate-500">{(score * 100).toFixed(1)}%</div>
                    <div className="col-span-2 h-[7px] overflow-hidden rounded-full bg-slate-900/10" style={{ boxShadow: "inset 0 1px 2px rgba(0,0,0,.5)" }}>
                      <motion.div
                        className="h-full rounded-full"
                        style={{ background: `linear-gradient(180deg,rgba(255,255,255,.4),transparent 55%), ${catColor(cat)}` }}
                        initial={{ width: 0 }} animate={{ width: `${score * 100}%` }}
                        transition={{ duration: 0.8, delay: 0.05 + i * 0.08, ease: [0.2, 0.85, 0.25, 1] }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      </div>

      {result && (
        <ActionPanel category={result.predicted_category} confidence={result.confidence} />
      )}
    </div>
  );
}
