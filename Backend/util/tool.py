"""Tool schemas and helpers used by LLM tool-calling."""

from typing import Any, Dict


def build_search_companies_tool_schema() -> Dict[str, Any]:
    """
    Returns the JSON schema for the `search_companies` tool used by the chat assistant.
    Keeping this in a util helps reuse and testing.
    """
    return {
        "type": "function",
        "function": {
            "name": "search_companies",
            "description": "This function is used to search companies based on the search_query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": (
                            "The search query to search the companies.\n"
                            "eg: 'tech companies in San Francisco' or "
                            "'large manufacturing companies'"
                        ),
                    },
                },
                "required": ["search_query"],
            },
        },
    }
def build_web_search_companies_tool_schema() -> Dict[str, Any]:
    """JSON schema for `web_search_companies` tool using SerpApi-backed web search.
    Keeps signature parallel to `search_companies` for drop-in use.
    """
    return {
        "type": "function",
        "function": {
            "name": "web_search_companies",
            "description": (
                "Search the web for relevant companies using a search engine (SerpApi). "
                "Only return company-related results relevant to the user query (e.g., industry, location)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": (
                            "A concise domain-specific query to find companies (e.g., 'healthcare companies in Boston', 'AI startups in EU')."
                        ),
                    },
                },
                "required": ["search_query"],
            },
        },
    }



def get_all_tools(web_search_enabled: bool = False) -> list[Dict[str, Any]]:
    """
    Returns available tool schemas. If `web_search_enabled` is True, include
    the SerpApi-backed `web_search_companies` tool first so the assistant can
    prefer it when instructed by the prompt.
    """
    # If web search is enabled, expose ONLY the web tool to comply with policy
    if web_search_enabled:
        return [build_web_search_companies_tool_schema()]
    # Otherwise, expose the DB search tool
    return [build_search_companies_tool_schema()]


