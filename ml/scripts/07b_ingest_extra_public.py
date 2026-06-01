"""Materialise the extra public scam-message sources into JSONL.

Two sources added 2026-06-01 to fix the corpus category imbalance (the UCI +
Premium-Times mix yielded almost only advance_fee_fraud):

  - Nazario phishing/419 email corpus  -> data/raw/nazario/nazario_emails.jsonl
  - Mendeley SMS-phishing dataset       -> data/raw/smishing/smishing_sms.jsonl

Both land in our JSONL schema so 02_normalise.py can fold them in alongside the
UCI and regional streams. Records carry category=not_a_scam (placeholder); the
real taxonomy label is assigned in the human/assisted labelling pass.

NOTE: the Nazario .mbox files are large binaries that the sandboxed shell cannot
read back (overlay quirk). Run this script with the sandbox disabled.

Run with: ``python ml/scripts/07b_ingest_extra_public.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.loaders import load_nazario_mbox_dir, load_smishing_csv, load_moz_smishing_csv
from src.schema import write_jsonl

RAW = ROOT / "data" / "raw"


def main() -> None:
    # Nazario emails
    naz_dir = RAW / "nazario"
    if any(naz_dir.glob("*.mbox")):
        items = list(load_nazario_mbox_dir(naz_dir))
        out = naz_dir / "nazario_emails.jsonl"
        n = write_jsonl(items, out)
        print(f"Nazario: parsed {n:,} emails -> {out}")
    else:
        print(f"[skip] no .mbox files in {naz_dir}")

    # Smishing SMS
    smi_csv = RAW / "smishing" / "Dataset_5971.csv"
    if smi_csv.exists():
        items = list(load_smishing_csv(smi_csv))
        out = RAW / "smishing" / "smishing_sms.jsonl"
        n = write_jsonl(items, out)
        print(f"Smishing: kept {n:,} non-ham SMS -> {out}")
    else:
        print(f"[skip] {smi_csv} not found")

    # MOZ-Smishing (mobile-money, Portuguese)
    moz_csv = RAW / "moz_smishing" / "test.csv"
    if moz_csv.exists():
        items = list(load_moz_smishing_csv(moz_csv))
        out = RAW / "moz_smishing" / "moz_smishing.jsonl"
        n = write_jsonl(items, out)
        print(f"MOZ-Smishing: kept {n:,} smishing SMS -> {out}")
    else:
        print(f"[skip] {moz_csv} not found")

    print("\nNext: re-run python ml/scripts/02_normalise.py to fold these in.")


if __name__ == "__main__":
    main()
