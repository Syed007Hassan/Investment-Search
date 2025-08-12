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
from serpapi import GoogleSearch
from urllib.parse import urlparse
from models.database import get_db_session

logger = logging.getLogger(__name__)

 


class ChatService:
    """
    This class is responsible for generating responses for the chatbot.
    """

    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "openai/gpt-oss-20b"
        # Always use PostgreSQL searcher
        logger.info("Using PostgreSQL as vector database for search")
        self.searcher = PostgresSearcher(Company)
        self.serp_api_key = config.SERP_API_KEY
        try:
            if self.serp_api_key:
                # Configure global key to avoid param mismatch issues
                GoogleSearch.SERP_API_KEY = self.serp_api_key
                logger.info("Configured SerpApi global key")
        except Exception as _:
            pass

    def search_companies(self, search_query: str):
        """
        This function is used to search companies based on the search_query.
        Works with PostgreSQL searcher.
        """
        company_recommendations = []
        try:
            logger.info(f"Searching companies with query: {search_query} using PostgreSQL")
            response: list[Company] = self.searcher.search_and_embed(search_query)
            # Deduplicate by id while preserving order
            seen_ids: set[int] = set()
            unique_response: list[Company] = []
            for c in response:
                if c.id not in seen_ids:
                    seen_ids.add(c.id)
                    unique_response.append(c)
            company_recommendations.extend(unique_response)
            
            if not response:
                return "No companies found for the given search query.", []
            
            # Create response text from company content
            response_text = "\n".join([
                company.content if company.content else company.to_str()
                for company in company_recommendations
            ])
            
            return (
                "Retrieved the following companies based on your search query (using PostgreSQL):\n"
                f"{response_text}"
            ), company_recommendations
            
        except Exception as e:
            logger.error(f"Error searching companies with PostgreSQL: {e}")
            return f"Error searching companies: {str(e)}", []

    def web_search_companies(self, search_query: str):
        """
        Use SerpApi Google search to discover likely company entities for a given query.
        Filters organic results to entries that look like company pages and maps them
        into lightweight Company-like dicts (without DB persistence).
        """
        try:
            if not self.serp_api_key:
                raise ValueError("SERP_API_KEY is not configured")

            def run_query(q: str) -> list[dict]:
                search = GoogleSearch({
                    "q": q,
                    "num": 10,
                    "hl": "en",
                    # passing key explicitly as well as global setting above
                    "api_key": self.serp_api_key,
                })
                data = search.get_dict()
                if isinstance(data, dict) and data.get("error"):
                    logger.error("SerpApi error for query '%s': %s", q, data.get("error"))
                    return []
                meta = data.get("search_metadata", {})
                logger.info(
                    "SerpApi meta: status=%s id=%s total_time=%s",
                    meta.get("status"), meta.get("id"), meta.get("total_time")
                )
                return data.get("organic_results", []) or []

            organic = run_query(search_query)

            # Relaxed company detection with domain allow/deny and title cleanup
            deny_hosts = {
                "wikipedia.org", "forbes.com", "bloomberg.com", "nytimes.com", "reuters.com",
                "theguardian.com", "techcrunch.com", "medium.com", "reddit.com", "youtube.com",
                "glassdoor.com", "indeed.com"
            }
            allow_hosts_extra = {"linkedin.com", "crunchbase.com"}

            def looks_like_company(title: str, link: str) -> bool:
                try:
                    host = urlparse(link).hostname or ""
                except Exception:
                    host = ""
                host = host.lower()
                # Allow company domains and certain directories
                if any(h in host for h in allow_hosts_extra):
                    return True
                if host and not any(h in host for h in deny_hosts):
                    # Likely corporate domain
                    return True
                # Fallback on title cues
                lowered = title.lower()
                if any(k in lowered for k in ["inc", "ltd", "llc", "gmbh", "corporation", "corp", "company"]):
                    return True
                return False

            def clean_name(title: str) -> str:
                base = title.split("|")[0].split(" – ")[0].split(" - ")[0]
                return base.replace("Official Site", "").replace("Homepage", "").strip()

            companies: list[Company] = []
            for item in organic:
                title = (item.get("title") or "").strip()
                snippet = (item.get("snippet") or item.get("about_this_result", {}).get("source", {}).get("description") or "").strip()
                link = (item.get("link") or "").strip()
                if not title or not link:
                    continue
                if not looks_like_company(title, link):
                    continue

                name_probe = clean_name(title)

                # Try to resolve to DB company by name substring match
                matched_db_company: Company | None = None
                with get_db_session() as session:
                    candidate = (
                        session.query(Company)
                        .filter(Company.name.ilike(f"%{name_probe}%"))
                        .first()
                    )
                    if candidate:
                        matched_db_company = candidate

                if matched_db_company:
                    companies.append(matched_db_company)
                else:
                    c = Company(
                        name=name_probe[:255],
                        description=(snippet or "Web discovered company"),
                        industry="",
                        size="",
                        location="",
                        content=f"Company: {name_probe}\nDescription: {snippet}\nWebsite: {link}",
                        embedding=[],
                    )
                    companies.append(c)

            # If nothing found, try a site-restricted follow-up query targeting likely company pages
            if not companies:
                alt_q = f"{search_query} site:linkedin.com/company OR site:crunchbase.com"
                for item in run_query(alt_q):
                    title = (item.get("title") or "").strip()
                    snippet = (item.get("snippet") or "").strip()
                    link = (item.get("link") or "").strip()
                    if not title or not link:
                        continue
                    name_probe = clean_name(title)
                    matched_db_company: Company | None = None
                    with get_db_session() as session:
                        candidate = (
                            session.query(Company)
                            .filter(Company.name.ilike(f"%{name_probe}%"))
                            .first()
                        )
                        if candidate:
                            matched_db_company = candidate
                    if matched_db_company:
                        companies.append(matched_db_company)
                    else:
                        c = Company(
                            name=name_probe[:255],
                            description=(snippet or "Web discovered company"),
                            industry="",
                            size="",
                            location="",
                            content=f"Company: {name_probe}\nDescription: {snippet}\nWebsite: {link}",
                            embedding=[],
                        )
                        companies.append(c)

            if not companies:
                return "No companies found on the web for the given search query.", []

            response_text = "\n".join([c.content if c.content else c.to_str() for c in companies])
            # Only return DB-resolved companies to the UI (have ids)
            ui_companies = [c for c in companies if getattr(c, "id", None)]
            return (
                "Retrieved the following companies based on your search query (using Web Search):\n"
                f"{response_text}"
            ), ui_companies
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error searching companies on the web: {e}")
            return f"Error searching companies on the web: {str(e)}", []

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

    def generate_response(self, user_query, web_search: bool = False):
        """
        This function is used to generate response for the user query.
        """
        messages = [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": user_query},
        ]
        company_recommendations = []
        while True:
            # Decide and log which tools are exposed to the model
            web_enabled = bool(web_search) and bool(self.serp_api_key)
            tools_for_call = get_all_tools(web_search_enabled=web_enabled)
            tool_names = [t.get("function", {}).get("name") for t in tools_for_call]
            if web_search and not self.serp_api_key:
                logger.warning(
                    "web_search requested but SERP_API_KEY missing; exposing tools=%s",
                    tool_names,
                )
            else:
                logger.info(
                    "Exposing tools to model (web_search=%s, serp_key=%s): %s",
                    bool(web_search), bool(self.serp_api_key), tool_names,
                )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tool_choice="auto",
                tools=tools_for_call,
                max_tokens=4096,
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
                    if tool_name == "web_search_companies":
                        tool_result, company_recommendations = self.web_search_companies(**tool_args)
                    else:
                        tool_result, company_recommendations = self.search_companies(**tool_args)
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
