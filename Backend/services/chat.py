"""
    This contains the ChatService
"""

import logging
import json
from groq import Groq

from services.postgres_searcher import PostgresSearcher
from config.main import config
from models.company import Company
from util.prompt import PROMPT
from util.tool import get_all_tools

logger = logging.getLogger(__name__)

 


class ChatService:
    """
    This class is responsible for generating responses for the chatbot.
    """

    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        # Always use PostgreSQL searcher
        logger.info("Using PostgreSQL as vector database for search")
        self.searcher = PostgresSearcher(Company)

    def search_companies(self, search_query: str):
        """
        This function is used to search companies based on the search_query.
        Works with PostgreSQL searcher.
        """
        company_recommendations = []
        try:
            logger.info(f"Searching companies with query: {search_query} using PostgreSQL")
            response: list[Company] = self.searcher.search_and_embed(search_query)
            company_recommendations.extend(response)
            
            if not response:
                return "No companies found for the given search query.", []
            
            # Create response text from company content
            response_text = "\n".join([
                company.content if company.content else company.to_str() 
                for company in response
            ])
            
            return (
                "Retrieved the following companies based on your search query (using PostgreSQL):\n"
                f"{response_text}"
            ), company_recommendations
            
        except Exception as e:
            logger.error(f"Error searching companies with PostgreSQL: {e}")
            return f"Error searching companies: {str(e)}", []

    def search_tool_definition(self):
        """
        This function is used to get the definition of the search tool.
        """
        # Use centralized tool registry so future tools are auto-included
        # while preserving current single-tool behavior for compatibility.
        # Consumers of this method expect a single tool schema, so default to the
        # first one for backward compatibility.
        tools = get_all_tools()
        return tools[0] if tools else {}

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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tool_choice="auto",
                tools=get_all_tools(),
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
