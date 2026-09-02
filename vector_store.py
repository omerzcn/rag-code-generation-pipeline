from config import FAISS_INDEX_PATH, CHUNKS_PATH
from embeddings import embedding_chunks, embedded_question

import faiss
import json

def faiss_builder(embedded_text):
    dimension = embedded_text.shape[1]
    faiss_index = faiss.IndexFlatIP(dimension)
    faiss_index.add(embedded_text)
    return faiss_index

def faiss_retriever(chunks, faiss_index, question, k: int = 4):
    retrieved_faiss = []

    question = embedded_question(question)

    scores, numbers = faiss_index.search(question, k=k)

    for score, idx in zip(scores[0], numbers[0]):
        retrieved_faiss.append({
            "score": score.item(),
            "filename": chunks[idx]["filename"],
            "header": chunks[idx]["header"],   
            "text": chunks[idx]["text"],
        })
    return retrieved_faiss

def saving_chunks(chunks, file_path):
    try:
        with open(file_path, "w") as file:
            json.dump(chunks, file)
        return True
    except Exception as e:
        print(f"Failed to save chunks due to: {e}")
        return None

def loading_chunks(file_path):
    try:
        with open(file_path, "r") as file:
            loaded_chunks = json.load(file)
        return loaded_chunks
    except Exception as e:
        print(f"Failed to load chunks from {file_path} due to: {e}")
        return None

def saving_faiss(faiss_index, file_path):
    try:
        faiss.write_index(faiss_index, str(file_path))
        return True
    except Exception as e:
        print(f"Failed to save index due to: {e}")
        return None

def loading_faiss(file_path):
    try:
        loaded_index = faiss.read_index(str(file_path))
        print("Index successfully loaded")
        return loaded_index
    except Exception as e:
        print(f"Failed to load index from {file_path} due to: {e}")
        raise ValueError(f"Failed to load index from {file_path}") from e

def main():
    chunks, embedded_text = embedding_chunks()

    faiss_index = faiss_builder(embedded_text)

    manual_retrieved_result = faiss_retriever(chunks, faiss_index=faiss_index, question="How do I count vibration events using an SW-420 sensor?", k=4)

    saved_chunks = saving_chunks(chunks, file_path=CHUNKS_PATH)
    if not saved_chunks:
        print("Exiting! Chunks were not saved, cannot load chunks.")
        return None
    loaded_chunks = loading_chunks(file_path=CHUNKS_PATH)

    saved_faiss = saving_faiss(faiss_index=faiss_index, file_path=FAISS_INDEX_PATH)
    if not saved_faiss:
        print("Exiting! Index was not saved, cannot load faiss.")
        return None
    loaded_faiss = loading_faiss(file_path=FAISS_INDEX_PATH)

    loaded_retrieved_result = faiss_retriever(chunks=loaded_chunks, faiss_index=loaded_faiss, question="How do I count vibration events using an SW-420 sensor?", k=4)

    are_results_equal = manual_retrieved_result == loaded_retrieved_result
    if are_results_equal:
        print("The results are equal!")
    else:
        print("The results do NOT match!")

if __name__ == "__main__":
    main()
