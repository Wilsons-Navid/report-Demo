"""Non-interactive batch auto-suggestion pass over the unlabelled corpus.

This is the head-start for the human labelling pass, not a substitute for it.
It runs the heuristic ``suggest()`` engine over every record in
``unlabelled.jsonl`` and writes the result to
``data/labelled/auto_suggested.jsonl`` with ``label_source=AUTO``.

Integrity note: every record here is marked AUTO, never RATER1. These are
machine *suggestions*. The accepted corpus (``rater1.jsonl``) is produced by a
human running 03b and confirming or correcting each suggestion; the κ audit
(scripts 04/05) is run on that human file. Nothing here counts toward the
κ ≥ 0.7 acceptance criterion.

What it gives you:
  - a category distribution preview, so you can see whether the heuristic is
    finding the regional/mobile-money signal or collapsing everything to
    not_a_scam;
  - a confidence breakdown (STRONG / TENTATIVE / WEAK), so the human pass can
    prioritise confirming STRONG suggestions first.

Run with: ``python ml/scripts/03c_batch_autolabel.py``
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.auto_label import confidence_band, suggest
from src.schema import LabelSource, read_jsonl, write_jsonl
from src.taxonomy import ScamCategory

LABELLED = ROOT / "data" / "labelled"
INPUT_PATH = LABELLED / "unlabelled.jsonl"
OUTPUT_PATH = LABELLED / "auto_suggested.jsonl"


def main() -> None:
    if not INPUT_PATH.exists():
        print(f"No unlabelled corpus at {INPUT_PATH}.")
        print("Run 01_download_public.py + 07_scrape_regional.py + 02_normalise.py first.")
        sys.exit(1)

    items = list(read_jsonl(INPUT_PATH))
    print(f"Loaded {len(items):,} unlabelled items.\n")

    out = []
    cat_counts: Counter[str] = Counter()
    band_counts: Counter[str] = Counter()
    cat_by_stream: dict[str, Counter[str]] = {}

    for item in items:
        cat, conf, _reason = suggest(item.text)
        band = confidence_band(conf)
        cat_counts[cat.value] += 1
        band_counts[band] += 1
        cat_by_stream.setdefault(item.source_stream.value, Counter())[cat.value] += 1
        out.append(item.model_copy(update={
            "category": cat,
            "label_source": LabelSource.AUTO,
        }))

    n = write_jsonl(out, OUTPUT_PATH)

    print(f"Wrote {n:,} AUTO-suggested records -> {OUTPUT_PATH}\n")

    print("Suggested category distribution (whole corpus):")
    for cat in ScamCategory:
        c = cat_counts.get(cat.value, 0)
        pct = 100 * c / len(items) if items else 0
        print(f"  {cat.value:24} {c:6,}  ({pct:5.1f}%)")

    print("\nConfidence bands:")
    for band in ("STRONG", "TENTATIVE", "WEAK"):
        c = band_counts.get(band, 0)
        pct = 100 * c / len(items) if items else 0
        print(f"  {band:10} {c:6,}  ({pct:5.1f}%)")

    print("\nSuggested scam categories by source stream (excl. not_a_scam):")
    for stream, counter in sorted(cat_by_stream.items()):
        scam = {k: v for k, v in counter.items() if k != ScamCategory.NOT_A_SCAM.value}
        total_scam = sum(scam.values())
        print(f"  [{stream}] {total_scam:,} flagged as scam of "
              f"{sum(counter.values()):,} items")
        for k, v in sorted(scam.items(), key=lambda kv: -kv[1]):
            print(f"      {k:24} {v:5,}")

    print("\nNext (human-in-the-loop): python ml/scripts/03b_assisted_label.py")
    print("  -> confirm/correct the STRONG suggestions first; output is rater1.jsonl.")


if __name__ == "__main__":
    main()
