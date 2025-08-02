"""
QdrantSearcher provides vector search functionality using Qdrant vector database.
Simple implementation for RAG use case.
"""

import logging
from typing import List, Optional, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from services.embedding import Embedding
from config.main import config
from models.company import Company

embedding_util = Embedding()
logger = logging.getLogger(__name__)


class QdrantSearcher:
    """
    Simple Qdrant searcher for RAG vector search functionality.
    """

    def __init__(self, db_model, embed_dimensions: int = 1024):
        self.db_model = db_model
        self.embed_dimensions = embed_dimensions
        self.collection_name = config.QDRANT_COLLECTION_NAME
        
        # Initialize client
        logger.info(f"Initializing Qdrant client with URL: {config.QDRANT_URL}")
        if config.QDRANT_API_KEY:
            logger.info("Using Qdrant with API key (cloud mode)")
            self.client = QdrantClient(
                url=config.QDRANT_URL,
                api_key=config.QDRANT_API_KEY,
            )
        else:
            logger.info("Using Qdrant without API key (local mode)")
            self.client = QdrantClient(url=config.QDRANT_URL)
        
        # Ensure collection exists
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections()
            if not any(col.name == self.collection_name for col in collections.collections):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embed_dimensions,
                        distance=Distance.COSINE
                    ),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection '{self.collection_name}' already exists")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            logger.error(f"Check your Qdrant configuration - URL: {config.QDRANT_URL}")
            logger.error(f"Make sure your QDRANT_URL and QDRANT_API_KEY are correctly set in .env file")
            raise
    
    def upsert_company(self, company: Company) -> bool:
        """Store company in Qdrant."""
        try:
            if company.embedding is None or len(company.embedding) == 0:
                return False
            
            point = PointStruct(
                id=company.id,
                vector=company.embedding,
                payload={
                    "name": company.name,
                    "description": company.description,
                    "industry": company.industry,
                    "size": company.size,
                    "location": company.location,
                    "content": company.content
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return True
            
        except Exception as e:
            logger.error(f"Error upserting company to Qdrant: {e}")
            return False
    
    def search_and_embed(self, query_text: str, top: int = 5) -> List[Company]:
        """
        Search for companies using text query.
        
        Args:
            query_text: Search query
            top: Number of results to return
            
        Returns:
            List of Company objects
        """
        try:
            # Generate embedding
            try:
                query_vector = embedding_util.generate_pinecone(query_text, self.embed_dimensions)
            except Exception:
                query_vector = embedding_util.generate(query_text, self.embed_dimensions)
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top,
                with_payload=True
            )
            
            # Convert to Company objects
            companies = []
            for result in search_results:
                payload = result.payload
                company = Company(
                    id=result.id,
                    name=payload.get("name"),
                    description=payload.get("description"),
                    industry=payload.get("industry"),
                    size=payload.get("size"),
                    location=payload.get("location"),
                    content=payload.get("content")
                )
                companies.append(company)
            
            return companies
            
        except Exception as e:
            logger.error(f"Error in Qdrant search: {e}")
            return []