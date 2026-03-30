"""
scripts/add_invoice_spike.py

Simulates a new weekly invoice arriving for "Restaurante Paco" where
Olive Oil (Aceite de Oliva) suddenly spikes in price by 50%+.
"""

import sys
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import datetime
from sqlalchemy import select
from agent.db.session import AsyncSessionLocal
from agent.db.models import Restaurant, Invoice, LineItem

async def add_spike():
    async with AsyncSessionLocal() as session:
        # 1. Find Restaurante Paco
        stmt = select(Restaurant).where(Restaurant.name == "Restaurante Paco")
        paco = (await session.execute(stmt)).scalar_one_or_none()
        
        if not paco:
            print("❌ Restaurant not found. Run seed_db.py first.")
            return

        # 2. Find the date of the last invoice
        stmt = select(Invoice).where(Invoice.restaurant_id == paco.id).order_by(Invoice.issued_at.desc())
        last_invoice = (await session.execute(stmt)).scalars().first()
        
        new_date = last_invoice.issued_at + datetime.timedelta(weeks=1)

        # 3. Create a new invoice
        new_invoice = Invoice(restaurant_id=paco.id, issued_at=new_date)
        session.add(new_invoice)
        await session.flush()

        # 4. Add the line items
        # Tomates stay expensive (simulating no improvement yet)
        session.add(LineItem(
            invoice_id=new_invoice.id,
            ingredient="Tomates",
            unit_price=4.30,
            quantity_kg=50.0,
        ))

        # ⚠️ THE SPIKE: Olive oil jumps from the stable 8.50 to 13.00 €/kg
        session.add(LineItem(
            invoice_id=new_invoice.id,
            ingredient="Aceite de Oliva",
            unit_price=13.00,  # +52.9% from 8.50
            quantity_kg=10.0,
        ))

        await session.commit()
        print(f"✅ Added new invoice for week of {new_date.strftime('%Y-%m-%d')}")
        print("   Aceite de Oliva is now at 13.00 €/kg! 🚨")

if __name__ == "__main__":
    asyncio.run(add_spike())
