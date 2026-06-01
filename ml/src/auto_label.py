"""Heuristic category suggester for the AI-assisted labelling pass.

Given a scam-text record, returns the most likely ``ScamCategory`` plus a
confidence score in [0, 1] and a one-line human-readable reason citing the
patterns that triggered.

This is a SUGGESTION engine, not an autolabeller. The human rater is still
the authority — they confirm or override every suggestion. The pre-pass
exists to cut labelling time from ~60 items/hour to ~250 items/hour by
turning the task from "decide" into "confirm or correct".

Methodology (kept simple on purpose so the reasoning is auditable):
  - For each category, a small bag of patterns (regex + keyword sets) with
    weights. Hits accumulate to a per-category score.
  - The category with the highest score wins. Confidence is the winner's
    share of the total positive score across categories, clamped to [0, 1].
  - If no category accumulates any positive score, default to NOT_A_SCAM
    with a confidence of 0.2 (i.e. "no clear pattern, please decide").
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .taxonomy import ScamCategory


# ---------------------------------------------------------------------------
# Pattern banks (keyword sets + regex). Weights are eyeballed; refine as the
# rater observes systematic mistakes. Lowercased matching throughout.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Pattern:
    label: str           # one-word slug used in the reason string
    weight: float
    keywords: tuple[str, ...] = ()
    regex: str | None = None     # compiled lazily


_PATTERNS: dict[ScamCategory, tuple[Pattern, ...]] = {
    ScamCategory.ADVANCE_FEE_FRAUD: (
        Pattern("prize_award", 3.0, keywords=(
            # English
            "winner", "you have won", "you won", "congratulations", "selected",
            "claim your prize", "claim prize", "lucky winner", "fa cup",
            "txt fa", "cash prize", "free entry", "1st prize", "grand prize",
            "lottery", "raffle", "draw", "award",
            # French
            "felicitations", "vous avez gagne", "vous avez gagné",
            "gagnant", "gagnante", "tirage", "tirage au sort", "loterie",
            "vous etes selectionne", "vous etes le gagnant",
            "votre prix", "votre cadeau", "grand prix", "lot",
            "vous avez ete choisi", "vous avez été choisi",
        )),
        Pattern("inheritance", 2.5, keywords=(
            # English
            "inheritance", "next of kin", "beneficiary", "late mr", "late mrs",
            "deceased", "estate", "will of", "executor",
            # French
            "heritage", "héritage", "succession", "defunt", "défunt",
            "beneficiaire", "bénéficiaire", "feu monsieur", "feu madame",
        )),
        Pattern("processing_fee", 2.5, keywords=(
            # English
            "processing fee", "release fee", "transfer fee", "clearance fee",
            "advance fee", "courier fee", "shipping fee to claim",
            "administrative fee", "delivery fee to receive",
            # French
            "frais de traitement", "frais de transfert", "frais de dossier",
            "frais d'administration", "frais de livraison",
            "frais d'envoi", "frais de declaration", "frais de déclaration",
        )),
        Pattern("western_union", 1.5, keywords=(
            "western union", "moneygram", "send via western union",
        )),
        Pattern("money_amount_with_claim", 2.0, regex=(
            r"(?:\$|£|€|ngn|n)\s?[\d,]{3,}.{0,40}(?:claim|win|prize|award)"
        )),
    ),

    ScamCategory.MOBILE_MONEY_FRAUD: (
        Pattern("momo_operators", 2.0, keywords=(
            # English
            "mtn momo", "mtn mobile money", "orange money", "airtel money",
            "wave money", "m-pesa", "mpesa", "mobile wallet", "mobile money",
            # French
            "porte-monnaie mobile", "porte monnaie mobile", "argent mobile",
        )),
        Pattern("pin_request", 3.0, keywords=(
            # English
            "send your pin", "send pin", "your pin", "confirm pin",
            "verify pin", "enter pin", "share pin", "give pin", "your m-pesa pin",
            # French
            "envoyer votre code pin", "envoyez votre pin", "votre code pin",
            "confirmer votre pin", "verifier votre pin", "vérifier votre pin",
            "partagez votre code", "code secret",
        )),
        Pattern("agent_fraud", 2.0, keywords=(
            "agent transaction", "agent reversal", "wrong transfer",
            "reverse the transfer", "reversal request", "send back the money",
            "i sent money by mistake", "sent by mistake",
        )),
        Pattern("sim_swap", 2.5, keywords=(
            "sim swap", "sim-swap", "sim replacement", "new sim card",
        )),
        Pattern("verification_code", 2.0, keywords=(
            "verification code", "otp", "one-time password", "one time password",
            "verify code", "share the code", "share the otp",
        )),
    ),

    ScamCategory.PHISHING: (
        Pattern("click_to_verify", 3.0, keywords=(
            # English
            "click here", "click the link", "click below", "click to verify",
            "click to confirm", "click to restore", "click to update",
            "verify your account", "verify your identity", "confirm your account",
            "update your details", "secure your account",
            # French
            "cliquez ici", "cliquez sur le lien", "cliquez ci-dessous",
            "verifiez votre compte", "vérifiez votre compte",
            "confirmez votre compte", "mettre a jour vos informations",
            "securiser votre compte", "sécuriser votre compte",
        )),
        Pattern("account_locked", 2.5, keywords=(
            # English
            "account suspended", "account locked", "account blocked",
            "account expired", "access blocked", "account will be suspended",
            "your access has been blocked", "limited access", "deactivated",
            # French
            "compte suspendu", "compte bloque", "compte bloqué",
            "compte expire", "compte expiré", "acces bloque", "accès bloqué",
            "compte desactive", "compte désactivé",
        )),
        Pattern("bank_impersonation", 2.5, keywords=(
            "gtbank", "guaranty trust", "first bank", "uba", "zenith bank",
            "access bank", "fidelity bank", "polaris bank", "stanbic",
            "ecobank", "fcmb", "wema bank", "afriland",
            "your bank account", "from your bank",
        )),
        Pattern("suspicious_url", 2.5, regex=(
            r"https?://[^\s]+|bit\.ly|tinyurl|t\.co/|\.tk|\.ml|\.cf|\.ga"
        )),
        Pattern("login_credentials", 2.0, keywords=(
            "log in", "log-in", "sign in", "sign-in", "username and password",
            "your password", "enter your password", "credentials",
        )),
    ),

    ScamCategory.ROMANCE_SCAM: (
        Pattern("relationship_language", 2.5, keywords=(
            # English
            "my darling", "my love", "honey", "sweetheart",
            "i love you", "miss you so much", "marry me",
            "want to marry", "want to come to you", "future together",
            "i feel a connection", "soul mate", "my queen", "my king",
            # French
            "mon amour", "mon cheri", "mon chéri", "ma cherie", "ma chérie",
            "je t'aime", "tu me manques", "epouse moi", "épouse moi",
            "notre avenir ensemble", "ame soeur", "âme sœur",
        )),
        Pattern("stranded_abroad", 3.0, keywords=(
            "stranded", "stuck in customs", "shipping container",
            "lost my wallet", "no money to come back", "need help with shipping",
            "package stuck at customs", "court fees", "soldier deployed",
            "doctor abroad", "engineer in", "oil rig",
        )),
        Pattern("send_money_personal", 2.0, keywords=(
            "send me money", "send some money", "wire some money",
            "help me with money", "pay for my flight", "pay for my ticket",
        )),
    ),

    ScamCategory.IDENTITY_THEFT: (
        Pattern("id_credentials", 3.0, keywords=(
            # English
            "nin", "bvn", "national identification", "drivers license",
            "passport number", "national id number", "social security",
            "voters card", "voter's card", "biometric data",
            # French
            "cni", "carte nationale d'identite", "carte nationale d'identité",
            "piece d'identite", "pièce d'identité", "numero de passeport",
            "numéro de passeport", "carte d'electeur", "carte d'électeur",
            "donnees biometriques", "données biométriques",
        )),
        Pattern("personal_information", 2.0, keywords=(
            "your personal information", "your full name and dob",
            "date of birth and address", "mother's maiden name",
            "your details to verify", "share your id",
        )),
        Pattern("account_takeover", 2.0, keywords=(
            "your account has been compromised", "unauthorised access",
            "unauthorized access", "someone tried to log in",
            "fraudulent activity detected", "we noticed login from",
        )),
    ),

    ScamCategory.SYNTHETIC_MEDIA_FRAUD: (
        Pattern("voice_video_impersonation", 3.0, keywords=(
            "voice note from", "voice call from", "video call from",
            "audio message from", "sounds exactly like", "ai-generated voice",
            "deepfake", "voice clone",
        )),
        Pattern("urgent_family_emergency", 2.5, keywords=(
            "i am your son", "this is your brother", "this is your sister",
            "your mother is in hospital", "your father is in hospital",
            "i have been in an accident", "i have been kidnapped",
            "i need money urgently", "ransom",
        )),
    ),
}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_pattern(text_lc: str, pattern: Pattern) -> tuple[float, str | None]:
    """Return ``(score, hit_label)`` for a single pattern; ``hit_label`` is the
    pattern's slug if at least one keyword or regex matched, else ``None``.
    """
    for kw in pattern.keywords:
        if kw in text_lc:
            return pattern.weight, pattern.label
    if pattern.regex and re.search(pattern.regex, text_lc, re.IGNORECASE):
        return pattern.weight, pattern.label
    return 0.0, None


def suggest(text: str) -> tuple[ScamCategory, float, str]:
    """Return ``(category, confidence, reason)`` for ``text``.

    ``confidence`` in [0, 1]. ``reason`` is a short human-readable string
    naming the patterns that hit (e.g., ``"phishing: click_to_verify, suspicious_url"``).
    """
    if not text or not text.strip():
        return ScamCategory.NOT_A_SCAM, 0.1, "empty text"

    text_lc = text.lower()
    scores: dict[ScamCategory, float] = {}
    hits: dict[ScamCategory, list[str]] = {}

    for category, patterns in _PATTERNS.items():
        for p in patterns:
            s, hit = _score_pattern(text_lc, p)
            if s > 0:
                scores[category] = scores.get(category, 0.0) + s
                hits.setdefault(category, []).append(hit or p.label)

    if not scores:
        return (
            ScamCategory.NOT_A_SCAM,
            0.2,
            "no scam pattern detected (default not_a_scam)",
        )

    winner = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = scores[winner] / total if total else 0.0
    # Bump confidence by the absolute winner score (more evidence -> more confidence)
    confidence = min(1.0, confidence * 0.6 + min(scores[winner] / 6.0, 0.4))

    hit_labels = ", ".join(sorted(set(hits[winner])))
    reason = f"{winner.value}: {hit_labels} (score={scores[winner]:.1f})"
    return winner, confidence, reason


# Cosmetic helper for the CLI
def confidence_band(c: float) -> str:
    if c >= 0.70:
        return "STRONG"
    if c >= 0.45:
        return "TENTATIVE"
    return "WEAK"
