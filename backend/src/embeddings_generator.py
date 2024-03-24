from typing import List
from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from backend.src.utils.log import get_logger

_logger = get_logger(__name__)


class EmbeddingsGenerator:
    def __init__(self, api_key: str, model: str):
        self.embedding_model = OpenAIEmbeddings(model=model,
                                                openai_api_key=api_key)

    def generate_embeddings(self, documents: List[Document]) -> List[List[float]]:
        _logger.info(f"Generating embeddings for {len(documents)} documents.")

        texts = [doc.page_content for doc in documents]
        embeddings = self.embedding_model.embed_documents(texts)

        _logger.info("Embeddings generated.")

        return embeddings
