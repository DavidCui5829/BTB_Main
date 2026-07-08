import requests
import os
import sys

# Load secrets from BTB_Prepare/.env (gitignored). No-op if python-dotenv isn't
# installed or the file is missing, in which case real env vars are used.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
URL = "https://api.siliconflow.cn/v1/audio/transcriptions"


def transcribe(file_path: str) -> str:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    with open(file_path, "rb") as audio_file:
        ext = os.path.splitext(file_path)[1].lstrip(".")
        files = {
            "file": (os.path.basename(file_path), audio_file),
            "model": (None, "FunAudioLLM/SenseVoiceSmall"),
        }
        response = requests.post(URL, headers=headers, files=files)
    response.raise_for_status()
    return response.json().get("text", "")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else (
        r"MichaelAdelemoni\Interview with Google Software Engineer Michael Adelemoni - BeyondtheBlueprint (128k).mp3"
    )
    print(f"Transcribing: {path}")
    text = transcribe(path)
    out_path = os.path.splitext(path)[0] + ".txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved to: {out_path}")
    print("\n--- Transcript ---\n")
    print(text.encode("utf-8", errors="replace").decode("utf-8"))
