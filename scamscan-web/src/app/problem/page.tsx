import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, MessageSquare, Mail, Smartphone, Globe, Filter } from "lucide-react";
import { Reveal } from "@/components/site/reveal";

export const metadata: Metadata = {
  title: "The problem — ScamScan",
  description:
    "Why scam messages over SMS, email and mobile money hit hardest in low-resource markets, and why generic spam filters miss them.",
};

const channels = [
  { icon: MessageSquare, t: "SMS & smishing", d: "Text messages carrying a malicious link or a fake alert. No app, no account, just a phone number and a plausible sender name." },
  { icon: Smartphone, t: "Mobile money", d: "M-Pesa, MoMo and agent scams that ask for a PIN, an OTP, or a reversal of a 'wrong' transfer. The money moves immediately." },
  { icon: Mail, t: "Email", d: "Classic phishing and advance-fee lures, still effective and still arriving in the same inbox as legitimate mail." },
];

const whyHarder = [
  { t: "Mobile money is the account", d: "For many people a wallet is the primary way to hold and move cash. A drained wallet is not an inconvenience, it is the savings." },
  { t: "Transfers rarely reverse", d: "Once a payment or PIN leaves the device, recovery is unlikely. Prevention at the message is the only reliable point of control." },
  { t: "Language is mixed", d: "Messages blend English, Portuguese and local languages in one line. Filters tuned to a single language lose the signal." },
];

export default function ProblemPage() {
  return (
    <>
      {/* hero */}
      <section className="px-6 pt-32">
        <Reveal className="mx-auto max-w-3xl">
          <p className="mono-label">The problem</p>
          <h1 className="font-display mt-3 text-5xl font-bold leading-[1.03]">
            Fraud arrives as a message
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-slate-600">
            The scam that costs someone their savings is no longer a phone call from a stranger.
            It is a single text, email, or wallet prompt that looks ordinary enough to act on.
            That shift is what ScamScan is built for.
          </p>
        </Reveal>
        <Reveal delay={0.1} className="mx-auto mt-12 max-w-5xl">
          <div className="glass-card overflow-hidden rounded-3xl p-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/scam-message.jpg" alt="A hand holding a phone showing a suspicious text message" className="h-64 w-full rounded-[1.1rem] object-cover object-center md:h-80" />
          </div>
        </Reveal>
      </section>

      {/* channels */}
      <section className="px-6 pt-24">
        <Reveal className="mx-auto max-w-5xl">
          <h2 className="font-display text-3xl font-bold">Three channels, one inbox</h2>
          <p className="mt-3 max-w-xl text-[15px] leading-relaxed text-slate-500">
            Fraud reaches people through the same channels they use for everything else, which is
            exactly why it works.
          </p>
        </Reveal>
        <div className="mx-auto mt-10 grid max-w-5xl gap-4 md:grid-cols-3">
          {channels.map((c, i) => {
            const Icon = c.icon;
            return (
              <Reveal key={c.t} delay={i * 0.07}>
                <div className="h-full rounded-2xl glass-card p-6">
                  <Icon className="h-6 w-6 text-[var(--brand-ink)]" />
                  <h3 className="font-display mt-5 text-lg font-bold">{c.t}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">{c.d}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </section>

      {/* why harder here */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto grid max-w-5xl items-center gap-8 md:grid-cols-[1fr_.9fr]">
          <div>
            <h2 className="font-display text-3xl font-bold leading-[1.08]">Why it hits harder in low-resource markets</h2>
            <div className="mt-7 flex flex-col gap-6">
              {whyHarder.map((w) => (
                <div key={w.t} className="border-t border-slate-200 pt-5">
                  <h3 className="font-display text-lg font-semibold text-slate-800">{w.t}</h3>
                  <p className="mt-2 max-w-md text-sm leading-relaxed text-slate-600">{w.d}</p>
                </div>
              ))}
            </div>
          </div>
          <Reveal delay={0.1} className="glass-card overflow-hidden rounded-3xl p-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/person-phone.jpg" alt="A person reading an incoming message on their phone" className="h-72 w-full rounded-[1.1rem] object-cover md:h-[26rem]" />
          </Reveal>
        </Reveal>
      </section>

      {/* why filters fail */}
      <section className="px-6 pt-28">
        <Reveal className="mx-auto max-w-4xl rounded-3xl glass-card p-8 md:p-10">
          <div className="flex items-start gap-4">
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-[var(--brand-ink)]/15 text-[var(--brand-ink)]">
              <Filter className="h-5 w-5" />
            </span>
            <div>
              <h2 className="font-display text-2xl font-bold">Why generic filters miss it</h2>
              <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-slate-600">
                Most spam classifiers were trained on Western, English-language email. They learn
                the shape of that fraud well, and almost nothing about a Portuguese M-Pesa PIN
                request or a code-mixed prize lure sent over SMS. A model that never saw the
                problem cannot catch it.
              </p>
              <p className="mt-3 max-w-2xl text-[15px] leading-relaxed text-slate-600">
                ScamScan starts from a corpus built around these channels and these languages, and
                reads the message text on its own terms.
              </p>
            </div>
          </div>
        </Reveal>
      </section>

      {/* transition */}
      <section className="px-6 pt-24 pb-4">
        <Reveal className="mx-auto flex max-w-4xl flex-col items-start gap-5 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <Globe className="h-6 w-6 text-[var(--brand-ink)]" />
            <p className="max-w-md text-[15px] leading-relaxed text-slate-600">
              The problem is regional and language-shaped. So is the solution.
            </p>
          </div>
          <Link
            href="/how-it-works"
            className="inline-flex shrink-0 items-center gap-2 rounded-2xl bg-[var(--brand-ink)] px-6 py-3.5 font-semibold text-white transition hover:-translate-y-0.5"
            style={{ boxShadow: "0 16px 36px -14px rgba(34,211,238,.7), inset 0 1px 0 rgba(255,255,255,.5)" }}
          >
            See the approach <ArrowRight className="h-4 w-4" />
          </Link>
        </Reveal>
      </section>
    </>
  );
}
