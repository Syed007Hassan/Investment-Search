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


def get_all_tools() -> list[Dict[str, Any]]:
    """
    Returns all available tool schemas. Extend this by appending new tool schemas
    to the list as new capabilities are added.
    """
    return [
        build_search_companies_tool_schema(),
    ]


