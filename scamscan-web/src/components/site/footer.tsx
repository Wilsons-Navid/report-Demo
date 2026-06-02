import Link from "next/link";
import { ShieldCheck, ExternalLink } from "lucide-react";

export function Footer() {
  return (
    <footer className="mt-24 border-t border-slate-200 px-6 py-12">
      <div className="mx-auto flex max-w-5xl flex-col gap-8 md:flex-row md:items-start md:justify-between">
        <div className="max-w-sm">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-[var(--brand-ink)]" />
            <span className="font-display text-lg font-bold">ScamScan</span>
          </div>
          <p className="mt-3 text-sm text-slate-500">
            Initial model · TF-IDF + Logistic Regression · test macro-F1 0.94. The final
            evaluation uses a human, inter-rater-verified corpus.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-10 text-sm">
          <div className="flex flex-col gap-2">
            <span className="mb-1 text-xs uppercase tracking-widest text-slate-400">The story</span>
            <Link href="/problem" className="text-slate-600 hover:text-slate-900">Problem</Link>
            <Link href="/how-it-works" className="text-slate-600 hover:text-slate-900">Approach</Link>
            <Link href="/classify" className="text-slate-600 hover:text-slate-900">Demo</Link>
            <Link href="/model" className="text-slate-600 hover:text-slate-900">Results</Link>
            <Link href="/future" className="text-slate-600 hover:text-slate-900">Future work</Link>
          </div>
          <div className="flex flex-col gap-2">
            <span className="mb-1 text-xs uppercase tracking-widest text-slate-400">Links</span>
            <a href="https://scam-classifier-api.onrender.com/docs" className="flex items-center gap-1.5 text-slate-600 hover:text-slate-900" target="_blank" rel="noreferrer">API · Swagger</a>
            <a href="https://github.com/Wilsons-Navid/report-Demo" className="flex items-center gap-1.5 text-slate-600 hover:text-slate-900" target="_blank" rel="noreferrer"><ExternalLink className="h-3.5 w-3.5" /> GitHub</a>
          </div>
        </div>
      </div>
      <p className="mx-auto mt-10 max-w-5xl text-xs text-slate-400">
        © {new Date().getFullYear()} ScamScan — capstone demonstration.
      </p>
    </footer>
  );
}
