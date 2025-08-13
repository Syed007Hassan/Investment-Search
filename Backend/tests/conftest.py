import os
import sys


# Ensure the Backend directory is on sys.path for imports when running from repo root
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


def pytest_configure():
    # Set safe defaults for env vars used by services
    os.environ.setdefault("GROQ_API_KEY", "test-key")
    os.environ.setdefault("SERP_API_KEY", "")
    os.environ.setdefault("PINECONE_API_KEY", "test-pinecone-key")
    os.environ.setdefault("DATABASE_NAME", "postgres")
    os.environ.setdefault("DATABASE_USER", "postgres")
    os.environ.setdefault("DATABASE_PASSWORD", "postgres")
    os.environ.setdefault("DATABASE_URL", "localhost")
    os.environ.setdefault("DATABASE_PORT", "5432")
    os.environ.setdefault("REDIS_HOST", "localhost")
    os.environ.setdefault("REDIS_PORT", "6379")

