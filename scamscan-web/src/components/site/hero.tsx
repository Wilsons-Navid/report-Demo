"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

const headline = ["Read", "a", "message.", "Know", "its", "intent."];

const chip = [
  { name: "Advance-Fee Fraud", v: 98.3, color: "var(--c-advance)" },
  { name: "Phishing", v: 0.9, color: "var(--c-phishing)" },
  { name: "Not a Scam", v: 0.6, color: "var(--c-safe)" },
  { name: "Mobile-Money Fraud", v: 0.2, color: "var(--c-momo)" },
];

export function Hero() {
  return (
    <section className="relative flex min-h-[90dvh] items-center px-6 pt-28">
      <div className="mx-auto grid w-full max-w-6xl items-center gap-12 lg:grid-cols-[1.05fr_.95fr]">
        {/* copy */}
        <div>
          <motion.span
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-600 shadow-sm"
          >
            <Sparkles className="h-3.5 w-3.5 text-[var(--brand-ink)]" />
            Scam-message intelligence
          </motion.span>

          <h1 className="font-display mt-6 text-5xl font-bold leading-[0.98] tracking-tight text-slate-900 sm:text-6xl lg:text-7xl">
            {headline.map((w, i) => (
              <motion.span
                key={i}
                initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.15 + i * 0.07, ease: [0.2, 0.8, 0.2, 1] }}
                className={`mr-3 inline-block ${i >= 3 ? "text-[var(--brand-ink)]" : ""}`}
              >
                {w}
              </motion.span>
            ))}
          </h1>

          <motion.p
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7, duration: 0.6 }}
            className="mt-6 max-w-md text-base leading-relaxed text-slate-600"
          >
            A classical-ML classifier that flags <b className="font-semibold text-slate-900">phishing</b>,{" "}
            <b className="font-semibold text-slate-900">mobile-money fraud</b>, and{" "}
            <b className="font-semibold text-slate-900">advance-fee fraud</b> from a single message, served
            live over a hosted API.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.85, duration: 0.6 }}
            className="mt-9 flex flex-wrap items-center gap-4"
          >
            <Link
              href="/classify"
              className="group inline-flex items-center gap-2 rounded-2xl bg-[var(--brand-ink)] px-7 py-4 font-semibold text-white transition hover:-translate-y-0.5"
              style={{ boxShadow: "0 18px 40px -16px rgba(14,116,144,.55)" }}
            >
              Try the classifier
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <a
              href="https://scam-classifier-api.onrender.com/docs"
              target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-300 bg-white px-7 py-4 font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50"
            >
              View the API
            </a>
          </motion.div>
        </div>

        {/* real phone photo + floating verdict chip */}
        <motion.div
          initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.9, ease: [0.2, 0.8, 0.2, 1] }}
          className="relative hidden lg:block"
        >
          <div className="glass-card overflow-hidden rounded-[2rem] p-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/img/africa-phone-1.jpg"
              alt="A young woman in Abuja checking a message on her phone"
              className="h-[30rem] w-full rounded-[1.6rem] object-cover object-top"
            />
          </div>
          <div className="floaty glass-card absolute -bottom-6 -left-6 w-[280px] rounded-2xl p-5">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Verdict</p>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="font-display text-4xl font-bold tabular-nums" style={{ color: "var(--c-advance)" }}>98%</span>
              <span className="text-[10px] uppercase tracking-widest text-slate-400">confidence</span>
            </div>
            <div className="font-display text-lg font-bold" style={{ color: "var(--c-advance)" }}>Advance-Fee Fraud</div>
            <div className="mt-4 flex flex-col gap-2.5">
              {chip.map((c) => (
                <div key={c.name}>
                  <div className="flex justify-between text-[11px] text-slate-600">
                    <span>{c.name}</span>
                    <span className="tabular-nums text-slate-400">{c.v}%</span>
                  </div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full rounded-full" style={{ width: `${c.v}%`, background: c.color }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
