from backend.src.utils.log import get_logger
from backend.src.consts.directory import DATA_DIRECTORY
from backend.src.config.config import Configurations
from backend.src.embeddings_generator import EmbeddingsGenerator
from backend.src.pdf_uploader import PDFLoader
from backend.src.vector_store import VectorStore
import time

_logger = get_logger(__name__)