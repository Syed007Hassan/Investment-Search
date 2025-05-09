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
                # Try using Pinecone embeddings first
                logger.info(f"Generating Pinecone embedding for company: {company.name}")
                company.embedding = embedding_service.generate_pinecone(company.content)
                logger.info(f"Successfully generated Pinecone embedding for company: {company.name}")
            except Exception as e:
                logger.error(f"Error generating Pinecone embedding: {e}")
                # Fallback to OpenAI if Pinecone fails
                logger.info(f"Falling back to OpenAI embedding for company: {company.name}")
                try:
                    company.embedding = embedding_service.generate(company.content)
                except Exception as openai_error:
                    logger.error(f"Error generating OpenAI embedding: {openai_error}")
                    logger.error(f"Skipping company: {company.name} due to embedding generation failure")
                    continue
                
            session.add(company)
        session.commit()


if __name__ == "__main__":
    load_data()
