# pylint:disable=all

import logging
from typing import (
    TypedDict,
    Union,
)

from openai import OpenAI
from pinecone import Pinecone
from config.main import config

logger = logging.getLogger(__name__)

class Embedding:
    def __init__(self):
        """
        Initializes the Embedding object with Pinecone and OpenAI clients.

        :param api_key: API key for the OpenAI service.
        :param model_name: The name of the model to use for generating embeddings.
        """
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.embedding_model_name = "text-embedding-3-small"
        # Initialize Pinecone client
        self.pinecone_client = Pinecone(api_key=config.PINECONE_API_KEY)
        self.pinecone_model = "multilingual-e5-large"

    def generate(self, content, dimensions=None):
        """
        Generates an embedding for the given content using the specified model.

        :param content: The text content to generate an embedding for.
        :return: A list representing the generated embedding.
        """
        content = content.replace("\n", " ").strip()
        res = self.client.embeddings.create(
            input=[content], model=self.embedding_model_name,
            dimensions=dimensions if dimensions else 1536
        )
        embed = res.data[
            0
        ].embedding  # Assuming the response contains a list of embeddings
        return embed

    def generate_multiple(self, contents):
        """
        Generates embeddings for multiple pieces of content using the specified model.

        :param contents: A list of text content to generate embeddings for.
        :return: A list of embeddings corresponding to the input content.
        """
        contents = [content.replace("\n", " ").strip() for content in contents]
        res = self.client.embeddings.create(
            input=contents, model=self.embedding_model_name
        )
        embeddings = [item.embedding for item in res.data]
        return embeddings

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

