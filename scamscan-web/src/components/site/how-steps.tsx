"use client";

import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { Database, Filter, Tags, Cpu, SplitSquareHorizontal, Server } from "lucide-react";

gsap.registerPlugin(ScrollTrigger, useGSAP);

const STAGES = [
  { icon: Database, t: "Sources", d: "Public corpora are pulled in: UCI SMS, the Nazario phishing/419 email set, the Mendeley SMS-phishing dataset, and MOZ-Smishing (Portuguese mobile-money)." },
  { icon: Filter, t: "Normalise", d: "Everything is mapped to one schema, schema-validated, exact- and near-deduplicated (Jaccard size-banding), and length-filtered — 8,536 unique messages." },
  { icon: Tags, t: "Label", d: "The demo model uses each source's own labels. The final evaluation uses a human, inter-rater-verified corpus (Cohen's κ ≥ 0.7)." },
  { icon: Cpu, t: "Features", d: "Messages become TF-IDF vectors: word 1–2 grams, sublinear term frequency, accent-stripped, a 30k vocabulary." },
  { icon: SplitSquareHorizontal, t: "Train & compare", d: "TF-IDF → Logistic Regression vs Random Forest, on a 70/15/15 stratified split. Logistic Regression wins at macro-F1 0.94." },
  { icon: Server, t: "Serve", d: "The fitted pipeline ships behind a FastAPI endpoint with Swagger, consumed by this web app." },
];

export function HowSteps() {
  const root = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.utils.toArray<HTMLElement>(".how-step").forEach((el) => {
      gsap.from(el, {
        opacity: 0, y: 56, duration: 0.8, ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 82%" },
      });
    });
    gsap.fromTo(".how-line-fill",
      { scaleY: 0 },
      { scaleY: 1, transformOrigin: "top", ease: "none",
        scrollTrigger: { trigger: root.current, start: "top 55%", end: "bottom 75%", scrub: true } });
  }, { scope: root });

  return (
    <div ref={root} className="relative mx-auto max-w-3xl pl-12">
      {/* progress rail */}
      <div className="absolute left-[18px] top-2 bottom-2 w-px bg-slate-900/10" />
      <div className="how-line-fill absolute left-[18px] top-2 bottom-2 w-px bg-[var(--brand-ink)]" />

      <div className="flex flex-col gap-12">
        {STAGES.map((s, i) => {
          const Icon = s.icon;
          return (
            <div key={s.t} className="how-step relative">
              <span className="absolute -left-12 grid h-9 w-9 place-items-center rounded-xl border border-slate-200 bg-white text-[var(--brand-ink)] shadow-sm">
                <Icon className="h-[18px] w-[18px]" />
              </span>
              <span className="font-mono text-xs text-slate-400">Stage 0{i + 1}</span>
              <h3 className="font-display mt-1 text-2xl font-bold">{s.t}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-500">{s.d}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
