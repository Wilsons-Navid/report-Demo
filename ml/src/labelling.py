"""Labelling-workflow helpers: audit sampling + Cohen's κ.

Two-stage protocol locked by proposal Section 3.4.1:
  1. Rater 1 labels every retained item (category in [taxonomy.ScamCategory]).
  2. A random 100-item sample is independently relabelled by Rater 2.
  3. Cohen's κ is computed on that sample; must be ≥ 0.7 to accept the corpus.
  4. Disagreements are adjudicated by discussion and resolution propagated.

When the supervisor approves Objective 1, this module migrates to
``ml/src/labelling.py``.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Iterable

from .schema import LabelledItem, LabelSource, read_jsonl, write_jsonl
from .taxonomy import ScamCategory


# -----------------------------------------------------------------------------
# Audit sampling
# -----------------------------------------------------------------------------

def sample_audit(items: list[LabelledItem], *, n: int = 100,
                 seed: int = 42) -> list[LabelledItem]:
    """Return a stratified random sample of ``n`` items for Rater 2.

    Stratified across categories so that each category contributes roughly
    its share of the sample, never zero items if the source has any.
    """
    rng = random.Random(seed)
    by_category: dict[ScamCategory, list[LabelledItem]] = {}
    for item in items:
        by_category.setdefault(item.category, []).append(item)

    if not by_category:
        return []

    base_per_cat = n // len(by_category)

    sample: list[LabelledItem] = []
    chosen_ids: set[str] = set()
    for cat, cat_items in by_category.items():
        k = min(base_per_cat, len(cat_items))
        for it in rng.sample(cat_items, k):
            sample.append(it)
            chosen_ids.add(it.id)

    # Backfill up to ``n`` from everything not yet chosen. Small categories cap
    # out below ``base_per_cat`` (e.g. mobile_money_fraud may only have a
    # handful of items), so the deficit is ``n - len(sample)``, not just the
    # ``n // len`` remainder — covering the full deficit keeps the audit at the
    # committed size whenever the corpus has enough total items.
    deficit = n - len(sample)
    if deficit > 0:
        leftover = [
            item
            for cat_items in by_category.values()
            for item in cat_items
            if item.id not in chosen_ids
        ]
        rng.shuffle(leftover)
        sample.extend(leftover[:deficit])

    rng.shuffle(sample)
    return sample[:n]


def write_audit_sample(items: list[LabelledItem], path: Path) -> int:
    """Write the audit sample to disk for Rater 2 to consume."""
    # Strip the label so Rater 2 sees only the text + metadata.
    blinded = [
        item.model_copy(update={
            "category": ScamCategory.NOT_A_SCAM,
            "label_source": LabelSource.AUTO,
        })
        for item in items
    ]
    return write_jsonl(blinded, path)


# -----------------------------------------------------------------------------
# Cohen's κ
# -----------------------------------------------------------------------------

def cohen_kappa(rater1_labels: list[ScamCategory],
                rater2_labels: list[ScamCategory]) -> float:
    """Compute Cohen's κ between two raters on identical item sets.

    Both lists must be the same length, with index-aligned labels.
    """
    if len(rater1_labels) != len(rater2_labels):
        raise ValueError("Rater lists must be equal length")
    if not rater1_labels:
        return 0.0

    from sklearn.metrics import cohen_kappa_score

    return float(cohen_kappa_score(
        [c.value for c in rater1_labels],
        [c.value for c in rater2_labels],
    ))


def kappa_from_paths(rater1_path: Path, rater2_path: Path) -> float:
    """Convenience: read two JSONL files and compute κ on aligned items.

    Items are aligned by their ``id`` field; only the intersection is scored.
    """
    r1 = {item.id: item.category for item in read_jsonl(rater1_path)}
    r2 = {item.id: item.category for item in read_jsonl(rater2_path)}

    shared = sorted(set(r1) & set(r2))
    if not shared:
        return 0.0

    return cohen_kappa(
        [r1[i] for i in shared],
        [r2[i] for i in shared],
    )


# Acceptance threshold from proposal Objective 1
KAPPA_ACCEPTANCE_THRESHOLD = 0.7
