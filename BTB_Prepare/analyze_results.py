"""analyze_results.py — Run Phase 5 analysis on saved classified_qa.csv"""
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "classified_qa.csv"))

print("=== Phase 5: Analysis ===")
print(f"Total Q&A pairs:  {len(df)}")
print(f"Interviews:       {df['interview'].nunique()}")
print(f"Mean confidence:  {df['ds_confidence'].mean():.3f}")

print("\nTopic distribution (all interviews):")
for label, count in df["ds_label"].value_counts().items():
    bar = "#" * count
    print(f"  {label:20s} {count:3d}  {bar}")

print("\nPer-interview breakdown:")
for interview in df["interview"].unique():
    sub = df[df["interview"] == interview]
    top = sub["ds_label"].value_counts().index[0]
    print(f"\n  -- {interview} ({len(sub)} Q&As, dominant: {top}) --")
    for label, count in sub["ds_label"].value_counts().items():
        print(f"     {label:20s} {count}")

low = df[df["ds_confidence"] < 0.65].sort_values("ds_confidence")
print()
if len(low):
    print(f"Flagged for review (conf < 0.65): {len(low)} pairs")
    for _, row in low.iterrows():
        print(f"  [{row['interview']} Q{row['qa_index']}] conf={row['ds_confidence']:.2f} -> {row['ds_label']}")
        print(f"    Q: {row['question'][:90]}...")
else:
    print("All classifications high confidence (>= 0.65)")

QA_FOLDERS = {
    "AzizBamak": "AzizBamak",
    "ElliotStokes": "ElliotStokes",
    "MichaelAdelemoni": "MichaelAdelemoni",
    "MutaharMehkri": "MutaharMehkri",
    "NandiniHarinath": "NandiniHarinath",
    "XavierEldridge": "XavierEldridge",
}

print("\nSaving per-interview CSVs...")
for interview, folder in QA_FOLDERS.items():
    if interview not in df["interview"].values:
        continue
    sub = df[df["interview"] == interview][
        ["qa_index", "question", "answer", "ds_label", "ds_confidence",
         "tfidf_label", "review_priority"]
    ]
    out = os.path.join(BASE_DIR, folder, "classified_topics.csv")
    sub.to_csv(out, index=False)
    print(f"  Saved: {out}")

print("\nDone.")
