"""Confirm-or-correct pass over the prioritised worklist.

Reads ``data/labelled/worklist.jsonl`` (built by 08, optionally improved by a
smarter-suggestion pass) and shows each item with its PRE-COMPUTED suggested
category. The rater confirms with a single keypress or overrides. Confirmed
labels are written to ``rater1.jsonl`` with ``label_source=RATER1`` — i.e. a
human decided every one. Resume-safe (skips ids already in rater1.jsonl).

This is the fast path: because the worklist is scam-first and the suggestions
are pre-computed (not the weak live heuristic), most items are a single Enter.

Keys:
  y / <enter>    accept the shown suggestion
  1-7            override to a specific category
  s              skip (do not write)
  u              undo last write (pops the last line from rater1.jsonl)
  q              save and quit
  ?              help

Run with: ``python ml/scripts/09_confirm_worklist.py``
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.schema import LabelledItem, LabelSource, read_jsonl, write_jsonl
from src.taxonomy import ScamCategory, CATEGORY_DESCRIPTIONS

LABELLED = ROOT / "data" / "labelled"
INPUT_PATH = LABELLED / "worklist.jsonl"
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
CATEGORY_TO_KEY = {v: k for k, v in KEY_TO_CATEGORY.items()}


def already_labelled() -> set[str]:
    if not OUTPUT_PATH.exists():
        return set()
    return {item.id for item in read_jsonl(OUTPUT_PATH)}


def append_jsonl(item: LabelledItem) -> None:
    with OUTPUT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(item.model_dump_json() + "\n")


def pop_last_line() -> str | None:
    """Remove and return the id of the last written record (undo)."""
    if not OUTPUT_PATH.exists():
        return None
    lines = OUTPUT_PATH.read_text(encoding="utf-8").splitlines()
    if not lines:
        return None
    last = lines.pop()
    OUTPUT_PATH.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    try:
        import json
        return json.loads(last).get("id")
    except ValueError:
        return None


def show_help() -> None:
    print()
    for key, cat in KEY_TO_CATEGORY.items():
        print(f"  {key}  {cat.value:24} {CATEGORY_DESCRIPTIONS[cat][:60]}")
    print("  y/<enter> accept   s skip   u undo last   q quit   ? help")


def main() -> None:
    if not INPUT_PATH.exists():
        print(f"No worklist at {INPUT_PATH}. Run 08_build_worklist.py first.")
        sys.exit(1)

    seen = already_labelled()
    items = [it for it in read_jsonl(INPUT_PATH) if it.id not in seen]
    if not items:
        print(f"Nothing left: every worklist item is already in {OUTPUT_PATH.name}.")
        sys.exit(0)

    done = len(seen)
    total = done + len(items)
    print(f"{len(items):,} to confirm ({done:,} already done, {total:,} in worklist).")
    print("Enter = accept the suggestion. Type ? for the category key.\n")

    written = Counter()
    i = 0
    while i < len(items):
        item = items[i]
        suggestion = item.category
        sug_key = CATEGORY_TO_KEY[suggestion]
        print("-" * 72)
        print(f"[{done + i + 1}/{total}] id={item.id}  lang={item.language}  "
              f"stream={item.source_stream.value}")
        print(f"text: {item.text[:400]}{'...' if len(item.text) > 400 else ''}")
        print(f"  >>> suggestion: [{sug_key}] {suggestion.value}")
        key = input("  > ").strip().lower()

        if key == "q":
            print("\nSaved and quit.")
            break
        if key == "?":
            show_help()
            continue
        if key == "u":
            uid = pop_last_line()
            print(f"  undid last write (id={uid}). Re-deciding previous item.")
            if i > 0:
                i -= 1
            continue
        if key == "s":
            i += 1
            continue
        if key in ("", "y"):
            chosen = suggestion
        elif key in KEY_TO_CATEGORY:
            chosen = KEY_TO_CATEGORY[key]
        else:
            print("  ?? unknown key; ? for help")
            continue

        append_jsonl(item.model_copy(update={
            "category": chosen,
            "label_source": LabelSource.RATER1,
        }))
        written[chosen.value] += 1
        i += 1

    n_written = sum(written.values())
    print(f"\nWrote {n_written:,} confirmed labels this session -> {OUTPUT_PATH}")
    print(f"Cumulative rater1 total: {len(already_labelled()):,}")
    if written:
        print("This session by category:")
        for cat, c in written.most_common():
            print(f"  {cat:24} {c:,}")


if __name__ == "__main__":
    main()
