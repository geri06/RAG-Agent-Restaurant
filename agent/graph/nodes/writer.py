"""
Writer Node — agent/graph/nodes/writer.py

ROLE: Copywriter ✍️
  Uses the Groq LLM (Llama 3) to draft a personalised email
  for the Customer Success team to send to the restaurant.

WHY GROQ + LLAMA 3?
  Groq is a free API that runs Meta's Llama 3 model.
  Llama 3 is open-source (no proprietary lock-in).
  The API is structurally identical to OpenAI's — great for learning.

HOW THE PROMPT WORKS:
  We construct a "system + user" message pair:
  - system: defines the AI persona ("Fina", Haddock's internal assistant)
  - user:   provides the alert data + strategy advice as context

WRITES TO STATE: email_draft (str)
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from agent.graph.state import HaddockState

load_dotenv()

# Initialise the Groq LLM client
# temperature=0.3 → fairly focused, low creativity (we want professional emails)
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # Fast, free, 8-billion parameter open-source model
    temperature=0.1,
    api_key=os.environ["GROQ_API_KEY"],
)

SYSTEM_PROMPT = """
Eres "Fina", la asistente de IA interna de Haddock.
Tu rol es ayudar al equipo de Customer Success a redactar comunicaciones
claras, empáticas y orientadas a solución para los restaurantes clientes.
Escribe siempre en español profesional. Sé concisa y directa.
""".strip()


async def writer_node(state: HaddockState) -> HaddockState:
    """
    LangGraph node: uses Llama 3 via Groq to draft a client email.

    Parameters
    ----------
    state : HaddockState
        Must have `alerts` and `strategy_advice`.

    Returns
    -------
    HaddockState
        Updated state with `email_draft` populated.
    """
    print("\n✍️  [writer_node] Drafting email with Llama 3 via Groq...")

    if not state["alerts"]:
        return {**state, "email_draft": ""}

    # Format the alert data for the prompt
    alert_summary = "\n".join(
        f"- {a['restaurant_name']} ({a['contact_email']}): "
        f"{a['ingredient']} subió {a['pct_increase']}% en {a['weeks_observed']} semanas "
        f"(de {a['first_price']:.2f} €/kg a {a['last_price']:.2f} €/kg)"
        for a in state["alerts"]
    )

    user_message = f"""
Alertas detectadas:
{alert_summary}

Consejo estratégico de Haddock (basado en nuestro manual):
{state['strategy_advice']}

Redacta un email profesional para el equipo de Customer Success
que puedan enviar al restaurante. El email debe:
1. Reconocer la situación del restaurante con empatía
2. Proponer una reunión para revisar sus datos y optimizar costes
3. Ofrecer el valor específico de Haddock (visibilidad de precios de mercado)
4. Terminar con un call-to-action claro
""".strip()

    # Call the LLM — this is the actual AI generation
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]
    response = await llm.ainvoke(messages)
    email_draft = response.content

    print(f"  ✅ Email drafted ({len(email_draft)} chars).")
    return {**state, "email_draft": email_draft}
