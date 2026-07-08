"""Retrieval-augmented generation over the BTB interview Q&A dataset."""

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

SYSTEM_PROMPT = (
    "You are an assistant for the Beyond the Blueprint podcast, which interviews "
    "professionals about their careers. Answer the user's question using ONLY the "
    "interview excerpts given in the context below. Cite which interviewee(s) you "
    "drew from. If the context doesn't contain enough information to answer, say so "
    "plainly instead of guessing."
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
            "(e.g. resolving pronouns like 'he'/'that project'). If it is already "
            "standalone, return it unchanged. Reply with ONLY the rewritten "
            "question, no preamble.",
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


def retrieve(question: str, top_k: int | None = None) -> list[Document]:
    named_ids = mentions_named_interviewee(question)
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
    docs = retrieve(standalone_question, top_k)
    chain = PROMPT | get_llm() | StrOutputParser()
    answer = chain.invoke(
        {"context": format_docs(docs), "question": question, "history": history}
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
