import type { Metadata } from "next";
import Link from "next/link";
import { Reveal } from "@/components/site/reveal";
import { CATS } from "@/lib/api";
import { Info, ArrowRight } from "lucide-react";

export const metadata: Metadata = {
  title: "Results — ScamScan",
  description: "Architecture, metrics, per-class scores, and the honest limitations of the initial scam classifier.",
};

const models = [
  { name: "TF-IDF + Logistic Regression", acc: "0.958", f1: "0.943", best: true },
  { name: "TF-IDF + Random Forest (500)", acc: "0.950", f1: "0.928", best: false },
];

const perClass = [
  { key: "mobile_money_fraud", f1: 0.99 },
  { key: "phishing", f1: 0.96 },
  { key: "not_a_scam", f1: 0.96 },
  { key: "advance_fee_fraud", f1: 0.86 },
] as const;

export default function ModelPage() {
  return (
    <section className="px-6 pt-32 pb-4">
      <Reveal className="mx-auto max-w-4xl">
        <p className="mono-label">Results</p>
        <h1 className="font-display mt-3 text-5xl font-bold leading-[1.03]">
          What's under the <span className="text-gradient-amber">hood</span>
        </h1>
        <p className="mt-6 max-w-2xl text-base leading-relaxed text-slate-600">
          A deliberately classical pipeline: TF-IDF features feeding a linear model. Here is how the
          two candidates compare, how each class scores, and where the numbers should be read with
          care.
        </p>
      </Reveal>

      {/* model comparison */}
      <Reveal delay={0.05} className="mx-auto mt-12 max-w-4xl">
        <div className="grid gap-4 sm:grid-cols-2">
          {models.map((m) => (
            <div key={m.name} className={`rounded-2xl border p-6 ${m.best ? "border-[var(--brand)]/40 bg-[var(--brand-ink)]/[0.07]" : "border-slate-200 bg-slate-900/[0.03]"}`}>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">{m.name}</span>
                {m.best && <span className="rounded-full bg-[var(--brand-ink)]/20 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-[var(--brand-ink)]">served</span>}
              </div>
              <div className="mt-5 flex gap-8">
                <div>
                  <div className="font-display text-3xl font-bold tabular-nums">{m.acc}</div>
                  <div className="text-xs uppercase tracking-widest text-slate-400">accuracy</div>
                </div>
                <div>
                  <div className="font-display text-3xl font-bold tabular-nums text-[var(--brand-ink)]">{m.f1}</div>
                  <div className="text-xs uppercase tracking-widest text-slate-400">macro-F1</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Reveal>

      {/* per-class — dot plot on a zoomed 0.80–1.00 axis */}
      <Reveal delay={0.1} className="mx-auto mt-8 max-w-4xl rounded-2xl glass-card p-6 md:p-8">
        <div className="flex items-baseline justify-between">
          <h2 className="font-display text-xl font-bold">Per-class F1</h2>
          <span className="font-mono text-xs text-slate-500">held-out test · n = 664</span>
        </div>
        <div className="mt-7 flex flex-col gap-5">
          {perClass.map((p) => {
            const meta = CATS[p.key];
            const dot = ({ mobile_money_fraud: "#6d28d9", phishing: "#e11d48", not_a_scam: "#047857", advance_fee_fraud: "#b45309" } as Record<string, string>)[p.key] ?? meta.color;
            const pct = ((p.f1 - 0.8) / 0.2) * 100;
            return (
              <div key={p.key} className="grid grid-cols-[140px_1fr_40px] items-center gap-4 sm:grid-cols-[170px_1fr_44px]">
                <span className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: dot }} />
                  {meta.name}
                </span>
                <div className="relative h-1 rounded-full bg-slate-200">
                  <span
                    className="absolute top-1/2 h-3.5 w-3.5 -translate-y-1/2 rounded-full ring-2 ring-white"
                    style={{ left: `calc(${pct}% - 7px)`, background: dot, boxShadow: "0 1px 3px rgba(15,23,42,.3)" }}
                  />
                </div>
                <span className="text-right font-mono text-sm tabular-nums text-slate-800">{p.f1.toFixed(2)}</span>
              </div>
            );
          })}
        </div>
        <div className="mt-3 grid grid-cols-[140px_1fr_40px] gap-4 sm:grid-cols-[170px_1fr_44px]">
          <span />
          <div className="flex justify-between font-mono text-[10px] text-slate-400">
            <span>0.80</span>
            <span>0.90</span>
            <span>1.00</span>
          </div>
          <span />
        </div>
        <p className="mt-6 text-sm leading-relaxed text-slate-500">
          Advance-fee fraud trails the others: its lures overlap with both phishing and benign
          promotional copy, which is exactly the boundary the verified corpus is meant to sharpen.
        </p>
      </Reveal>

      {/* honesty + scope */}
      <Reveal delay={0.1} className="mx-auto mt-8 max-w-4xl">
        <div className="flex gap-3 rounded-2xl glass-card p-6">
          <Info className="mt-0.5 h-5 w-5 shrink-0 text-[var(--brand-ink)]" />
          <div className="text-sm leading-relaxed text-slate-600">
            <b className="text-slate-800">This is the initial model.</b> Its labels come from each
            source dataset, so the numbers are slightly optimistic. The dissertation's final
            evaluation runs on a human, inter-rater-verified corpus. Three further categories,
            romance, identity-theft, and synthetic-media (deepfake) fraud, are future work, since no
            public message datasets exist for them in text form.
          </div>
        </div>
      </Reveal>

      {/* CTA */}
      <Reveal delay={0.1} className="mx-auto mt-10 flex max-w-4xl flex-col items-start gap-4 sm:flex-row sm:items-center">
        <Link
          href="/classify"
          className="inline-flex items-center gap-2 rounded-2xl bg-[var(--brand-ink)] px-6 py-3.5 font-semibold text-white transition hover:-translate-y-0.5"
          style={{ boxShadow: "0 16px 36px -14px rgba(34,211,238,.7), inset 0 1px 0 rgba(255,255,255,.5)" }}
        >
          Test it on a message <ArrowRight className="h-4 w-4" />
        </Link>
        <Link
          href="/future"
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 px-6 py-3.5 font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-900/5"
        >
          What comes next <ArrowRight className="h-4 w-4" />
        </Link>
      </Reveal>
    </section>
  );
}
