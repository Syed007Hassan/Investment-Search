"""
    This module contains the configuration classes for the project.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    """
    Base configuration class. Contains all the default configurations.
    """

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    
    # Qdrant Configuration
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")  
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "companies")
    
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "postgres")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    SQLALCHEMY_DATABASE_URL: str = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_URL}:{DATABASE_PORT}/{DATABASE_NAME}"
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))


config = Config()
