"""
Shared Agent State — agent/graph/state.py

WHY A SHARED STATE?
  In LangGraph, all nodes (analyst, RAG, writer, notifier) communicate
  through a single shared dictionary called the "state".
  Each node reads what it needs and writes what it produces.
  This avoids passing long argument lists between functions.

FLOW:
  analyst_node   → writes: alerts
  rag_node       → writes: strategy_advice
  writer_node    → writes: email_draft
  notifier_node  → writes: notification_sent
"""

from typing import TypedDict


class Alert(TypedDict):
    """Represents a detected cost anomaly for one restaurant."""
    restaurant_id: int
    restaurant_name: str
    contact_email: str
    ingredient: str
    first_price: float     # €/kg in week 1
    last_price: float      # €/kg in the most recent week
    pct_increase: float    # Total % increase across the period
    weeks_observed: int


class CompanyState(TypedDict):
    """
    The shared state that flows through all agent nodes.

    Think of this as a "baton" passed from node to node in a relay race.
    Each node enriches it with new information.
    """
    # Set by analyst_node
    alerts: list[Alert]

    # Set by rag_node (one advice string per alert, or a single general advice)
    strategy_advice: str

    # Set by writer_node
    email_draft: str

    # Set by notifier_node
    notification_sent: bool
