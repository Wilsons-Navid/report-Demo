# Project Walkthrough — Scam-Message Classifier (Initial Demo)

This document explains the full build behind the demonstration: the data, the model,
the deployment, how to run it, and a video walkthrough guide. The top-level `README.md`
is the short demo-focused version; this is the detailed account.

- **Live web app:** https://frontend-inky-xi-23.vercel.app
- **Live API (Swagger):** https://scam-classifier-api.onrender.com/docs
- **Repo:** https://github.com/Wilsons-Navid/report-Demo

---

## 1. What this is

A classical machine-learning system that reads a short message (SMS, email, chat) and
classifies it as one of four categories:

| Category | What it captures |
|---|---|
| `phishing` | Credential / link harvesting ("verify your account", malicious links) |
| `mobile_money_fraud` | Wallet / PIN / agent / OTP fraud (e.g. M-Pesa, MoMo) |
| `advance_fee_fraud` | Prize, lottery, 419, inheritance lures |
| `not_a_scam` | Benign / legitimate messages |

It is delivered two ways: a REST **API** (FastAPI, with Swagger UI) and a **web front-end**.

> **Scope note (honest framing).** This is the *initial* model. It is trained on
> **source-provenance labels** — i.e. each public dataset's own labels — to get a working
> baseline for the demonstration milestone. The *final* dissertation evaluation will use a
> **human, inter-rater-verified corpus** (Cohen's κ ≥ 0.7), which is a separate labelling
> effort still in progress. Three further categories — romance, identity-theft, and
> synthetic-media (deepfake) fraud — are **future work**: no public *message* datasets
> exist for them (deepfake data is audio/video, not text; romance-scam message corpora are
> behind anti-bot walls or restricted access).

---

## 2. Data

### 2.1 Sources

The corpus is assembled from public datasets, each contributing a class it covers well:

| Source | Records used | Contributes | Access |
|---|---|---|---|
| UCI SMS Spam Collection | 4,952 | benign negatives + prize/advance-fee SMS | direct download |
| Nazario phishing corpus | 2,280 emails | phishing + Nigerian 419 advance-fee | direct download |
| Mendeley SMS-phishing (Mishra & Soni) | 374 | smishing / phishing SMS | direct download |
| MOZ-Smishing (AfricaNLP 2025) | 538 | **mobile-money smishing** (Portuguese / Mozambican) | Hugging Face |
| Premium Times (regional news) | ~392 | regional context (mostly filtered to not_a_scam) | WordPress REST API |

The regional news stream was an experiment: scraping West-African news for scam reports.
It turned out news articles *report about* fraud rather than *being* scam messages, so it
contributed little usable signal — a documented finding. The institutional advisory sites
(ngCERT, ANTIC, EFCC) are blocked by anti-bot protection.

### 2.2 How the dataset was built

Each source is downloaded, parsed into a common schema, merged, schema-validated,
de-duplicated (exact + near-duplicate via Jaccard size-banding), length-filtered, and
labelled. The pooled corpus is **8,536** unique messages; the demo training set
(`ml/data/labelled/demo_labeled.jsonl`, **committed in this repo**) is **4,422** labelled rows:

| Class | Count |
|---|---|
| phishing | 2,401 |
| not_a_scam | 1,200 |
| mobile_money_fraud | 538 |
| advance_fee_fraud | 283 |

Languages: English (3,885) + Portuguese (537). The full corpus-construction pipeline
(scrapers, normaliser, and the κ-audit tooling for the final human-verified corpus) lives
in the separate research workspace; this demo repo ships only the assembled dataset.

---

## 3. Model

### 3.1 Architecture (`ml/src/demo_model.py`)

Classical ML — chosen over deep networks for interpretability, robustness on a small
corpus, and cheap low-resource deployment. Two classifiers share one representation:

- **Feature extraction — TF-IDF.** Word 1–2 grams, `min_df=2`, sublinear term frequency,
  IDF weighting, unicode accent-stripping, vocabulary capped at 30,000.
- **Model A — Logistic Regression.** Linear model; softmax decision function over the four
  classes. Optimised by the **lbfgs** solver minimising L2-regularised cross-entropy
  (`C=4`, `max_iter=2000`, `class_weight='balanced'`).
- **Model B — Random Forest.** 500 CART trees, Gini splits, bootstrap aggregation, majority
  vote (`class_weight='balanced'`).
- **Protocol.** 70/15/15 stratified split, fixed seed (42); metrics on the held-out test set.

### 3.2 Results (held-out test set, n = 664)

| Model | Accuracy | Macro-F1 |
|---|---|---|
| **TF-IDF + Logistic Regression** | **0.958** | **0.943** |
| TF-IDF + Random Forest | 0.950 | 0.928 |

Per-class F1 (Logistic Regression): mobile-money **0.99**, phishing **0.96**,
not-a-scam **0.96**, advance-fee **0.86**. Logistic Regression is the saved/served model.

The full analysis — distributions, a class×source provenance heatmap, confusion matrices,
per-class F1 comparison, and the top weighted terms per class — is in the executed notebook
`ml/notebooks/model_demo.ipynb`.

> **Metric caveat.** Because labels come from dataset provenance, the numbers are somewhat
> optimistic (the model partly learns "which corpus" a message resembles). The rigorous
> per-category figures will come from the human κ-verified corpus in the final evaluation.

---

## 4. Deployment

```
[ Browser ]  →  Vercel (static front-end)  →  fetch /predict  →  Render (FastAPI)  →  model
```

- **API — FastAPI (`ml/serve/app.py`)** on **Render** (free tier). `render.yaml` trains the
  model at build time from the committed dataset (so the runtime scikit-learn always matches
  the one that pickled it), then runs Uvicorn. Endpoints: `GET /health`, `POST /predict`,
  `POST /predict_batch`, Swagger at `/docs`. CORS is enabled so the browser front-end can
  call it cross-origin (`ALLOWED_ORIGINS`).
- **Front-end — static HTML/CSS/JS (`frontend/`)** on **Vercel**. Configurable API base
  (`API_BASE` in `app.js`, or `?api=<url>` at runtime). Shows the predicted category, a
  confidence figure, and a probability bar per class, with clickable example messages.

Free-tier note: the Render service sleeps after ~15 min idle, so the first request
cold-starts (~30–50s). Warm it before demoing.

---

## 5. Repository structure

```
ml/
├── notebooks/model_demo.ipynb     executed model notebook (EDA, architecture, metrics)
├── src/demo_model.py              TF-IDF + LogReg / RandomForest pipelines
├── serve/app.py                   FastAPI app (Swagger UI)
├── data/labelled/demo_labeled.jsonl   the 4,422-row labelled dataset
├── models/                        trained classifier + metrics.json
├── DEMONSTRATION.md               demo-focused readme
└── requirements.txt
frontend/                          static web UI (Vercel)
docs/
├── PROJECT_WALKTHROUGH.md         this file
├── PROJECT_WALKTHROUGH.docx       Word version
└── screens/                       interface screenshots
render.yaml                        Render blueprint for the API
```

---

## 6. Run it locally

```bash
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r ml/requirements.txt

python ml/src/demo_model.py                        # train (saves model + metrics)
python -m uvicorn ml.serve.app:app --port 8000     # API → http://127.0.0.1:8000/docs

cd frontend && python -m http.server 5500          # web UI → http://127.0.0.1:5500
```

---

## 7. Video walkthrough guide (5–10 min)

**Before recording:** open the live site once so the Render API is warm (no cold-start lag).

| Time | Segment | What to show / say |
|---|---|---|
| 0:00–0:30 | **Intro** | "Initial demo of a scam-message classifier — phishing, mobile-money fraud, advance-fee fraud, plus not-a-scam. Classical ML, deployed as an API and a web app." |
| 0:30–3:00 | **Notebook** (`model_demo.ipynb`) | §1 data — class / source / language charts + the class×source **provenance heatmap**. §2 **architecture** — read the TF-IDF → LogReg / RF + optimisation lines. §3 **metrics** — say "**95.8% accuracy, macro-F1 0.94**" and show the **confusion matrices**. §4 per-class F1 comparison. §5 top terms per class. |
| 3:00–5:00 | **Live web app** | Open the site. Click each example chip — phishing, the **Portuguese M-Pesa** one, prize/419, benign — and show the verdict + probability bars updating. Then paste your own message. |
| 5:00–5:45 | **API / Swagger** | Open `/docs`, expand **POST /predict**, "Try it out", run a message, show the JSON response (`predicted_category`, `confidence`, `scores`). |
| 5:45–6:00 | **Close** | One line on the stack (Vercel + Render) and that the final model will retrain on the human κ-verified corpus. |

Keep narration focused on the *functionality* (per the assignment): less research backstory,
more "here is the model, here are the numbers, here it is working live."

**After recording:** paste the video link into `README.md` and `ml/DEMONSTRATION.md`.

---

## 8. Limitations & future work

- **Initial labels are dataset-provenance, not human-adjudicated** — final evaluation uses
  the κ-verified corpus.
- **Three categories deferred** (romance, identity-theft, synthetic-media) — no public
  message data; candidate sources are anti-bot-walled or access-restricted.
- **Regional/multilingual coverage is thin** — Portuguese (mobile-money) is the main
  non-English slice; French / Pidgin coverage is future work.
- **Model is linear/bag-of-words** — deliberate for the baseline; transformer comparison is
  out of scope for this milestone.
