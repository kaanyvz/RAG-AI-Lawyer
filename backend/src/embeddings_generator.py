from typing import List
from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from backend.src.utils.log import get_logger
import time

_logger = get_logger(__name__)


class EmbeddingsGenerator:
    def __init__(self, api_key: str, model: str):
        self.embedding_model = OpenAIEmbeddings(model=model,
                                                openai_api_key=api_key)

    def generate_embeddings(self, documents: List[Document]) -> List[List[float]]:
        _logger.info(f"Generating embeddings for {len(documents)} documents.")

        texts = [doc.page_content for doc in documents]
        embeddings = []

        # Define batch size and delay
        batch_size = 50
        delay_seconds = 5

        total_documents = len(texts)
        processed_documents = 0

        # Iterate over each chunk of documents and generate embeddings
        for text_chunk in self._chunks(texts, batch_size):
            # Generate embeddings for the current chunk
            chunk_embeddings = self.embedding_model.embed_documents(text_chunk)
            embeddings.extend(chunk_embeddings)

            # Update progress
            processed_documents += len(text_chunk)
            _logger.info(f"Processed {processed_documents} out of {total_documents} documents.")

            # Add a delay to avoid rate limit
            time.sleep(delay_seconds)

        _logger.info("Embeddings generated.")

        return embeddings

    def _chunks(self, lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
