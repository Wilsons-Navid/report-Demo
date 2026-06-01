"""Convert raw downloaded datasets into a single JSONL file with quality phase.

Reads from ``ml/data/raw/*`` and writes a deduplicated, length-filtered,
schema-conforming JSONL file at ``ml/data/labelled/unlabelled.jsonl``.

Run with: ``python ml/scripts/02_normalise.py``

Output rows still have ``category=not_a_scam`` (placeholder); the real
category is assigned by the rater in step 03.

Quality phase (per proposal §3.4.2):
  1. Schema validation (Pydantic — implicit when items are constructed)
  2. Exact-text deduplication by id (SHA1 hash of text)
  3. Near-duplicate detection (character 5-gram Jaccard ≥ 0.85)
  4. Length filtering (drop < 20 chars or > 2000 chars)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.loaders import load_uci_sms_spam, load_nazario_phishing
from src.schema import LabelledItem, read_jsonl, write_jsonl


RAW = ROOT / "data" / "raw"
LABELLED = ROOT / "data" / "labelled"
LABELLED.mkdir(parents=True, exist_ok=True)

# Quality phase thresholds (per proposal §3.4.2)
MIN_TEXT_LEN = 20
MAX_TEXT_LEN = 2000
NEAR_DUP_JACCARD_THRESHOLD = 0.85
NEAR_DUP_NGRAM_N = 5


def gather() -> list[LabelledItem]:
    """Collect items from every available raw source."""
    items: list[LabelledItem] = []

    uci_path = RAW / "uci_sms_spam" / "SMSSpamCollection"
    if uci_path.exists():
        items.extend(load_uci_sms_spam(uci_path))
        print(f"  loaded UCI SMS Spam: running total = {len(items):,}")
    else:
        print(f"  [missing] {uci_path}; run 01_download_public.py first")

    nazario_dir = RAW / "nazario"
    if nazario_dir.exists():
        items.extend(load_nazario_phishing(nazario_dir))
        print(f"  loaded Nazario phishing: running total = {len(items):,}")
    else:
        print(f"  [missing] {nazario_dir}; manual download required, see 01_download_public.py")

    # JSONL-materialised streams (already in our schema): regional news
    # (07_scrape_regional.py) plus the extra public sources (07b).
    for label, rel in (
        ("regional stream", RAW / "regional" / "regional_news.jsonl"),
        ("Nazario emails", RAW / "nazario" / "nazario_emails.jsonl"),
        ("smishing SMS", RAW / "smishing" / "smishing_sms.jsonl"),
        ("MOZ smishing", RAW / "moz_smishing" / "moz_smishing.jsonl"),
    ):
        if rel.exists():
            before = len(items)
            items.extend(read_jsonl(rel))
            print(f"  loaded {label}: +{len(items) - before:,}, "
                  f"running total = {len(items):,}")
        else:
            print(f"  [missing] {rel}")

    return items


def deduplicate(items: list[LabelledItem]) -> list[LabelledItem]:
    """Drop exact-text duplicates by id (SHA1 hash of text)."""
    seen: set[str] = set()
    keep: list[LabelledItem] = []
    for item in items:
        if item.id in seen:
            continue
        seen.add(item.id)
        keep.append(item)
    dropped = len(items) - len(keep)
    print(f"  exact-dedup: kept {len(keep):,} of {len(items):,} ({dropped:,} dropped)")
    return keep


def _ngram_set(text: str, n: int = NEAR_DUP_NGRAM_N) -> frozenset[str]:
    """Character n-gram set for Jaccard similarity."""
    t = text.lower().strip()
    if len(t) < n:
        return frozenset([t])
    return frozenset(t[i:i + n] for i in range(len(t) - n + 1))


def near_dedup(items: list[LabelledItem]) -> list[LabelledItem]:
    """Drop near-duplicates by character 5-gram Jaccard similarity ≥ 0.85.

    Items are checked in arrival order, so the FIRST occurrence wins.

    Scales past the naive O(n²) by exploiting a property of Jaccard: if
    J(A,B) ≥ t then min(|A|,|B|)/max(|A|,|B|) ≥ t, because |A∩B| ≤ min and
    |A∪B| ≥ max. So a candidate need only be compared against kept fingerprints
    whose size lies in ``[t·|fp|, |fp|/t]``. Kept fingerprints are held in arrays
    sorted by size, and ``bisect`` selects just that band — turning the cross-
    product into per-item comparisons against same-length neighbours only.
    """
    import bisect

    t = NEAR_DUP_JACCARD_THRESHOLD
    sizes: list[int] = []                  # kept fingerprint sizes, sorted
    fps: list[frozenset[str]] = []         # kept fingerprints, aligned to sizes
    keep: list[LabelledItem] = []
    for item in items:
        fp = _ngram_set(item.text)
        s = len(fp)
        if s == 0:
            keep.append(item)
            continue
        lo = bisect.bisect_left(sizes, t * s)
        hi = bisect.bisect_right(sizes, s / t)
        is_near = False
        for j in range(lo, hi):
            existing = fps[j]
            inter = len(fp & existing)
            union = s + sizes[j] - inter
            if union and (inter / union) >= t:
                is_near = True
                break
        if not is_near:
            keep.append(item)
            pos = bisect.bisect_left(sizes, s)
            sizes.insert(pos, s)
            fps.insert(pos, fp)
    dropped = len(items) - len(keep)
    print(f"  near-dedup:  kept {len(keep):,} of {len(items):,} "
          f"({dropped:,} dropped, J>={NEAR_DUP_JACCARD_THRESHOLD})")
    return keep


def length_filter(items: list[LabelledItem]) -> list[LabelledItem]:
    """Drop records outside the [MIN_TEXT_LEN, MAX_TEXT_LEN] character band."""
    keep = [it for it in items if MIN_TEXT_LEN <= len(it.text) <= MAX_TEXT_LEN]
    dropped = len(items) - len(keep)
    print(f"  length-filt: kept {len(keep):,} of {len(items):,} "
          f"({dropped:,} dropped, band [{MIN_TEXT_LEN}, {MAX_TEXT_LEN}])")
    return keep


if __name__ == "__main__":
    print(f"Reading from {RAW}\n")
    items = gather()
    if not items:
        print("\nNo items loaded. Did you run 01_download_public.py?")
        sys.exit(1)
    print()
    items = deduplicate(items)
    items = length_filter(items)
    items = near_dedup(items)
    out = LABELLED / "unlabelled.jsonl"
    n = write_jsonl(items, out)
    print(f"\nWrote {n:,} records to {out}")
    print("Next: python ml/scripts/03_label_helper.py")
