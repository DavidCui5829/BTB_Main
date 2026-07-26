"""Tokenless 2-speaker diarization for the interview transcripts.

Reuses the accurate Groq word/segment timestamps (from transcribe_groq.py) and
adds "who spoke" labels without any gated model or HF token:

  1. load the source audio at 16 kHz
  2. compute a speaker embedding (Resemblyzer / ECAPA-style VoiceEncoder) for
     each Groq segment
  3. cluster the embeddings into 2 speakers
  4. label the cluster that asks the questions as the Interviewer

Outputs, next to each person's audio:
  <Name>.diarized.txt   readable [ts --> ts] Speaker: text
  <Name>.diarized.json  segments annotated with speaker + cluster
"""

import json
import os
import sys

import librosa
import numpy as np
from resemblyzer import VoiceEncoder
from sklearn.cluster import KMeans

SR = 16000
MIN_DUR = 0.6  # segments shorter than this are labelled by continuity, not embedded

TARGETS = {
    "AzizBamak": "AzizBamak/Interview with 10 year Project Manager at GTT Aziz Bamik - BeyondtheBlueprint (128k).mp3",
    "ElliotStokes": "ElliotStokes/Interview with Chemical Engineer and Director of Process Safety Management Elliot Wolf Stokes - BeyondtheBlueprint (128k).mp3",
    "MichaelAdelemoni": "MichaelAdelemoni/Interview with Google Software Engineer Michael Adelemoni - BeyondtheBlueprint (128k).mp3",
    "MutaharMehkri": "MutaharMehkri/Interview with Nasa Aerospace Engineer Mutahar Mehkri - BeyondtheBlueprint (128k).mp3",
    "NandiniHarinath": "NandiniHarinath/Interview with ISRO Aerospace Engineer_ Nandini Harinath..mp3",
    "XavierEldridge": "XavierEldridge/XavierEldridgeAudio.mp3",
}

_ENCODER = None


def encoder() -> VoiceEncoder:
    global _ENCODER
    if _ENCODER is None:
        _ENCODER = VoiceEncoder("cpu", verbose=False)
    return _ENCODER


def fmt_ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def embed_segments(wav: np.ndarray, segments: list) -> tuple:
    """Return (embeddings array, index list) for segments long enough to embed."""
    enc = encoder()
    embeds, idx = [], []
    for i, seg in enumerate(segments):
        if seg["end"] - seg["start"] < MIN_DUR:
            continue
        a = int(seg["start"] * SR)
        b = int(seg["end"] * SR)
        clip = wav[a:b]
        if len(clip) < int(MIN_DUR * SR):
            continue
        embeds.append(enc.embed_utterance(clip))
        idx.append(i)
    return np.asarray(embeds), idx


def label_speakers(segments: list, labels_by_idx: dict) -> dict:
    """Decide which cluster is the Interviewer (the one asking questions)."""
    stats = {0: {"q": 0, "n": 0, "dur": 0.0, "first": None},
             1: {"q": 0, "n": 0, "dur": 0.0, "first": None}}
    for i, seg in enumerate(segments):
        c = labels_by_idx.get(i)
        if c is None:
            continue
        s = stats[c]
        s["n"] += 1
        s["dur"] += seg["end"] - seg["start"]
        if "?" in seg["text"]:
            s["q"] += 1
        if s["first"] is None:
            s["first"] = i

    # Question ratio is the primary signal; the interviewer asks far more often.
    q_ratio = {c: (stats[c]["q"] / stats[c]["n"] if stats[c]["n"] else 0) for c in (0, 1)}
    if q_ratio[0] != q_ratio[1]:
        interviewer = 0 if q_ratio[0] > q_ratio[1] else 1
    else:
        # Fallback: the interviewer typically talks less overall.
        interviewer = 0 if stats[0]["dur"] < stats[1]["dur"] else 1
    return {interviewer: "Interviewer", 1 - interviewer: "Interviewee"}


def diarize(name: str, base: str) -> None:
    audio = os.path.join(base, TARGETS[name])
    out_dir = os.path.dirname(audio)
    tj = os.path.join(out_dir, f"{name}.json")
    if not os.path.exists(tj):
        print(f"[skip] no Groq transcript for {name} ({tj}); run transcribe_groq.py first")
        return

    with open(tj, encoding="utf-8") as f:
        transcript = json.load(f)
    segments = transcript.get("segments", [])
    if not segments:
        print(f"[skip] {name}: transcript has no segments")
        return

    print(f"[{name}] loading audio + embedding {len(segments)} segments...")
    wav, _ = librosa.load(audio, sr=SR, mono=True)
    embeds, idx = embed_segments(wav, segments)
    if len(embeds) < 2:
        print(f"[skip] {name}: not enough embeddable speech")
        return

    # Embeddings are L2-normalised, so KMeans behaves like spherical (cosine)
    # clustering and, unlike average-linkage, won't peel off a single outlier.
    clusters = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(embeds)
    labels_by_idx = {idx[k]: int(clusters[k]) for k in range(len(idx))}

    # Fill short/unembedded segments by continuity with the previous labelled one.
    last = None
    for i in range(len(segments)):
        if i in labels_by_idx:
            last = labels_by_idx[i]
        elif last is not None:
            labels_by_idx[i] = last

    naming = label_speakers(segments, labels_by_idx)

    txt_path = os.path.join(out_dir, f"{name}.diarized.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        prev = None
        for i, seg in enumerate(segments):
            spk = naming.get(labels_by_idx.get(i), "Unknown")
            text = seg["text"].strip()
            start, end = fmt_ts(seg["start"]), fmt_ts(seg["end"])
            if spk != prev:
                f.write(f"\n{spk}:\n")
                prev = spk
            f.write(f"  [{start} --> {end}] {text}\n")
            seg["speaker"] = spk
            seg["cluster"] = labels_by_idx.get(i)

    json_path = os.path.join(out_dir, f"{name}.diarized.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    # quick report
    counts = {}
    for seg in segments:
        counts[seg["speaker"]] = counts.get(seg["speaker"], 0) + 1
    print(f"    speakers: {counts}")
    print(f"    saved {txt_path}")
    print(f"    saved {json_path}")


def main() -> None:
    base = os.path.dirname(os.path.abspath(__file__))
    for name in (sys.argv[1:] or list(TARGETS)):
        if name not in TARGETS:
            print(f"[skip] unknown target: {name}")
            continue
        diarize(name, base)


if __name__ == "__main__":
    main()
