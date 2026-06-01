"""FastAPI serving app for the initial scam-message classifier.

Deployment MVP for the software-demonstration milestone (ML track,
"API UI - Swagger UI" option). Loads the fitted TF-IDF pipeline saved by
`src/demo_model.py` and exposes a prediction endpoint with interactive
Swagger docs at /docs.

Run:
    python -m uvicorn ml.serve.app:app --reload --port 8000
    # then open http://127.0.0.1:8000/docs

The model classifies a message into one of four classes:
    advance_fee_fraud | mobile_money_fraud | phishing | not_a_scam
"""

from __future__ import annotations

import json
from pathlib import Path

import os

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
MODEL_PATH = MODELS / "scam_classifier.joblib"
CARD_PATH = MODELS / "model_card.json"

app = FastAPI(
    title="Scam Message Classifier — Initial Model",
    description=(
        "Classical ML (TF-IDF + Logistic Regression) classifier for scam "
        "messages across phishing, mobile-money fraud, and advance-fee fraud, "
        "plus a not_a_scam residual. Initial/preliminary model trained on "
        "source-provenance labels; final evaluation uses the human "
        "inter-rater-verified corpus."
    ),
    version="0.1.0",
)

# CORS — allow the static front-end (Vercel) to call this API from the browser.
# Set ALLOWED_ORIGINS env (comma-separated) in production; defaults to "*" for the demo.
_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins],
    allow_methods=["*"],
    allow_headers=["*"],
)

_model = None
_card: dict = {}


def get_model():
    global _model, _card
    if _model is None:
        if not MODEL_PATH.exists():
            raise HTTPException(503, "Model not trained yet. Run python ml/src/demo_model.py")
        _model = joblib.load(MODEL_PATH)
        if CARD_PATH.exists():
            _card = json.loads(CARD_PATH.read_text())
    return _model


class Message(BaseModel):
    text: str = Field(..., min_length=1, examples=[
        "URGENT! Your mobile number won a 2000 prize GUARANTEED. Call 09061790121 to claim."])


class Prediction(BaseModel):
    text: str
    predicted_category: str
    confidence: float
    scores: dict[str, float]


@app.get("/", summary="Service info")
def root():
    return {
        "service": "scam-message-classifier",
        "status": "ok",
        "model": _card.get("best_model", "tfidf_logreg"),
        "classes": _card.get("classes", []),
        "docs": "/docs",
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "healthy", "model_loaded": MODEL_PATH.exists()}


@app.post("/predict", response_model=Prediction, summary="Classify a single message")
def predict(msg: Message):
    model = get_model()
    proba = model.predict_proba([msg.text])[0]
    classes = list(model.classes_)
    scores = {c: round(float(p), 4) for c, p in zip(classes, proba)}
    top = max(scores, key=scores.get)
    return Prediction(text=msg.text, predicted_category=top,
                      confidence=scores[top], scores=scores)


@app.post("/predict_batch", summary="Classify many messages")
def predict_batch(messages: list[Message]):
    model = get_model()
    texts = [m.text for m in messages]
    probas = model.predict_proba(texts)
    classes = list(model.classes_)
    out = []
    for text, proba in zip(texts, probas):
        scores = {c: round(float(p), 4) for c, p in zip(classes, proba)}
        top = max(scores, key=scores.get)
        out.append({"text": text, "predicted_category": top,
                    "confidence": scores[top], "scores": scores})
    return out
