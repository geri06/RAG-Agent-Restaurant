"""
Notifier Node — agent/graph/nodes/notifier.py

ROLE: Messenger 📣
  Sends a Slack notification to the Sales team when a high-risk
  client is detected.

CURRENT STATUS: STUB
  Instead of actually calling Slack, this node prints the message
  to the console. This lets you develop and test without needing
  a real Slack workspace.

  To make it real: replace the print() with agent/integrations/slack.py

WRITES TO STATE: notification_sent (bool)
"""

from agent.graph.state import CompanyState


async def notifier_node(state: CompanyState) -> CompanyState:
    """
    LangGraph node: notifies the Sales team (via Slack stub).

    Parameters
    ----------
    state : CompanyState
        Must have `alerts` and `email_draft`.

    Returns
    -------
    CompanyState
        Updated state with `notification_sent = True`.
    """
    print("\n📣 [notifier_node] Sending Slack notification (STUB)...")

    if not state["alerts"]:
        print("  No alerts — nothing to notify.")
        return {**state, "notification_sent": False}

    # Build the Slack message
    alert_lines = "\n".join(
        f"• *{a['restaurant_name']}* — {a['ingredient']} subió "
        f"*{a['pct_increase']}%* en {a['weeks_observed']} semanas"
        for a in state["alerts"]
    )

    slack_message = f"""
🚨 *Company-Flow Alert* — Restaurantes en Riesgo

{alert_lines}

El equipo de Customer Success tiene un draft de email listo para enviar.
Revisar en el dashboard: http://localhost:3000
""".strip()

    # ── STUB: In production this would call agent/integrations/slack.py ──────
    print("\n" + "─" * 60)
    print("💬 SLACK MESSAGE (#ventas):")
    print(slack_message)
    print("─" * 60)
    # ─────────────────────────────────────────────────────────────────────────

    return {**state, "notification_sent": True}
