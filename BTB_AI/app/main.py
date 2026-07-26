"""FastAPI backend exposing the BTB interview RAG Q&A over HTTP."""

import json
import logging
import os
import secrets
import shutil
import subprocess
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from pydantic import BaseModel, Field

from app.config import ADMIN_TOKEN, INTERVIEWS_JSON_PATH, REBUILD_ON_SAVE, WEBSITE_DIR
from app.rag import answer_question

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="BTB Q&A Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session history, keyed by session_id. Fine for local/dev testing;
# swap for a real store (Redis, DB) before running multiple workers or in prod.
SESSIONS: dict[str, list[BaseMessage]] = {}


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)


class Source(BaseModel):
    interview: str
    topic: str
    excerpt: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[Source]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id or str(uuid.uuid4())
    history = SESSIONS.setdefault(session_id, [])

    try:
        result = answer_question(req.question, history, req.top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    history.append(HumanMessage(req.question))
    history.append(AIMessage(result["answer"]))

    return ChatResponse(session_id=session_id, **result)


@app.delete("/chat/{session_id}")
def clear_session(session_id: str) -> dict:
    SESSIONS.pop(session_id, None)
    return {"status": "cleared"}


# --------------------------------------------------------------------------
# Interview catalog admin (used by the website's unlisted /admin page).
# Reads and writes BTB_Website/src/data/interviews.json — the same file the
# site imports at build time, so the Vite dev server hot-reloads edits.
# --------------------------------------------------------------------------


class Interview(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    ragId: str = ""
    episode: int = Field(ge=1)
    name: str = Field(min_length=1)
    role: str = ""
    org: str = ""
    field: str = ""
    video: str = ""
    date: str = ""  # YouTube upload date (ISO 8601); used for VideoObject uploadDate
    intro: str = ""
    highlights: list[str] = Field(default_factory=list)
    quote: str = ""
    questions: list[str] = Field(default_factory=list)


def require_admin(x_admin_token: str = Header(default="")) -> None:
    if not secrets.compare_digest(x_admin_token.encode(), ADMIN_TOKEN.encode()):
        raise HTTPException(status_code=401, detail="Invalid admin token")


def _read_interviews() -> list[dict]:
    try:
        with open(INTERVIEWS_JSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Interviews file not found at {INTERVIEWS_JSON_PATH}",
        ) from exc


def _write_interviews(items: list[dict]) -> None:
    tmp = INTERVIEWS_JSON_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, INTERVIEWS_JSON_PATH)


@app.get("/admin/interviews", response_model=list[Interview])
def list_interviews() -> list[dict]:
    return _read_interviews()


@app.put(
    "/admin/interviews",
    response_model=list[Interview],
    dependencies=[Depends(require_admin)],
)
def replace_interviews(items: list[Interview]) -> list[dict]:
    ids = [item.id for item in items]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise HTTPException(status_code=422, detail=f"Duplicate ids: {', '.join(dupes)}")

    data = [item.model_dump() for item in items]
    _write_interviews(data)
    _rebuild_site()
    return data


def _rebuild_site() -> None:
    """Rebuild the static site so a production deployment shows the new data.

    Fire-and-forget: the JSON write already succeeded, and the next save (or a
    manual `npm run build`) can recover from a failed build.
    """
    if not REBUILD_ON_SAVE:
        return
    npm = shutil.which("npm")
    if npm is None:
        logger.warning("BTB_REBUILD_ON_SAVE is set but npm was not found on PATH")
        return
    subprocess.Popen(
        [npm, "run", "build"],
        cwd=WEBSITE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
