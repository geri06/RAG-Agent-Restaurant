"""
Langfuse Observability — agent/observability/langfuse_handler.py

WHAT IS LANGFUSE?
  Langfuse is an open-source LLM observability platform.
  Every time an LLM is called, Langfuse records:
  - The full prompt sent to the model
  - The model's response
  - How long it took
  - How many tokens were used (and the cost)
  - The full trace tree (which node called which LLM)

WHY IS THIS IMPORTANT?
  - You can debug why an agent gave a wrong answer
  - You can measure latency and cost per run
  - Company's JD explicitly mentions this as a "stand out" requirement

HOW TO USE:
  Import `get_langfuse_callback` and pass it as a callback to ainvoke():

  from agent.observability.langfuse_handler import get_langfuse_callback

  result = await graph.ainvoke(initial_state, config={
      "callbacks": [get_langfuse_callback()]
  })
"""

import os
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler

load_dotenv()


def get_langfuse_callback() -> CallbackHandler:
    """
    Creates a new Langfuse callback handler for a single agent run.

    Each call creates a fresh trace in Langfuse (visible in the dashboard).

    Returns
    -------
    CallbackHandler
        LangChain-compatible callback that sends traces to Langfuse.
    """
    # Langfuse automatically reads LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, 
    # and LANGFUSE_HOST from environment variables.
    return CallbackHandler()
