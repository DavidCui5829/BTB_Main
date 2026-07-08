"""Build (or rebuild) the FAISS vector store from classified_qa.csv."""

import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app import config


def load_documents() -> list[Document]:
    df = pd.read_csv(config.QA_CSV_PATH)

    documents = []
    for _, row in df.iterrows():
        label_v2 = row.get("ds_label_v2")
        topic = label_v2 if pd.notna(label_v2) else row.get("ds_label")
        content = f"Q: {row['question']}\nA: {row['answer']}"
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "interview": row["interview"],
                    "qa_index": int(row["qa_index"]),
                    "topic": topic,
                },
            )
        )
    return documents


def get_interview_names() -> list[str]:
    df = pd.read_csv(config.QA_CSV_PATH)
    return sorted(df["interview"].unique().tolist())


def build_vectorstore() -> FAISS:
    documents = load_documents()
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
    store = FAISS.from_documents(documents, embeddings)
    store.save_local(str(config.VECTOR_STORE_DIR))
    return store


if __name__ == "__main__":
    build_vectorstore()
    print(f"Vector store built at {config.VECTOR_STORE_DIR}")
