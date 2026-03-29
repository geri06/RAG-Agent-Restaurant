"""
FastAPI Application — agent/main.py

WHY FASTAPI?
  FastAPI is an async web framework for Python.
  It automatically generates API documentation (visit /docs after starting).
  It's built around Python type hints, making it beginner-friendly.

ENDPOINTS:
  GET  /healthz      → Quick health check (confirms server is running)
  POST /api/run      → Triggers the full LangGraph agent pipeline

HOW TO RUN:
  uv run uvicorn agent.main:app --reload

  --reload means the server restarts automatically when you save a file.
  Perfect for development.
"""

from dotenv import load_dotenv
load_dotenv()  # Must be before any other imports that read env vars

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent.graph.graph import graph
from agent.graph.state import HaddockState
from agent.observability.langfuse_handler import get_langfuse_callback

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Haddock-Flow",
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


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/healthz", tags=["infra"])
async def health_check():
    """Returns 200 OK if the server is running. Used by monitoring tools."""
    return {"status": "ok", "service": "haddock-flow"}


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
    initial_state: HaddockState = {
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
