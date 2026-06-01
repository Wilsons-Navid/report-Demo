"""Unified JSONL schema for labelled items.

Every record in ``data/labelled/*.jsonl`` is one ``LabelledItem`` serialised
to JSON. This is the contract the rest of the pipeline depends on.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable, Iterator, Optional

from pydantic import BaseModel, Field

from .taxonomy import ScamCategory


class SourceStream(str, Enum):
    PUBLIC = "public"        # Nazario / UCI / Kaggle / HuggingFace / etc.
    REGIONAL = "regional"    # ngCERT / ANTIC / EFCC / West African news
    PILOT = "pilot"          # collected from the W8 pilot in Lagos / Douala


class LabelSource(str, Enum):
    RATER1 = "rater1"
    RATER2 = "rater2"
    ADJUDICATED = "adjudicated"
    AUTO = "auto"            # placeholder; never used at audit time


class LabelledItem(BaseModel):
    """One row of the corpus."""

    id: str = Field(description="UUID4 or stable text-hash")
    text: str
    language: str = Field(description="ISO 639-1; use 'pcm' for Nigerian Pidgin")
    source_stream: SourceStream
    source_url: Optional[str] = None
    original_label: Optional[str] = Field(
        default=None,
        description="The source dataset's own label, kept for traceability.",
    )

    category: ScamCategory
    label_source: LabelSource
    labelled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# -----------------------------------------------------------------------------
# I/O helpers
# -----------------------------------------------------------------------------

def stable_id(text: str) -> str:
    """Return a 12-char stable hash of ``text``; used when no id is given."""
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:12]


def write_jsonl(items: Iterable[LabelledItem], path: Path) -> int:
    """Write ``items`` to ``path`` as JSON-Lines. Returns the count written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as fh:
        for item in items:
            fh.write(item.model_dump_json() + "\n")
            count += 1
    return count


def read_jsonl(path: Path) -> Iterator[LabelledItem]:
    """Yield ``LabelledItem`` records from a JSONL file."""
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield LabelledItem.model_validate(json.loads(line))
