"""Timestamped transcription via Groq's Whisper large-v3.

Groq's endpoint is OpenAI-compatible. Requesting response_format=verbose_json
with segment/word timestamp granularities returns per-segment timing that the
SiliconFlow endpoint does not provide.

Files above Groq's ~25 MB upload limit are transcoded down to 16 kHz mono FLAC
(lossless, but far smaller) before upload.
"""

import json
import os
import subprocess
import sys
import tempfile

import requests

# Load secrets from BTB_Prepare/.env (gitignored). No-op if python-dotenv isn't
# installed or the file is missing, in which case real env vars are used.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MODEL = "whisper-large-v3"

# Stay safely under Groq's 25 MB free-tier upload cap.
SIZE_LIMIT = 24 * 1024 * 1024

# One representative audio file per interviewee.
TARGETS = {
    "AzizBamak": "AzizBamak/Interview with 10 year Project Manager at GTT Aziz Bamik - BeyondtheBlueprint (128k).mp3",
    "ElliotStokes": "ElliotStokes/Interview with Chemical Engineer and Director of Process Safety Management Elliot Wolf Stokes - BeyondtheBlueprint (128k).mp3",
    "MichaelAdelemoni": "MichaelAdelemoni/Interview with Google Software Engineer Michael Adelemoni - BeyondtheBlueprint (128k).mp3",
    "MutaharMehkri": "MutaharMehkri/Interview with Nasa Aerospace Engineer Mutahar Mehkri - BeyondtheBlueprint (128k).mp3",
    "NandiniHarinath": "NandiniHarinath/Interview with ISRO Aerospace Engineer_ Nandini Harinath..mp3",
    "XavierEldridge": "XavierEldridge/XavierEldridgeAudio.mp3",
    "NancyLi": "NancyLi/Interview with Pipeline Engineer_ Nancy Li.mp3",
}


def compress_for_upload(src: str) -> str:
    """Transcode to 16 kHz mono MP3 (64 kbps) in a temp file; return its path.

    Whisper resamples to 16 kHz mono internally, so this discards nothing the
    model uses while keeping even ~1 hour interviews well under the upload cap.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-ac", "1", "-ar", "16000", "-b:a", "64k", tmp.name],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return tmp.name


def transcribe(file_path: str) -> dict:
    upload_path = file_path
    tmp_path = None
    if os.path.getsize(file_path) > SIZE_LIMIT:
        print(f"    compressing (over {SIZE_LIMIT // (1024*1024)} MB)...")
        tmp_path = compress_for_upload(file_path)
        upload_path = tmp_path

    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        with open(upload_path, "rb") as audio_file:
            files = {"file": (os.path.basename(upload_path), audio_file)}
            data = {
                "model": MODEL,
                "response_format": "verbose_json",
                "timestamp_granularities[]": ["segment", "word"],
            }
            response = requests.post(headers=headers, url=URL, files=files, data=data)
        response.raise_for_status()
        return response.json()
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def fmt_ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def write_outputs(name: str, out_dir: str, result: dict) -> None:
    json_path = os.path.join(out_dir, f"{name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    txt_path = os.path.join(out_dir, f"{name}.timestamped.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for seg in result.get("segments", []):
            start = fmt_ts(seg["start"])
            end = fmt_ts(seg["end"])
            f.write(f"[{start} --> {end}] {seg['text'].strip()}\n")

    print(f"    saved {json_path}")
    print(f"    saved {txt_path}")


def main() -> None:
    base = os.path.dirname(os.path.abspath(__file__))
    selected = sys.argv[1:] or list(TARGETS)
    for name in selected:
        rel = TARGETS.get(name)
        if rel is None:
            print(f"[skip] unknown target: {name}")
            continue
        src = os.path.join(base, rel)
        if not os.path.exists(src):
            print(f"[skip] missing file: {src}")
            continue
        print(f"[{name}] transcribing...")
        result = transcribe(src)
        write_outputs(name, os.path.join(base, os.path.dirname(rel)), result)


if __name__ == "__main__":
    main()
