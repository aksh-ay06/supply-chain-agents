# Architecture

## System Overview

Supply Chain Intelligence Agents (SCIA) is a multi-agent system built with LangGraph that analyzes CPG supply chain data using specialized AI agents.

## Agent Architecture

```mermaid
graph TD
    User[User Query] --> Router[Coordinator / Router]
    Router -->|demand queries| DA[Demand Analyst]
    Router -->|inventory queries| IM[Inventory Monitor]
    Router -->|supplier queries| SA[Supplier Analyst]
    DA --> Synth[Synthesizer]
    IM --> Synth
    SA --> Synth
    Synth --> Report[Final Report]

    subgraph Tools
        T1[query_sales_data]
        T2[forecast_demand]
        T3[get_latest_inventory]
        T4[calculate_days_of_supply]
        T5[get_supplier_summary]
        T6[web_search]
        T7[generate_report]
    end

    DA -.-> T1
    DA -.-> T2
    IM -.-> T3
    IM -.-> T4
    SA -.-> T5
    SA -.-> T6
```

## Design Pattern: Supervisor with Conditional Fan-Out

The system uses LangGraph's **supervisor pattern**:

1. **Router Node**: An LLM classifies the user query and selects which specialist agents to invoke
2. **Agent Nodes**: Each specialist runs as a ReAct agent with its own tool set
3. **Synthesizer Node**: Combines all agent outputs into a unified executive summary

This pattern allows:
- **Selective execution**: Only relevant agents run for each query
- **Parallel capability**: Independent agents can execute concurrently
- **Composability**: New agents can be added by defining tools + prompt + node

## LLM Provider Abstraction

```mermaid
graph LR
    Config[config.py] --> |LLM_PROVIDER env var| Factory[get_llm]
    Factory -->|ollama| Ollama[ChatOllama]
    Factory -->|openai| OpenAI[ChatOpenAI]
    Factory -->|anthropic| Anthropic[ChatAnthropic]
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant R as Router
    participant A as Agent(s)
    participant T as Tools
    participant S as Synthesizer

    U->>R: Natural language query
    R->>R: Classify → select agents
    R->>A: Dispatch to selected agents
    A->>T: Call tools (data, search, forecast)
    T-->>A: Tool results
    A-->>S: Agent analysis
    S->>S: Combine into executive summary
    S-->>U: Final report (markdown)
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Orchestration | LangGraph StateGraph | Type-safe state, conditional routing, built-in persistence support |
| Agent type | ReAct (create_react_agent) | Reasoning + acting loop, well-suited for tool-use tasks |
| Routing | LLM-based classification | Flexible, handles ambiguous queries, easy to extend |
| Data layer | Pandas + CSV | Simple for demo; swappable for database in production |
| LLM provider | Configurable via env | Supports local (Ollama) and cloud (OpenAI/Anthropic) |
