"""
    This script drops and recreates all database tables.
"""

import sys
import logging
from sqlalchemy import text
sys.path.append(".")

from models.database import engine, SessionLocal
from models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    """
    Drop all tables and recreate them.
    """
    # First, drop any existing tables
    logger.info("Dropping all tables...")
    
    # Drop the index if it exists
    with engine.connect() as connection:
        try:
            connection.execute(text("DROP INDEX IF EXISTS hnsw_index_for_innerproduct_company_embedding_ada002"))
            connection.commit()
            logger.info("Dropped index hnsw_index_for_innerproduct_company_embedding_ada002")
        except Exception as e:
            logger.error(f"Error dropping index: {e}")
    
    # Drop all tables
    Base.metadata.drop_all(engine)
    logger.info("Tables dropped successfully.")
    
    # Create all tables
    logger.info("Creating all tables...")
    Base.metadata.create_all(engine)
    logger.info("Tables created successfully.")
    
    # Verify the vector dimension in the Company table
    with engine.connect() as connection:
        try:
            result = connection.execute(text("SELECT typname, typelem, typarray FROM pg_type WHERE typname = 'vector'"))
            logger.info(f"Vector type info: {result.fetchall()}")
            
            result = connection.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'Company'"))
            logger.info(f"Company table columns: {result.fetchall()}")
            
            # Check the dimension of the embedding column
            result = connection.execute(text("SELECT pg_typeof(embedding) FROM \"Company\" LIMIT 1"))
            logger.info(f"Embedding column type: {result.fetchall()}")
        except Exception as e:
            logger.info(f"Could not verify vector dimension: {e}")

if __name__ == "__main__":
    reset_database() 