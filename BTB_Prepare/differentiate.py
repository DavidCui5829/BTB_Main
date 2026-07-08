import os
import sys
import requests

# Load secrets from BTB_Prepare/.env (gitignored). No-op if python-dotenv isn't
# installed or the file is missing, in which case real env vars are used.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-v4-flash"  # DeepSeek V4 Flash

SYSTEM_PROMPT = (
    "You are an expert transcript analyst. "
    "Your job is to read raw interview transcripts and clearly label each segment "
    "as either a QUESTION (asked by the interviewer) or an ANSWER (given by the interviewee). "
    "Output only the labeled transcript — no commentary, no summaries."
)

USER_PROMPT = """\
Below is a raw podcast interview transcript with no speaker labels. \
Differentiate every question and every answer. Use this exact format:

Q: <question text>

A: <answer text>

Rules:
- Preserve the original wording exactly (do not paraphrase or correct grammar)
- If multiple short follow-up questions are asked together, group them under one Q: block
- Ignore filler words that are clearly transitional (e.g. "okay", "yeah", "thank you") \
  unless they are part of a substantive question or answer
- Output Q/A pairs in the order they appear in the transcript

TRANSCRIPT:
{transcript}
"""

TRANSCRIPTION_FILES = [
    r"AzizBamak\Interview with 10 year Project Manager at GTT Aziz Bamik - BeyondtheBlueprint (128k).txt",
    r"ElliotStokes\Interview with Chemical Engineer and Director of Process Safety Management Elliot Wolf Stokes - BeyondtheBlueprint (128k).txt",
    r"MichaelAdelemoni\Interview with Google Software Engineer Michael Adelemoni - BeyondtheBlueprint (128k).txt",
    r"MutaharMehkri\Interview with Nasa Aerospace Engineer Mutahar Mehkri - BeyondtheBlueprint (128k).txt",
    r"NandiniHarinath\Interview with ISRO Aerospace Engineer_ Nandini Harinath..txt",
    r"XavierEldridge\transcription.txt",
]


def differentiate(transcript: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(transcript=transcript)},
        ],
        "max_tokens": 8192,
        "temperature": 0.0,
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def process_file(full_path: str):
    print(f"Processing: {full_path}")
    with open(full_path, "r", encoding="utf-8") as f:
        transcript = f.read().strip()

    if not transcript:
        print("  SKIP: file is empty")
        return

    result = differentiate(transcript)

    out_path = os.path.splitext(full_path)[0] + "_qa.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"  Saved: {out_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) > 1:
        targets = [os.path.join(base_dir, p) for p in sys.argv[1:]]
    else:
        targets = [os.path.join(base_dir, p) for p in TRANSCRIPTION_FILES]

    for path in targets:
        try:
            process_file(path)
        except requests.HTTPError as e:
            print(f"  HTTP ERROR {e.response.status_code}: {e.response.text}")
        except Exception as e:
            print(f"  ERROR: {e}")
