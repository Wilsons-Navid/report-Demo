"""Assemble the labelled dataset for the INITIAL (demo) model.

This is the dataset for the software-demonstration milestone — an initial,
preliminary model. Labels come from each source's own provenance (not the
human κ-verified corpus, which is the artefact for the FINAL Objective-3
evaluation):

  - phishing            <- Nazario phishing emails + Mendeley smishing (smishing)
  - mobile_money_fraud  <- MOZ-Smishing (dataset-labelled smishing)
  - advance_fee_fraud   <- UCI prize/lottery SMS + Nazario 419 (hand-confirmed)
  - not_a_scam          <- UCI ham (genuine benign personal SMS)

The three thin categories (romance/identity/synthetic) are out of scope for the
initial model — no public message data exists for them (see memory). The scam
labels are taken from `worklist.jsonl` (which already carries the best
per-item suggestion: hand-label > source-label > heuristic).

Output: `data/labelled/demo_labeled.jsonl` with {id, text, language, category,
source}. The notebook does the stratified train/dev/test split.

Run with: ``python ml/scripts/10_build_demo_dataset.py``
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.schema import read_jsonl

LABELLED = ROOT / "data" / "labelled"
WORKLIST = LABELLED / "worklist.jsonl"
CORPUS = LABELLED / "unlabelled.jsonl"
OUT = LABELLED / "demo_labeled.jsonl"

SCAM_CLASSES = {"phishing", "mobile_money_fraud", "advance_fee_fraud"}
HAM_TARGET = 1200          # genuine UCI ham as the not_a_scam class
SEED = 42


def _src(item) -> str:
    ol = item.original_label or ""
    if ol.startswith("nazario"):
        return "nazario_email"
    if ol.startswith("smishing_ds"):
        return "mendeley_smishing"
    if ol.startswith("moz_smishing"):
        return "moz_smishing"
    if ol.startswith("premium_times"):
        return "regional_news"
    if ol in ("ham", "spam"):
        return "uci_sms"
    return "other"


def main() -> None:
    if not WORKLIST.exists():
        print(f"No worklist at {WORKLIST}. Run 08_build_worklist.py first.")
        sys.exit(1)

    rows: list[dict] = []

    # Scam classes from the worklist (best available per-item label).
    for it in read_jsonl(WORKLIST):
        if it.category.value in SCAM_CLASSES:
            rows.append({
                "id": it.id, "text": it.text, "language": it.language,
                "category": it.category.value, "source": _src(it),
            })

    # not_a_scam = genuine UCI ham (benign personal SMS), sampled to HAM_TARGET.
    ham = [it for it in read_jsonl(CORPUS) if (it.original_label or "") == "ham"]
    rng = random.Random(SEED)
    rng.shuffle(ham)
    for it in ham[:HAM_TARGET]:
        rows.append({
            "id": it.id, "text": it.text, "language": it.language,
            "category": "not_a_scam", "source": "uci_sms",
        })

    rng.shuffle(rows)
    with OUT.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows):,} labelled rows -> {OUT}\n")
    print("Class distribution:")
    for k, v in Counter(r["category"] for r in rows).most_common():
        print(f"  {k:20} {v:5,}")
    print("\nBy source:")
    for k, v in Counter(r["source"] for r in rows).most_common():
        print(f"  {k:20} {v:5,}")
    print("\nLanguage:")
    for k, v in Counter(r["language"] for r in rows).most_common():
        print(f"  {k:20} {v:5,}")


if __name__ == "__main__":
    main()
