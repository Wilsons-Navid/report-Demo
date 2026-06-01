"""Build a prioritised, balanced labelling worklist with source-aware suggestions.

The raw corpus is dominated by not_a_scam (UCI ham) and now also carries
trustworthy source labels (Nazario = phishing/419 email; the Mendeley/MOZ
smishing sets carry their own smishing/spam labels). Streaming top-to-bottom
or trusting the weak keyword heuristic both waste the rater's time, so this
builds a focused worklist whose ``category`` field is the BEST available
suggestion per item:

  1. If a prior hand-label exists for the id (``_overrides_b*.json``) — use it.
     This preserves the 711-item relabel already done; the rater never redoes it.
  2. Else if the item came from a labelled source, combine that prior with the
     keyword heuristic:
       - Nazario email   -> keyword cat if it's advance_fee/romance, else phishing
       - smishing (yes)  -> keyword cat if non-residual, else phishing
       - MOZ momo smish  -> keyword cat if non-residual, else mobile_money_fraud
  3. Else (UCI, regional, smishing-spam) -> the keyword heuristic alone.

Every record stays label_source=AUTO (a suggestion). The human confirm pass
(09_confirm_worklist.py) accepts/overrides and writes rater1.jsonl.

Worklist = all items suggested as a scam category (scam-first, source-backed
first) + a fixed not_a_scam sample. Output: ``data/labelled/worklist.jsonl``.

Run with: ``python ml/scripts/08_build_worklist.py``
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.auto_label import suggest
from src.schema import LabelSource, LabelledItem, read_jsonl, write_jsonl
from src.taxonomy import ScamCategory

LABELLED = ROOT / "data" / "labelled"
INPUT_PATH = LABELLED / "unlabelled.jsonl"
OUTPUT_PATH = LABELLED / "worklist.jsonl"

HAM_SAMPLE = 150
SEED = 42

NS = ScamCategory.NOT_A_SCAM
PH = ScamCategory.PHISHING
AFF = ScamCategory.ADVANCE_FEE_FRAUD
ROM = ScamCategory.ROMANCE_SCAM
MOMO = ScamCategory.MOBILE_MONEY_FRAUD


def load_overrides() -> dict[str, ScamCategory]:
    """Prior hand-labels from _overrides_b*.json (preserve earlier relabel)."""
    out: dict[str, ScamCategory] = {}
    for p in sorted(LABELLED.glob("_overrides_b*.json")):
        for k, v in json.loads(p.read_text(encoding="utf-8")).items():
            out[k] = ScamCategory(v)
    return out


def suggestion_for(item: LabelledItem, overrides: dict[str, ScamCategory]) -> tuple[ScamCategory, int]:
    """Return (suggested_category, source_priority). Lower priority sorts first."""
    if item.id in overrides:
        return overrides[item.id], 0

    kw, _conf, _r = suggest(item.text)
    ol = (item.original_label or "")

    if ol.startswith("nazario"):
        return (kw if kw in (AFF, ROM) else PH), 1
    if ol == "smishing_ds:smishing":
        return (kw if kw != NS else PH), 1
    if ol.startswith("moz_smishing"):
        return (kw if kw != NS else MOMO), 1
    return kw, 2


def main() -> None:
    if not INPUT_PATH.exists():
        print(f"No unlabelled corpus at {INPUT_PATH}. Run 02_normalise.py first.")
        sys.exit(1)

    overrides = load_overrides()
    print(f"Loaded {len(overrides):,} prior hand-labels from _overrides_b*.json")

    items = list(read_jsonl(INPUT_PATH))
    print(f"Loaded {len(items):,} unlabelled items.\n")

    scam: list[tuple[int, LabelledItem]] = []
    ham: list[LabelledItem] = []
    for item in items:
        cat, prio = suggestion_for(item, overrides)
        suggested = item.model_copy(update={"category": cat, "label_source": LabelSource.AUTO})
        if cat == NS:
            ham.append(suggested)
        else:
            scam.append((prio, suggested))

    # Scam-first; source-backed (priority 0/1) ahead of keyword-only (2).
    scam.sort(key=lambda t: t[0])
    scam_items = [it for _p, it in scam]

    rng = random.Random(SEED)
    rng.shuffle(ham)
    ham_sample = ham[:HAM_SAMPLE]

    worklist = scam_items + ham_sample
    n = write_jsonl(worklist, OUTPUT_PATH)

    print(f"Worklist: {len(scam_items):,} scam-flagged + {len(ham_sample):,} ham = {n:,}")
    print(f"Wrote -> {OUTPUT_PATH}\n")

    dist = Counter(it.category.value for it in worklist)
    print("Suggested-category composition:")
    for cat in ScamCategory:
        print(f"  {cat.value:24} {dist.get(cat.value, 0):5,}")

    # how many suggestions are source-backed vs keyword-only
    backed = sum(1 for p, _ in scam if p <= 1)
    print(f"\n  scam suggestions source-backed (hand-label/Nazario/smishing): {backed:,}")
    print(f"  scam suggestions keyword-only:                                {len(scam) - backed:,}")
    print("\nNext: python ml/scripts/09_confirm_worklist.py")


if __name__ == "__main__":
    main()
