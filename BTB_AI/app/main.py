"""FastAPI backend exposing the BTB interview RAG Q&A over HTTP."""

import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from pydantic import BaseModel, Field

from app.rag import answer_question

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
