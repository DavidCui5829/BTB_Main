"""
classify.py — BTB Topic Classification Pipeline
Phase 1: Parse Q&A data
Phase 2: DeepSeek V4 Flash bootstrap labeling
Phase 3: Priority review queue
Phase 4: TF-IDF + LogReg baseline
Phase 5: Analysis & per-interview output
"""

import sys
import os
import re
import json
import requests
import pandas as pd
import numpy as np
from tqdm import tqdm

# Load secrets from BTB_Prepare/.env (gitignored). No-op if python-dotenv isn't
# installed or the file is missing, in which case real env vars are used.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

sys.stdout.reconfigure(encoding="utf-8")

# ── Config ───────────────────────────────────────────────────────────────────
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-flash"  # DeepSeek V4 Flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

QA_FILES = {
    "AzizBamak": r"AzizBamak\Interview with 10 year Project Manager at GTT Aziz Bamik - BeyondtheBlueprint (128k)_qa.txt",
    "ElliotStokes": r"ElliotStokes\Interview with Chemical Engineer and Director of Process Safety Management Elliot Wolf Stokes - BeyondtheBlueprint (128k)_qa.txt",
    "MichaelAdelemoni": r"MichaelAdelemoni\Interview with Google Software Engineer Michael Adelemoni - BeyondtheBlueprint (128k)_qa.txt",
    "MutaharMehkri": r"MutaharMehkri\Interview with Nasa Aerospace Engineer Mutahar Mehkri - BeyondtheBlueprint (128k)_qa.txt",
    "NandiniHarinath": r"NandiniHarinath\Interview with ISRO Aerospace Engineer_ Nandini Harinath._qa.txt",
    "XavierEldridge": r"XavierEldridge\transcription_qa.txt",
}

# ── Phase 1: Taxonomy ─────────────────────────────────────────────────────────
TAXONOMY = {
    "career_journey":    "How the person entered their field, education, early career steps, pivotal decisions, career path evolution",
    "daily_work":        "Typical workday, day-to-day responsibilities, workflow, regular job duties and routines",
    "technical_skills":  "Specific tools, technologies, equipment, software, certifications, technical knowledge required for the role",
    "projects":          "Specific projects worked on, concrete examples of work, case studies, notable accomplishments",
    "challenges":        "Obstacles faced, problem-solving, difficulties encountered in the role or industry",
    "advice":            "Career advice for students, recommendations on entering the field, guidance on skills to develop",
    "workplace_culture": "Team dynamics, work environment, interpersonal aspects, industry norms, mentorship, collaboration",
}
LABELS = list(TAXONOMY.keys())


# ── Phase 1: Parse ────────────────────────────────────────────────────────────
def parse_qa_file(filepath):
    """Split a _qa.txt file into [{question, answer}] pairs."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n(?=Q: |A: )", content.strip())
    pairs = []
    current_q = None

    for block in blocks:
        block = block.strip()
        if block.startswith("Q: "):
            if current_q is not None:
                pairs.append({"question": current_q, "answer": ""})
            current_q = block[3:].strip()
        elif block.startswith("A: ") and current_q is not None:
            pairs.append({"question": current_q, "answer": block[3:].strip()})
            current_q = None

    if current_q is not None:
        pairs.append({"question": current_q, "answer": ""})

    return pairs


def load_all_qa():
    """Load every _qa.txt file into a single DataFrame."""
    rows = []
    for name, rel_path in QA_FILES.items():
        full_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(full_path):
            print(f"  SKIP (file not found): {full_path}")
            continue
        pairs = parse_qa_file(full_path)
        for i, p in enumerate(pairs):
            rows.append({
                "interview":  name,
                "qa_index":   i + 1,
                "question":   p["question"],
                "answer":     p["answer"],
                # Combined text sent to DeepSeek and TF-IDF
                "full_text":  f"Q: {p['question']}\nA: {p['answer']}",
            })
        print(f"  {name}: {len(pairs)} Q&A pairs")
    return pd.DataFrame(rows)


# ── Phase 2: DeepSeek Classification ─────────────────────────────────────────
_SYSTEM = (
    "You are a topic classifier for career-interview podcast content.\n"
    "Given a question and its answer from an interview, classify the pair into exactly ONE category.\n\n"
    "Categories:\n{categories}\n\n"
    "Rules:\n"
    '- Respond ONLY with a JSON object: {{"label": "<category>", "confidence": <0.0-1.0>}}\n'
    "- confidence = how clearly the pair fits that category\n"
    "- No explanation, no extra text, only the JSON"
)


def deepseek_classify(text, taxonomy):
    """Return (label, confidence) for one Q&A pair."""
    categories = "\n".join(f"- {k}: {v}" for k, v in taxonomy.items())
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "temperature": 0,
        "max_tokens": 60,
        "messages": [
            {"role": "system", "content": _SYSTEM.format(categories=categories)},
            {"role": "user", "content": text[:2500]},
        ],
    }
    try:
        resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        label = str(parsed.get("label", "career_journey")).lower().replace(" ", "_")
        if label not in taxonomy:
            label = min(taxonomy, key=lambda k: abs(len(k) - len(label)))
        return label, float(parsed.get("confidence", 0.5))
    except Exception as e:
        print(f"    [warn] {e}")
        return "career_journey", 0.0


# Phase 2.2: second-pass disagreement detection
_SYSTEM2 = (
    "Classify this career interview excerpt into ONE topic.\n"
    "Topics: {label_list}\n"
    "Reply with only the topic name, nothing else."
)


def deepseek_classify_v2(text, labels):
    """Simple second-pass classification (different prompt framing)."""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "temperature": 0,
        "max_tokens": 20,
        "messages": [
            {
                "role": "system",
                "content": _SYSTEM2.format(label_list=", ".join(labels)),
            },
            {"role": "user", "content": text[:2500]},
        ],
    }
    try:
        resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip().lower()
        return next((l for l in labels if l in raw), labels[0])
    except Exception:
        return labels[0]


def run_classification(df, taxonomy):
    """Phase 2.1 — bulk classify; Phase 2.2 — disagreement pass."""
    labels, confs = [], []
    print("  Pass 1 (JSON + confidence)...")
    for _, row in tqdm(df.iterrows(), total=len(df), desc="  DeepSeek"):
        l, c = deepseek_classify(row["full_text"], taxonomy)
        labels.append(l)
        confs.append(c)
    df["ds_label"] = labels
    df["ds_confidence"] = confs

    print("  Pass 2 (disagreement detection — random sample)...")
    sample_idx = df.sample(min(30, len(df)), random_state=42).index
    v2_labels = []
    for idx in tqdm(sample_idx, desc="  Pass 2"):
        v2_labels.append(deepseek_classify_v2(df.loc[idx, "full_text"], LABELS))
    df.loc[sample_idx, "ds_label_v2"] = v2_labels

    return df


# ── Phase 3: Priority review queue ────────────────────────────────────────────
def build_review_queue(df):
    def priority(row):
        score = 0
        if row["ds_confidence"] < 0.4:
            score += 3
        elif row["ds_confidence"] < 0.6:
            score += 2
        elif row["ds_confidence"] < 0.8:
            score += 1
        if pd.notna(row.get("ds_label_v2")) and row["ds_label"] != row.get("ds_label_v2"):
            score += 2
        return score

    df["review_priority"] = df.apply(priority, axis=1)
    queue = df.sort_values("review_priority", ascending=False)
    queue[["interview", "qa_index", "question", "answer", "ds_label",
           "ds_confidence", "review_priority"]].to_csv(
        os.path.join(BASE_DIR, "review_queue.csv"), index=False
    )
    print(f"  Priority 3+  (review first): {(df['review_priority'] >= 3).sum()}")
    print(f"  Priority 1-2 (check these):  {((df['review_priority'] >= 1) & (df['review_priority'] < 3)).sum()}")
    print(f"  Priority 0   (likely ok):    {(df['review_priority'] == 0).sum()}")
    return df


# ── Phase 4: TF-IDF + LogReg baseline ────────────────────────────────────────
def tfidf_baseline(df):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import classification_report

    X_texts = df["full_text"].tolist()
    y = df["ds_label"].tolist()

    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), sublinear_tf=True)
    X = tfidf.fit_transform(X_texts)

    lr = LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced")

    counts = pd.Series(y).value_counts()
    min_count = counts.min()
    n_folds = min(5, int(min_count))

    if n_folds >= 2:
        cv_scores = cross_val_score(lr, X, y, cv=n_folds, scoring="f1_macro")
        print(f"  {n_folds}-fold CV macro F1: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    else:
        print("  (too few samples per class for cross-validation)")

    lr.fit(X, y)
    df["tfidf_label"] = lr.predict(X)

    agree = (df["ds_label"] == df["tfidf_label"]).sum()
    print(f"  DeepSeek vs TF-IDF agreement: {agree}/{len(df)} ({100*agree/len(df):.1f}%)")

    return df, tfidf, lr


# ── Phase 5: Analysis ─────────────────────────────────────────────────────────
def analyze(df):
    print(f"\n  Total Q&A pairs:  {len(df)}")
    print(f"  Interviews:       {df['interview'].nunique()}")
    print(f"  Mean confidence:  {df['ds_confidence'].mean():.3f}")

    print("\n  Topic distribution (all interviews combined):")
    for label, count in df["ds_label"].value_counts().items():
        bar = "#" * count
        print(f"    {label:20s} {count:3d}  {bar}")

    print("\n  Per-interview breakdown:")
    for interview in df["interview"].unique():
        sub = df[df["interview"] == interview]
        top = sub["ds_label"].value_counts().index[0]
        print(f"\n    -- {interview} ({len(sub)} Q&As, dominant topic: {top}) --")
        for label, count in sub["ds_label"].value_counts().items():
            bar = "-" * count
            print(f"      {label:20s} {count}  {bar}")

    low = df[df["ds_confidence"] < 0.65].sort_values("ds_confidence")
    if len(low):
        print(f"\n  Flagged for review (confidence < 0.65) - {len(low)} pairs:")
        for _, row in low.iterrows():
            print(f"    [{row['interview']} Q{row['qa_index']}] "
                  f"conf={row['ds_confidence']:.2f} → {row['ds_label']}")
            print(f"      Q: {row['question'][:90]}...")
    else:
        print("\n  All classifications are high confidence (≥ 0.65).")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  BTB Topic Classification Pipeline")
    print("=" * 60)

    # Phase 1 — load
    print("\nPhase 1: Loading Q&A data")
    df = load_all_qa()
    print(f"  Total: {len(df)} Q&A pairs across {df['interview'].nunique()} interviews\n")

    with open(os.path.join(BASE_DIR, "taxonomy.json"), "w") as f:
        json.dump(TAXONOMY, f, indent=2)
    print("  Saved: taxonomy.json\n")

    # Phase 2 — classify
    print("Phase 2: DeepSeek classification")
    df = run_classification(df, TAXONOMY)
    print(f"\n  Label distribution:\n{df['ds_label'].value_counts().to_string()}")

    # Phase 3 — review queue
    print("\nPhase 3: Priority review queue")
    df = build_review_queue(df)
    print("  Saved: review_queue.csv")

    # Phase 4 — TF-IDF baseline
    print("\nPhase 4: TF-IDF + LogReg baseline")
    df, tfidf, lr = tfidf_baseline(df)

    # Save master CSV (before analysis so data is never lost)
    master_out = os.path.join(BASE_DIR, "classified_qa.csv")
    df.to_csv(master_out, index=False)
    print(f"\n  Saved: classified_qa.csv")

    # Save per-interview CSVs
    for interview, rel_path in QA_FILES.items():
        if interview not in df["interview"].values:
            continue
        sub = df[df["interview"] == interview][
            ["qa_index", "question", "answer", "ds_label", "ds_confidence",
             "tfidf_label", "review_priority"]
        ].copy()
        folder = os.path.join(BASE_DIR, os.path.dirname(rel_path))
        out = os.path.join(folder, "classified_topics.csv")
        sub.to_csv(out, index=False)
        print(f"  Saved: {os.path.relpath(out, BASE_DIR)}")

    # Phase 5 — analysis
    print("\nPhase 5: Analysis")
    analyze(df)

    print("\nDone.")
