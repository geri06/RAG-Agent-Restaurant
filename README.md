# Company-Flow 🌊
> **Internal Ops Intelligence Agent** for Company Customer Success & Sales teams.

**Company-Flow** is an autonomous multi-agent system built to scan operational metrics, cross-reference them with the company's internal strategy manual, and autonomously draft data-driven outreach emails to customers before they even realize they have a problem.

---

## 🏗️ Architecture

Company-Flow consists of two main parts:

### 1. The Multi-Agent Backend (Python/FastAPI)
Built using `LangGraph` and `Langchain`, it triggers a cyclic workflow of specific AI agents:
1. **Analyst Node (SQL)**: Executes real-time SQL queries against the Supabase database to detect sudden spikes in ingredient costs for restaurants.
2. **RAG Node (Vector Search)**: Takes the triggered anomalies and queries a local `pgvector` store containing the `strategy_manual.md` for specific guidance.
3. **Writer Node (Llama 3 via Groq)**: Reads both the SQL alerts and the strategy context, and drafts a highly personalized, empathetic outreach email in Spanish.
4. **Notifier Node (Slack/HubSpot)**: Fires an alert to the internal Sales team so they can review the draft.

### 2. The Ops Dashboard (Next.js)
A fully custom, dark-mode GUI for the Customer Success team to trigger the backend agents, view anomalies in a cleanly designed grid, and copy the generated emails. 

*No Tailwind used. Engineered strictly with vanilla CSS Modules for maximum aesthetic control and performance.*

---

## 🚀 Quick Start Guide

### Step 1. Prerequisites
You will need the following installed:
1. **`uv`** (Python package manager)
2. **`npm`** (Node.js)
3. API Keys for **Supabase**, **Groq**, and **Langfuse**.

### Step 2. Environment Setup
Create a `.env` file in the root of the project with the following configuration:
```env
# 1. Groq (Free fast Llama-3 inference)
GROQ_API_KEY="your_groq_key"

# 2. Supabase (The connection string must be the Session Pooler URL, resolving to IPv4)
# Example: postgresql+asyncpg://postgres.xyz:[PASSWORD]@aws-0-eu-west-3.pooler.supabase.com:5432/postgres
DATABASE_URL="your_supabase_pooler_url"

# 3. Langfuse (For tracing and observability of the LLM agents)
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_HOST="https://cloud.langfuse.com"
```

### Step 3. Initialize the Database
Company-Flow uses Supabase & `pgvector`. Seed the mock operations database by running:
```bash
uv run python scripts/seed_db.py
```
*(This sets up a fictional "Restaurante Paco" with normal weekly operating costs).*

### Step 4. Index the Knowledge Base
The RAG system requires the company strategy manual to be chunked, embedded, and saved to the vector database:
```bash
uv run python -m agent.rag.loader
```

### Step 5. Simulate a Market Spike (The "Anomaly")
To give the agents something to actually detect, simulate a sudden 50%+ spike in the price of Olive Oil and Tomatoes for our test restaurant:
```bash
uv run python scripts/add_invoice_spike.py
```

### Step 6. Run the Application
You will need two terminal windows to run both the FastAPI Backend and Next.js Frontend.

**Terminal 1 (Backend - FastAPI):**
```bash
# Starts the agent server on http://localhost:8000
uv run uvicorn agent.main:app --reload
```

**Terminal 2 (Frontend - Next.js):**
```bash
# Enter the frontend directory and start the UI on http://localhost:3000
cd dashboard
npm install
npm run dev
```

### Step 7. Trigger the Agents
1. Open your browser and navigate to **[http://localhost:3000](http://localhost:3000)**
2. Click **"Run Intelligence Agent 🤖"**
3. The dashboard will trigger the Python backend, which will spin up the graph, query the SQL DB, pull embedded data from pgvector, draft an email via Llama-3, and return the data directly to your beautiful UI.
4. Watch the underlying "thinking" process rendered securely on your **Langfuse** cloud dashboard!
