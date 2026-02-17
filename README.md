# Supply Chain Intelligence Agents (SCIA)

A multi-agent AI system for CPG supply chain analysis, built with **LangChain** and **LangGraph**.

Three specialist agents — Demand Analyst, Inventory Monitor, and Supplier Analyst — are orchestrated by a supervisor that routes queries, delegates to the right agents, and synthesizes findings into actionable reports. Input and output guardrails ensure safe, on-topic interactions.

## Architecture

```
User Query → Input Guardrail → Coordinator (Router) → [Demand Analyst | Inventory Monitor | Supplier Analyst] → Synthesizer → Output Guardrail → Report
```

See [architecture.md](architecture.md) for detailed diagrams and design decisions.

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) installed and running (for local development)

### Setup

```bash
# Clone and install
git clone https://github.com/aksh-ay06/supply-chain-agents.git
cd supply-chain-agents
pip install -e .
# or using uv (then prefix commands with `uv run`)
uv sync

# Pull an LLM model
ollama pull llama3.1

# Copy env config
cp .env.example .env
```

### Run (CLI)

```bash
# Single query
python app.py "What products are at risk of stockout?"

# Interactive mode
python app.py --interactive
```

### Run (Streamlit UI)

```bash
streamlit run streamlit_app.py
```

### Run (Docker)

```bash
docker compose up --build
# Open http://localhost:8501
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app
3. Select the repo, branch `main`, and main file `streamlit_app.py`
4. Under **Advanced settings > Secrets**, add:
   ```toml
   LLM_PROVIDER = "groq"
   GROQ_API_KEY = "your-groq-api-key"
   ```
5. Get a free Groq API key at [console.groq.com](https://console.groq.com)

On Streamlit Cloud with Groq free tier, agents run **sequentially** with retry/backoff to stay within rate limits. Locally, agents run **in parallel** for faster execution.

## Example Queries

| Query | Agents Invoked |
|-------|---------------|
| "What products are at risk of stockout?" | Inventory Monitor |
| "Analyze demand trends for product P001" | Demand Analyst |
| "How are our suppliers performing?" | Supplier Analyst |
| "Give me a full supply chain report" | All three agents |

## Guardrails

The system includes both input and output guardrails integrated as nodes in the LangGraph workflow.

**Input guardrails** (run before any LLM call):
- Domain relevance — blocks off-topic queries (no LLM cost incurred)
- Prompt injection detection — regex patterns for common injection techniques
- Input length limit — rejects queries over 1000 characters

**Output guardrails** (run after synthesis):
- PII redaction — SSNs, credit card numbers, emails, API keys/credentials
- Hallucination flagging — detects hedging language and appends a warning
- Data disclaimer — appended to every response

## Project Structure

```
├── app.py                    # CLI entrypoint
├── streamlit_app.py          # Streamlit chat UI
├── src/
│   ├── config.py             # LLM provider config + environment detection
│   ├── models.py             # Pydantic domain models
│   ├── guardrails.py         # Input validation + output sanitization
│   ├── agents/               # Specialist agents (demand, inventory, supplier)
│   ├── tools/                # LangChain tools (data, forecasting, search, reports)
│   ├── graph/                # LangGraph workflow (state, supervisor, routing)
│   └── observability/        # Callback handlers for tracing
├── data/
│   └── sample_data.csv       # Synthetic CPG supply chain dataset
├── requirements.txt          # Pinned deps for Streamlit Cloud
├── Dockerfile
├── docker-compose.yml
└── architecture.md           # Detailed architecture docs
```

## LLM Provider Configuration

Set `LLM_PROVIDER` in `.env` (local) or Streamlit secrets (cloud):

| Provider | Value | Model Env Var | Notes |
|----------|-------|--------------|-------|
| Ollama (default) | `ollama` | `OLLAMA_MODEL` | Local inference, no API key needed |
| Groq | `groq` | `GROQ_MODEL` | Free tier available, ideal for demos |
| OpenAI | `openai` | `OPENAI_MODEL` | Paid API |
| Anthropic | `anthropic` | `ANTHROPIC_MODEL` | Paid API |

## Execution Modes

| Environment | Detection | Agent Execution | Rate Limit Handling |
|-------------|-----------|----------------|---------------------|
| Local development | Default | Parallel (fan-out) | None needed |
| Streamlit Cloud + Groq free tier | `/mount/src` exists + `LLM_PROVIDER=groq` | Sequential | Retry with exponential backoff |
| Streamlit Cloud + paid provider | `/mount/src` exists | Parallel (fan-out) | None needed |

## Tech Stack

- **LangChain** — Agent framework, tool definitions, chat models
- **LangGraph** — Multi-agent orchestration with supervisor pattern
- **Ollama / Groq / OpenAI / Anthropic** — Flexible LLM backend
- **Pandas** — Data analysis
- **Streamlit** — Web UI + cloud deployment
- **Pydantic** — Data validation
- **Docker** — Containerized deployment
