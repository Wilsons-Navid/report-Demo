"""Harvest the regional stream and write it to data/raw/regional/.

Runs every scraper in ``src.scrapers`` (Premium Times works today; the
institutional advisory sites are blocked and log why). The combined output is
written as JSONL to ``ml/data/raw/regional/regional_news.jsonl`` so that
``02_normalise.py`` can fold it into the unlabelled corpus alongside the public
datasets.

Records land with ``category=not_a_scam`` / ``label_source=auto`` placeholders;
the real category is assigned in the human labelling pass (script 03b).

Run with: ``python ml/scripts/07_scrape_regional.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scrapers import harvest_regional
from src.schema import write_jsonl

RAW_REGIONAL = ROOT / "data" / "raw" / "regional"
RAW_REGIONAL.mkdir(parents=True, exist_ok=True)
OUT = RAW_REGIONAL / "regional_news.jsonl"


def main() -> None:
    print("Harvesting regional stream...\n")
    items = harvest_regional()
    if not items:
        print("\nNo regional records harvested (all sources blocked or empty).")
        print("The public stream still carries the corpus; see 01/02.")
        sys.exit(0)

    # Drop within-batch exact-text duplicates early (paragraphs repeat across
    # related articles). Downstream 02_normalise does the full dedup pass too.
    seen: set[str] = set()
    deduped = []
    for it in items:
        if it.id in seen:
            continue
        seen.add(it.id)
        deduped.append(it)

    n = write_jsonl(deduped, OUT)
    print(f"\nHarvested {len(items):,} paragraph-records "
          f"({n:,} unique) -> {OUT}")
    print("Next: re-run python ml/scripts/02_normalise.py to fold these in.")


if __name__ == "__main__":
    main()
