"""
cluster_viz.py -- BTB Q&A clustering visualization.

Pipeline:
  TF-IDF (3k features, bigrams)
    -> PCA 50D  (noise reduction + speedup)
    -> Agglomerative Hierarchical Clustering / Ward linkage  (on PCA-50 space)
    -> t-SNE 2D  (visual layout only — does NOT drive clustering)

Why Agglomerative over K-Means:
  - Ward linkage minimises within-cluster variance bottom-up, so it finds
    natural groupings instead of forcing spherical equal-size blobs
  - Deterministic, no eps sensitivity, works well with ~70 samples
  - t-SNE is used for display; clustering happens in the richer 50-D space
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(BASE_DIR, "classified_qa.csv"))
print(f"Loaded {len(df)} Q&A pairs | {df['interview'].nunique()} interviews")

# ── TF-IDF ───────────────────────────────────────────────────────────────────
tfidf = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), sublinear_tf=True)
X = tfidf.fit_transform(df["full_text"])
print(f"TF-IDF: {X.shape}")

# ── PCA 50D ───────────────────────────────────────────────────────────────────
print("PCA 50D ...")
pca50 = PCA(n_components=min(50, X.shape[1] - 1), random_state=42)
X50 = pca50.fit_transform(X.toarray())

# ── Agglomerative Hierarchical Clustering (Ward, k=7) ────────────────────────
print("Agglomerative clustering (Ward, k=7) ...")
agg = AgglomerativeClustering(n_clusters=7, metric="euclidean", linkage="ward")
df["agg_cluster"] = agg.fit_predict(X50)
print(f"  Cluster sizes: { {c: (df['agg_cluster']==c).sum() for c in range(7)} }")

# ── t-SNE 2D: sweep perplexity × iterations, keep best silhouette ─────────────
# Silhouette score on 2D coords vs agglomerative labels measures visual separation.
# Higher = clusters are more spread apart relative to their internal spread.
print("t-SNE sweep (perplexity x iterations) ...")
agg_labels = df["agg_cluster"].values
best_coords, best_score, best_params = None, -1, {}

for perp in [5, 8, 12, 20, 30]:
    for iters in [2000, 5000, 10000]:
        ts = TSNE(n_components=2, perplexity=perp, learning_rate="auto",
                  init="pca", random_state=42, max_iter=iters)
        c = ts.fit_transform(X50)
        score = silhouette_score(c, agg_labels)
        print(f"  perplexity={perp:2d}  iters={iters:5d}  silhouette={score:.4f}")
        if score > best_score:
            best_score, best_coords, best_params = score, c, {"perplexity": perp, "iters": iters}

print(f"\n  Best: perplexity={best_params['perplexity']}  iters={best_params['iters']}  silhouette={best_score:.4f}")
coords = best_coords
df["tx"] = coords[:, 0]
df["ty"] = coords[:, 1]

# ── Palettes ──────────────────────────────────────────────────────────────────
TOPIC_COLORS = {
    "career_journey":    "#e74c3c",
    "daily_work":        "#3498db",
    "technical_skills":  "#2ecc71",
    "projects":          "#f39c12",
    "challenges":        "#9b59b6",
    "advice":            "#1abc9c",
    "workplace_culture": "#e67e22",
}
TOPIC_SHORT = {
    "career_journey":    "CJ",
    "daily_work":        "DW",
    "technical_skills":  "TS",
    "projects":          "PR",
    "challenges":        "CH",
    "advice":            "AD",
    "workplace_culture": "WC",
}
INTERVIEW_MARKERS = dict(zip(
    df["interview"].unique(),
    ["o", "s", "^", "D", "v", "P"]
))

CLUSTER_PALETTE = [
    "#f72585", "#7209b7", "#3a0ca3", "#4361ee",
    "#4cc9f0", "#06d6a0", "#ffd166",
]

# ── Figure ────────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 9))
fig.patch.set_facecolor("#0f1117")
for ax in (ax1, ax2):
    ax.set_facecolor("#1a1d27")
    ax.tick_params(colors="#999999")
    ax.xaxis.label.set_color("#999999")
    ax.yaxis.label.set_color("#999999")
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a2a3a")

# ── Left: Agglomerative clusters ─────────────────────────────────────────────
for cid in range(7):
    sub = df[df["agg_cluster"] == cid]
    dominant = sub["ds_label"].value_counts().index[0]
    purity = sub["ds_label"].value_counts().iloc[0] / len(sub) * 100

    ax1.scatter(sub["tx"], sub["ty"],
                color=CLUSTER_PALETTE[cid], s=95, alpha=0.88,
                edgecolors="white", linewidths=0.45,
                label=f"C{cid}  {dominant.replace('_',' ')}  ({len(sub)}, {purity:.0f}% pure)")

    # Soft ellipse around cluster
    if len(sub) >= 3:
        cx, cy = sub["tx"].mean(), sub["ty"].mean()
        sx, sy = sub["tx"].std(), sub["ty"].std()
        ax1.add_patch(Ellipse(
            (cx, cy),
            width=max(sx, 2) * 3.5, height=max(sy, 2) * 3.5,
            edgecolor=CLUSTER_PALETTE[cid], facecolor=CLUSTER_PALETTE[cid],
            alpha=0.10, linewidth=1.5, linestyle="--"
        ))
        ax1.text(cx, cy, f"C{cid}\n{TOPIC_SHORT[dominant]}",
                 color="white", fontsize=7.5, ha="center", va="center",
                 fontweight="bold", alpha=0.85)

# Short topic codes on every point
for _, row in df.iterrows():
    ax1.annotate(TOPIC_SHORT[row["ds_label"]],
                 (row["tx"], row["ty"]),
                 fontsize=5, color="white", alpha=0.40,
                 ha="center", va="bottom",
                 xytext=(0, 5), textcoords="offset points")

ax1.legend(loc="upper left", fontsize=7.5, ncol=1,
           facecolor="#1a1d27", edgecolor="#444455", labelcolor="white",
           title="Agglomerative cluster  (dominant topic, n, purity)", title_fontsize=7.5)

ax1.set_title(
    "Agglomerative Hierarchical Clustering  (Ward linkage, k=7)\n"
    "Clustered in PCA-50 space  |  Displayed via t-SNE",
    color="white", fontsize=12, fontweight="bold", pad=12)
ax1.set_xlabel("t-SNE dim 1")
ax1.set_ylabel("t-SNE dim 2")

# ── Right: DeepSeek topic labels ─────────────────────────────────────────────
for interview in df["interview"].unique():
    for label, color in TOPIC_COLORS.items():
        sub = df[(df["interview"] == interview) & (df["ds_label"] == label)]
        if sub.empty:
            continue
        ax2.scatter(sub["tx"], sub["ty"],
                    c=color, marker=INTERVIEW_MARKERS[interview],
                    s=90, alpha=0.88,
                    edgecolors="white", linewidths=0.45)

for _, row in df.iterrows():
    ax2.annotate(TOPIC_SHORT[row["ds_label"]],
                 (row["tx"], row["ty"]),
                 fontsize=5, color="white", alpha=0.40,
                 ha="center", va="bottom",
                 xytext=(0, 5), textcoords="offset points")

topic_patches = [mpatches.Patch(color=c, label=l.replace("_", " ").title())
                 for l, c in TOPIC_COLORS.items()]
iv_handles = [plt.scatter([], [], c="#aaaaaa",
                          marker=INTERVIEW_MARKERS[iv], s=70, label=iv)
              for iv in df["interview"].unique()]
ax2.legend(handles=topic_patches + iv_handles,
           loc="upper left", fontsize=7.5, ncol=1,
           facecolor="#1a1d27", edgecolor="#444455", labelcolor="white",
           title="DeepSeek Topic  |  Interview", title_fontsize=7.5)

ax2.set_title(
    "DeepSeek Topic Labels  (ground truth)\n"
    "Same t-SNE layout — compare to Ward clusters on left",
    color="white", fontsize=12, fontweight="bold", pad=12)
ax2.set_xlabel("t-SNE dim 1")
ax2.set_ylabel("t-SNE dim 2")

# ── Footer ────────────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.01,
    f"72 Q&A pairs  |  6 interviews  |  TF-IDF 3k bigrams  ->  PCA 50D  ->  Agglomerative Ward k=7  |  "
    f"t-SNE best: perplexity={best_params['perplexity']}  iters={best_params['iters']}  silhouette={best_score:.3f}",
    ha="center", color="#555566", fontsize=8.5,
)

plt.tight_layout(rect=[0, 0.03, 1, 1])
out = os.path.join(BASE_DIR, "cluster_chart.png")
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: cluster_chart.png")

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\nAgglomerative cluster summary (Ward linkage, k=7):")
print(f"  {'Cluster':>9}  {'n':>3}  {'Dominant topic':25}  {'Purity':>7}  Interviews")
for cid in range(7):
    sub = df[df["agg_cluster"] == cid]
    dominant = sub["ds_label"].value_counts().index[0]
    dominant_n = sub["ds_label"].value_counts().iloc[0]
    purity = dominant_n / len(sub) * 100
    ivs = ", ".join(sub["interview"].unique())
    print(f"  C{cid}        {len(sub):>3}  {dominant:25}  {purity:>6.0f}%  {ivs}")

overall_purity = sum(
    df[df["agg_cluster"] == c]["ds_label"].value_counts().iloc[0]
    for c in range(7)
) / len(df) * 100
print(f"\n  Overall purity (dominant topic per cluster): {overall_purity:.1f}%")
