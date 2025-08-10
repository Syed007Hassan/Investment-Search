"""
    This file loads the data from sample_products.json
    and inserts it into the database.
"""

import json
import sys
import logging
sys.path.append(".")

from models.company import Company
from models.database import get_db_session
from services.embedding import Embedding
from services.chat import ChatService

embedding_service = Embedding()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def load_data():
    """
    This function is used to load the data from sample_products.json
    and insert it into the database.
    """
    with open("scripts/sample_companies.json", "r") as f: #pylint: disable=unspecified-encoding
        data = json.load(f)
        data = data["companies"]
    with get_db_session() as session:
        for item in data:
            company = Company(**item)
            company.content = company.to_str()
            
            try:
                logger.info(f"Generating Pinecone embedding for company: {company.name}")
                company.embedding = embedding_service.generate_pinecone(company.content, 1024)
                logger.info(f"Successfully generated Pinecone embedding for company: {company.name}")
            except Exception as e:
                logger.error(f"Error generating Pinecone embedding: {e}")
                logger.error(f"Skipping company: {company.name} due to embedding generation failure")
                continue
                
            session.add(company)
        session.commit()
        
        # No Qdrant sync; using PostgreSQL only


if __name__ == "__main__":
    load_data()
