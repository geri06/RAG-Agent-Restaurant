"""
RAG Node — agent/graph/nodes/rag.py

ROLE: Librarian 📚
  Takes the alerts from the analyst and searches the strategy manual
  to find the best advice for the Customer Success team.

WHAT IS RAG?
  Retrieval-Augmented Generation = search a knowledge base for relevant
  documents, then feed those documents to the LLM as context.

  Without RAG: LLM only knows what it was trained on.
  With RAG:    LLM knows your company's specific playbook.

FLOW:
  1. Build a search query from the alerts (e.g. "rising tomato costs")
  2. Search the vector database for similar strategy advice
  3. Return the top matching chunks as context

WRITES TO STATE: strategy_advice (str)
"""

from agent.graph.state import HaddockState
from agent.rag.retriever import retrieve


async def rag_node(state: HaddockState) -> HaddockState:
    """
    LangGraph node: retrieves strategy advice from the knowledge base.

    Parameters
    ----------
    state : HaddockState
        Must contain `alerts` (populated by analyst_node).

    Returns
    -------
    HaddockState
        Updated state with `strategy_advice` populated.
    """
    print("\n📚 [rag_node] Searching strategy manual...")

    if not state["alerts"]:
        print("  No alerts — skipping RAG.")
        return {**state, "strategy_advice": ""}

    # Build a natural-language query from the alerts
    # Example: "Rising cost of Tomates for restaurant Restaurante Paco"
    alert_descriptions = [
        f"Rising cost of {a['ingredient']} for {a['restaurant_name']} "
        f"(+{a['pct_increase']}% over {a['weeks_observed']} weeks)"
        for a in state["alerts"]
    ]
    query = "How should the Customer Success team respond to: " + "; ".join(alert_descriptions)

    print(f"  Query: {query[:100]}...")

    # retrieve() does the actual vector similarity search
    advice_chunks = await retrieve(query, top_k=3)
    strategy_advice = "\n\n---\n\n".join(advice_chunks)

    print(f"  ✅ Retrieved {len(advice_chunks)} relevant strategy chunks.")
    return {**state, "strategy_advice": strategy_advice}
