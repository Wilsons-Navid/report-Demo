"""Download the public datasets named in proposal Section 3.4.1.

This is the FIRST step in building the corpus. Each download is small enough
to fit comfortably in a free-tier disk allowance (a few hundred MB at most).

Run with: ``python ml_potential/scripts/01_download_public.py``

When the supervisor approves Objective 1, this script migrates to
``ml/scripts/``.
"""

from __future__ import annotations

import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)


def _download(url: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  [skip] {dest.name} already present ({dest.stat().st_size:,} bytes)")
        return dest
    print(f"  [get ] {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    print(f"         -> {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def fetch_uci_sms_spam() -> None:
    """UCI SMS Spam Collection — 5,574 labelled SMS messages, English."""
    print("UCI SMS Spam Collection")
    zip_path = _download(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip",
        RAW / "uci_sms_spam" / "smsspamcollection.zip",
    )
    out_dir = RAW / "uci_sms_spam"
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(out_dir)
    print(f"         extracted to {out_dir}")


def fetch_nazario_phishing() -> None:
    """Nazario phishing corpus — placeholder.

    The original distribution is hosted at https://monkey.org/~jose/phishing/
    and is gated behind a manual download form. Add a guidance message rather
    than a broken URL.
    """
    print("Nazario phishing corpus")
    print("  [todo] Manual download from https://monkey.org/~jose/wiki/doku.php?id=PhishingCorpus")
    print("         Save the .mbox / .tar archives into ml/data/raw/nazario/")


def fetch_kaggle_phishing() -> None:
    """Kaggle phishing/scam datasets — placeholder.

    Kaggle's API requires an authenticated kaggle.json token. Print
    instructions rather than attempting an unauthenticated download.
    """
    print("Kaggle phishing/scam datasets")
    print("  [todo] Configure ~/.kaggle/kaggle.json with your API token")
    print("         Then: kaggle datasets download <author>/<dataset> -p ml/data/raw/kaggle/")


if __name__ == "__main__":
    print(f"Downloading into {RAW}\n")
    fetch_uci_sms_spam()
    print()
    fetch_nazario_phishing()
    print()
    fetch_kaggle_phishing()
    print("\nDone. Next: python ml/scripts/02_normalise.py")
