"""
RAG Retriever — agent/rag/retriever.py

HOW VECTOR SEARCH WORKS:
  1. Every chunk of the strategy manual was converted to an "embedding"
     (a list of ~1000 numbers that captures semantic meaning).
  2. When we search, we convert the query to an embedding too.
  3. pgvector finds the database chunks whose embeddings are closest
     to the query embedding (cosine similarity).
  4. We return the top-k most similar chunks as context for the LLM.

WHY NOT KEYWORD SEARCH?
  Keyword search fails on synonyms and paraphrasing.
  Vector search finds semantically similar text even with different words.
  Example: "rising tomato costs" matches "vegetable price increase".

EMBEDDING MODEL:
  We use a small local embedding model via HuggingFace's sentence-transformers.
  It runs on CPU, no API key needed.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.documents import Document

load_dotenv()

# ── Embedding model ─────────────────────────────────────────────────────────
# "all-MiniLM-L6-v2" is a tiny but good model (~80MB) that runs on CPU
# It converts text → 384-dimensional vectors
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# ── pgvector connection ──────────────────────────────────────────────────────
# We reuse the same Postgres DB but store embeddings in a separate table
COLLECTION_NAME = "haddock_strategy"

_vectorstore: Optional[PGVector] = None


def get_vectorstore() -> PGVector:
    """Lazy-initialise the vector store (connects only when needed)."""
    global _vectorstore
    if _vectorstore is None:
        # pgvector needs "postgresql+psycopg2://" (sync driver) for LangChain
        db_url = os.environ["DATABASE_URL"].replace("+asyncpg", "+psycopg2")
        _vectorstore = PGVector(
            connection_string=db_url,
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME,
        )
    return _vectorstore


async def retrieve(query: str, top_k: int = 3) -> list[str]:
    """
    Searches the vector store for chunks semantically similar to `query`.

    Parameters
    ----------
    query : str
        The search question (e.g. "rising vegetable costs restaurant")
    top_k : int
        How many chunks to return (default 3)

    Returns
    -------
    list[str]
        The text content of the top-k most relevant strategy chunks.
    """
    vectorstore = get_vectorstore()
    # similarity_search returns Document objects; we extract .page_content
    docs: list[Document] = vectorstore.similarity_search(query, k=top_k)
    return [doc.page_content for doc in docs]
