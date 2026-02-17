import time
import logging
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from src.graph.state import SupervisorState
from src.config import get_llm, IS_FREE_TIER
from src.agents import create_demand_analyst, create_inventory_monitor, create_supplier_analyst

logger = logging.getLogger("scia")

AGENT_NAMES = ["demand_analyst", "inventory_monitor", "supplier_analyst"]

ROUTER_PROMPT = """You are a supply chain coordinator. Given the user's query, decide which specialist agents to invoke.

Available agents:
- demand_analyst: Sales trends, demand forecasting, seasonal patterns
- inventory_monitor: Stock levels, stockout risks, reorder alerts
- supplier_analyst: Supplier performance, lead times, costs, market context

Respond with ONLY a comma-separated list of agent names to invoke (no explanation).
For broad queries, invoke all relevant agents. Examples:
- "What products are at risk?" -> inventory_monitor
- "Analyze demand for P001" -> demand_analyst
- "Full supply chain report" -> demand_analyst,inventory_monitor,supplier_analyst
- "How are our suppliers doing?" -> supplier_analyst"""


def _invoke_with_retry(fn, *args, max_retries=3, **kwargs):
    """Invoke with exponential backoff on rate limit errors. Only retries on free-tier APIs."""
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if IS_FREE_TIER and ("429" in str(e) or "rate_limit" in str(e).lower()):
                wait = 2 ** attempt * 30
                logger.warning(f"Rate limited, retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                raise
    return fn(*args, **kwargs)


def route_query(state: SupervisorState) -> dict:
    """Coordinator node: classify query and decide which agents to call."""
    llm = get_llm()
    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        state["messages"][-1],
    ]
    response = _invoke_with_retry(llm.invoke, messages)
    raw = response.content.strip().lower()
    selected = [name.strip() for name in raw.split(",") if name.strip() in AGENT_NAMES]
    if not selected:
        selected = AGENT_NAMES
    return {"next_agents": selected}


def _run_agent(state, create_fn, name):
    agent = create_fn()
    result = _invoke_with_retry(agent.invoke, {"messages": state["messages"]})
    last_msg = result["messages"][-1].content
    return {"agent_outputs": {name: last_msg}}


# --- Sequential execution (free-tier / Streamlit Cloud) ---

def run_agents_sequentially(state: SupervisorState) -> dict:
    """Run selected agents one at a time to stay within free-tier rate limits."""
    agent_map = {
        "demand_analyst": create_demand_analyst,
        "inventory_monitor": create_inventory_monitor,
        "supplier_analyst": create_supplier_analyst,
    }
    outputs = {}
    for name in state.get("next_agents", AGENT_NAMES):
        if name in agent_map:
            result = _run_agent(state, agent_map[name], name)
            outputs.update(result["agent_outputs"])
    return {"agent_outputs": outputs}


# --- Parallel execution (local development) ---

def run_demand_analyst(state: SupervisorState) -> dict:
    return _run_agent(state, create_demand_analyst, "demand_analyst")


def run_inventory_monitor(state: SupervisorState) -> dict:
    return _run_agent(state, create_inventory_monitor, "inventory_monitor")


def run_supplier_analyst(state: SupervisorState) -> dict:
    return _run_agent(state, create_supplier_analyst, "supplier_analyst")


def synthesize(state: SupervisorState) -> dict:
    """Combine agent outputs into a final report."""
    llm = get_llm()
    agent_results = "\n\n".join(
        f"## {name.replace('_', ' ').title()} Report\n{output}"
        for name, output in state["agent_outputs"].items()
    )
    messages = [
        SystemMessage(content=(
            "You are a supply chain coordinator. Synthesize the following specialist agent "
            "reports into a single, coherent executive summary. Highlight key findings, risks, "
            "and recommended actions. Use markdown formatting."
        )),
        HumanMessage(content=f"Original query: {state['messages'][0].content}\n\nAgent Reports:\n{agent_results}"),
    ]
    response = _invoke_with_retry(llm.invoke, messages)
    return {"final_report": response.content}


def build_workflow():
    workflow = StateGraph(SupervisorState)

    workflow.add_node("router", route_query)
    workflow.add_node("synthesizer", synthesize)

    if IS_FREE_TIER:
        # Sequential: router -> agents (one node) -> synthesizer
        workflow.add_node("agents", run_agents_sequentially)
        workflow.add_edge(START, "router")
        workflow.add_edge("router", "agents")
        workflow.add_edge("agents", "synthesizer")
    else:
        # Parallel: router -> fan-out to agent nodes -> synthesizer
        workflow.add_node("demand_analyst", run_demand_analyst)
        workflow.add_node("inventory_monitor", run_inventory_monitor)
        workflow.add_node("supplier_analyst", run_supplier_analyst)
        workflow.add_edge(START, "router")

        def route_to_agents(state: SupervisorState) -> list[str]:
            return state.get("next_agents", AGENT_NAMES)

        workflow.add_conditional_edges("router", route_to_agents, AGENT_NAMES)

        for agent_name in AGENT_NAMES:
            workflow.add_edge(agent_name, "synthesizer")

    workflow.add_edge("synthesizer", END)

    return workflow.compile()
