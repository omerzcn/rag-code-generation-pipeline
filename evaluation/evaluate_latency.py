import time
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CHUNKS_PATH, FAISS_INDEX_PATH, MODEL_TRANSFORMER, RESULT_EVALUATION_PATH

from vector_store import loading_chunks, loading_faiss
from rag import generate_rag_answer
from langchain_pipeline.rag_chain import generate_langchain_rag_answer, build_lcel_chain
from langchain_pipeline.retriever import chunks_to_documents, SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS

def measure_latency(custom_function, langchain_function, question, runs: int):
    custom_latencies = []
    langchain_latencies = []

    for _ in range(runs):
        start = time.perf_counter()
        custom_function(question)
        end = time.perf_counter()
        custom_latencies.append(end - start)

        start = time.perf_counter()
        langchain_function(question)
        end = time.perf_counter()
        langchain_latencies.append(end - start)

    custom_results = {
        "average": sum(custom_latencies) / len(custom_latencies),
        "minimum": min(custom_latencies),
        "maximum": max(custom_latencies),
        "runs": runs,
    }

    langchain_results = {
        "average": sum(langchain_latencies) / len(langchain_latencies),
        "minimum": min(langchain_latencies),
        "maximum": max(langchain_latencies),
        "runs": runs,
    }

    return custom_results, langchain_results

def save_latency_results(file_path, experiment_name, custom_results, langchain_results):
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M")
    with open(file_path, "a") as file:
        file.write(f"## Experiment: {experiment_name} - [{current_time}]\n\n")
        file.write("### Custom\n")
        file.write(f"- Average: {custom_results['average']:.3f} s\n")
        file.write(f"- Minimum: {custom_results['minimum']:.3f} s\n")
        file.write(f"- Maximum: {custom_results['maximum']:.3f} s\n")
        file.write(f"- Runs: {custom_results['runs']}\n\n")

        file.write("### LangChain\n")
        file.write(f"- Average: {langchain_results['average']:.3f} s\n")
        file.write(f"- Minimum: {langchain_results['minimum']:.3f} s\n")
        file.write(f"- Maximum: {langchain_results['maximum']:.3f} s\n")
        file.write(f"- Runs: {langchain_results['runs']}\n\n")     

def main():
    loaded_chunks = loading_chunks(file_path=CHUNKS_PATH)
    loaded_faiss = loading_faiss(file_path=FAISS_INDEX_PATH)

    documents = chunks_to_documents(chunks=loaded_chunks)
    embeddings = SentenceTransformerEmbeddings(model=MODEL_TRANSFORMER)
    vector_store = FAISS.from_documents(
        documents=documents, embedding=embeddings,
    )
    chain = build_lcel_chain()

    def custom_generator(question):
        return generate_rag_answer(
            question=question, loaded_chunks=loaded_chunks, loaded_faiss=loaded_faiss,
        )

    def lc_generator(question):
        return generate_langchain_rag_answer(
            vector_store=vector_store, question=question, chain=chain,
        )

    fallback_question = "What does IoT mean?"
    custom_generator(fallback_question)
    lc_generator(fallback_question)

    custom_fallback, lc_fallback = measure_latency(
        custom_function=custom_generator,
        langchain_function=lc_generator,
        question=fallback_question,
        runs=10,
    )

    print("##Custom Fallback Latency:\n")
    print(custom_fallback)

    print("##LangChain Fallback latency\n")
    print(lc_fallback)

    save_latency_results(
        file_path=RESULT_EVALUATION_PATH, experiment_name="LLM Fallback End-to-End Latency",
        custom_results=custom_fallback, langchain_results=lc_fallback,
    )

if __name__ == "__main__":
    main()
