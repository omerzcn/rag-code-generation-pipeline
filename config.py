import os
from dotenv import load_dotenv 
load_dotenv()

from pathlib import Path

from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).resolve().parent / "data"

VECTOR_STORE_DIR = Path(__file__).resolve().parent / "vector_store"
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "saved_index.faiss"
CHUNKS_PATH = VECTOR_STORE_DIR / "saved_chunks.json"

EVALUATION_DIR = Path(__file__).resolve().parent / "evaluation"
QUESTIONS_PATH = EVALUATION_DIR / "questions.json"
RESULT_EVALUATION_PATH = EVALUATION_DIR / "results.md"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

MODEL_TRANSFORMER = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

OLLAMA_MODEL = "qwen2.5-coder:7b"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "~deepseek/deepseek-v4-flash-latest"
