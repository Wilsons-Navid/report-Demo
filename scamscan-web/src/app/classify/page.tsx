import type { Metadata } from "next";
import Link from "next/link";
import { Classifier } from "@/components/site/classifier";
import { Reveal } from "@/components/site/reveal";

export const metadata: Metadata = {
  title: "Live demo — ScamScan",
  description: "Paste a message and get a live fraud-class prediction from the hosted model.",
};

export default function ClassifyPage() {
  return (
    <>
      <section className="px-6 pt-32">
        <Reveal className="mx-auto max-w-3xl">
          <p className="mono-label">Live demo</p>
          <h1 className="font-display mt-3 text-5xl font-bold leading-[1.03]">
            Classify a <span className="text-gradient-amber">message</span>
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-slate-600">
            The same pipeline from the approach page, running live. Your text is scored across the
            four classes, then every verdict comes with a risk level, what to do next, and who to
            report it to in your region. On the free tier the first call can take 30 to 50 seconds
            to wake the server, then it is instant.
          </p>
          <div className="mt-5 flex flex-wrap gap-x-6 gap-y-2 text-sm">
            <Link href="/how-it-works" className="font-medium text-[var(--brand-ink)] hover:underline">How it&apos;s built →</Link>
            <Link href="/model" className="font-medium text-[var(--brand-ink)] hover:underline">How accurate it is →</Link>
          </div>
        </Reveal>
      </section>

      <section className="px-6 pt-12 pb-4">
        <Reveal delay={0.1} className="mx-auto max-w-5xl">
          <Classifier />
        </Reveal>
      </section>
    </>
  );
}
