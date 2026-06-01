"""Produce a 70/15/15 train/dev/test split, stratified by (category × language).

Reads from ``ml/data/labelled/rater1.jsonl`` (post-audit, post-adjudication)
and writes:

  ml/data/labelled/train.jsonl   (70%)
  ml/data/labelled/dev.jsonl     (15%)
  ml/data/labelled/test.jsonl    (15%)

Stratification is on the joint (category, language) cell so both dimensions
stay balanced across the splits. The held-out test set is the artefact that
Objective 3 numbers are reported on; per proposal §3.4.2 it must be touched
exactly once, after all model decisions are finalised.

Run with: ``python ml/scripts/06_split.py``
"""

from __future__ import annotations

import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.schema import LabelledItem, read_jsonl, write_jsonl


LABELLED = ROOT / "data" / "labelled"
SOURCE = LABELLED / "rater1.jsonl"

TRAIN_RATIO = 0.70
DEV_RATIO = 0.15
TEST_RATIO = 0.15
SEED = 42


def stratified_split(
    items: list[LabelledItem],
    *,
    train_ratio: float = TRAIN_RATIO,
    dev_ratio: float = DEV_RATIO,
    seed: int = SEED,
) -> tuple[list[LabelledItem], list[LabelledItem], list[LabelledItem]]:
    """Stratify on (category, language) and split each cell train/dev/test.

    Items within a cell are shuffled with ``seed`` then cut at ``train_ratio``
    and ``train_ratio + dev_ratio``. Remaining items go to test.
    """
    rng = random.Random(seed)
    cells: dict[tuple[str, str], list[LabelledItem]] = defaultdict(list)
    for item in items:
        key = (item.category.value, item.language)
        cells[key].append(item)

    train: list[LabelledItem] = []
    dev: list[LabelledItem] = []
    test: list[LabelledItem] = []

    for key, cell_items in cells.items():
        rng.shuffle(cell_items)
        n = len(cell_items)
        n_train = round(n * train_ratio)
        n_dev = round(n * dev_ratio)
        train.extend(cell_items[:n_train])
        dev.extend(cell_items[n_train:n_train + n_dev])
        test.extend(cell_items[n_train + n_dev:])

    return train, dev, test


def _report_distribution(
    name: str,
    items: list[LabelledItem],
) -> None:
    by_cat: dict[str, int] = defaultdict(int)
    by_lang: dict[str, int] = defaultdict(int)
    for it in items:
        by_cat[it.category.value] += 1
        by_lang[it.language] += 1
    print(f"  {name}: {len(items):,} items")
    print(f"    by category: {dict(sorted(by_cat.items()))}")
    print(f"    by language: {dict(sorted(by_lang.items()))}")


def main() -> None:
    if not SOURCE.exists():
        print(f"No corpus at {SOURCE}.")
        print("Did you finish steps 03 (label) and 05 (κ check)?")
        sys.exit(1)

    items = list(read_jsonl(SOURCE))
    print(f"Loaded {len(items):,} labelled items from {SOURCE}\n")

    train, dev, test = stratified_split(items)

    train_path = LABELLED / "train.jsonl"
    dev_path = LABELLED / "dev.jsonl"
    test_path = LABELLED / "test.jsonl"

    write_jsonl(train, train_path)
    write_jsonl(dev, dev_path)
    write_jsonl(test, test_path)

    print(f"Split with seed={SEED}, ratios {TRAIN_RATIO:.2f}/{DEV_RATIO:.2f}/{TEST_RATIO:.2f}")
    print()
    _report_distribution("train", train)
    _report_distribution("dev  ", dev)
    _report_distribution("test ", test)
    print()
    print(f"Wrote:")
    print(f"  {train_path}")
    print(f"  {dev_path}")
    print(f"  {test_path}")
    print()
    print("Corpus is now ready for the comparative evaluation (Objective 3).")
    print("The test set must be touched only ONCE, after all model decisions are finalised.")


if __name__ == "__main__":
    main()
