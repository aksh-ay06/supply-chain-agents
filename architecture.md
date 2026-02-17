# Architecture

## System Overview

Supply Chain Intelligence Agents (SCIA) is a multi-agent system built with LangGraph that analyzes CPG supply chain data using specialized AI agents. It includes input/output guardrails and adapts its execution strategy based on the deployment environment.

## Full Pipeline

```mermaid
graph TD
    User[User Query] --> IG[Input Guardrail]
    IG -->|blocked| END1[Blocked Response]
    IG -->|passed| Router[Coordinator / Router]
    Router -->|demand queries| DA[Demand Analyst]
    Router -->|inventory queries| IM[Inventory Monitor]
    Router -->|supplier queries| SA[Supplier Analyst]
    DA --> Synth[Synthesizer]
    IM --> Synth
    SA --> Synth
    Synth --> OG[Output Guardrail]
    OG --> Report[Final Report]

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

## Guardrails

```mermaid
graph LR
    subgraph Input Guardrail
        A1[Length Check] --> A2[Prompt Injection Detection]
        A2 --> A3[Domain Relevance Check]
    end

    subgraph Output Guardrail
        B1[PII Redaction] --> B2[Hallucination Flagging]
        B2 --> B3[Disclaimer Append]
    end
```

**Input guardrails** run before any LLM call, saving cost on invalid queries:
- **Domain relevance**: Keyword-based check ensures queries relate to supply chain topics
- **Prompt injection**: Regex patterns detect common injection techniques (e.g., "ignore previous instructions")
- **Length limit**: Rejects queries over 1000 characters

**Output guardrails** sanitize agent responses before returning to the user:
- **PII redaction**: SSNs, credit card numbers, email addresses, API keys/credentials
- **Hallucination flagging**: Detects hedging language and appends a warning
- **Disclaimer**: Every response includes a note about sample data and AI-generated insights

## Design Pattern: Supervisor with Conditional Fan-Out

The system uses LangGraph's **supervisor pattern**:

1. **Input Guardrail Node**: Validates the query; blocks or passes through
2. **Router Node**: An LLM classifies the user query and selects which specialist agents to invoke
3. **Agent Nodes**: Each specialist runs as a ReAct agent with its own tool set
4. **Synthesizer Node**: Combines all agent outputs into a unified executive summary
5. **Output Guardrail Node**: Sanitizes and validates the final response

This pattern allows:
- **Selective execution**: Only relevant agents run for each query
- **Parallel capability**: Independent agents can execute concurrently (local mode)
- **Composability**: New agents can be added by defining tools + prompt + node
- **Safety**: Guardrails wrap the entire pipeline without modifying agent logic

## Execution Modes

The system adapts its execution strategy based on the deployment environment:

```mermaid
graph TD
    Start[build_workflow] --> Check{IS_FREE_TIER?}
    Check -->|Yes: Streamlit Cloud + Groq| Seq[Sequential Execution]
    Check -->|No: Local / Paid API| Par[Parallel Fan-Out]

    Seq --> S1[Router] --> S2[Agent 1] --> S3[Agent 2] --> S4[Agent 3] --> S5[Synthesizer]
    Par --> P1[Router] --> P2a[Agent 1] & P2b[Agent 2] & P2c[Agent 3] --> P3[Synthesizer]
```

| Environment | Agent Execution | Rate Limit Handling |
|-------------|----------------|---------------------|
| Local (Ollama) | Parallel fan-out | None needed |
| Streamlit Cloud + Groq free tier | Sequential with retry | Exponential backoff (30s, 60s, 120s) |
| Any environment + paid API | Parallel fan-out | None needed |

**Detection**: Streamlit Cloud is detected by the presence of `/mount/src`. Free tier is flagged when `IS_STREAMLIT_CLOUD` is true and `LLM_PROVIDER` is `groq`.

## LLM Provider Abstraction

```mermaid
graph LR
    Config[config.py] --> |LLM_PROVIDER env var| Factory[get_llm]
    Factory -->|ollama| Ollama[ChatOllama]
    Factory -->|openai| OpenAI[ChatOpenAI]
    Factory -->|anthropic| Anthropic[ChatAnthropic]
    Factory -->|groq| Groq[ChatGroq]
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant IG as Input Guardrail
    participant R as Router
    participant A as Agent(s)
    participant T as Tools
    participant S as Synthesizer
    participant OG as Output Guardrail

    U->>IG: Natural language query
    IG->>IG: Validate (length, injection, domain)
    alt Blocked
        IG-->>U: Rejection message
    else Passed
        IG->>R: Forward query
        R->>R: Classify → select agents
        R->>A: Dispatch to selected agents
        A->>T: Call tools (data, search, forecast)
        T-->>A: Tool results
        A-->>S: Agent analysis
        S->>S: Combine into executive summary
        S->>OG: Raw report
        OG->>OG: Redact PII, flag hallucinations, add disclaimer
        OG-->>U: Final report (markdown)
    end
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Orchestration | LangGraph StateGraph | Type-safe state, conditional routing, built-in persistence support |
| Agent type | ReAct (create_react_agent) | Reasoning + acting loop, well-suited for tool-use tasks |
| Routing | LLM-based classification | Flexible, handles ambiguous queries, easy to extend |
| Guardrails | Custom rule-based (no LLM) | Zero latency and cost for input validation; deterministic output sanitization |
| Execution mode | Environment-aware | Parallel locally for speed, sequential on free-tier cloud to respect rate limits |
| Data layer | Pandas + CSV | Simple for demo; swappable for database in production |
| LLM provider | Configurable via env | Supports local (Ollama), free cloud (Groq), and paid (OpenAI/Anthropic) |
