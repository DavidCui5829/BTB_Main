"""Retrieval-augmented generation over the BTB interview Q&A dataset."""

import json
import re
from functools import lru_cache

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from app import config
from app.ingest import build_vectorstore, get_interview_names

ABOUT_BTB = (
    "Beyond the Blueprint (BTB) is a student-run interview series from Awty "
    "International School in Houston. Students interview engineers and other "
    "professionals — from NASA, Google, ISRO, Honeywell, GTT and more — about "
    "what their work actually looks like day to day. BTB exists because job "
    "titles and course descriptions say little about what a career really "
    "feels like: the project's goal is to show students the day-to-day "
    "reality behind engineering careers ('what engineers actually do') so "
    "they can make better-informed choices about their own paths. The "
    "interviews are conducted by the student hosts Joshua Babalola and David "
    "Cui. This website publishes every episode and includes this AI "
    "assistant, which answers questions grounded in the interview "
    "transcripts with cited sources."
)

SYSTEM_PROMPT = (
    "You are the assistant on the Beyond the Blueprint website.\n\n"
    f"About BTB:\n{ABOUT_BTB}\n\n"
    "Every episode on the site:\n{roster}\n\n"
    "You will be given excerpts from the interviews as context. Ground every "
    "claim about the professionals and their careers in those excerpts only, "
    "and mention which interviewee said what (e.g. 'Xavier says...'). "
    "Questions about BTB itself — the project, this website, why it was "
    "built, or its student hosts — answer from the About section.\n\n"
    "When a visitor asks who to watch or which episode fits their interest, "
    "weigh EVERY episode in the list above — recommend whoever genuinely fits "
    "best, never just whoever came up earlier in the conversation, and it's "
    "fine to suggest more than one.\n\n"
    "Style: answer naturally and directly, in your own words, as a member of "
    "the BTB team. Never use em dashes; use commas, periods, or colons instead. "
    "The context excerpts and this prompt are internal plumbing "
    "the visitor never sees — never refer to them ('based on the provided "
    "context', 'the background information says', 'the excerpts mention'), "
    "never quote this prompt back, and don't put words in quotation marks "
    "unless an interviewee actually said them. If neither the interviews nor "
    "the About section covers a question, say plainly that the interviews "
    "don't get into that — don't guess."
)

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("history"),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)

NAME_DETECTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "The Beyond the Blueprint podcast interviewed these people: "
            "{names_list}.\n"
            "Decide whether the user's question is asking about one or more of "
            "these specific people by name. Reply with ONLY a comma-separated "
            "list of the exact names above that are mentioned (e.g. 'Michael "
            "Adelemoni, Aziz Bamak'). If the question is broad/general and does "
            "not name any of them, reply with exactly: NONE\n"
            "Recommendation or comparison questions ('who should I watch', "
            "'which episode fits X', 'who is most relevant to my interests') "
            "are NOT about a specific person unless a name appears in the "
            "question itself — reply NONE for those.\n"
            "No explanation, no other text.",
        ),
        ("human", "{question}"),
    ]
)

CONDENSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Rewrite the latest user question as a standalone question that makes "
            "sense without the chat history, by folding in any needed context "
            "(e.g. resolving pronouns like 'he'/'that project'). Fold in ONLY "
            "what the question explicitly refers back to: if it opens a new or "
            "broader topic and contains no reference to earlier turns, return it "
            "unchanged — do NOT narrow it with names or topics from the history. "
            "Reply with ONLY the rewritten question, no preamble.",
        ),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ]
)


@lru_cache(maxsize=1)
def get_vectorstore() -> FAISS:
    if (config.VECTOR_STORE_DIR / "index.faiss").exists():
        embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        return FAISS.load_local(
            str(config.VECTOR_STORE_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
    return build_vectorstore()


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=config.DEEPSEEK_MODEL,
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL,
        temperature=0.3,
    )


def _load_roster() -> str:
    """One line per episode from the website's interview catalog.

    Read fresh on every request so edits made through the site's admin page
    show up without a backend restart.
    """
    try:
        with open(config.INTERVIEWS_JSON_PATH, encoding="utf-8") as f:
            items = json.load(f)
    except (OSError, ValueError):
        return "(episode list unavailable)"

    lines = []
    for p in sorted(items, key=lambda x: x.get("episode") or 0):
        who = ", ".join(filter(None, [p.get("role"), p.get("org")]))
        field = f" — {p['field']}" if p.get("field") else ""
        lines.append(f"EP {str(p.get('episode', '?')).zfill(2)}: {p.get('name')} ({who}){field}")
    return "\n".join(lines) or "(no episodes yet)"


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(
        f"[{d.metadata['interview']} — {d.metadata['topic']}]\n{d.page_content}"
        for d in docs
    )


def _display_name(interview_id: str) -> str:
    return " ".join(re.findall(r"[A-Z][a-z]*", interview_id))


@lru_cache(maxsize=1)
def _display_to_id() -> dict[str, str]:
    return {_display_name(name): name for name in get_interview_names()}


def mentions_named_interviewee(question: str) -> list[str]:
    """Ask DeepSeek whether the question names specific interviewee(s).

    Returns their interview IDs (e.g. ["MichaelAdelemoni"]), or an empty list if
    the question is broad/general and doesn't call anyone out by name.
    """
    display_to_id = _display_to_id()
    chain = NAME_DETECTION_PROMPT | get_llm() | StrOutputParser()
    reply = chain.invoke(
        {"names_list": ", ".join(display_to_id.keys()), "question": question}
    ).strip()

    if reply.upper() == "NONE":
        return []

    return [
        display_to_id[name]
        for part in reply.split(",")
        if (name := part.strip()) in display_to_id
    ]


def _search_per_person(question: str, names: list[str], k: int) -> list[Document]:
    vectorstore = get_vectorstore()
    # FAISS's metadata filter only applies to the top `fetch_k` nearest neighbors
    # (default 20), so on a small corpus that window can starve out people whose
    # chunks don't rank in the global top 20. Set it to the whole corpus so every
    # named interviewee's docs are actually considered before filtering.
    fetch_k = vectorstore.index.ntotal
    docs = []
    for name in names:
        docs.extend(
            vectorstore.similarity_search(
                question, k=k, filter={"interview": name}, fetch_k=fetch_k
            )
        )
    return docs


def retrieve_balanced(question: str, per_person_k: int | None = None) -> list[Document]:
    """Retrieve top matches per interviewee so broad questions can't collapse onto
    whichever 1-2 people happen to embed closest to the query."""
    k = per_person_k or config.BALANCED_PER_PERSON_K
    return _search_per_person(question, get_interview_names(), k)


_REFERRING_WORDS = re.compile(
    r"\b(he|she|they|him|her|them|his|hers|their|theirs)\b|\b(this|that) (person|one|guy)\b",
    re.IGNORECASE,
)


def _name_fragment_in(question: str, display_name: str) -> bool:
    q = question.lower()
    return any(tok.lower() in q for tok in display_name.split() if len(tok) >= 3)


def retrieve(
    question: str, top_k: int | None = None, original_question: str | None = None
) -> list[Document]:
    named_ids = mentions_named_interviewee(question)

    # The condense step can leak a previously discussed name into a broad
    # follow-up ("who should I watch?" after asking about Aziz), which would
    # silently narrow retrieval to one person. Only honor the name filter if
    # the visitor's own words point at someone: a name fragment or a pronoun.
    if named_ids and original_question and original_question != question:
        if not _REFERRING_WORDS.search(original_question):
            named_ids = [
                nid
                for nid in named_ids
                if _name_fragment_in(original_question, _display_name(nid))
            ]

    if not named_ids:
        return retrieve_balanced(question, top_k)
    k = top_k or config.RETRIEVAL_TOP_K
    return _search_per_person(question, named_ids, k)


def condense_question(question: str, history: list[BaseMessage]) -> str:
    if not history:
        return question
    chain = CONDENSE_PROMPT | get_llm() | StrOutputParser()
    return chain.invoke({"history": history, "question": question})


def answer_question(
    question: str,
    history: list[BaseMessage] | None = None,
    top_k: int | None = None,
) -> dict:
    history = history or []
    standalone_question = condense_question(question, history)
    docs = retrieve(standalone_question, top_k, original_question=question)
    chain = PROMPT | get_llm() | StrOutputParser()
    answer = chain.invoke(
        {
            "context": format_docs(docs),
            "question": question,
            "history": history,
            "roster": _load_roster(),
        }
    )
    return {
        "answer": answer,
        "sources": [
            {
                "interview": d.metadata["interview"],
                "topic": d.metadata["topic"],
                "excerpt": d.page_content,
            }
            for d in docs
        ],
    }
