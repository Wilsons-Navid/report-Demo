# ScamScan — web demo

Multi-page web app for the scam-message classifier: reads a message, returns a verdict across
four fraud classes, then shows the **risk**, **what to do next**, and **who to report it to** by region.

**Live:** https://scamscan-web.vercel.app

Next.js 16 · React 19 · TypeScript · Tailwind v4 · Framer Motion · GSAP. Visual system follows a
Stripe-derived token set (`DESIGN.md`, via getdesign.md). Real photography from Pexels.

Run: `npm install && npm run dev`. Build: `npm run build`. Deploy: `npx vercel deploy --prod`.
Set `NEXT_PUBLIC_API_BASE` in `.env.local` to point at a different API.
