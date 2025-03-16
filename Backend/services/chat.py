"""
    This contains the ChatService
"""

import logging
import json
from groq import Groq
from openai import OpenAI

from services.postgres_searcher import PostgresSearcher
from config.main import config
from models.company import Company

logger = logging.getLogger(__name__)

PROMPT = """
You are a company search assistant.
You provide an overview of the companies found based on the search query.
You just tell about the companies names that are only relevant to the search query, ranks them in order of relevance to the search query.
You must use tool `search_companies` to search for companies based on the search query.

- Always output well formatted markdown text.
- Use the `search_companies` tool to search for companies based on the search query.
- Keep your answers concise and to the point.
- Your answer must always show a two liner summary of all the companies found.
"""


class ChatService:
    """
    This class is responsible for generating responses for the chatbot.
    """

    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        self.openai_model = "gpt-4o-2024-08-06"
        self.searcher = PostgresSearcher(Company)
        self.open_source = True

    def search_companies(self, search_query: str):
        """
        This function is used to search companies based on the search_query.
        """
        company_recommendations = []
        try:
            logger.info(f"Searching companies with query: {search_query}")
            response: list[Company] = self.searcher.search_and_embed(search_query)
            company_recommendations.extend(response)
            if not response:
                return "No companies found for the given search query.", []
            response_text = "\n".join([i.content for i in response])
            
            return (
                "Retrieved the following companies based on your search query:\n"
                f"{response_text}"
            ), company_recommendations
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return f"Error searching companies: {str(e)}", []

    def search_tool_definition(self):
        """
        This function is used to get the definition of the search tool.
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

    def generate_response(self, user_query):
        """
        This function is used to generate response for the user query.
        """
        messages = [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": user_query},
        ]
        company_recommendations = []
        while True:
            if self.open_source:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tool_choice="auto",
                    tools=[self.search_tool_definition()],
                )
            else:
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=messages,
                    tool_choice="auto",
                    tools=[self.search_tool_definition()],
                )
            response_message = response.choices[0].message

            if response_message.tool_calls:
                tool_calls = response_message.tool_calls
                messages.append(
                    {
                        "role": "assistant",
                        "tool_calls": [
                            tool_call.model_dump() for tool_call in tool_calls
                        ],
                    }
                )
                tools_names = [tool_call.function.name for tool_call in tool_calls]
                logger.info("Tools used: %s", tools_names)
                tool_call = tool_calls[0]
                try:
                    logger.info("Calling tool: %s", tool_call.function.name)
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    logger.info("Tool arguments: %s", tool_args)
                    tool_result, company_recommendations = self.search_companies(
                        **tool_args
                    )
                except Exception as e:  # pylint: disable=broad-except
                    tool_result = str(e)

                logger.info("Tool result: %s", tool_result)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": tool_result,
                    }
                )
            else:
                break

        return response_message.content, company_recommendations
