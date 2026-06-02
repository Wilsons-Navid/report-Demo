import type { ClassKey } from "@/lib/api";

export type RiskLevel = "high" | "elevated" | "safe";

export function riskFor(category: string, confidence: number): { level: RiskLevel; label: string } {
  if (category === "not_a_scam") return { level: "safe", label: "Looks safe" };
  if (confidence >= 0.66) return { level: "high", label: "High risk" };
  return { level: "elevated", label: "Elevated risk" };
}

/** What to do now, per predicted class. Safety advice only — never asks the user to share secrets. */
export const STEPS: Record<ClassKey, string[]> = {
  mobile_money_fraud: [
    "Do not share your PIN or any OTP. No bank, telecom or agent will ever ask for them.",
    "Do not approve or “reverse” a transaction you did not start.",
    "If you already shared a PIN or OTP, call your provider now and ask to freeze the account.",
    "Report the sender’s number to your mobile operator.",
  ],
  phishing: [
    "Do not click the link or enter any login details.",
    "Open the bank or service app yourself, or type the official address. Never follow the link in the message.",
    "If you already entered a password, change it now and turn on two-factor authentication.",
    "Report the message, then delete it.",
  ],
  advance_fee_fraud: [
    "There is no prize, refund or inheritance. Never pay a fee to receive money.",
    "Do not send money, airtime, gift cards or personal documents.",
    "Verify any “official” claim directly with the organisation it names.",
    "Report the number and block the sender.",
  ],
  not_a_scam: [
    "This message looks ordinary, so no action is needed.",
    "Stay alert anyway: if it ever asks for a PIN, OTP, password or an up-front payment, treat it as a scam regardless of the score.",
  ],
};

export interface Contact {
  label: string;
  value: string;
  href?: string;
}
export interface Region {
  id: string;
  label: string;
  contacts: Contact[];
}

/** Official reporting channels, verified June 2026. Shown with a "confirm on the agency site" note. */
export const REGIONS: Region[] = [
  {
    id: "ke",
    label: "Kenya",
    contacts: [
      { label: "Forward the SMS to (free)", value: "333" },
      { label: "Safaricom customer care", value: "100" },
      { label: "National KE-CIRT/CC", value: "ke-cirt.go.ke", href: "https://www.ke-cirt.go.ke/" },
      { label: "Safaricom fraud awareness", value: "fraud-awareness", href: "https://www.safaricom.co.ke/fraud-awareness" },
    ],
  },
  {
    id: "ng",
    label: "Nigeria",
    contacts: [
      { label: "Report a spam number", value: "7726 (SPAM)" },
      { label: "NCC complaints line", value: "622" },
      { label: "Opt out of unsolicited SMS", value: "text STOP to 2442" },
      { label: "EFCC fraud report", value: "efcc.gov.ng", href: "https://www.efcc.gov.ng/efcc/channels-of-reporting-complaints-2" },
    ],
  },
  {
    id: "gh",
    label: "Ghana",
    contacts: [
      { label: "Cyber Security Authority (call / SMS)", value: "292" },
      { label: "CSA WhatsApp", value: "0501603111" },
      { label: "CSA incident report", value: "csa.gov.gh/report", href: "https://www.csa.gov.gh/report" },
    ],
  },
  {
    id: "intl",
    label: "Other / Global",
    contacts: [
      { label: "Forward spam to (where supported)", value: "7726 (SPAM)" },
      { label: "Your bank / wallet", value: "use the number on the official app or card" },
      { label: "Local police / cybercrime unit", value: "your national cybercrime line" },
    ],
  },
];
