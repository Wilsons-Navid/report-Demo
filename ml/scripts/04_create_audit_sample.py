"""Generate a blinded 100-item audit sample for rater 2.

Reads from ``ml/data/labelled/rater1.jsonl`` (the rater-1 output of step 03)
and writes a stratified random sample to ``ml/data/audits/audit_sample_blinded.jsonl``
with categories stripped so rater 2 cannot see rater 1's decision.

Run with: ``python ml/scripts/04_create_audit_sample.py``

The sample is stratified across the seven taxonomy labels so every category
that has any items contributes roughly its share. The random seed is fixed
(``seed=42``) so the audit sample is reproducible from the locked corpus.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.labelling import sample_audit, write_audit_sample
from src.schema import read_jsonl


LABELLED = ROOT / "data" / "labelled"
AUDITS = ROOT / "data" / "audits"
AUDITS.mkdir(parents=True, exist_ok=True)

RATER1_PATH = LABELLED / "rater1.jsonl"
AUDIT_OUT = AUDITS / "audit_sample_blinded.jsonl"

AUDIT_SAMPLE_SIZE = 100


def main() -> None:
    if not RATER1_PATH.exists():
        print(f"No rater-1 corpus at {RATER1_PATH}.")
        print("Did you finish step 03? Need at least 100 labelled items.")
        sys.exit(1)

    items = list(read_jsonl(RATER1_PATH))
    if len(items) < AUDIT_SAMPLE_SIZE:
        print(f"Only {len(items)} items labelled in rater1.jsonl.")
        print(f"Need at least {AUDIT_SAMPLE_SIZE} to draw a representative audit sample.")
        sys.exit(1)

    sample = sample_audit(items, n=AUDIT_SAMPLE_SIZE, seed=42)
    n = write_audit_sample(sample, AUDIT_OUT)

    print(f"Drew stratified {n}-item audit sample from {len(items):,} rater-1 items.")
    print(f"Wrote (with categories blinded) to {AUDIT_OUT}.")
    print()
    print("Hand AUDIT_OUT to rater 2. Rater 2 should label every item independently")
    print("using the same CLI as rater 1 (script 03), writing the labelled output")
    print(f"to {AUDITS}/rater2.jsonl.")
    print()
    print("Next: python ml/scripts/05_compute_kappa.py")


if __name__ == "__main__":
    main()
