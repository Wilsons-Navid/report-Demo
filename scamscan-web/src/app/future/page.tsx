import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, BrainCircuit, ScanFace, Languages, HeartCrack, Network, ShieldHalf } from "lucide-react";
import { Reveal } from "@/components/site/reveal";

export const metadata: Metadata = {
  title: "Future work — ScamScan",
  description:
    "The roadmap beyond the initial classifier: a language-model arm, synthetic-media fraud, new classes, more languages, and an action-enabling layer.",
};

const roadmap = [
  { icon: BrainCircuit, t: "A language-model arm", d: "Benchmark an LLM classifier against the classical baseline on the same verified corpus, to measure what the heavier model actually buys in accuracy, cost and latency." },
  { icon: ScanFace, t: "Synthetic-media fraud", d: "Voice clones and deepfake video are the next channel. Detecting them is out of scope for a text model, and squarely on the roadmap." },
  { icon: HeartCrack, t: "Romance & identity theft", d: "Two more fraud classes the field needs. Both wait on real message data, since no public text datasets exist for them yet." },
  { icon: Languages, t: "More languages and dialects", d: "The corpus starts in English and Portuguese. Adding regional languages and code-mixed dialects widens coverage where the fraud actually lands." },
];

export default function FuturePage() {
  return (
    <>
      {/* hero */}
      <section className="px-6 pt-32">
        <Reveal className="mx-auto max-w-3xl">
          <p className="mono-label">Future work</p>
          <h1 className="font-display mt-3 text-5xl font-bold leading-[1.03]">
            Where it goes next
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-slate-600">
            The initial model is a baseline, not a finish line. The dissertation scopes a clear
            line between what ships now and what comes after, so the claims stay honest.
          </p>
        </Reveal>
      </section>

      {/* roadmap grid */}
      <section className="px-6 pt-24">
        <Reveal className="mx-auto max-w-5xl">
          <h2 className="font-display text-3xl font-bold">On the roadmap</h2>
        </Reveal>
        <div className="mx-auto mt-10 grid max-w-5xl gap-4 md:grid-cols-2">
          {roadmap.map((r, i) => {
            const Icon = r.icon;
            return (
              <Reveal key={r.t} delay={i * 0.06}>
                <div className="h-full rounded-2xl glass-card p-6">
                  <Icon className="h-6 w-6 text-[var(--brand-ink)]" />
                  <h3 className="font-display mt-5 text-lg font-bold">{r.t}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">{r.d}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </section>

      {/* the action layer / escalation tiers */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto max-w-5xl">
          <div className="flex items-center gap-3">
            <ShieldHalf className="h-6 w-6 text-[var(--brand-ink)]" />
            <h2 className="font-display text-3xl font-bold">From a verdict to an action</h2>
          </div>
          <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-slate-600">
            A score is only useful if a person can act on it. The design separates that into three
            tiers, and is deliberate about which one is in scope now.
          </p>
        </Reveal>
        <div className="mx-auto mt-10 grid max-w-5xl gap-4 md:grid-cols-3">
          <Reveal>
            <div className="h-full rounded-2xl border border-[var(--brand)]/40 bg-[var(--brand-ink)]/[0.07] p-6">
              <span className="rounded-full bg-[var(--brand-ink)]/20 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-[var(--brand-ink)]">In scope</span>
              <h3 className="font-display mt-4 text-lg font-bold">Tier 1 · Help me act</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                The interface turns a verdict into a next step: block, report, or verify through an
                official channel. The user stays in control.
              </p>
            </div>
          </Reveal>
          <Reveal delay={0.07}>
            <div className="h-full rounded-2xl glass-card p-6">
              <span className="rounded-full bg-slate-900/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">Future</span>
              <h3 className="font-display mt-4 text-lg font-bold">Tier 2 · Partner escalation</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                With the user's consent, forward a confirmed scam to a telecom or bank partner. A
                partnership and a consent model, not just code.
              </p>
            </div>
          </Reveal>
          <Reveal delay={0.14}>
            <div className="h-full rounded-2xl glass-card p-6">
              <span className="rounded-full bg-slate-900/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">Future</span>
              <h3 className="font-display mt-4 text-lg font-bold">Tier 3 · Automated response</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                Network-level action on high-confidence campaigns. The most powerful tier, and the
                one with the highest bar for accuracy and governance.
              </p>
            </div>
          </Reveal>
        </div>
      </section>

      {/* data partnerships */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto max-w-4xl rounded-3xl glass-card p-8 md:p-10">
          <div className="flex items-start gap-4">
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-[var(--brand-ink)]/15 text-[var(--brand-ink)]">
              <Network className="h-5 w-5" />
            </span>
            <div>
              <h2 className="font-display text-2xl font-bold">Better data, not just bigger models</h2>
              <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-slate-600">
                The hardest constraint is real, regional scam data. The strongest gains will come
                from collaboration with regional smishing-honeynet research and consented
                user reports, feeding a continuously verified corpus rather than a one-time
                snapshot.
              </p>
            </div>
          </div>
        </Reveal>
      </section>

      {/* close */}
      <section className="px-6 pt-24 pb-4">
        <Reveal className="mx-auto flex max-w-4xl flex-col items-start gap-5 md:flex-row md:items-center md:justify-between">
          <p className="max-w-md text-[15px] leading-relaxed text-slate-600">
            Want to see what already works today?
          </p>
          <Link
            href="/classify"
            className="inline-flex shrink-0 items-center gap-2 rounded-2xl bg-[var(--brand-ink)] px-6 py-3.5 font-semibold text-white transition hover:-translate-y-0.5"
            style={{ boxShadow: "0 16px 36px -14px rgba(34,211,238,.7), inset 0 1px 0 rgba(255,255,255,.5)" }}
          >
            Try the live demo <ArrowRight className="h-4 w-4" />
          </Link>
        </Reveal>
      </section>
    </>
  );
}
