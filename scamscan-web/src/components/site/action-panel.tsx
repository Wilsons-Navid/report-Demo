"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ExternalLink, CheckCircle2 } from "lucide-react";
import type { ClassKey } from "@/lib/api";
import { riskFor, STEPS, REGIONS, INTENT } from "@/lib/guidance";

const TONE = {
  high: { bg: "bg-rose-50", border: "border-rose-200", text: "text-rose-800", chip: "bg-rose-700" },
  elevated: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-900", chip: "bg-amber-700" },
  safe: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-800", chip: "bg-emerald-700" },
} as const;

export function ActionPanel({ category, confidence }: { category: string; confidence: number }) {
  const [regionId, setRegionId] = useState(REGIONS[0].id);
  const risk = riskFor(category, confidence);
  const steps = STEPS[category as ClassKey] ?? STEPS.not_a_scam;
  const region = REGIONS.find((r) => r.id === regionId) ?? REGIONS[0];
  const tone = TONE[risk.level];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="glass-card rounded-2xl p-6 md:p-7"
    >
      {/* risk banner */}
      <div className={`flex flex-wrap items-center gap-x-3 gap-y-1.5 rounded-xl border ${tone.border} ${tone.bg} px-4 py-3.5`}>
        <span className={`rounded-md px-2 py-0.5 text-[11px] font-bold uppercase tracking-wider text-white ${tone.chip}`}>
          {risk.label}
        </span>
        <p className={`text-sm font-medium ${tone.text}`}>
          {INTENT[category as ClassKey] ?? INTENT.not_a_scam}
        </p>
      </div>

      <div className="mt-6 grid gap-8 md:grid-cols-2">
        {/* what to do */}
        <div>
          <h3 className="font-display text-lg font-bold text-slate-900">What to do now</h3>
          <ul className="mt-4 flex flex-col gap-3">
            {steps.map((s, i) => (
              <li key={i} className="flex gap-2.5 text-sm leading-relaxed text-slate-600">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[var(--brand-ink)]" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* who to contact */}
        <div>
          <div className="flex items-center justify-between gap-3">
            <h3 className="font-display text-lg font-bold text-slate-900">Who to contact</h3>
            <select
              value={regionId}
              onChange={(e) => setRegionId(e.target.value)}
              aria-label="Select your region"
              className="rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-sm text-slate-700 outline-none transition focus:border-[var(--brand-ink)]"
            >
              {REGIONS.map((r) => (
                <option key={r.id} value={r.id}>{r.label}</option>
              ))}
            </select>
          </div>
          <ul className="mt-4 flex flex-col">
            {region.contacts.map((c, i) => (
              <li key={i} className="flex items-start justify-between gap-3 border-b border-slate-100 py-2.5 last:border-0">
                <span className="text-sm text-slate-600">{c.label}</span>
                {c.href ? (
                  <a href={c.href} target="_blank" rel="noreferrer" className="inline-flex shrink-0 items-center gap-1 text-sm font-semibold text-[var(--brand-ink)] hover:underline">
                    {c.value}
                    <ExternalLink className="h-3 w-3" />
                  </a>
                ) : (
                  <span className="shrink-0 font-mono text-sm font-semibold text-slate-900">{c.value}</span>
                )}
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-400">
            Official reporting channels. Confirm details on the agency’s own site before acting.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
