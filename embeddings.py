from config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, MODEL_TRANSFORMER
from chunker import build_chunks

model = MODEL_TRANSFORMER

def get_chunks():
    chunks = build_chunks(data_path=DATA_DIR, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return chunks

def embedding_chunks():
    chunks = get_chunks()
    texts_to_embed = []
    for text in chunks:
        texts_to_embed.append(
            text["header"] + "\n" + text["text"]
        )
    embedded_text = model.encode(texts_to_embed, normalize_embeddings=True)
    return chunks, embedded_text

def embedded_question(question:str):
    return model.encode([question], normalize_embeddings=True)

def manual_retriever(chunks:list[dict[str, str]], embeddings, question:str, k:int = 5):
    encoded = embedded_question(question)
    similarity = model.similarity(encoded, embeddings)
    
    top_values, top_indices = similarity.topk(k=k, dim=1)
    results = []
    for score, index in zip(top_values[0], top_indices[0]):
        chunk = chunks[index.item()]
        results.append({
            "score": score.item(),
            "filename": chunk["filename"],
            "header": chunk["header"],
            "text": chunk["text"],
        })
    return results

def main():
    chunks, embeddings = embedding_chunks()
    questions = [
        "How do I count vibration events using an SW-420 sensor?",
        "Show me the reviewed pattern for vibration_event_counter.",
        "How do I log obstacle detections to a file?",
    ]
    for q in questions:
        print(f"\n=={q}==\n")
        results = manual_retriever(chunks, embeddings, question=q)
        for r in results:
            print("score:", r["score"])
            print("header:", r["header"])
            print("text:", r["text"])
            print()

if __name__ == "__main__":
    main()
