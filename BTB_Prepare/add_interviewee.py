#!/usr/bin/env python
"""add_interviewee.py — add one interviewee to BTB end to end (AI + website).

Point it at a BTB_Prepare/<ragId>/ folder that contains the interview audio and
give it the basic facts. It then, in order (every stage is idempotent — a re-run
skips work that's already done unless you pass --force):

  1. transcribes the audio            (Groq Whisper large-v3)
  2. splits it into Q&A               (DeepSeek)
  3. labels each pair by topic and appends to classified_qa.csv
  4. rebuilds the AI vector store     (BTB_AI/app/ingest.py)
  5. writes the website transcript    (BTB_Website/src/data/transcripts/<id>.json)
  6. drafts the catalog copy (bio / highlights / quote / questions) and writes the
     BTB_Website/src/data/interviews.json entry

It does NOT deploy — review the drafted copy first, then run deploy/deploy_*.sh
and rebuild the vector store on the server (see the printed reminder).

Usage:
  python add_interviewee.py --ragId NancyLi \\
      --name "Nancy Li" --role "Integrity Tech Services Engineer" \\
      --org "Phillips 66" --field "Pipeline Integrity" \\
      --video "https://youtu.be/XXXX" [--episode 7] [--force]

Keys come from BTB_Prepare/.env (GROQ_API_KEY, DEEPSEEK_API_KEY).
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import urllib.request

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Reuse the proven per-stage logic. These imports only load .env (the heavy
# pipelines are guarded by __main__), so importing is free of side effects.
import transcribe_groq as tg          # noqa: E402
import differentiate as diffmod        # noqa: E402
import classify as clf                 # noqa: E402

WEB = os.path.normpath(os.path.join(HERE, "..", "BTB_Website"))
AI = os.path.normpath(os.path.join(HERE, "..", "BTB_AI"))
CSV_PATH = os.path.join(HERE, "classified_qa.csv")
INTERVIEWS = os.path.join(WEB, "src", "data", "interviews.json")
TRANSCRIPTS_DIR = os.path.join(WEB, "src", "data", "transcripts")

CSV_COLUMNS = [
    "interview", "qa_index", "question", "answer", "full_text",
    "ds_label", "ds_confidence", "ds_label_v2", "review_priority", "tfidf_label",
]
AUDIO_EXTS = (".mp3", ".m4a", ".wav", ".flac", ".mp4", ".mov")


def log(step, msg):
    print(f"[{step}] {msg}", flush=True)


def kebab(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def find_audio(folder):
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(AUDIO_EXTS):
            return os.path.join(folder, f)
    return None


def transcript_text(folder, ragId):
    """The full transcript text — from the Groq JSON, else transcription.txt."""
    j = os.path.join(folder, f"{ragId}.json")
    if os.path.exists(j):
        return json.load(io.open(j, encoding="utf-8")).get("text", "").strip()
    t = os.path.join(folder, "transcription.txt")
    return io.open(t, encoding="utf-8").read().strip() if os.path.exists(t) else ""


# ── stage 1: transcribe ──────────────────────────────────────────────────────
def stage_transcribe(ragId, folder, force):
    out_json = os.path.join(folder, f"{ragId}.json")
    if os.path.exists(out_json) and not force:
        log("transcribe", "already done, skipping")
    else:
        audio = find_audio(folder)
        if not audio:
            sys.exit(f"[transcribe] no audio file found in {folder}")
        log("transcribe", f"Groq Whisper on {os.path.basename(audio)} ...")
        tg.write_outputs(ragId, folder, tg.transcribe(audio))
    # always ensure a plain transcription.txt exists for the next stage
    txt = os.path.join(folder, "transcription.txt")
    if not os.path.exists(txt) or force:
        io.open(txt, "w", encoding="utf-8", newline="\n").write(transcript_text(folder, ragId))


# ── stage 2: differentiate (Q&A) ─────────────────────────────────────────────
def stage_differentiate(folder, force):
    qa = os.path.join(folder, "transcription_qa.txt")
    if os.path.exists(qa) and not force:
        log("qa", "already done, skipping")
        return
    log("qa", "splitting transcript into Q&A (DeepSeek) ...")
    text = io.open(os.path.join(folder, "transcription.txt"), encoding="utf-8").read().strip()
    io.open(qa, "w", encoding="utf-8", newline="\n").write(diffmod.differentiate(text))


# ── stage 3: classify + append to the master CSV ─────────────────────────────
def stage_classify(ragId, folder, force):
    df = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame(columns=CSV_COLUMNS)
    if ragId in set(df.get("interview", [])) and not force:
        log("classify", f"{ragId} already in classified_qa.csv, skipping")
        return
    df = df[df.get("interview") != ragId] if "interview" in df else df  # de-dupe on --force

    pairs = clf.parse_qa_file(os.path.join(folder, "transcription_qa.txt"))
    log("classify", f"labelling {len(pairs)} Q&A pairs by topic (DeepSeek) ...")
    rows = []
    for i, p in enumerate(pairs, 1):
        full = f"Q: {p['question']}\nA: {p['answer']}"
        label, conf = clf.deepseek_classify(full, clf.TAXONOMY)
        rows.append({
            "interview": ragId, "qa_index": i,
            "question": p["question"], "answer": p["answer"], "full_text": full,
            "ds_label": label, "ds_confidence": conf,
            "ds_label_v2": "", "review_priority": 0, "tfidf_label": "",
        })
    out = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)[CSV_COLUMNS]
    out.to_csv(CSV_PATH, index=False)
    log("classify", f"appended {len(rows)} rows -> classified_qa.csv (now {len(out)} total)")


# ── stage 4: rebuild the AI vector store ─────────────────────────────────────
def stage_ingest():
    log("ingest", "rebuilding FAISS vector store from classified_qa.csv ...")
    try:
        r = subprocess.run([sys.executable, "-m", "app.ingest"], cwd=AI)
        ok = r.returncode == 0
    except Exception:
        ok = False
    if not ok:
        log("ingest", "skipped locally (embedding deps live in the server venv) — "
                      "rebuild on the server instead; continuing")


# ── stage 5: website transcript ──────────────────────────────────────────────
def paragraphs(text, per=4):
    clean = re.sub(r"\s+", " ", text).strip()
    sentences = re.findall(r"[^.!?]+[.!?]+(?:\s|$)", clean) or [clean]
    out, cur = [], []
    for s in sentences:
        cur.append(s.strip())
        if len(cur) >= per:
            out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def stage_transcript(ragId, folder, slug):
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    dest = os.path.join(TRANSCRIPTS_DIR, f"{slug}.json")
    data = {"paragraphs": paragraphs(transcript_text(folder, ragId))}
    io.open(dest, "w", encoding="utf-8", newline="\n").write(json.dumps(data) + "\n")
    log("transcript", f"wrote {os.path.relpath(dest, WEB)} ({len(data['paragraphs'])} paragraphs)")


# ── stage 6: catalog copy + interviews.json entry ────────────────────────────
def scrape_youtube_date(url):
    m = re.search(r"(?:v=|youtu\.be/|embed/)([\w-]{6,})", url or "")
    if not m:
        return ""
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/watch?v={m.group(1)}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
        d = re.search(r'"uploadDate":"([^"]+)"', html)
        return d.group(1) if d else ""
    except Exception:
        return ""


def draft_copy(name, role, org, text):
    """Ask DeepSeek for the bio / highlights / quote / suggested questions."""
    import requests
    prompt = (
        f"From this interview transcript, write website copy for {name} "
        f"({role} at {org}) on a student-run engineering interview site. "
        "Reply with ONLY a JSON object with these keys:\n"
        '- "intro": a 55-75 word third-person bio covering their path and what '
        "they do now.\n"
        '- "highlights": exactly 4 short phrases (3 to 6 words) of what the '
        "episode covers.\n"
        '- "quote": one memorable sentence the interviewee actually says, close '
        "to verbatim.\n"
        '- "questions": exactly 3 natural questions a student might ask about '
        "this interview.\n"
        "Never use em dashes. Plain, warm, concrete language.\n\n"
        f"TRANSCRIPT:\n{text[:12000]}"
    )
    payload = {
        "model": clf.DEEPSEEK_MODEL, "temperature": 0.4, "max_tokens": 700,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        resp = requests.post(
            clf.DEEPSEEK_URL,
            headers={"Authorization": f"Bearer {clf.DEEPSEEK_API_KEY}",
                     "Content-Type": "application/json"},
            json=payload, timeout=60,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        raw = raw.replace("```json", "").replace("```", "").strip()
        c = json.loads(raw)
        return {
            "intro": c.get("intro", "").replace(" — ", ", ").strip(),
            "highlights": [h.strip() for h in c.get("highlights", [])][:4],
            "quote": c.get("quote", "").replace(" — ", ", ").strip().strip('"'),
            "questions": [q.strip() for q in c.get("questions", [])][:3],
        }
    except Exception as e:
        log("copy", f"draft failed ({e}); leaving placeholders for you to fill")
        return {"intro": "", "highlights": [], "quote": "", "questions": []}


def stage_catalog(args, folder, slug):
    items = json.load(io.open(INTERVIEWS, encoding="utf-8"))
    episode = args.episode or (max((p.get("episode") or 0 for p in items), default=0) + 1)
    date = args.date or scrape_youtube_date(args.video)

    existing = next((p for p in items if p.get("id") == slug), None)
    copy = draft_copy(args.name, args.role, args.org, transcript_text(folder, args.ragId))
    log("copy", "drafted intro / highlights / quote / questions (review before publishing)")

    entry = {
        "id": slug, "ragId": args.ragId, "episode": episode,
        "name": args.name, "role": args.role, "org": args.org, "field": args.field,
        "video": args.video or "", "date": date,
        "intro": copy["intro"], "highlights": copy["highlights"],
        "quote": copy["quote"], "questions": copy["questions"],
    }
    if existing:
        items[items.index(existing)] = entry
    else:
        items.append(entry)
    items.sort(key=lambda p: p.get("episode") or 0)
    io.open(INTERVIEWS, "w", encoding="utf-8", newline="\n").write(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n"
    )
    log("catalog", f"wrote interviews.json entry (EP {episode:02d}, id={slug})")


def main():
    ap = argparse.ArgumentParser(description="Add one interviewee to BTB end to end.")
    ap.add_argument("--ragId", required=True, help="CamelCase folder name, e.g. NancyLi")
    ap.add_argument("--name", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--org", required=True)
    ap.add_argument("--field", required=True)
    ap.add_argument("--video", default="", help="YouTube URL (optional; add later)")
    ap.add_argument("--episode", type=int, default=0, help="0 = next available")
    ap.add_argument("--date", default="", help="ISO date (else scraped from YouTube)")
    ap.add_argument("--force", action="store_true", help="redo finished stages")
    args = ap.parse_args()

    folder = os.path.join(HERE, args.ragId)
    if not os.path.isdir(folder):
        sys.exit(f"folder not found: {folder} (create BTB_Prepare/{args.ragId}/ and drop the audio in)")
    slug = kebab(args.name)

    stage_transcribe(args.ragId, folder, args.force)
    stage_differentiate(folder, args.force)
    stage_classify(args.ragId, folder, args.force)
    stage_ingest()
    stage_transcript(args.ragId, folder, slug)
    stage_catalog(args, folder, slug)

    print("\nDone locally. Next:")
    print("  1. Review the drafted copy in BTB_Website/src/data/interviews.json")
    print("  2. bash deploy/deploy_frontend.sh")
    print("  3. Ship the new vector store + classified_qa.csv to the server and")
    print("     restart btb-backend (or rebuild the store there), and add the entry")
    print("     to the server's interviews.json (it is preserved across deploys).")


if __name__ == "__main__":
    main()
