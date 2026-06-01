"""Interactive CLI for labelling items one at a time.

Reads from ``ml_potential/data/labelled/unlabelled.jsonl`` and writes labelled
records into ``ml_potential/data/labelled/rater1.jsonl`` (or a configurable
output path). Resume-safe: items already in the output file are skipped.

Run with: ``python ml_potential/scripts/03_label_helper.py``

Usage at the prompt:
  1   → advance_fee_fraud
  2   → mobile_money_fraud
  3   → phishing
  4   → romance_scam
  5   → identity_theft
  6   → synthetic_media_fraud
  7   → not_a_scam
  s   → skip (item will not be written)
  q   → save and quit
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.schema import LabelledItem, LabelSource, read_jsonl, write_jsonl
from src.taxonomy import ScamCategory, all_categories


LABELLED = ROOT / "data" / "labelled"
INPUT_PATH = LABELLED / "unlabelled.jsonl"
OUTPUT_PATH = LABELLED / "rater1.jsonl"


KEY_TO_CATEGORY = {
    "1": ScamCategory.ADVANCE_FEE_FRAUD,
    "2": ScamCategory.MOBILE_MONEY_FRAUD,
    "3": ScamCategory.PHISHING,
    "4": ScamCategory.ROMANCE_SCAM,
    "5": ScamCategory.IDENTITY_THEFT,
    "6": ScamCategory.SYNTHETIC_MEDIA_FRAUD,
    "7": ScamCategory.NOT_A_SCAM,
}


def already_labelled() -> set[str]:
    if not OUTPUT_PATH.exists():
        return set()
    return {item.id for item in read_jsonl(OUTPUT_PATH)}


def append_jsonl(item: LabelledItem) -> None:
    with OUTPUT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(item.model_dump_json() + "\n")


def label_one(item: LabelledItem) -> LabelledItem | None:
    print("\n" + "-" * 70)
    print(f"id={item.id}  lang={item.language}  stream={item.source_stream.value}  "
          f"original_label={item.original_label}")
    print(f"text:\n{item.text[:600]}{'...' if len(item.text) > 600 else ''}")
    print()
    print("  1=advance_fee_fraud  2=mobile_money_fraud  3=phishing  "
          "4=romance_scam")
    print("  5=identity_theft     6=synthetic_media_fraud  7=not_a_scam")
    print("  s=skip               q=save & quit")
    while True:
        key = input("> ").strip().lower()
        if key == "q":
            return None
        if key == "s":
            return item.model_copy()  # signal: skip
        if key in KEY_TO_CATEGORY:
            return item.model_copy(update={
                "category": KEY_TO_CATEGORY[key],
                "label_source": LabelSource.RATER1,
            })
        print("  ?? unknown key; try again")


def main() -> None:
    if not INPUT_PATH.exists():
        print(f"No unlabelled corpus at {INPUT_PATH}.")
        print("Did you run 01_download_public.py and 02_normalise.py?")
        sys.exit(1)

    seen = already_labelled()
    items = [item for item in read_jsonl(INPUT_PATH) if item.id not in seen]

    if not items:
        print("Nothing left to label. All items in unlabelled.jsonl are in rater1.jsonl.")
        sys.exit(0)

    print(f"{len(items):,} items remaining to label.")
    print(f"Labels will be appended to {OUTPUT_PATH} (resume-safe).")

    labelled = 0
    skipped = 0
    for item in items:
        result = label_one(item)
        if result is None:
            print("\nSaved and quit.")
            break
        if result.label_source != LabelSource.RATER1:
            # 's' was pressed; do not write
            skipped += 1
            continue
        append_jsonl(result)
        labelled += 1
        if labelled % 25 == 0:
            print(f"\n  progress: {labelled} labelled, {skipped} skipped")

    print(f"\nDone. {labelled} new labels written to {OUTPUT_PATH}.")
    print(f"Cumulative rater1 total: "
          f"{len(already_labelled()) if OUTPUT_PATH.exists() else 0}")


if __name__ == "__main__":
    main()
