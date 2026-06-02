import type { Metadata } from "next";
import { Geist, Geist_Mono, Space_Grotesk } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/site/navbar";
import { Footer } from "@/components/site/footer";

const sans = Geist({ variable: "--font-sans", subsets: ["latin"] });
const mono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });
// Technical grotesque for display — distinctive without reading as a fashion serif.
const display = Space_Grotesk({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

export const metadata: Metadata = {
  title: "ScamScan — Scam Message Intelligence",
  description:
    "A classical-ML classifier that reads a message and flags phishing, mobile-money fraud, and advance-fee fraud. Live demo with a hosted API.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body
        className={`${sans.variable} ${mono.variable} ${display.variable} antialiased min-h-dvh`}
      >
        {/* soft light atmosphere wash */}
        <div className="aurora" aria-hidden="true" />
        <Navbar />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
