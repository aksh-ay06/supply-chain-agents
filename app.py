"""CLI entrypoint for Supply Chain Intelligence Agents."""
import argparse
import sys
from langchain_core.messages import HumanMessage


def main():
    parser = argparse.ArgumentParser(
        description="Supply Chain Intelligence Agents - Multi-agent system for supply chain analysis"
    )
    parser.add_argument("query", nargs="?", help="Query to analyze (or use --interactive for chat mode)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive chat mode")
    args = parser.parse_args()

    from src.graph import build_workflow
    graph = build_workflow()

    if args.interactive:
        print("Supply Chain Intelligence Agents")
        print("Type 'quit' to exit.\n")
        while True:
            try:
                query = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            if query.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if not query:
                continue
            result = graph.invoke({
                "messages": [HumanMessage(content=query)],
                "next_agents": [],
                "agent_outputs": {},
                "final_report": "",
                "guardrail_blocked": False,
            })
            print(f"\n{result['final_report']}\n")
    elif args.query:
        result = graph.invoke({
            "messages": [HumanMessage(content=args.query)],
            "next_agents": [],
            "agent_outputs": {},
            "final_report": "",
        })
        print(result["final_report"])
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
