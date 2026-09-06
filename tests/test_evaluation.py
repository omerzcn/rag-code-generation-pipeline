import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import PATTERN_REQUIREMENTS_PATH, CHUNKS_PATH, FAISS_INDEX_PATH, QUESTIONS_PATH

from vector_store import loading_chunks, loading_faiss

from evaluation.evaluate_retrieval import load_questions, calculate_hit
from evaluation.evaluate_generation import load_evaluation_cases, evaluate_generation

@pytest.fixture(scope="session")
def loaded_chunks():
    return loading_chunks(file_path=CHUNKS_PATH)

@pytest.fixture(scope="session")
def loaded_faiss():
    return loading_faiss(file_path=FAISS_INDEX_PATH)

@pytest.fixture(scope="session")
def loaded_cases():
    return load_evaluation_cases(file_path=PATTERN_REQUIREMENTS_PATH)

@pytest.fixture(scope="session")
def loaded_questions():
    return load_questions(file_path=QUESTIONS_PATH)

def test_generation_regression(loaded_cases, loaded_chunks, loaded_faiss):

    results = evaluate_generation(
        cases=loaded_cases, loaded_chunks=loaded_chunks, loaded_faiss=loaded_faiss
    )
    assert results["pass_rate"] >= 0.80

def test_retrieval_sanity(loaded_questions, loaded_chunks, loaded_faiss):

    results = calculate_hit(
        questions=loaded_questions, loaded_chunks=loaded_chunks, loaded_faiss=loaded_faiss
    )
    assert results["hit_at_5"] >= 0.70
    