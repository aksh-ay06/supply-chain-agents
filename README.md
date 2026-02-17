# Supply Chain Intelligence Agents (SCIA)

A multi-agent AI system for CPG supply chain analysis, built with **LangChain** and **LangGraph**.

Three specialist agents — Demand Analyst, Inventory Monitor, and Supplier Analyst — are orchestrated by a supervisor that routes queries, delegates to the right agents, and synthesizes findings into actionable reports.

## Architecture

```
User Query → Coordinator (Router) → [Demand Analyst | Inventory Monitor | Supplier Analyst] → Synthesizer → Report
```

See [architecture.md](architecture.md) for detailed diagrams and design decisions.

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) installed and running

### Setup

```bash
# Clone and install
git clone <repo-url>
cd supply-chain-agents
pip install -e .

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

## Example Queries

| Query | Agents Invoked |
|-------|---------------|
| "What products are at risk of stockout?" | Inventory Monitor |
| "Analyze demand trends for product P001" | Demand Analyst |
| "How are our suppliers performing?" | Supplier Analyst |
| "Give me a full supply chain report" | All three agents |

## Project Structure

```
├── app.py                    # CLI entrypoint
├── streamlit_app.py          # Streamlit chat UI
├── src/
│   ├── config.py             # LLM provider config (Ollama/OpenAI/Anthropic)
│   ├── models.py             # Pydantic domain models
│   ├── agents/               # Specialist agents (demand, inventory, supplier)
│   ├── tools/                # LangChain tools (data, forecasting, search, reports)
│   ├── graph/                # LangGraph workflow (state, supervisor, routing)
│   └── observability/        # Callback handlers for tracing
├── data/
│   └── sample_data.csv       # Synthetic CPG supply chain dataset
├── Dockerfile
├── docker-compose.yml
└── architecture.md           # Detailed architecture docs
```

## LLM Provider Configuration

Set `LLM_PROVIDER` in `.env`:

| Provider | Value | Model Env Var |
|----------|-------|--------------|
| Ollama (default) | `ollama` | `OLLAMA_MODEL` |
| OpenAI | `openai` | `OPENAI_MODEL` |
| Anthropic | `anthropic` | `ANTHROPIC_MODEL` |

## Tech Stack

- **LangChain** — Agent framework, tool definitions, chat models
- **LangGraph** — Multi-agent orchestration with supervisor pattern
- **Ollama** — Local LLM inference
- **Pandas** — Data analysis
- **Streamlit** — Web UI
- **Pydantic** — Data validation
- **Docker** — Containerized deployment
