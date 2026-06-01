"""Compute Cohen's κ between rater 1 and rater 2 on the audit sample.

Reads rater-1 labels from ``ml/data/labelled/rater1.jsonl`` and rater-2 labels
from ``ml/data/audits/rater2.jsonl``, intersects on item id, computes κ, and
prints the result.

Per proposal §3.4.1, the corpus is not accepted for use in the comparative
evaluation until **κ ≥ 0.7**.

Run with: ``python ml/scripts/05_compute_kappa.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.labelling import KAPPA_ACCEPTANCE_THRESHOLD, kappa_from_paths
from src.schema import read_jsonl


LABELLED = ROOT / "data" / "labelled"
AUDITS = ROOT / "data" / "audits"

RATER1_PATH = LABELLED / "rater1.jsonl"
RATER2_PATH = AUDITS / "rater2.jsonl"


def main() -> None:
    if not RATER1_PATH.exists():
        print(f"No rater-1 file at {RATER1_PATH}")
        sys.exit(1)
    if not RATER2_PATH.exists():
        print(f"No rater-2 file at {RATER2_PATH}")
        print("Did rater 2 finish labelling the audit sample? Output should land at")
        print(f"  {RATER2_PATH}")
        sys.exit(1)

    r1 = {item.id: item.category for item in read_jsonl(RATER1_PATH)}
    r2 = {item.id: item.category for item in read_jsonl(RATER2_PATH)}
    shared = sorted(set(r1) & set(r2))

    print(f"  rater 1: {len(r1):,} items total")
    print(f"  rater 2: {len(r2):,} items total")
    print(f"  shared:  {len(shared):,} items in both files")

    if not shared:
        print("\nNo overlapping item ids. Did rater 2 use the blinded audit sample?")
        sys.exit(1)

    kappa = kappa_from_paths(RATER1_PATH, RATER2_PATH)
    print(f"\nCohen's κ = {kappa:.4f}")
    print(f"  threshold = {KAPPA_ACCEPTANCE_THRESHOLD}")

    if kappa >= KAPPA_ACCEPTANCE_THRESHOLD:
        print(f"  PASS — corpus accepted for use in the comparative evaluation.")
        print(f"\nNext: python ml/scripts/06_split.py")
    else:
        print(f"  FAIL — adjudicate disagreements and re-rate the disputed items.")
        print(f"  Disagreement summary (rater1 → rater2):")
        for item_id in shared:
            if r1[item_id] != r2[item_id]:
                print(f"    {item_id}: {r1[item_id].value} → {r2[item_id].value}")


if __name__ == "__main__":
    main()
