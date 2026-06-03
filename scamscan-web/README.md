# ScamScan — web demo

The multi-page web app for the scam-message classifier. It reads a message, returns a
calibrated verdict across four fraud classes, and then does the part that matters: it tells
the user the **risk**, **what to do next**, and **who to report it to** in their region.

**Live:** https://scamscan-web.vercel.app

## What it demonstrates

- **Live classifier** — the message is sent to the hosted FastAPI model and scored across
  `phishing`, `mobile_money_fraud`, `advance_fee_fraud`, and `not_a_scam`.
- **Action layer (Tier 1)** — every verdict shows a colour-coded risk level, a plain-language
  read of what the message is trying to do, class-specific safety steps (e.g. *never share a
  PIN or OTP*), and a region selector that swaps in real reporting contacts for Kenya, Nigeria,
  Ghana, and a global fallback.
- **The story** — Problem, Approach (corpus -> TF-IDF -> model -> API), live Demo, Results
  (per-class F1), and Future work, with an interactive orbital view of the four classes.

## Stack

Next.js 16 (App Router, RSC) - React 19 - TypeScript - Tailwind CSS v4 - Framer Motion - GSAP -
lucide-react. Classical-ML backend (TF-IDF + Logistic Regression) served via FastAPI.

## Run it locally

    npm install
    npm run dev          # http://localhost:3000

By default the app calls the hosted API. To point it elsewhere, set `NEXT_PUBLIC_API_BASE` in
`.env.local`. Production build: `npm run build && npm start`.

## Deployment

Hosted on Vercel: `npx vercel deploy --prod`.

## Note on the reporting contacts

The agency numbers and links in the action panel (`src/lib/guidance.ts`) are real, public
reporting channels verified at build time, shown with a "confirm on the agency's own site
before acting" note. Re-verify periodically.
