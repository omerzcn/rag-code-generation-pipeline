import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import QUESTIONS_PATH, CHUNKS_PATH, FAISS_INDEX_PATH, RESULT_EVALUATION_PATH
from vector_store import loading_chunks, loading_faiss, faiss_retriever

def load_questions(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Questions file Not Found: {e}")

def calculate_hit(questions, loaded_chunks, loaded_faiss):
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

    overall_hit_1 = total_hit_1 / len(questions)
    overall_hit_3 = total_hit_3 / len(questions)
    overall_hit_5 = total_hit_5 / len(questions)

    return overall_hit_1, overall_hit_3, overall_hit_5

def save_results(file_path, experiment_name, representation, hit_1, hit_3, hit_5):
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M")
    with open(file_path, "a") as file:
        file.write(f"## Experiment: {experiment_name} - [{current_time}]\n\n")
        file.write(f"**Representation:** `{representation}`\n\n")
        file.write(f"- Hit@1: {hit_1:.1%}\n")
        file.write(f"- Hit@3: {hit_3:.1%}\n")
        file.write(f"- Hit@5: {hit_5:.1%}\n\n")

def main():
    questions = load_questions(file_path=QUESTIONS_PATH)

    loaded_chunks = loading_chunks(file_path=CHUNKS_PATH)

    loaded_faiss = loading_faiss(file_path=FAISS_INDEX_PATH)

    overall_hit_1, overall_hit_3, overall_hit_5 = calculate_hit(questions=questions, loaded_chunks=loaded_chunks, loaded_faiss=loaded_faiss)

    save_results(file_path=RESULT_EVALUATION_PATH, experiment_name="Double header", representation="header + header + text", hit_1=overall_hit_1, hit_3=overall_hit_3, hit_5=overall_hit_5)     

    print(f"Overall Hit@1: {overall_hit_1}")
    print(f"Overall Hit@3: {overall_hit_3}")
    print(f"Overall Hit@5: {overall_hit_5}")


if __name__ == "__main__":
    main()

