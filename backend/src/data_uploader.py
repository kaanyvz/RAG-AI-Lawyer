from backend.src.utils.log import get_logger
from backend.src.consts.directory import DATA_DIRECTORY
from backend.src.config.config import Configurations
from backend.src.embeddings_generator import EmbeddingsGenerator
from backend.src.pdf_uploader import PDFUploader
from backend.src.embeddings_store import EmbeddingsStore
import time

_logger = get_logger(__name__)

def main() -> None:
    settings = Configurations()

    filenames = ["TCK-1.pdf", "TCK-2.pdf", "TCK-3.pdf", "TCK-4.pdf", "TCK-5.pdf", "TCK-6.pdf"]
    chunk_size = 1000
    chunk_overlap = 100

    index_name = "langchain-doc-index"
    embedding_model = "text-embedding-ada-002"
    embedding_dimension = 1536
    metric = "cosine"

    batch_size = 100
    for filename in filenames:

        _logger.info(f"Processing PDF: {filename}")
        document_fp = DATA_DIRECTORY / filename
        pdf_processor = PDFUploader(filepath=document_fp, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        documents = pdf_processor.load_data()

        _logger.info("Generating document embeddings.")
        embedding_generator = EmbeddingsGenerator(api_key=settings.openai_configuration.api_key, model=embedding_model)
        embeddings = embedding_generator.generate_embeddings(documents)

        _logger.info("Upserting documents into Pinecone index.")
        vector_store = EmbeddingsStore(
            api_key=settings.pinecone_configuration.api_key, index_name=index_name, dimension=embedding_dimension, metric=metric
        )
        vector_store.upsert_documents(data=documents, embeddings=embeddings, batch_size=batch_size)
        time.sleep(60)

if __name__ == "__main__":
    main()