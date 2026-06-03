# ScamScan — web demo

The multi-page web app for the scam-message classifier. It reads a message, returns a
calibrated verdict across four fraud classes, and then tells the user the **risk**, **what to
do next**, and **who to report it to** in their region.

**Live:** https://scamscan-web.vercel.app

## Demonstrates
- **Live classifier** scoring `phishing`, `mobile_money_fraud`, `advance_fee_fraud`, `not_a_scam` via the hosted FastAPI model.
- **Action layer (Tier 1):** risk level, a plain-language read of what the message is trying to do, class-specific safety steps, and a region selector with real reporting contacts (Kenya/Nigeria/Ghana/global).
- **The story:** Problem, Approach, live Demo, Results (per-class F1), Future work + an orbital view of the classes.

## Stack & design
Next.js 16 (App Router) · React 19 · TypeScript · Tailwind v4 · Framer Motion · GSAP. Visual system follows a Stripe-derived token set (`DESIGN.md`, via getdesign.md): blurple accent, navy ink, soft canvas, pill CTAs.

## Run
    npm install
    npm run dev          # http://localhost:3000
Set `NEXT_PUBLIC_API_BASE` in `.env.local` to change the API. Build: `npm run build && npm start`. Deploy: `npx vercel deploy --prod`.
