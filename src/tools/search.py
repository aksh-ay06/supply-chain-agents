from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for supply chain news, market trends, or supplier information.
    Returns top search results with titles, snippets, and URLs."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No search results found."
        formatted = []
        for r in results:
            formatted.append(f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Search failed: {e}"
