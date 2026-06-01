"""Loaders that normalise raw public datasets into ``LabelledItem`` records.

Each loader yields ``LabelledItem`` instances with ``category=NOT_A_SCAM``
as the starting label — the real category is assigned during the labelling
pass. Loaders only do extraction and language tagging.

When the supervisor approves Objective 1, these modules migrate to
``ml/src/loaders.py``.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from .schema import LabelledItem, LabelSource, SourceStream, stable_id
from .taxonomy import ScamCategory


def load_uci_sms_spam(path: Path) -> Iterator[LabelledItem]:
    """Load the UCI SMS Spam Collection (TSV with columns: label, text).

    The native labels are ``ham`` / ``spam``. We retain them as
    ``original_label`` and leave ``category=NOT_A_SCAM`` for the labelling
    pass to overwrite.
    """
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        for row in reader:
            if len(row) != 2:
                continue
            original, text = row[0].strip(), row[1].strip()
            if not text:
                continue
            yield LabelledItem(
                id=stable_id(text),
                text=text,
                language="en",
                source_stream=SourceStream.PUBLIC,
                source_url="https://archive.ics.uci.edu/ml/datasets/sms+spam+collection",
                original_label=original,
                category=ScamCategory.NOT_A_SCAM,    # placeholder; relabelled in pass
                label_source=LabelSource.AUTO,
            )


def load_nazario_phishing(directory: Path) -> Iterator[LabelledItem]:
    """Load the Nazario phishing-email corpus (one email per file).

    The corpus distribution is a directory of email files; this loader walks
    the directory, treats the body of each as a single text record, and tags
    every record as English (the corpus is English-only).

    TODO: real implementation needs an email parser (``email`` standard
    library). For the scaffold we just walk plain-text files.
    """
    for path in sorted(directory.rglob("*.txt")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            continue
        if not text:
            continue
        yield LabelledItem(
            id=stable_id(text),
            text=text,
            language="en",
            source_stream=SourceStream.PUBLIC,
            source_url="https://monkey.org/~jose/wiki/doku.php?id=PhishingCorpus",
            original_label="phishing",
            category=ScamCategory.NOT_A_SCAM,
            label_source=LabelSource.AUTO,
        )


def _iter_mbox_messages(path: Path) -> Iterator[bytes]:
    """Yield raw message bytes from an mbox file.

    The stdlib ``mailbox`` module fails on Windows here, so we split manually on
    the ``\\nFrom `` separator that begins each mbox entry.
    """
    raw = path.read_bytes()
    for i, part in enumerate(raw.split(b"\nFrom ")):
        if i > 0:
            part = b"From " + part
        if len(part) > 50:
            yield part


def load_nazario_mbox_dir(directory: Path, *, lead_chars: int = 1500) -> Iterator[LabelledItem]:
    """Load the Nazario phishing/419 email corpus from a directory of .mbox files.

    Each email becomes one record whose text is ``Subject + body lead`` (capped
    at ``lead_chars`` so it survives the normaliser's length band; full emails
    routinely exceed 2,000 chars). The corpus is real phishing and West-African
    advance-fee ("419") mail — so ``original_label='nazario_phishing'`` and the
    true taxonomy category (phishing vs advance_fee_fraud) is set at labelling.
    """
    import email
    from email import policy

    for mbox_path in sorted(directory.glob("*.mbox")):
        for raw in _iter_mbox_messages(mbox_path):
            try:
                msg = email.message_from_bytes(raw, policy=policy.default)
            except Exception:
                continue
            subject = str(msg.get("Subject", "") or "").strip()
            body = ""
            try:
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_content()
                            break
                elif msg.get_content_type() == "text/plain":
                    body = msg.get_content()
            except Exception:
                body = ""
            if not isinstance(body, str):
                body = ""
            text = " ".join(f"{subject} {body}".split())[:lead_chars].strip()
            if not text:
                continue
            yield LabelledItem(
                id=stable_id(text),
                text=text,
                language="en",
                source_stream=SourceStream.PUBLIC,
                source_url="https://monkey.org/~jose/phishing/",
                original_label="nazario_phishing",
                category=ScamCategory.NOT_A_SCAM,
                label_source=LabelSource.AUTO,
            )


def load_smishing_csv(path: Path) -> Iterator[LabelledItem]:
    """Load the Mendeley SMS-phishing dataset (Mishra & Soni, f45bkkt8pr).

    Columns: LABEL, TEXT, URL, EMAIL, PHONE. LABEL in {ham, spam, Smishing}
    (case varies). We keep the non-ham rows (smishing + spam) — the ham is the
    UCI base we already have — and carry the dataset's own label through as
    ``original_label`` for traceability.
    """
    with path.open("r", encoding="latin-1") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            label = (row.get("LABEL") or "").strip().lower()
            if label == "ham":
                continue
            text = (row.get("TEXT") or "").strip()
            if not text:
                continue
            yield LabelledItem(
                id=stable_id(text),
                text=text,
                language="en",
                source_stream=SourceStream.PUBLIC,
                source_url="mendeley:f45bkkt8pr",
                original_label=f"smishing_ds:{label}",
                category=ScamCategory.NOT_A_SCAM,
                label_source=LabelSource.AUTO,
            )


def load_moz_smishing_csv(path: Path) -> Iterator[LabelledItem]:
    """Load the MOZ-Smishing benchmark (HF MOZNLP/MOZ-Smishing).

    Columns: id, source, text, label (label in {Legitimate, Smishing}).
    Crowd-sourced Mozambican mobile-money smishing, mostly Portuguese microtext.
    We keep the Smishing rows — the gap the English sources don't fill
    (mobile_money_fraud + lusophone-Africa coverage). language='pt'.
    """
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            if (row.get("label") or "").strip() != "Smishing":
                continue
            text = (row.get("text") or "").strip()
            if not text:
                continue
            yield LabelledItem(
                id=stable_id(text),
                text=text,
                language="pt",
                source_stream=SourceStream.PUBLIC,
                source_url="hf:MOZNLP/MOZ-Smishing",
                original_label="moz_smishing",
                category=ScamCategory.NOT_A_SCAM,
                label_source=LabelSource.AUTO,
            )


def load_kaggle_scam_csv(path: Path, *, text_col: str, label_col: str | None = None,
                        language: str = "en") -> Iterator[LabelledItem]:
    """Generic loader for Kaggle scam/phishing CSVs.

    Supply the column name that holds the text and (optionally) the column
    that holds the source's own label. Adjust per-dataset.
    """
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            text = (row.get(text_col) or "").strip()
            if not text:
                continue
            original = row.get(label_col) if label_col else None
            yield LabelledItem(
                id=stable_id(text),
                text=text,
                language=language,
                source_stream=SourceStream.PUBLIC,
                source_url=f"kaggle:{path.name}",
                original_label=original,
                category=ScamCategory.NOT_A_SCAM,
                label_source=LabelSource.AUTO,
            )
