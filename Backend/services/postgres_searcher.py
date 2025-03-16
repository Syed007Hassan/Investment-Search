"""
PostgresSearcher is a class that searches for items in a PostgreSQL 
database using a hybrid search strategy.
"""

# pylint:disable=import-error,missing-function-docstring,missing-class-docstring,unsupported-binary-operation
from typing import Union
from sqlalchemy import Float, Integer, column, select, text
from sqlalchemy.orm import joinedload
import logging

from services.embedding import Embedding
from models.database import get_db_session

embedding_util = Embedding()
logger = logging.getLogger(__name__)


class PostgresSearcher:
    """
    A class that implements hybrid search functionality combining vector and full-text search in PostgreSQL.
    
    Attributes:
        embed_model (str): The embedding model name used for vector search
        db_model: The SQLAlchemy model class for the database table
        embed_dimensions (int): Dimensions of the embedding vector
    """

    embed_model: str = "multilingual-e5-large"

    def __init__(
        self,
        db_model,
        embed_dimensions: Union[int, None] = 1024,
    ):
        self.db_model = db_model
        self.embed_dimensions = embed_dimensions

    def build_filter_clause(self, filters) -> tuple[str, str]:
        """
        Builds SQL filter clauses from a list of filter dictionaries.
        
        Args:
            filters (list[dict]): List of filter specifications with keys:
                - column: The column name
                - comparison_operator: The SQL comparison operator
                - value: The value to compare against
            example:
                filters = [
                    {"column": "name", "comparison_operator": "=", "value": "Apple"}
                ]
        
        Returns:
            tuple[str, str]: A tuple containing:
                - WHERE clause string
                - AND clause string
        """
        if filters is None:
            return "", ""
        filter_clauses = []
        for filter in filters:
            if isinstance(filter["value"], str):
                filter["value"] = f"'{filter['value']}'"
            elif isinstance(filter["value"], list):
                comparison_operator = filter["comparison_operator"]
                if comparison_operator != "&&":
                    filter["value"] = (
                        "(" + ",".join([f"'{v}'" for v in filter["value"]]) + ")"
                    )
                else:
                    _vals = [f'"{v}"' for v in filter["value"]]
                    filter["value"] = "'{" + ",".join(_vals) + "}'"
            filter_clauses.append(
                f"{filter['column']} {filter['comparison_operator']} {filter['value']}"
            )
        filter_clause = " AND ".join(filter_clauses)
        if len(filter_clause) > 0:
            return f"WHERE {filter_clause}", f"AND {filter_clause}"
        return "", ""

    def search(
        self,
        query_text: Union[str, None],
        query_vector: Union[list[float], list],
        top: int = 5,
        filters: Union[list[dict], None] = None,
    ):
        """
        Performs hybrid search combining vector similarity and full-text search.
        
        Args:
            query_text (str | None): The text query for full-text search
            query_vector (list[float]): The embedding vector for similarity search
            top (int): Maximum number of results to return
            filters (list[dict] | None): Additional filters to apply
        
        Returns:
            list: List of matching database objects
            
        The search combines three possible approaches:
        1. Vector search: Uses cosine similarity with embeddings
        2. Full-text search: Uses PostgreSQL's ts_vector/ts_query
        3. Hybrid: Combines both approaches with a weighted score
        """
        filter_clause_where, filter_clause_and = self.build_filter_clause(filters)

        table_name = self.db_model.__tablename__
        embedding_field_name = self.db_model.get_embedding_field()
        search_text_field_name = self.db_model.get_text_search_field()

        vector_query = f"""
            SELECT id, RANK () OVER (ORDER BY {embedding_field_name} <=> :embedding) AS rank
                FROM "{table_name}"
                {filter_clause_where}
                ORDER BY {embedding_field_name} <=> :embedding
                LIMIT 20
            """

        fulltext_query = f"""
            SELECT id, RANK () OVER (ORDER BY ts_rank_cd(to_tsvector('english', {search_text_field_name}), query) DESC)
                FROM "{table_name}", plainto_tsquery('english', :query) query
                WHERE to_tsvector('english', {search_text_field_name}) @@ query {filter_clause_and}
                ORDER BY ts_rank_cd(to_tsvector('english', {search_text_field_name}), query) DESC
                LIMIT 20
            """

        hybrid_query = f"""
        WITH vector_search AS (
            {vector_query}
        ),
        fulltext_search AS (
            {fulltext_query}
        )
        SELECT
            COALESCE(vector_search.id, fulltext_search.id) AS id,
            COALESCE(1.0 / (:k + vector_search.rank), 0.0) +
            COALESCE(1.0 / (:k + fulltext_search.rank), 0.0) AS score
        FROM vector_search
        FULL OUTER JOIN fulltext_search ON vector_search.id = fulltext_search.id
        ORDER BY score DESC
        LIMIT 20
        """

        if query_text is not None and len(query_vector) > 0:
            print("hybrid_query", hybrid_query)
            sql = text(hybrid_query).columns(
                column("id", Integer), column("score", Float)
            )
        elif len(query_vector) > 0:
            print("vector_query", vector_query)
            sql = text(vector_query).columns(
                column("id", Integer), column("rank", Integer)
            )
        elif query_text is not None:
            print("fulltext_query", fulltext_query)
            sql = text(fulltext_query).columns(
                column("id", Integer), column("rank", Integer)
            )
        else:
            raise ValueError("Both query text and query vector are empty")

        results = []
        with get_db_session() as db_session:
            results = (
                db_session.execute(
                    sql,
                    {"embedding": str(query_vector), "query": query_text, "k": 60},
                )
            ).fetchall()

        # Convert results to models
        items = []
        for id, _ in results[:top]:
            with get_db_session() as db_session:
                if table_name == "menu_item":
                    item = db_session.execute(
                        select(self.db_model)
                        .where(self.db_model.id == id)
                        .options(joinedload(self.db_model.options))
                    )
                else:
                    item = db_session.execute(
                        select(self.db_model).where(self.db_model.id == id)
                    )
                items.append(item.scalar())
        return items

    def search_and_embed(
        self,
        query_text: Union[str, None] = None,
        top: int = 5,
        enable_vector_search: bool = True,
        enable_text_search: bool = True,
        filters: Union[list[dict], None] = None,
    ):
        """
        High-level search function that handles embedding generation and search execution.
        
        Args:
            query_text (str | None): The search query text
            top (int): Maximum number of results to return
            enable_vector_search (bool): Whether to use vector similarity search
            enable_text_search (bool): Whether to use full-text search
            filters (list[dict] | None): Additional filters to apply
            
        Returns:
            list: List of matching database objects
            
        This method automatically generates embeddings if vector search is enabled
        and provides a simplified interface to the search functionality.
        """
        vector: list[float] = []
        if enable_vector_search and query_text is not None:
            try:
                # Try using Pinecone embeddings first
                logger.info(f"Generating Pinecone embedding for search query: {query_text}")
                vector = embedding_util.generate_pinecone(
                    query_text,
                    self.embed_dimensions,
                )
                logger.info("Successfully generated Pinecone embedding for search query")
            except Exception as e:
                logger.error(f"Error generating Pinecone embedding: {e}")
                # Fallback to OpenAI if Pinecone fails
                logger.info(f"Falling back to OpenAI embedding for search query")
                try:
                    vector = embedding_util.generate(
                        query_text,
                        self.embed_dimensions,
                    )
                except Exception as openai_error:
                    logger.error(f"Error generating OpenAI embedding: {openai_error}")
                    # If both fail, continue with text search only
                    vector = []
                    
        if not enable_text_search:
            query_text = None

        return self.search(query_text, vector, top, filters)
