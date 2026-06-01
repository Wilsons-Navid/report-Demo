# `ml/` — Capstone corpus + classical ML evaluation

**Status:** Active. Migrated from `ml_potential/` on 2026-05-28 after Thadee approved the proposal. This directory is the working track for Objectives 1 and 3.

## Scope (approved 2026-05-28)

- Classical-only ML evaluation: TF-IDF + Logistic Regression vs TF-IDF + Random Forest (500 estimators)
- Six-category scam taxonomy + `not_a_scam` residual
- Two data streams: public (Nazario / UCI SMS Spam / Kaggle / etc.) and regional (ngCERT / ANTIC / EFCC / West African news)
- No live pilot; no LLM comparison (both retained as future work)

## Binding deadlines (from proposal §1.3.1)

| Objective | Deliverable | Deadline |
|---|---|---|
| **1** | Labelled corpus ≥500 items, Cohen's κ ≥ 0.7 on 100-item audit | **12 Jun 2026** |
| **2** | Working Android build (separate track in `mobile/`) | 26 Jun 2026 |
| **3** | LR vs RF comparison table with per-category metrics | 10 Jul 2026 |

## The six-category taxonomy (locked)

Defined in `src/taxonomy.py`:

1. `advance_fee_fraud`
2. `mobile_money_fraud`
3. `phishing`
4. `romance_scam`
5. `identity_theft`
6. `synthetic_media_fraud`
7. `not_a_scam` (residual, for training-time false positives)

## Layout

```
ml/
├── README.md                          ← this file
├── requirements.txt                   ← Python deps (pydantic, pandas, scikit-learn, requests)
├── src/
│   ├── __init__.py
│   ├── taxonomy.py                    ← six-category enum + descriptions
│   ├── schema.py                      ← Pydantic LabelledItem model + JSONL I/O
│   ├── loaders.py                     ← UCI SMS Spam, Nazario, Kaggle CSV loaders
│   ├── scrapers.py                    ← regional advisory scrapers (ngCERT / ANTIC / EFCC / news)
│   └── labelling.py                   ← audit sampling + Cohen's κ
├── scripts/
│   ├── 01_download_public.py          ← fetch public datasets into data/raw/
│   ├── 02_normalise.py                ← raw → JSONL, with quality phase (length filter, near-dup)
│   ├── 03_label_helper.py             ← interactive CLI for rater 1
│   ├── 03c_batch_autolabel.py        ← non-interactive AUTO-suggest pass (bootstrap, not human labels)
│   ├── 04_create_audit_sample.py      ← stratified 100-item sample for rater 2 (blinded)
│   ├── 05_compute_kappa.py            ← Cohen's κ on the audit sample
│   ├── 06_split.py                    ← 70/15/15 stratified train/dev/test split
│   └── 07_scrape_regional.py          ← harvest the regional stream into data/raw/regional/
├── data/
│   ├── raw/                           ← unmodified downloaded datasets (gitignored)
│   ├── labelled/                      ← JSONL corpus (gitignored except corpus_v*.jsonl)
│   └── audits/                        ← second-rater audit samples for κ
└── notebooks/                         ← ad-hoc EDA (gitignored)
```

## Regional stream reachability (probed 2026-06-01)

Only one of the four regional sources is currently scrapable:

| Source | Status | Notes |
|---|---|---|
| Premium Times (news, EN) | **works** | WordPress REST API `/wp-json/wp/v2/posts?search=…`; 393 unique scam-relevant paragraphs harvested |
| ngCERT (`cert.gov.ng`) | blocked | Cloudflare anti-bot, HTTP 403 |
| ANTIC (`antic.cm`, FR) | blocked | host unreachable (connect timeout) |
| EFCC (`efccnigeria.org`) | blocked | empty shell / news path 404 |

The blocked sources are kept as honest, non-crashing probes in `src/scrapers.py`
that log why they yielded nothing — the unavailability of official advisories is
itself a data-collection limitation to report. French/Pidgin coverage remains a
gap the public + Premium-Times streams do not fill.

## End-to-end pipeline

```bash
# 1. Fetch public datasets (UCI SMS Spam auto-fetches; Nazario + Kaggle are manual)
python ml/scripts/01_download_public.py

# 1b. Harvest the regional stream (Premium Times; gov sites are blocked, logged)
python ml/scripts/07_scrape_regional.py

# 2. Normalise + quality phase (schema validate, deduplicate, length-filter, write JSONL)
#    Folds in both the public datasets and data/raw/regional/regional_news.jsonl
python ml/scripts/02_normalise.py

# 3a. (optional bootstrap) batch AUTO-suggest pass to make the human pass confirm-or-correct
python ml/scripts/03c_batch_autolabel.py

# 3. Label rater-1 pass — interactive, resume-safe. 03b is the AI-assisted variant.
python ml/scripts/03b_assisted_label.py    # (or 03_label_helper.py for pure-manual)

# 4. Once ≥500 items are labelled, generate a stratified 100-item audit sample for rater 2
python ml/scripts/04_create_audit_sample.py

# 5. After rater 2 labels the audit sample, compute Cohen's κ
python ml/scripts/05_compute_kappa.py

# 6. If κ ≥ 0.7, lock the corpus and produce the stratified 70/15/15 split
python ml/scripts/06_split.py
```

## Schema (one record per JSONL line)

| Field | Type | Notes |
|---|---|---|
| `id` | str | Stable 12-char SHA1 hash of `text` |
| `text` | str | Free-text incident description |
| `language` | str | ISO 639-1; `pcm` for Nigerian Pidgin |
| `source_stream` | enum | `public` / `regional` |
| `source_url` | str (optional) | Provenance link |
| `original_label` | str (optional) | Source dataset's own label |
| `category` | enum | One of the seven taxonomy labels |
| `label_source` | enum | `rater1` / `rater2` / `adjudicated` / `auto` |
| `labelled_at` | datetime (UTC) | When the label was applied |

## Quality phase rules (per proposal §3.4.2)

Applied in `02_normalise.py` before any training:

1. **Schema validation** — Pydantic rejects records missing required fields or with unknown language tags.
2. **Deduplication** — exact-text by `id` (SHA1 of text).
3. **Near-duplicate detection** — character 5-gram fingerprint with Jaccard ≥ 0.85 → collapse to first occurrence.
4. **Length filtering** — drop records with `len(text) < 20` or `len(text) > 2000`.

## Audit + κ workflow

- `04_create_audit_sample.py` writes `data/audits/audit_sample_blinded.jsonl` — items with category stripped, ready for rater 2.
- Rater 2 saves their labels as `data/audits/rater2.jsonl`.
- `05_compute_kappa.py` reads both rater files, computes κ on the shared item-id intersection, prints the value.
- The proposal threshold is **κ ≥ 0.7**.
