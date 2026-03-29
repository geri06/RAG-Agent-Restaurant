"""
Analyst Node — agent/graph/nodes/analyst.py

ROLE: Detective 🔍
  Queries the database to find restaurants where ingredient costs
  have risen by more than THRESHOLD_PCT over the observed period.

WHAT IT DOES:
  1. Fetches all line items grouped by restaurant + ingredient
  2. Compares first vs last recorded price
  3. Returns an Alert for every ingredient above the threshold

WRITES TO STATE: alerts (list of Alert dicts)
"""

from sqlalchemy import select, func
from agent.db.session import get_session
from agent.db.models import Restaurant, Invoice, LineItem
from agent.graph.state import HaddockState, Alert

# Ingredients with a cost increase above this % are flagged
THRESHOLD_PCT = 15.0


async def analyst_node(state: HaddockState) -> HaddockState:
    """
    LangGraph node: queries DB and detects rising ingredient costs.

    Parameters
    ----------
    state : HaddockState
        The current agent state (alerts will be empty at this point).

    Returns
    -------
    HaddockState
        Updated state with `alerts` list populated.
    """
    print("\n🔍 [analyst_node] Scanning invoices for cost anomalies...")
    alerts: list[Alert] = []

    async with get_session() as session:
        # ── Query: get all line items joined with invoice and restaurant ─────
        # We order by issued_at so we can compare first vs last price easily
        stmt = (
            select(
                Restaurant.id.label("restaurant_id"),
                Restaurant.name.label("restaurant_name"),
                Restaurant.contact_email,
                LineItem.ingredient,
                LineItem.unit_price,
                Invoice.issued_at,
            )
            .join(Invoice, Invoice.restaurant_id == Restaurant.id)
            .join(LineItem, LineItem.invoice_id == Invoice.id)
            .order_by(Restaurant.id, LineItem.ingredient, Invoice.issued_at)
        )
        rows = (await session.execute(stmt)).all()

    # ── Group rows by (restaurant_id, ingredient) ────────────────────────────
    # Python dict: key=(restaurant_id, ingredient), value=list of price rows
    groups: dict[tuple, list] = {}
    for row in rows:
        key = (row.restaurant_id, row.ingredient)
        groups.setdefault(key, []).append(row)

    # ── Compare first and last price for each group ───────────────────────────
    for (restaurant_id, ingredient), price_rows in groups.items():
        first = price_rows[0]
        last = price_rows[-1]

        first_price = float(first.unit_price)
        last_price = float(last.unit_price)

        if first_price == 0:
            continue  # Avoid division by zero

        pct_increase = ((last_price - first_price) / first_price) * 100

        if pct_increase >= THRESHOLD_PCT:
            alert: Alert = {
                "restaurant_id": restaurant_id,
                "restaurant_name": first.restaurant_name,
                "contact_email": first.contact_email,
                "ingredient": ingredient,
                "first_price": first_price,
                "last_price": last_price,
                "pct_increase": round(pct_increase, 1),
                "weeks_observed": len(price_rows),
            }
            alerts.append(alert)
            print(
                f"  ⚠️  {first.restaurant_name} — {ingredient}: "
                f"+{alert['pct_increase']}% over {alert['weeks_observed']} weeks"
            )

    if not alerts:
        print("  ✅ No anomalies detected.")

    return {**state, "alerts": alerts}
