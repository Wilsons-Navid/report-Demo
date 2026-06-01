"""Generate and execute the model-demonstration notebook.

Produces `ml/notebooks/model_demo.ipynb` with embedded outputs + plots, built
from the same `src/demo_model.py` used for training, so the notebook and the
served model agree. Run:

    python ml/notebooks/build_model_notebook.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

HERE = Path(__file__).resolve().parent
OUT = HERE / "model_demo.ipynb"

md = lambda s: nbf.v4.new_markdown_cell(s)
code = lambda s: nbf.v4.new_code_cell(s)

cells = [
    md("# Scam-Message Classifier — Initial Model\n"
       "Classical ML (TF-IDF + Logistic Regression / Random Forest) that classifies a short "
       "message as **advance-fee fraud**, **mobile-money fraud**, **phishing**, or **not-a-scam**.\n\n"
       "*Initial/preliminary model trained on source-provenance labels (Nazario, MOZ-Smishing, "
       "Mendeley smishing, UCI). The final evaluation uses the human inter-rater-verified corpus.*"),

    md("## 1 · Data engineering"),
    code("import sys, json\n"
         "from pathlib import Path\n"
         "import pandas as pd, numpy as np\n"
         "import matplotlib.pyplot as plt, seaborn as sns\n"
         "sys.path.insert(0, str(Path.cwd().parent))\n"
         "from src import demo_model as dm\n"
         "sns.set_theme(style='whitegrid')\n"
         "df = dm.load_df()\n"
         "print(f'{len(df):,} labelled messages')\n"
         "df.head(4)"),

    code("# Class distribution\n"
         "fig, ax = plt.subplots(1, 3, figsize=(15, 4))\n"
         "df['category'].value_counts().plot.bar(ax=ax[0], color='#2a9d8f', title='Class distribution')\n"
         "df['source'].value_counts().plot.bar(ax=ax[1], color='#264653', title='Source')\n"
         "df['language'].value_counts().plot.bar(ax=ax[2], color='#e76f51', title='Language (en / pt)')\n"
         "for a in ax: a.tick_params(axis='x', rotation=30)\n"
         "plt.tight_layout(); plt.show()"),

    code("# Message-length distribution by class\n"
         "df['len'] = df['text'].str.len()\n"
         "plt.figure(figsize=(9,4))\n"
         "sns.boxplot(data=df[df['len']<800], x='category', y='len', palette='Set2')\n"
         "plt.title('Message length (chars) by class'); plt.xticks(rotation=15); plt.show()\n"
         "df.groupby('category')['len'].median()"),

    md("**Provenance — which source feeds which class.** A category × source cross-tab. "
       "Shows the corpus design: the Portuguese MOZ set carries mobile-money, the email "
       "corpus carries phishing / advance-fee, UCI carries the benign negatives."),
    code("ct = pd.crosstab(df['category'], df['source'])\n"
         "plt.figure(figsize=(9,4.2))\n"
         "sns.heatmap(ct, annot=True, fmt='d', cmap='rocket_r', cbar_kws={'label':'messages'})\n"
         "plt.title('Class × source provenance'); plt.ylabel(''); plt.xlabel('')\n"
         "plt.xticks(rotation=20, ha='right'); plt.tight_layout(); plt.show()"),

    md("## 2 · Model architecture\n"
       "Classical ML pipeline — chosen over deep networks per the approved methodology "
       "(interpretability, robustness on a small corpus, cheap low-resource deployment). "
       "Two classifiers share one feature representation.\n\n"
       "**Feature extraction — TF-IDF.** Word 1–2 grams, `min_df=2`, sublinear term "
       "frequency (`1+log tf`), IDF weighting, unicode accent-stripping, vocabulary "
       "capped at 30,000 → each message becomes a sparse weighted n-gram vector.\n\n"
       "**Model A — Logistic Regression.** Linear model whose decision function is a "
       "**softmax** over the 4 classes (multinomial analogue of a sigmoid activation). "
       "*Optimisation:* L2-regularised cross-entropy minimised by the **lbfgs** solver "
       "(quasi-Newton), inverse-reg `C=4`, `max_iter=2000`, `class_weight='balanced'`.\n\n"
       "**Model B — Random Forest.** Ensemble of **500 CART trees**, **Gini** splits, "
       "trained by **bootstrap aggregation (bagging)** with random feature subsampling; "
       "prediction by majority vote. `class_weight='balanced'`.\n\n"
       "**Training protocol.** 70/15/15 **stratified** split, fixed seed (42); metrics "
       "reported on the held-out test split."),
    code("train, dev, test = dm.split(df)\n"
         "print(f'train {len(train)} / dev {len(dev)} / test {len(test)}')\n"
         "pipes = dm.build_pipelines()\n"
         "for name, p in pipes.items():\n"
         "    p.fit(train['text'], train['category'])\n"
         "print('fitted:', list(pipes))"),

    md("## 3 · Performance metrics (held-out test set)"),
    code("rows = []\n"
         "for name, p in pipes.items():\n"
         "    m = dm.evaluate(p, test['text'], test['category'])\n"
         "    rows.append({'model': name, 'accuracy': round(m['accuracy'],3), 'macro_F1': round(m['macro_f1'],3)})\n"
         "summary = pd.DataFrame(rows).set_index('model'); summary"),

    code("best_name = summary['macro_F1'].idxmax()\n"
         "best = pipes[best_name]\n"
         "print(f'Best model: {best_name}')\n"
         "print(dm.evaluate(best, test['text'], test['category'])['report'])"),

    code("# Confusion matrices\n"
         "from sklearn.metrics import confusion_matrix\n"
         "fig, ax = plt.subplots(1, 2, figsize=(13,5))\n"
         "for i,(name,p) in enumerate(pipes.items()):\n"
         "    cm = confusion_matrix(test['category'], p.predict(test['text']), labels=dm.CLASS_ORDER)\n"
         "    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax[i],\n"
         "                xticklabels=dm.CLASS_ORDER, yticklabels=dm.CLASS_ORDER)\n"
         "    ax[i].set_title(f'{name}'); ax[i].set_xlabel('predicted'); ax[i].set_ylabel('true')\n"
         "    ax[i].tick_params(axis='x', rotation=30)\n"
         "plt.tight_layout(); plt.show()"),

    md("## 4 · Per-class agreement — Logistic Regression vs Random Forest\n"
       "F1 per class for both models on the test set (higher = better)."),
    code("import pandas as pd\n"
         "rowsf = []\n"
         "for name, p in pipes.items():\n"
         "    pc = dm.evaluate(p, test['text'], test['category'])['per_class']\n"
         "    for c, m in pc.items():\n"
         "        rowsf.append({'class': c, 'model': name, 'F1': m['f1']})\n"
         "fdf = pd.DataFrame(rowsf)\n"
         "plt.figure(figsize=(9,4.2))\n"
         "sns.barplot(data=fdf, x='class', y='F1', hue='model', palette=['#2a9d8f','#e76f51'])\n"
         "plt.ylim(0,1.05); plt.title('Per-class F1 by model'); plt.xticks(rotation=15)\n"
         "plt.legend(title=''); plt.tight_layout(); plt.show()"),

    md("## 5 · What the model keys on — top terms per class\n"
       "Largest Logistic-Regression coefficients per class (the n-grams that most push a "
       "message toward each label)."),
    code("lr = pipes['tfidf_logreg']\n"
         "vec = lr.named_steps['tfidf']; clf = lr.named_steps['clf']\n"
         "feats = np.array(vec.get_feature_names_out())\n"
         "fig, ax = plt.subplots(2, 2, figsize=(13, 7))\n"
         "colors = {'phishing':'#ff5a4d','advance_fee_fraud':'#f4a72c',\n"
         "          'mobile_money_fraud':'#b98cff','not_a_scam':'#43d39a'}\n"
         "for a, c in zip(ax.ravel(), clf.classes_):\n"
         "    idx = np.argsort(clf.coef_[list(clf.classes_).index(c)])[-12:]\n"
         "    a.barh(feats[idx], clf.coef_[list(clf.classes_).index(c)][idx], color=colors.get(c,'#888'))\n"
         "    a.set_title(c, fontsize=11); a.tick_params(labelsize=9)\n"
         "plt.suptitle('Top TF-IDF terms per class (LogReg weights)', y=1.02)\n"
         "plt.tight_layout(); plt.show()"),

    md("## 6 · Live inference"),
    code("examples = [\n"
         "  'URGENT! Your mobile number won a 2000 prize GUARANTEED. Call 09061790121 to claim.',\n"
         "  'Caro cliente, a sua conta M-Pesa foi bloqueada. Envie o seu PIN para reactivar.',\n"
         "  'Dear customer, click here to verify your bank account or it will be suspended: http://bit.ly/x9',\n"
         "  'Hey, are we still meeting for lunch at 1pm tomorrow?',\n"
         "]\n"
         "proba = best.predict_proba(examples); classes = list(best.classes_)\n"
         "for t, pr in zip(examples, proba):\n"
         "    s = sorted(zip(classes, pr), key=lambda x:-x[1])[0]\n"
         "    print(f'{s[0]:18} ({s[1]:.2f})  <- {t[:60]}')"),

    md("## 7 · Deployment\n"
       "The fitted pipeline is saved to `ml/models/scam_classifier.joblib` and served via "
       "**FastAPI** with interactive **Swagger UI**:\n\n"
       "```bash\n"
       "python -m uvicorn ml.serve.app:app --reload --port 8000\n"
       "# open http://127.0.0.1:8000/docs  ->  POST /predict\n"
       "```"),
]

nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata = {"kernelspec": {"name": "python3", "display_name": "Python 3"},
               "language_info": {"name": "python"}}

print("Executing notebook (trains models inline)...")
ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
ep.preprocess(nb, {"metadata": {"path": str(HERE)}})
nbf.write(nb, OUT)
print(f"Wrote executed notebook -> {OUT}")
