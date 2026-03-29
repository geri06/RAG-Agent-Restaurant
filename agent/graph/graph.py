"""
LangGraph Graph Definition — agent/graph/graph.py

HOW LANGGRAPH WORKS:
  LangGraph is a framework for building "agent graphs" — flows where
  each step (node) can be a Python function or an LLM call.

  It differs from a simple pipeline because:
  - Nodes can be conditional (take different paths based on state)
  - It has built-in support for loops (agents that retry or refine)
  - State is automatically checkpointed (resumable after failures)

THIS GRAPH:
  A simple linear chain: analyst → rag → writer → notifier
  Each node reads from state and writes back to state.

  analyst_node → rag_node → writer_node → notifier_node
       ↑                                        ↓
      START                                    END
"""

from langgraph.graph import StateGraph, START, END

from agent.graph.state import HaddockState
from agent.graph.nodes.analyst import analyst_node
from agent.graph.nodes.rag import rag_node
from agent.graph.nodes.writer import writer_node
from agent.graph.nodes.notifier import notifier_node


def build_graph():
    """
    Constructs and compiles the LangGraph agent graph.

    Returns
    -------
    CompiledGraph
        A compiled, runnable graph object.
    """
    # 1. Create the graph builder, specifying the state type
    builder = StateGraph(HaddockState)

    # 2. Add all nodes (name → function mapping)
    builder.add_node("analyst", analyst_node)
    builder.add_node("rag", rag_node)
    builder.add_node("writer", writer_node)
    builder.add_node("notifier", notifier_node)

    # 3. Define the edges (the flow between nodes)
    #    START is a special built-in node that represents the entry point
    builder.add_edge(START, "analyst")
    builder.add_edge("analyst", "rag")
    builder.add_edge("rag", "writer")
    builder.add_edge("writer", "notifier")
    builder.add_edge("notifier", END)

    # 4. Compile: validates the graph and returns a runnable object
    return builder.compile()


# Build the graph once at import time (reused across all API requests)
graph = build_graph()
