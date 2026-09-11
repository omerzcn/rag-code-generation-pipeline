import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CHUNKS_PATH, MODEL_TRANSFORMER, FAISS_INDEX_PATH
from vector_store import loading_chunks, loading_faiss, faiss_retriever

model = MODEL_TRANSFORMER

def chunks_to_documents(chunks):
    documents = []

    for chunk in chunks:
        doc = Document(
            page_content=(chunk["header"] + "\n" + chunk["header"] + "\n" + chunk["text"]),
            metadata={
                "filename": chunk["filename"],
                "header": chunk["header"],
                "text": chunk["text"],
            }
        )
        documents.append(doc)
    return documents

def langchain_retriever(vector_store, question, k: int = 5):
    results = vector_store.similarity_search_with_score(
        question, k=k
    )

    retrieved = []

    for doc, score in results:
        retrieved.append({
            "score": float(score),
            "filename": doc.metadata["filename"],
            "header": doc.metadata["header"],
            "text": doc.metadata["text"],
        })

    return retrieved

class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def embed_documents(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()
    
    def embed_query(self, text):
        return self.model.encode(text, normalize_embeddings=True).tolist()

def main():
    chunks = loading_chunks(file_path=CHUNKS_PATH)
    documents = chunks_to_documents(chunks=chunks)
    embeddings = SentenceTransformerEmbeddings(model=model)

    vector_store = FAISS.from_documents(
        documents=documents,
        embedding=embeddings
    )

    question = "How do I measure distance using HC-SR04?"

    custom_faiss = loading_faiss(file_path=FAISS_INDEX_PATH)
    custom_results = faiss_retriever(
        chunks=chunks, faiss_index=custom_faiss, question=question, k=5
    )

    print("\n## CUSTOM")
    for result in custom_results:
        print(f"Result: {result["score"]} -> {result["header"]} ")

    print("\n## LANGCHAIN")
    langchain_result = langchain_retriever(vector_store=vector_store, question=question, k=5)
    for result in langchain_result:
        print(f"Result: {result["score"]} -> {result["header"]} ")

if __name__ == "__main__":
    main()
