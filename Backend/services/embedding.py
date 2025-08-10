# pylint:disable=all
"""Embedding service using Pinecone for vector generation."""

import logging
from typing import (
    TypedDict,
    Union,
)

from pinecone import Pinecone
from config.main import config

logger = logging.getLogger(__name__)

class Embedding:
    def __init__(self):
        """
        Initializes the Embedding object with Pinecone client only.
        """
        # Initialize Pinecone client
        self.pinecone_client = Pinecone(api_key=config.PINECONE_API_KEY)
        self.pinecone_model = "multilingual-e5-large"

    def generate_pinecone(self, content, dimensions=None):
        """
        Generates an embedding for the given content using Pinecone's embedding service.

        :param content: The text content to generate an embedding for.
        :param dimensions: Optional dimensions for the embedding vector.
        :return: A list representing the generated embedding.
        """
        content = content.replace("\n", " ").strip()
        try:
            embeddings = self.pinecone_client.inference.embed(
                model=self.pinecone_model,
                inputs=[content],
                parameters={"input_type": "passage", "truncate": "END"}
            )
            # Return the first embedding's values
            return embeddings.data[0]['values']
        except Exception as e:
            logger.error(f"Error generating Pinecone embedding: {e}")
            raise

    def generate_multiple_pinecone(self, contents):
        """
        Generates embeddings for multiple pieces of content using Pinecone's embedding service.

        :param contents: A list of text content to generate embeddings for.
        :return: A list of embeddings corresponding to the input content.
        """
        contents = [content.replace("\n", " ").strip() for content in contents]
        try:
            embeddings = self.pinecone_client.inference.embed(
                model=self.pinecone_model,
                inputs=contents,
                parameters={"input_type": "passage", "truncate": "END"}
            )
            # Extract and return all embedding values
            return [item['values'] for item in embeddings.data]
        except Exception as e:
            logger.error(f"Error generating multiple Pinecone embeddings: {e}")
            raise

