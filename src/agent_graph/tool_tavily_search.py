from langchain_community.tools.tavily_search import TavilySearchResults
from agent_graph.load_tools_config import LoadToolsConfig
from langchain_core.tools import tool

TOOLS_CFG = LoadToolsConfig()

def load_tavily_search_tool(tavily_search_max_results: int):
    """
    Initialize the Tavily search tool with a configurable number of maximum search results.

    Args:
        tavily_search_max_results (int): Maximum number of search results to return for each query.

    Returns:
        TavilySearchResults: Instance of the Tavily search tool.
    """
    return TavilySearchResults(max_results=tavily_search_max_results)

tavily_search = load_tavily_search_tool(TOOLS_CFG.tavily_search_max_results)

@tool
def search_tool(query: str) -> str:
    """
    Search the web using Tavily based on the given query and return a formatted string of results.

    Args:
        query (str): The user's search query.

    Returns:
        str: Formatted search results (title, URL, content) or raw string if not in list format.
    """
    results = tavily_search.invoke(query)
    # Optionally, format the results as a string for LLM consumption
    if isinstance(results, list):
        return "\n\n".join(
            f"{item.get('title', '')}\n{item.get('url', '')}\n{item.get('content', '')}"
            for item in results
        )
    return str(results)