import Link from "next/link";
import { ArrowRight, Database, Cpu, Gauge } from "lucide-react";
import { Hero } from "@/components/site/hero";
import { Reveal } from "@/components/site/reveal";
import { FraudOrbital } from "@/components/site/fraud-orbital";

const steps = [
  { icon: Database, t: "Collect", d: "Pool public corpora (Nazario, MOZ-Smishing, Mendeley, UCI) into one schema, deduplicate and clean." },
  { icon: Cpu, t: "Model", d: "TF-IDF features into Logistic Regression and Random Forest, compared on a held-out split." },
  { icon: Gauge, t: "Serve", d: "Ship the best model behind a FastAPI endpoint with this live web app." },
];

const stats = [
  { v: "0.94", l: "test macro-F1" },
  { v: "95.8%", l: "accuracy" },
  { v: "4", l: "fraud classes" },
  { v: "en · pt", l: "languages" },
];

export default function Home() {
  return (
    <>
      <Hero />

      {/* THE PROBLEM */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto grid max-w-5xl items-center gap-8 md:grid-cols-2">
          <div>
            <p className="mono-label">The problem</p>
            <h2 className="font-display mt-3 text-4xl font-bold leading-[1.05]">
              Fraud now arrives as a message
            </h2>
            <p className="mt-5 max-w-md text-[15px] leading-relaxed text-slate-600">
              Phishing links, mobile-money cons and advance-fee lures reach people directly over
              SMS, email and wallet apps. Where mobile money is the main way to hold and move cash,
              one tapped link or shared PIN can empty an account in seconds, and the transfer is
              rarely reversible.
            </p>
            <p className="mt-3 max-w-md text-[15px] leading-relaxed text-slate-600">
              Generic spam filters learn from Western email. They miss the code-mixed,
              region-specific, wallet-centric scams that do the real damage here.
            </p>
            <Link href="/problem" className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-[var(--brand-ink)] transition-all hover:gap-3">
              See the problem in full <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="glass-card overflow-hidden rounded-3xl p-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/africa-street.jpg" alt="Banknotes changing hands at a market stall, the cash economy mobile money rides on" className="h-64 w-full rounded-[1.1rem] object-cover md:h-80" />
          </div>
        </Reveal>
      </section>

      {/* THE SOLUTION — four classes */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto max-w-5xl">
          <h2 className="font-display text-4xl font-bold leading-[1.05]">One verdict, four fraud classes</h2>
          <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-slate-600">
            ScamScan reads the message text itself. No metadata, no account access. It returns a
            calibrated score across the classes that matter in this context.
          </p>
        </Reveal>
        <div className="mx-auto mt-8 max-w-5xl">
          <div
            className="relative overflow-hidden rounded-[2rem] border border-slate-200"
            style={{
              background: "radial-gradient(120% 90% at 50% 0%, #122441 0%, #0a1224 55%, #070b16 100%)",
              boxShadow: "0 30px 80px -42px rgba(15,23,42,.5)",
            }}
          >
            <FraudOrbital />
          </div>
          <p className="mx-auto mt-4 max-w-sm text-center text-xs text-slate-400">
            Tap a node to inspect the class, its test F1, and the classes it gets confused with.
          </p>
        </div>
      </section>

      {/* THE APPROACH */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto max-w-5xl">
          <h2 className="font-display text-4xl font-bold leading-[1.05]">From corpus to live verdict</h2>
          <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-slate-600">
            Three moves: pool public corpora into one clean schema, train and compare classical
            models, then serve the winner behind a hosted API.
          </p>
        </Reveal>
        <div className="mx-auto mt-10 grid max-w-5xl gap-4 md:grid-cols-3">
          {steps.map((s, i) => {
            const Icon = s.icon;
            return (
              <Reveal key={s.t} delay={i * 0.08}>
                <div className="h-full rounded-2xl glass-card p-6">
                  <div className="flex items-center justify-between">
                    <Icon className="h-6 w-6 text-[var(--brand-ink)]" />
                    <span className="font-mono text-xs text-slate-400">0{i + 1}</span>
                  </div>
                  <h3 className="font-display mt-5 text-xl font-bold">{s.t}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">{s.d}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
        <Reveal className="mx-auto mt-8 max-w-5xl">
          <Link href="/how-it-works" className="inline-flex items-center gap-2 text-sm font-medium text-[var(--brand-ink)] transition-all hover:gap-3">
            See the full pipeline <ArrowRight className="h-4 w-4" />
          </Link>
        </Reveal>
      </section>

      {/* RESULTS */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto max-w-5xl rounded-3xl glass-card p-8 md:p-10">
          <p className="mono-label">Results</p>
          <h2 className="font-display mt-3 text-4xl font-bold leading-[1.05]">Measured, not claimed</h2>
          <div className="mt-8 grid grid-cols-2 gap-6 md:grid-cols-4">
            {stats.map((s) => (
              <div key={s.l}>
                <div className="font-display text-4xl font-bold tabular-nums">{s.v}</div>
                <div className="mt-1 text-xs uppercase tracking-widest text-slate-500">{s.l}</div>
              </div>
            ))}
          </div>
          <p className="mt-8 max-w-2xl text-sm leading-relaxed text-slate-500">
            These figures come from the initial, source-labelled corpus, so they read slightly
            high. The dissertation re-evaluates the model on a human, inter-rater-verified set.
          </p>
          <Link href="/model" className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-[var(--brand-ink)] transition-all hover:gap-3">
            Read the full results <ArrowRight className="h-4 w-4" />
          </Link>
        </Reveal>
      </section>

      {/* FUTURE */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto max-w-5xl">
          <h2 className="font-display text-4xl font-bold leading-[1.05]">Where it goes next</h2>
          <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-slate-600">
            A language-model arm to benchmark against the classical baseline, synthetic-media
            (deepfake) and romance and identity-theft classes once data exists, more languages and
            dialects, and a layer that helps a person act on a verdict, not just read it.
          </p>
          <Link href="/future" className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-[var(--brand-ink)] transition-all hover:gap-3">
            The roadmap <ArrowRight className="h-4 w-4" />
          </Link>
        </Reveal>
      </section>

      {/* CTA */}
      <section className="px-6 pt-28">
        <Reveal className="glass-card mx-auto flex max-w-5xl flex-col items-center gap-6 rounded-3xl px-8 py-14 text-center">
          <h2 className="font-display max-w-2xl text-4xl font-bold leading-[1.05] md:text-5xl">
            Paste a message. Get a verdict in a second.
          </h2>
          <Link
            href="/classify"
            className="inline-flex items-center gap-2 rounded-full bg-[var(--brand-ink)] px-8 py-4 font-semibold text-white transition hover:-translate-y-0.5"
            style={{ boxShadow: "0 18px 40px -14px rgba(83,58,253,.45), inset 0 1px 0 rgba(255,255,255,.5)" }}
          >
            Open the classifier <ArrowRight className="h-4 w-4" />
          </Link>
        </Reveal>
      </section>
    </>
  );
}
