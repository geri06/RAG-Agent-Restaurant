"""
scripts/seed_db.py — Convenience wrapper to run the DB seeder.

Usage:
    uv run python scripts/seed_db.py
"""

import asyncio
import sys
from pathlib import Path

# Make sure the project root is in the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.db.seed import seed

if __name__ == "__main__":
    asyncio.run(seed())
