"""Six-category scam taxonomy plus residual class.

Locked by proposal Section 3.4.1. Any change here is a scope change to the
proposal and must be approved by the supervisor before propagation.
"""

from __future__ import annotations

from enum import Enum


class ScamCategory(str, Enum):
    """Authoritative scam-category enum used across the pipeline.

    The six positive categories are the project's scope per Section 1.5 of the
    proposal; ``NOT_A_SCAM`` is a residual training-time false-positive class.
    """

    ADVANCE_FEE_FRAUD = "advance_fee_fraud"
    MOBILE_MONEY_FRAUD = "mobile_money_fraud"
    PHISHING = "phishing"
    ROMANCE_SCAM = "romance_scam"
    IDENTITY_THEFT = "identity_theft"
    SYNTHETIC_MEDIA_FRAUD = "synthetic_media_fraud"
    NOT_A_SCAM = "not_a_scam"


# Human-readable labels for the CLI labeller and the report
CATEGORY_DESCRIPTIONS: dict[ScamCategory, str] = {
    ScamCategory.ADVANCE_FEE_FRAUD: (
        "Promises a large payout in exchange for an up-front fee or personal "
        "details (classic 'Nigerian prince', inheritance scams, fake job "
        "offers requiring a processing fee)."
    ),
    ScamCategory.MOBILE_MONEY_FRAUD: (
        "Targets mobile-money users: false transaction-confirmation prompts, "
        "agent fraud, SIM-swap-enabled account takeover, fake refund requests."
    ),
    ScamCategory.PHISHING: (
        "Impersonates a legitimate organisation (bank, telecom, government) "
        "via SMS/email/social to harvest credentials or sensitive data."
    ),
    ScamCategory.ROMANCE_SCAM: (
        "Builds a long-running fake romantic relationship to extract money or "
        "personal information."
    ),
    ScamCategory.IDENTITY_THEFT: (
        "Acquires or uses another person's identifying information without "
        "consent for fraudulent purposes."
    ),
    ScamCategory.SYNTHETIC_MEDIA_FRAUD: (
        "Uses AI-generated voice, image, or video content to impersonate a "
        "known person (relative, banking rep, public figure) to induce "
        "transfer of funds or disclosure of credentials."
    ),
    ScamCategory.NOT_A_SCAM: (
        "Legitimate communication, benign spam, or other non-scam content. "
        "Reserved for training-time false-positive examples."
    ),
}


def all_categories() -> list[ScamCategory]:
    """Return the seven taxonomy labels in canonical order."""
    return list(ScamCategory)


def positive_categories() -> list[ScamCategory]:
    """Return the six scam categories, excluding the residual ``NOT_A_SCAM``."""
    return [c for c in ScamCategory if c != ScamCategory.NOT_A_SCAM]
