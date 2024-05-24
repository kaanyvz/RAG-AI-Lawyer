import time
import uuid
from typing import List

from langchain_core.documents import Document
from pinecone import Index, Pinecone, PodSpec
from retry import retry
from tqdm import tqdm

from backend.src.utils.log import get_logger, timed

_logger = get_logger(__name__)


class EmbeddingsStore:
    def __init__(self,
                 api_key: str,
                 index_name: str,
                 dimension: int,
                 metric: str) -> None:

        self.pc = Pinecone(api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric

        self.ensure_index()

    def ensure_index(self) -> None:
        _logger.info(f"Ensuring index {self.index_name} has already exists in Pinecone.")

        spec = PodSpec("gcp-starter")

        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(name=self.index_name,
                                 dimension=self.dimension,
                                 spec=spec,
                                 metric=self.metric)

            while not self.pc.describe_index(self.index_name).status["ready"]:
                time.sleep(1)

            _logger.info(f"Index {self.index_name} created in Pinecone.")
        else:
            _logger.info(f"Index {self.index_name} already exists in Pinecone.")

    @timed
    def upsert_documents(self, data: List[Document], embeddings: List[List[float]], batch_size: int = 100,
                         namespace: str = "default") -> None:
        _logger.info(f"Upserting {len(data)} documents into index: {self.index_name}")

        index = self.pc.Index(self.index_name)

        time.sleep(1)

        expected_vectors = 0

        for i in tqdm(range(0, len(data), batch_size)):
            batch_data = data[i: i + batch_size]
            batch_embeddings = embeddings[i: i + batch_size]
            self._upsert_batch(index=index, data=batch_data, embeddings=batch_embeddings, namespace=namespace)
            expected_vectors += len(batch_data)

            while index.describe_index_stats()["total_vector_count"] < expected_vectors:
                time.sleep(1)

            _logger.info(f"Batch upserted into Pinecone index.\n{index.describe_index_stats()}")

        _logger.info(f"A total of {len(data)} documents upserted into Pinecone index.\n{index.describe_index_stats()}")

    @retry(tries=10, delay=5, logger=_logger)
    def _upsert_batch(self, index: Index, data: List[Document], embeddings: List[List[float]], namespace: str) -> None:
        vectors_to_upsert = self._prepare_vectors_for_upsert(data, embeddings)
        try:
            index.upsert(vectors=vectors_to_upsert, namespace=namespace)
        except Exception as e:
            raise Exception(f"Failed to upsert vectors into Pinecone index: {e}")

    def _prepare_vectors_for_upsert(
            self, batch_data: List[Document], batch_embeddings: List[List[float]]
    ) -> List[dict]:

        vectors_to_upsert = []
        for doc, embedding in zip(batch_data, batch_embeddings):
            doc_id = str(uuid.uuid4())
            chunk_metadata = doc.metadata if doc.metadata else {}
            chunk_metadata.update({"context": doc.page_content})

            vectors_to_upsert.append({"id": doc_id, "values": embedding, "metadata": chunk_metadata})

        return vectors_to_upsert
