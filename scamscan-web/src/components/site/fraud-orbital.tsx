"use client";

import { Smartphone, Link2, ShieldAlert, CheckCircle2 } from "lucide-react";
import RadialOrbitalTimeline from "@/components/ui/radial-orbital-timeline";
import { CATS } from "@/lib/api";

// The four classes as an orbital constellation. energy = per-class test F1,
// relatedIds = the classes the model most confuses each one with.
const fraudData = [
  {
    id: 1,
    title: "Mobile-Money Fraud",
    date: "F1 0.99",
    content:
      "Wallet, PIN, agent and OTP cons targeting M-Pesa, MoMo and similar. The strongest class: its language is distinctive enough to separate cleanly.",
    category: "fraud",
    icon: Smartphone,
    relatedIds: [2],
    status: "completed" as const,
    energy: 99,
    color: CATS.mobile_money_fraud.color,
  },
  {
    id: 2,
    title: "Phishing",
    date: "F1 0.96",
    content:
      "Credential and link harvesting that impersonates a bank, telecom or service. Overlaps with advance-fee lures at the edges.",
    category: "fraud",
    icon: Link2,
    relatedIds: [1, 3],
    status: "completed" as const,
    energy: 96,
    color: CATS.phishing.color,
  },
  {
    id: 3,
    title: "Advance-Fee Fraud",
    date: "F1 0.86",
    content:
      "Prize, lottery, 419 and inheritance lures that ask for an up-front fee. The hardest class: it overlaps with both phishing and benign promotional copy.",
    category: "fraud",
    icon: ShieldAlert,
    relatedIds: [2, 4],
    status: "in-progress" as const,
    energy: 86,
    color: CATS.advance_fee_fraud.color,
  },
  {
    id: 4,
    title: "Not a Scam",
    date: "F1 0.96",
    content:
      "Ordinary, benign messages. The residual class that keeps precision honest by giving the model somewhere safe to land.",
    category: "benign",
    icon: CheckCircle2,
    relatedIds: [3],
    status: "completed" as const,
    energy: 96,
    color: CATS.not_a_scam.color,
  },
];

export function FraudOrbital() {
  return <RadialOrbitalTimeline timelineData={fraudData} />;
}
