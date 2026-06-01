"""AI-assisted labelling CLI: confirm-or-override loop.

For each unlabelled item, the assistant suggests a category with a short
reason citing the patterns that triggered. The human rater either confirms
(`y`) or overrides with the right digit (`1`-`7`).

Output is identical to the manual labeller — the same ``rater1.jsonl`` file
with ``label_source=RATER1`` — so the integrity story holds: every label was
confirmed by the human rater.

Throughput target: ~250 items/hour (vs ~60/hour with the pure-manual CLI).

Run with: ``python ml/scripts/03b_assisted_label.py``

Optional flags:
  --skip-strong   auto-accept anything with confidence >= 0.85 (use sparingly)
  --auto-mark     when --skip-strong, mark auto-accepted items label_source=AUTO
                  instead of RATER1 (so the integrity story stays accurate)

Keys at the prompt:
  y / <enter>    accept the suggested category
  1-7            override to a specific category
  s              skip (do not write)
  q              save and quit
  ?              show this help
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.auto_label import confidence_band, suggest
from src.schema import LabelledItem, LabelSource, read_jsonl, write_jsonl
from src.taxonomy import ScamCategory


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

CATEGORY_TO_KEY = {v: k for k, v in KEY_TO_CATEGORY.items()}

AUTO_ACCEPT_THRESHOLD = 0.85


def already_labelled() -> set[str]:
    if not OUTPUT_PATH.exists():
        return set()
    return {item.id for item in read_jsonl(OUTPUT_PATH)}


def append_jsonl(item: LabelledItem) -> None:
    with OUTPUT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(item.model_dump_json() + "\n")


def show_help() -> None:
    print()
    print("  y / <enter>  accept the AI-suggested category")
    print("  1 advance_fee_fraud      5 identity_theft")
    print("  2 mobile_money_fraud     6 synthetic_media_fraud")
    print("  3 phishing               7 not_a_scam")
    print("  4 romance_scam")
    print("  s            skip (do not write)")
    print("  q            save and quit")
    print("  ?            show this help")


def label_one(item: LabelledItem, *, auto_skip_strong: bool, auto_mark_source: LabelSource) -> tuple[LabelledItem | None, str]:
    """Return ``(item-or-None, action_str)``.

    ``item is None`` -> quit signal.
    ``action_str`` is one of: 'labelled', 'skipped', 'auto'.
    """
    cat, conf, reason = suggest(item.text)
    band = confidence_band(conf)

    if auto_skip_strong and conf >= AUTO_ACCEPT_THRESHOLD:
        return item.model_copy(update={
            "category": cat,
            "label_source": auto_mark_source,
        }), "auto"

    print("\n" + "-" * 70)
    print(f"id={item.id}  lang={item.language}  stream={item.source_stream.value}  "
          f"orig={item.original_label}")
    print(f"text:\n  {item.text[:600]}{'...' if len(item.text) > 600 else ''}")
    print()
    print(f"  >>> Suggestion: {cat.value}  [{band}, conf={conf:.2f}]")
    print(f"      reason: {reason}")
    print(f"      [y]=accept   1-7=override   s=skip   q=quit   ?=help")
    while True:
        key = input("> ").strip().lower()
        if key in ("", "y"):
            return item.model_copy(update={
                "category": cat,
                "label_source": LabelSource.RATER1,
            }), "labelled"
        if key == "q":
            return None, "quit"
        if key == "s":
            return None, "skipped"      # caller skips writing
        if key == "?":
            show_help()
            continue
        if key in KEY_TO_CATEGORY:
            return item.model_copy(update={
                "category": KEY_TO_CATEGORY[key],
                "label_source": LabelSource.RATER1,
            }), "labelled"
        print("  ?? unknown key; type ? for help")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI-assisted labelling CLI for the WA scam corpus.",
    )
    parser.add_argument(
        "--skip-strong",
        action="store_true",
        help=(f"Auto-accept suggestions with confidence >= {AUTO_ACCEPT_THRESHOLD}. "
              "Reduces clicks but you should spot-check the result."),
    )
    parser.add_argument(
        "--auto-mark",
        action="store_true",
        help=("Used with --skip-strong: mark auto-accepted items label_source=AUTO "
              "instead of RATER1, so the integrity story stays accurate. "
              "Recommend ON if you use --skip-strong."),
    )
    args = parser.parse_args()

    if not INPUT_PATH.exists():
        print(f"No unlabelled corpus at {INPUT_PATH}.")
        print("Did you run 01_download_public.py and 02_normalise.py?")
        sys.exit(1)

    seen = already_labelled()
    items = [item for item in read_jsonl(INPUT_PATH) if item.id not in seen]

    if not items:
        print("Nothing left to label. All items in unlabelled.jsonl are in rater1.jsonl.")
        sys.exit(0)

    auto_mark_source = LabelSource.AUTO if args.auto_mark else LabelSource.RATER1
    if args.skip_strong:
        print(f"--skip-strong: auto-accepting suggestions with confidence >= "
              f"{AUTO_ACCEPT_THRESHOLD} (marked label_source={auto_mark_source.value}).")

    print(f"{len(items):,} items remaining to label.")
    print(f"Labels will be appended to {OUTPUT_PATH} (resume-safe).")

    labelled = 0
    skipped = 0
    auto = 0
    try:
        for item in items:
            result, action = label_one(
                item,
                auto_skip_strong=args.skip_strong,
                auto_mark_source=auto_mark_source,
            )
            if action == "quit":
                print("\nSaved and quit.")
                break
            if action == "skipped":
                skipped += 1
                continue
            append_jsonl(result)  # type: ignore[arg-type]
            if action == "auto":
                auto += 1
            else:
                labelled += 1
            total_written = labelled + auto
            if total_written and total_written % 25 == 0:
                print(f"\n  progress: {labelled} confirmed, {auto} auto-accepted, "
                      f"{skipped} skipped")
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted. Progress saved up to the last accepted item.")

    print(f"\nDone. {labelled} confirmed + {auto} auto-accepted labels written "
          f"to {OUTPUT_PATH}.")
    print(f"Cumulative rater1+auto total in file: "
          f"{len(already_labelled())}")


if __name__ == "__main__":
    main()
