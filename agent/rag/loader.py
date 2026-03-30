"""
RAG Loader — agent/rag/loader.py

PURPOSE:
  Reads the strategy manual (docs/strategy_manual.md), splits it into
  overlapping chunks, converts them to vectors, and stores them in pgvector.

RUN ONCE (after seeding the DB):
  uv run python -m agent.rag.loader

WHY CHUNKING?
  LLMs have a context window limit (max tokens per call).
  Instead of sending the entire manual to the LLM, we:
  1. Split it into small chunks (~500 words)
  2. Only send the 3 most relevant chunks (retrieved by similarity search)
  This is cheaper, faster, and often more accurate.

WHY OVERLAP?
  If a key sentence falls at the boundary of two chunks, overlap
  ensures it appears in at least one of them fully.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.pgvector import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agent.rag.retriever import embeddings, COLLECTION_NAME

load_dotenv()

DOCS_PATH = Path(__file__).parent.parent.parent / "docs" / "strategy_manual.md"


def load_and_index() -> None:
    """
    Loads the strategy manual, chunks it, and stores embeddings in pgvector.
    Safe to re-run — PGVector will replace existing documents.
    """
    print(f"📄 Loading: {DOCS_PATH}")

    if not DOCS_PATH.exists():
        raise FileNotFoundError(
            f"Strategy manual not found at {DOCS_PATH}\n"
            "Create docs/strategy_manual.md first."
        )

    # Step 1: Load the raw text
    loader = TextLoader(str(DOCS_PATH), encoding="utf-8")
    raw_docs = loader.load()

    # Step 2: Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # ~500 characters per chunk
        chunk_overlap=50,     # 50-character overlap between consecutive chunks
        length_function=len,
    )
    chunks = splitter.split_documents(raw_docs)
    print(f"  Split into {len(chunks)} chunks.")

    # Step 3: Convert to vectors and store in pgvector
    db_url = os.environ["DATABASE_URL"].replace("+asyncpg", "+psycopg2")
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        connection_string=db_url,
        pre_delete_collection=True,  # Drop and recreate to avoid duplicates
    )
    print(f"  ✅ Indexed {len(chunks)} chunks into pgvector collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    load_and_index()
