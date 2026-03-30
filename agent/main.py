"""
FastAPI Application — agent/main.py

WHY FASTAPI?
  FastAPI is an async web framework for Python.
  It automatically generates API documentation (visit /docs after starting).
  It's built around Python type hints, making it beginner-friendly.

ENDPOINTS:
  GET  /healthz        → Quick health check (confirms server is running)
  GET  /api/prices     → Returns latest ingredient prices per restaurant
  POST /api/invoice    → Adds a new invoice with a single line item
  POST /api/run        → Triggers the full LangGraph agent pipeline

HOW TO RUN:
  uv run uvicorn agent.main:app --reload

  --reload means the server restarts automatically when you save a file.
  Perfect for development.
"""

import datetime
from typing import Optional

from dotenv import load_dotenv
load_dotenv()  # Must be before any other imports that read env vars

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, func

from agent.graph.graph import graph
from agent.graph.state import CompanyState
from agent.observability.langfuse_handler import get_langfuse_callback
from agent.db.session import get_session
from agent.db.models import Restaurant, Invoice, LineItem

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Company-Flow",
    description="Internal AI agent for Customer Success & Sales teams.",
    version="0.1.0",
)

# Allow the Next.js dashboard (running on port 3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ────────────────────────────────────────────────

class AddInvoiceRequest(BaseModel):
    """Body for POST /api/invoice"""
    restaurant_name: str = "Restaurante Paco"
    ingredient: str
    unit_price: float
    quantity_kg: float = 10.0
    date: Optional[str] = None  # ISO format YYYY-MM-DD; defaults to 1 week after latest


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/healthz", tags=["infra"])
async def health_check():
    """Returns 200 OK if the server is running. Used by monitoring tools."""
    return {"status": "ok", "service": "company-flow"}


@app.get("/api/prices", tags=["data"])
async def get_latest_prices():
    """
    Returns the latest unit price for each ingredient, independently.
    If ingredient A was last updated on March 10 and ingredient B on March 3,
    both are returned with their respective latest dates and prices.
    """
    async with get_session() as session:
        # Sub-query: for each (restaurant, ingredient), find the latest invoice date
        latest_per_ingredient = (
            select(
                Invoice.restaurant_id,
                LineItem.ingredient,
                func.max(Invoice.issued_at).label("max_date"),
            )
            .join(LineItem, LineItem.invoice_id == Invoice.id)
            .group_by(Invoice.restaurant_id, LineItem.ingredient)
            .subquery()
        )

        # Main query: join back to get the actual price from that specific date
        stmt = (
            select(
                Restaurant.name.label("restaurant_name"),
                Restaurant.contact_email,
                Invoice.issued_at,
                LineItem.ingredient,
                LineItem.unit_price,
            )
            .join(Invoice, Invoice.restaurant_id == Restaurant.id)
            .join(LineItem, LineItem.invoice_id == Invoice.id)
            .join(
                latest_per_ingredient,
                (Invoice.restaurant_id == latest_per_ingredient.c.restaurant_id)
                & (LineItem.ingredient == latest_per_ingredient.c.ingredient)
                & (Invoice.issued_at == latest_per_ingredient.c.max_date),
            )
            .order_by(Restaurant.name, LineItem.ingredient)
        )

        result = await session.execute(stmt)
        rows = result.all()

    prices = []
    for row in rows:
        prices.append({
            "restaurant_name": row.restaurant_name,
            "contact_email": row.contact_email,
            "date": row.issued_at.strftime("%Y-%m-%d"),
            "ingredient": row.ingredient,
            "unit_price": float(row.unit_price),
        })

    return {"prices": prices}


@app.post("/api/invoice", tags=["data"])
async def add_invoice(body: AddInvoiceRequest):
    """
    Adds a new invoice with a single line item for the given restaurant.
    If no date is provided, defaults to 1 week after the latest existing invoice.
    """
    async with get_session() as session:
        # Find the restaurant
        stmt = select(Restaurant).where(Restaurant.name == body.restaurant_name)
        restaurant = (await session.execute(stmt)).scalar_one_or_none()
        if not restaurant:
            raise HTTPException(status_code=404, detail=f"Restaurant '{body.restaurant_name}' not found")

        # Determine the date
        if body.date:
            invoice_date = datetime.datetime.strptime(body.date, "%Y-%m-%d")
        else:
            # Default: 1 week after the latest invoice
            latest = (
                await session.execute(
                    select(Invoice)
                    .where(Invoice.restaurant_id == restaurant.id)
                    .order_by(Invoice.issued_at.desc())
                )
            ).scalars().first()

            if latest:
                invoice_date = latest.issued_at + datetime.timedelta(weeks=1)
            else:
                invoice_date = datetime.datetime.now()

        # Create the invoice
        new_invoice = Invoice(restaurant_id=restaurant.id, issued_at=invoice_date)
        session.add(new_invoice)
        await session.flush()

        # Create the line item
        session.add(LineItem(
            invoice_id=new_invoice.id,
            ingredient=body.ingredient,
            unit_price=body.unit_price,
            quantity_kg=body.quantity_kg,
        ))

        await session.commit()

    return {
        "status": "created",
        "date": invoice_date.strftime("%Y-%m-%d"),
        "ingredient": body.ingredient,
        "unit_price": body.unit_price,
    }


@app.post("/api/run", tags=["agent"])
async def run_agent():
    """
    Triggers the full multi-agent pipeline:
    analyst → rag → writer → notifier

    Returns the final state including alerts, strategy advice,
    and the drafted email.
    """
    # The initial state — all fields start empty
    # Analysts will populate `alerts`, then subsequent nodes fill the rest
    initial_state: CompanyState = {
        "alerts": [],
        "strategy_advice": "",
        "email_draft": "",
        "notification_sent": False,
    }

    try:
        # ainvoke runs the full graph asynchronously
        # config passes the Langfuse callback so every step is traced
        final_state = await graph.ainvoke(
            initial_state,
            config={"callbacks": [get_langfuse_callback()]},
        )
    except Exception as exc:
        # Catch and surface errors clearly (don't expose raw stack traces in production)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "status": "completed",
        "alerts_found": len(final_state["alerts"]),
        "alerts": final_state["alerts"],
        "email_draft": final_state["email_draft"],
        "notification_sent": final_state["notification_sent"],
    }
