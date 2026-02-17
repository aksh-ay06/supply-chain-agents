"""Streamlit UI for Supply Chain Intelligence Agents."""
import os
import streamlit as st
from langchain_core.messages import HumanMessage

# Load Streamlit secrets into env vars (for Streamlit Cloud deployment)
for key in ("LLM_PROVIDER", "GROQ_API_KEY", "GROQ_MODEL", "OPENAI_API_KEY", "OPENAI_MODEL",
            "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "OLLAMA_BASE_URL", "OLLAMA_MODEL"):
    if key in st.secrets:
        os.environ[key] = st.secrets[key]

st.set_page_config(page_title="Supply Chain Intelligence Agents", page_icon="📦", layout="wide")
st.title("Supply Chain Intelligence Agents")
st.caption("Multi-agent system for CPG supply chain analysis powered by LangGraph")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This system uses **3 specialist AI agents** orchestrated by a supervisor:

    - **Demand Analyst** — Sales trends & forecasting
    - **Inventory Monitor** — Stock levels & stockout risks
    - **Supplier Analyst** — Supplier performance & market context

    The coordinator routes your query to the right agents and synthesizes their findings.
    """)
    st.divider()
    st.markdown("**Example queries:**")
    st.code("What products are at risk of stockout?")
    st.code("Analyze demand trends for all products")
    st.code("Give me a full supply chain report")
    st.code("How are our suppliers performing?")

# Chat state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about your supply chain..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agents working..."):
            from src.graph import build_workflow
            graph = build_workflow()
            result = graph.invoke({
                "messages": [HumanMessage(content=prompt)],
                "next_agents": [],
                "agent_outputs": {},
                "final_report": "",
            })

            # Show agent trace in expander
            with st.expander("Agent Trace", expanded=False):
                for agent_name, output in result.get("agent_outputs", {}).items():
                    st.subheader(agent_name.replace("_", " ").title())
                    st.markdown(output)

            # Show final report
            st.markdown(result["final_report"])

    st.session_state.messages.append({"role": "assistant", "content": result["final_report"]})
