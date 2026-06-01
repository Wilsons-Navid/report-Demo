"""Scrapers for West African regional-stream data.

The regional stream (proposal §3.4.1) is meant to capture scam narratives that
the public English/Western datasets miss: mobile-money fraud, West-African
advance-fee patterns, locally-named institutions, French- and Pidgin-language
framing.

Reachability reality (probed 2026-06-01):
  - Nigeria ngCERT (cert.gov.ng)      -> 403, Cloudflare anti-bot wall
  - Cameroon ANTIC (antic.cm)         -> connection timeout (host unreachable)
  - Nigeria EFCC (efccnigeria.org)    -> 200 but empty shell / news path 404
  - Premium Times (premiumtimesng.com)-> 200, and exposes a WordPress REST API

So the one source that reliably yields structured, query-filtered content is
Premium Times via its ``/wp-json/wp/v2/posts`` endpoint. The institutional
advisory scrapers are kept as documented, non-crashing probes: they attempt the
fetch, report the block, and yield nothing. That the official advisories are
unscrapable is itself a finding for the data-collection limitations section.

Granularity: a news article that narrates a scam is emitted as one or more
``LabelledItem`` records at the *paragraph* level, keeping only paragraphs that
trip a scam-relevance gate. Every record starts as ``category=NOT_A_SCAM`` /
``label_source=AUTO``; the real category is assigned in the human labelling
pass (script 03b), never here.

Run via ``python ml/scripts/07_scrape_regional.py``.
"""

from __future__ import annotations

import time
from typing import Iterable, Iterator

import requests
from bs4 import BeautifulSoup

from .schema import LabelledItem, LabelSource, SourceStream, stable_id
from .taxonomy import ScamCategory

# A browser User-Agent; several of these outlets 403 a bare urllib agent.
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
_HEADERS = {"User-Agent": _UA}
_TIMEOUT = 20
_POLITE_DELAY = 1.0  # seconds between requests; respect the outlet

# Paragraphs shorter than this are skipped as boilerplate/captions.
_MIN_PARA_LEN = 60
_MAX_PARA_LEN = 1500

# A paragraph is kept only if it actually talks about a scam. This is a coarse
# relevance gate, not a labeller — it just stops us harvesting unrelated prose
# from an article that happens to mention fraud once in passing.
_RELEVANCE_TERMS = (
    "scam", "scammer", "fraud", "fraudster", "fraudulent", "defraud",
    "phishing", "phished", "ponzi", "419", "advance fee", "advance-fee",
    "mobile money", "momo", "pos fraud", "sim swap", "sim-swap",
    "fake alert", "wire transfer", "impersonat", "yahoo boy", "yahoo-boy",
    "romance scam", "dating scam", "investment scam", "cloned", "deepfake",
    "one-time password", "otp", "bvn", "nin", "account takeover",
    "fake", "swindle", "dupe", "duped", "con artist", "extort",
)


def _is_relevant(text: str) -> bool:
    t = text.lower()
    return any(term in t for term in _RELEVANCE_TERMS)


def _clean_paragraphs(html: str) -> list[str]:
    """Return substantial, de-boilerplated paragraphs from a content blob."""
    soup = BeautifulSoup(html, "html.parser")
    out: list[str] = []
    seen: set[str] = set()
    for p in soup.find_all("p"):
        txt = " ".join(p.get_text(" ", strip=True).split())
        if not (_MIN_PARA_LEN <= len(txt) <= _MAX_PARA_LEN):
            continue
        if txt in seen:
            continue
        seen.add(txt)
        out.append(txt)
    return out


# ---------------------------------------------------------------------------
# Premium Times — the one source that works (WordPress REST API)
# ---------------------------------------------------------------------------

_PT_API = "https://www.premiumtimesng.com/wp-json/wp/v2/posts"

# Default search terms span the categories the regional stream is meant to add.
PREMIUM_TIMES_QUERIES = (
    "mobile money fraud",
    "POS fraud",
    "advance fee fraud",
    "romance scam",
    "phishing bank",
    "SIM swap fraud",
    "BVN fraud",
    "internet fraud Nigeria",
    "fake alert fraud",
    "deepfake scam",
)


def scrape_premium_times(
    queries: Iterable[str] = PREMIUM_TIMES_QUERIES,
    *,
    per_query: int = 15,
    max_paragraphs_per_article: int = 4,
    session: requests.Session | None = None,
) -> Iterator[LabelledItem]:
    """Yield regional-stream records harvested from Premium Times (Nigeria, EN).

    Uses the public WordPress REST API (``/wp-json/wp/v2/posts``), which returns
    query-filtered posts as JSON with the body in ``content.rendered``. For each
    post we keep up to ``max_paragraphs_per_article`` scam-relevant paragraphs,
    emitting one record per paragraph. De-duplication across the whole corpus is
    handled downstream by ``02_normalise.py``.
    """
    sess = session or requests.Session()
    sess.headers.update(_HEADERS)

    for q in queries:
        try:
            resp = sess.get(
                _PT_API,
                params={"search": q, "per_page": per_query, "_fields": "link,date,content,title"},
                timeout=_TIMEOUT,
            )
        except requests.RequestException as exc:
            print(f"  [premium_times] query {q!r} failed: {type(exc).__name__}")
            continue
        if resp.status_code != 200:
            print(f"  [premium_times] query {q!r} -> HTTP {resp.status_code}")
            continue

        try:
            posts = resp.json()
        except ValueError:
            print(f"  [premium_times] query {q!r} -> non-JSON body, skipped")
            continue

        kept = 0
        for post in posts:
            link = post.get("link")
            body = (post.get("content") or {}).get("rendered", "")
            paras = [p for p in _clean_paragraphs(body) if _is_relevant(p)]
            for para in paras[:max_paragraphs_per_article]:
                yield LabelledItem(
                    id=stable_id(para),
                    text=para,
                    language="en",
                    source_stream=SourceStream.REGIONAL,
                    source_url=link,
                    original_label=f"premium_times_search:{q}",
                    category=ScamCategory.NOT_A_SCAM,  # placeholder; human relabels
                    label_source=LabelSource.AUTO,
                )
                kept += 1
        print(f"  [premium_times] {q!r}: {len(posts)} posts -> {kept} relevant paragraphs")
        time.sleep(_POLITE_DELAY)


# ---------------------------------------------------------------------------
# Institutional advisory probes (currently blocked — kept honest, not crashing)
# ---------------------------------------------------------------------------

def _probe_blocked_source(name: str, url: str) -> Iterator[LabelledItem]:
    """Attempt a fetch, report the outcome, yield nothing.

    Several official advisory sites sit behind Cloudflare or are unreachable.
    Rather than raise, we record why the source produced no data so the
    limitation is documented rather than silent.
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        print(f"  [{name}] {url} -> HTTP {resp.status_code} "
              f"({len(resp.content):,} bytes); no usable advisory feed, skipped")
    except requests.RequestException as exc:
        print(f"  [{name}] {url} -> unreachable ({type(exc).__name__}); skipped")
    return iter(())


def scrape_ngcert_advisories() -> Iterator[LabelledItem]:
    """Nigeria ngCERT advisories — blocked by Cloudflare anti-bot (HTTP 403)."""
    yield from _probe_blocked_source("ngcert", "https://cert.gov.ng/advisories/")


def scrape_antic_bulletins() -> Iterator[LabelledItem]:
    """Cameroon ANTIC bulletins (French) — host currently unreachable."""
    yield from _probe_blocked_source("antic", "https://www.antic.cm")


def scrape_efcc_alerts() -> Iterator[LabelledItem]:
    """Nigeria EFCC alerts — site returns an empty shell / news path 404s."""
    yield from _probe_blocked_source("efcc", "https://efccnigeria.org")


def scrape_west_african_news() -> Iterator[LabelledItem]:
    """West-African news stream. Premium Times is the working outlet today.

    Vanguard (403) and others are anti-bot-walled; add them here if/when a
    reliable access path (REST API or sitemap) is found.
    """
    yield from scrape_premium_times()


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def harvest_regional() -> list[LabelledItem]:
    """Run every regional source and return the combined record list.

    Blocked sources contribute nothing but log why. Cross-source and
    cross-corpus de-duplication happens later in ``02_normalise.py``.
    """
    items: list[LabelledItem] = []
    items.extend(scrape_ngcert_advisories())
    items.extend(scrape_antic_bulletins())
    items.extend(scrape_efcc_alerts())
    items.extend(scrape_west_african_news())
    return items
