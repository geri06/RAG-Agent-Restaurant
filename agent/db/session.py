"""
Database Session — agent/db/session.py

Creates the async database connection pool.

WHY ASYNC?
  Our FastAPI server is asynchronous (handles many requests without blocking).
  An async DB session means the server stays responsive while waiting for queries.

HOW TO USE:
  async with get_session() as session:
      result = await session.execute(...)
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()  # Reads .env file into os.environ

# The DATABASE_URL must start with "postgresql+asyncpg://"
# asyncpg is the async Postgres driver
DATABASE_URL = os.environ["DATABASE_URL"]

# create_async_engine creates the connection pool.
# echo=True prints every SQL statement to the console — great for learning!
engine = create_async_engine(DATABASE_URL, echo=True)

# async_sessionmaker is a factory that creates new sessions on demand
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't refresh objects after commit (saves DB round-trips)
)


@asynccontextmanager
async def get_session():
    """
    Context manager that yields a DB session and always closes it when done.

    Usage:
        async with get_session() as session:
            ...  # use session here
    """
    async with AsyncSessionLocal() as session:
        yield session
