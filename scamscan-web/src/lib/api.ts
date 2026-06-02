export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "https://scam-classifier-api.onrender.com";

export type ClassKey =
  | "phishing"
  | "advance_fee_fraud"
  | "mobile_money_fraud"
  | "not_a_scam";

export interface CatMeta {
  name: string;
  color: string;
  note: string;
}

export const CATS: Record<ClassKey, CatMeta> = {
  phishing:           { name: "Phishing",            color: "#fb6f66", note: "Credential / link harvesting" },
  advance_fee_fraud:  { name: "Advance-Fee Fraud",   color: "#ffd24d", note: "Prize · 419 · inheritance lure" },
  mobile_money_fraud: { name: "Mobile-Money Fraud",  color: "#9d8cf2", note: "Wallet · PIN · agent / OTP" },
  not_a_scam:         { name: "Not a Scam",          color: "#4fd1a0", note: "Benign message" },
};

export const catColor = (k: string) => (CATS as Record<string, CatMeta>)[k]?.color ?? "#f6b13a";
export const catName = (k: string) => (CATS as Record<string, CatMeta>)[k]?.name ?? k;

export interface Prediction {
  text: string;
  predicted_category: string;
  confidence: number;
  scores: Record<string, number>;
}

export async function classify(text: string): Promise<Prediction> {
  const r = await fetch(`${API_BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!r.ok) throw new Error(`API returned ${r.status}`);
  return r.json();
}

export async function health(): Promise<boolean> {
  try {
    const r = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    return r.ok;
  } catch {
    return false;
  }
}

export const EXAMPLES: { label: string; cat: ClassKey; text: string }[] = [
  { label: "Phishing link", cat: "phishing",
    text: "Dear customer, your bank account is suspended. Click here to verify immediately: http://bit.ly/secure-acct" },
  { label: "M-Pesa (PT)", cat: "mobile_money_fraud",
    text: "Caro cliente, a sua conta M-Pesa foi bloqueada. Envie o seu codigo PIN para reactivar a conta agora." },
  { label: "Prize / 419", cat: "advance_fee_fraud",
    text: "URGENT! Your mobile number won a 2000 prize GUARANTEED. Call 09061790121 to claim before it expires." },
  { label: "Benign", cat: "not_a_scam",
    text: "Hey, are we still meeting for lunch at 1pm tomorrow? Let me know if the time still works." },
];

// Stock imagery (known-existing Unsplash photo IDs)
export const IMAGES = {
  heroAurora: "https://images.unsplash.com/photo-1432251407527-504a6b4174a2?q=80&w=1600&auto=format&fit=crop",
  network:    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1600&auto=format&fit=crop",
  circuit:    "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1600&auto=format&fit=crop",
  cyber:      "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=1600&auto=format&fit=crop",
};
