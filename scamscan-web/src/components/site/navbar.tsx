"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

const links = [
  { href: "/problem", label: "Problem" },
  { href: "/how-it-works", label: "Approach" },
  { href: "/classify", label: "Demo" },
  { href: "/model", label: "Results" },
  { href: "/future", label: "Future" },
];

export function Navbar() {
  const path = usePathname();
  return (
    <motion.header
      initial={{ y: -28, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.2, 0.8, 0.2, 1] }}
      className="fixed top-0 inset-x-0 z-50 px-4 pt-4"
    >
      <nav className="glass-card mx-auto flex max-w-5xl items-center justify-between rounded-2xl px-4 py-2.5">
        <Link href="/" className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-[var(--brand-ink)]" />
          <span className="font-display text-lg font-bold tracking-tight">ScamScan</span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {links.map((l) => {
            const active = l.href === "/" ? path === "/" : path.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-full px-3.5 py-1.5 text-sm transition-colors ${
                  active ? "bg-slate-900/10 text-slate-900" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </div>

        <Link
          href="/classify"
          className="rounded-full bg-[var(--brand-ink)] px-4 py-1.5 text-sm font-semibold text-white transition-transform hover:-translate-y-0.5"
          style={{ boxShadow: "0 8px 22px -10px rgba(34,211,238,.7)" }}
        >
          Try it
        </Link>
      </nav>
    </motion.header>
  );
}
