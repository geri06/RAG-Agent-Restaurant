"""
Database Seed Script — agent/db/seed.py

Populates the database with realistic mock data for testing.

SCENARIO:
  "Restaurante Paco" buys tomatoes every week.
  The price of tomatoes grows +20% each week for 8 weeks.
  This will trigger our analyst agent to flag it.

RUN ONCE:
  uv run python -m agent.db.seed

WHY A SEPARATE SEED SCRIPT?
  Keeping fake data generation separate from the main app keeps production code clean.
  You can reset the DB anytime by running this again.
"""

import asyncio
import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from agent.db.models import Base, Invoice, LineItem, Restaurant
from agent.db.session import AsyncSessionLocal

load_dotenv()


async def create_tables() -> None:
    """Create all tables if they don't exist yet."""
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("✅ Tables created (or already exist)")


async def seed() -> None:
    await create_tables()

    async with AsyncSessionLocal() as session:
        # ── 1. Create restaurant ─────────────────────────────────────────────
        paco = Restaurant(
            name="Restaurante Paco",
            contact_email="paco@restaurantepaco.es",
            city="Barcelona",
        )
        session.add(paco)
        await session.flush()  # flush assigns paco.id without committing

        # ── 2. Generate 8 weekly invoices with escalating tomato prices ──────
        base_price_tomato = 1.20  # €/kg starting price

        for week in range(8):
            invoice_date = datetime.datetime(2025, 1, 6) + datetime.timedelta(weeks=week)
            invoice = Invoice(restaurant_id=paco.id, issued_at=invoice_date)
            session.add(invoice)
            await session.flush()

            # Tomatoes: price grows 20% per week
            tomato_price = round(base_price_tomato * (1.20**week), 4)
            session.add(
                LineItem(
                    invoice_id=invoice.id,
                    ingredient="Tomates",
                    unit_price=tomato_price,
                    quantity_kg=50.0,
                )
            )

            # Olive oil: stable price (control ingredient)
            session.add(
                LineItem(
                    invoice_id=invoice.id,
                    ingredient="Aceite de Oliva",
                    unit_price=8.50,
                    quantity_kg=10.0,
                )
            )

            print(f"  Week {week + 1}: Tomates @ {tomato_price:.4f} €/kg")

        await session.commit()
        print(f"\n✅ Seeded {8} invoices for '{paco.name}'")
        print("   You should now see the data in your Supabase dashboard.")


if __name__ == "__main__":
    asyncio.run(seed())
