"""Apply improved category suggestions into the worklist.

Reads a JSON mapping ``{id: category_value}`` from a file (or stdin) and
overwrites the ``category`` field of matching records in ``worklist.jsonl``.
These are still SUGGESTIONS (label_source stays AUTO); the human confirm pass
(09_confirm_worklist.py) shows them and the rater accepts/overrides.

Used to fold in a smarter-than-keyword suggestion pass without re-running the
whole worklist build. Unknown ids are reported and skipped; unknown category
values raise.

Run with: ``python ml/scripts/apply_suggestions.py path/to/overrides.json``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.schema import read_jsonl, write_jsonl
from src.taxonomy import ScamCategory

WORKLIST = ROOT / "data" / "labelled" / "worklist.jsonl"

VALID = {c.value for c in ScamCategory}


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python ml/scripts/apply_suggestions.py <overrides.json>")
        sys.exit(2)

    overrides: dict[str, str] = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    bad = {v for v in overrides.values() if v not in VALID}
    if bad:
        print(f"Invalid category values: {bad}\nValid: {sorted(VALID)}")
        sys.exit(1)

    items = list(read_jsonl(WORKLIST))
    by_id = {it.id: it for it in items}

    applied = 0
    missing = []
    for item_id, cat in overrides.items():
        it = by_id.get(item_id)
        if it is None:
            missing.append(item_id)
            continue
        it.category = ScamCategory(cat)
        applied += 1

    write_jsonl(items, WORKLIST)
    print(f"Applied {applied:,} suggestion overrides to {WORKLIST.name}.")
    if missing:
        print(f"  {len(missing)} ids not found in worklist (skipped): {missing[:5]}...")


if __name__ == "__main__":
    main()
