import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, ShieldCheck, Feather, Server } from "lucide-react";
import { HowSteps } from "@/components/site/how-steps";
import { Reveal } from "@/components/site/reveal";

export const metadata: Metadata = {
  title: "The approach — ScamScan",
  description: "The pipeline from public corpora to a live, served scam-message classifier, and why the baseline is deliberately classical.",
};

const why = [
  { icon: ShieldCheck, t: "Interpretable", d: "A linear model over TF-IDF features can be read term by term. For a fraud tool, being able to say why a message was flagged matters as much as the verdict itself." },
  { icon: Feather, t: "Robust on a small corpus", d: "Verified scam data is scarce. A classical model learns a stable boundary from a few thousand examples, where a heavier model would overfit and memorise." },
  { icon: Server, t: "Cheap to serve", d: "The whole pipeline runs on free-tier infrastructure and answers in milliseconds. Reach across low-cost devices matters more than a fraction of a point." },
];

export default function HowItWorksPage() {
  return (
    <>
      <section className="px-6 pt-32">
        <Reveal className="mx-auto max-w-3xl">
          <p className="mono-label">The approach</p>
          <h1 className="font-display mt-3 text-5xl font-bold leading-[1.03]">
            From corpus to <span className="text-gradient-amber">verdict</span>
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-slate-600">
            The problem is regional and language-shaped, so the build is too. Six stages turn a
            pile of public scam datasets into one classifier you can call live. Follow the rail
            down.
          </p>
        </Reveal>
      </section>

      <section className="px-6 pt-16">
        <HowSteps />
      </section>

      {/* why classical */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto max-w-5xl">
          <h2 className="font-display text-3xl font-bold leading-[1.08]">Why a classical model, on purpose</h2>
          <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-slate-600">
            A large language model was the obvious reach. For the baseline the dissertation argues
            the opposite, and keeps the LLM as a measured comparison in future work.
          </p>
        </Reveal>
        <div className="mx-auto mt-10 grid max-w-5xl gap-4 md:grid-cols-3">
          {why.map((w, i) => {
            const Icon = w.icon;
            return (
              <Reveal key={w.t} delay={i * 0.07}>
                <div className="h-full rounded-2xl glass-card p-6">
                  <Icon className="h-6 w-6 text-[var(--brand-ink)]" />
                  <h3 className="font-display mt-5 text-lg font-bold">{w.t}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">{w.d}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </section>

      {/* CTA row */}
      <section className="px-6 pt-24 pb-4">
        <Reveal className="mx-auto flex max-w-5xl flex-col items-start gap-4 sm:flex-row sm:items-center">
          <Link
            href="/classify"
            className="inline-flex items-center gap-2 rounded-full bg-[var(--brand-ink)] px-6 py-3.5 font-semibold text-white transition hover:-translate-y-0.5"
            style={{ boxShadow: "0 16px 36px -14px rgba(83,58,253,.45), inset 0 1px 0 rgba(255,255,255,.5)" }}
          >
            Try it live <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/model"
            className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 px-6 py-3.5 font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-900/5"
          >
            See the results <ArrowRight className="h-4 w-4" />
          </Link>
        </Reveal>
      </section>
    </>
  );
}
