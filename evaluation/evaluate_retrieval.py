import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import QUESTIONS_PATH, CHUNKS_PATH, FAISS_INDEX_PATH
from vector_store import loading_chunks, loading_faiss, faiss_retriever

def load_questions(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Questions file Not Found: {e}")

def main():
    questions = load_questions(file_path=QUESTIONS_PATH)

    loaded_chunks = loading_chunks(file_path=CHUNKS_PATH)

    loaded_faiss = loading_faiss(file_path=FAISS_INDEX_PATH)

    total_hit_1 = 0
    total_hit_3 = 0
    total_hit_5 = 0

    for test_case in questions:
        question_query = test_case["question"]
        expected_header = test_case["expected_header"]

        retrieve = faiss_retriever(chunks=loaded_chunks, faiss_index=loaded_faiss, question=question_query, k=5)

        retrieved_headers = []
        for r in retrieve:
            retrieved_headers.append(r["header"])

        hit_at_1 = int(expected_header in retrieved_headers[:1])
        hit_at_3 = int(expected_header in retrieved_headers[:3])
        hit_at_5 = int(expected_header in retrieved_headers[:5])

        print(
            f"Question: {question_query}\n",
            f"Hit@1: {hit_at_1}\n",
            f"Hit@3: {hit_at_3}\n",
            f"Hit@5: {hit_at_5}\n",
        )

        total_hit_1 += hit_at_1
        total_hit_3 += hit_at_3
        total_hit_5 += hit_at_5

        if hit_at_3 == 0:
            print(f"Failed Hit@3\n")
            print(
                f"Question: {question_query}",
                f"Expected Header: {expected_header}",
                f"Hit@5: {hit_at_5}",
            )
            for rank, header in enumerate(retrieved_headers, start=1):
                print(rank, header) 

    print(f"Overall Hit@1: {total_hit_1 / len(questions)}")
    print(f"Overall Hit@3: {total_hit_3 / len(questions)}")
    print(f"Overall Hit@5: {total_hit_5 / len(questions)}")

if __name__ == "__main__":
    main()

