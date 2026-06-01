"""Initial (demo) scam-message classifier: TF-IDF + LogReg vs TF-IDF + RF.

Mirrors the approved classical-only scope (proposal §3.4): two pipelines on a
shared TF-IDF representation, compared on a held-out test split. Used by both
the model notebook and the training script; the fitted pipeline is saved for
the FastAPI serving app.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score,
                             precision_recall_fscore_support)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "labelled" / "demo_labeled.jsonl"
MODELS = ROOT / "models"

CLASS_ORDER = ["advance_fee_fraud", "mobile_money_fraud", "phishing", "not_a_scam"]
SEED = 42


def load_df(path: Path = DATA) -> pd.DataFrame:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return pd.DataFrame(rows)


def split(df: pd.DataFrame):
    """70/15/15 stratified by category, seed-fixed and reproducible."""
    train, temp = train_test_split(df, test_size=0.30, random_state=SEED,
                                   stratify=df["category"])
    dev, test = train_test_split(temp, test_size=0.50, random_state=SEED,
                                 stratify=temp["category"])
    return train, dev, test


def _vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=2,
                           sublinear_tf=True, strip_accents="unicode",
                           max_features=30000)


def build_pipelines() -> dict[str, Pipeline]:
    return {
        "tfidf_logreg": Pipeline([
            ("tfidf", _vectorizer()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced",
                                       C=4.0)),
        ]),
        "tfidf_rf": Pipeline([
            ("tfidf", _vectorizer()),
            ("clf", RandomForestClassifier(n_estimators=500, class_weight="balanced",
                                           n_jobs=-1, random_state=SEED)),
        ]),
    }


def evaluate(model: Pipeline, X, y) -> dict:
    pred = model.predict(X)
    p, r, f, _ = precision_recall_fscore_support(y, pred, labels=CLASS_ORDER,
                                                 average=None, zero_division=0)
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, average="macro", labels=CLASS_ORDER)),
        "per_class": {c: {"precision": float(p[i]), "recall": float(r[i]),
                          "f1": float(f[i])} for i, c in enumerate(CLASS_ORDER)},
        "confusion": confusion_matrix(y, pred, labels=CLASS_ORDER).tolist(),
        "report": classification_report(y, pred, labels=CLASS_ORDER, zero_division=0),
    }


def train_all(save: bool = True):
    df = load_df()
    train, dev, test = split(df)
    results = {}
    fitted = {}
    for name, pipe in build_pipelines().items():
        pipe.fit(train["text"], train["category"])
        results[name] = {
            "dev": evaluate(pipe, dev["text"], dev["category"]),
            "test": evaluate(pipe, test["text"], test["category"]),
        }
        fitted[name] = pipe

    if save:
        MODELS.mkdir(parents=True, exist_ok=True)
        best = max(results, key=lambda n: results[n]["test"]["macro_f1"])
        joblib.dump(fitted[best], MODELS / "scam_classifier.joblib")
        (MODELS / "metrics.json").write_text(json.dumps(results, indent=2))
        (MODELS / "model_card.json").write_text(json.dumps({
            "best_model": best,
            "classes": CLASS_ORDER,
            "n_train": len(train), "n_dev": len(dev), "n_test": len(test),
            "test_macro_f1": results[best]["test"]["macro_f1"],
            "test_accuracy": results[best]["test"]["accuracy"],
            "note": "INITIAL model on source-provenance labels; final eval uses "
                    "the human κ-verified corpus (Objective 3).",
        }, indent=2))
    return results, fitted, (train, dev, test)


if __name__ == "__main__":
    results, _fitted, (tr, dv, te) = train_all(save=True)
    print(f"split: train {len(tr)} / dev {len(dv)} / test {len(te)}\n")
    for name, res in results.items():
        t = res["test"]
        print(f"=== {name} ===  test accuracy={t['accuracy']:.3f}  macro-F1={t['macro_f1']:.3f}")
        print(t["report"])
