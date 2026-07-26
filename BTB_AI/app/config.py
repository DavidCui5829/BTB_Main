"""Settings loaded from environment / .env for the BTB RAG backend."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _resolve(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else (BASE_DIR / path).resolve()


DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

QA_CSV_PATH = _resolve(os.getenv("QA_CSV_PATH", "../BTB_Prepare/classified_qa.csv"))
VECTOR_STORE_DIR = _resolve(os.getenv("VECTOR_STORE_DIR", "vectorstore"))

RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "4"))
BALANCED_PER_PERSON_K = int(os.getenv("BALANCED_PER_PERSON_K", "2"))

# Interview catalog edited by the website's unlisted /admin page.
INTERVIEWS_JSON_PATH = _resolve(
    os.getenv("INTERVIEWS_JSON_PATH", "../BTB_Website/src/data/interviews.json")
)
# Token required (X-Admin-Token header) for write access to /admin endpoints.
ADMIN_TOKEN = os.getenv("BTB_ADMIN_TOKEN", "btb-admin")

# In production the site is a static build, so admin saves trigger a rebuild
# of the website (npm run build) to bake the new catalog in. Off by default
# for local dev, where the Vite dev server hot-reloads the JSON directly.
WEBSITE_DIR = _resolve(os.getenv("WEBSITE_DIR", "../BTB_Website"))
REBUILD_ON_SAVE = os.getenv("BTB_REBUILD_ON_SAVE", "0") == "1"
