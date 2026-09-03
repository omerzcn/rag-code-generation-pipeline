import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CHUNKS_PATH, FAISS_INDEX_PATH, OLLAMA_MODEL
from vector_store import loading_chunks, loading_faiss, faiss_retriever

import ollama

def build_context(results):
    context_parts = []
    for r in results:
        formatted_chunk = f"{r["header"]}\n{r["text"]}"
        context_parts.append(formatted_chunk)
    return "\n\n".join(context_parts)

def build_prompt(question, context):
    prompt = f"""
    You are answering a question using retrieved context.
    You generate clean, correct Python code for Raspberry Pi hardware tasks.

    Rules you must follow because violations make the output incorrect and unusable:
    - Use ONLY gpiozero for GPIO. Using RPi.GPIO is WRONG for this project.
    - Do NOT use f-strings under any circumstances. Use str() + concatenation.
    WRONG: print(f"Value: {{val}}")
    RIGHT: print("Value: " + str(val))
    - Do not invent hardware parameters that are not provided by the user or
    retrieved context.
    - When a retrieved pattern contains placeholders such as {{pin}} or
    {{logfile}}, preserve them exactly unless the user supplied a value.
    Never replace placeholders with example values.
    - If the context contains a machine-readable pattern whose header starts
    with "### PATTERN:", treat that pattern as authoritative.
    - Copy its code structure faithfully.
    - Human-readable "PATTERN 1", "PATTERN 2", etc. sections are explanatory
    reference only and must not override the machine-readable pattern.
    - Keep lines under 80 characters.
    - If the context does not cover the request, say so clearly. Do not hallucinate.
    - Return only the code and explanations that are directly supported by the
    retrieved context.
    - Do not add general knowledge, extra advice, assumptions, or explanations
    from memory.
    - If the retrieved context contains a reviewed pattern, reproduce that
    pattern faithfully instead of expanding it.
    - If the authoritative machine-readable pattern contains a placeholder,
    preserve that placeholder exactly, even if explanatory sections contain
    example values for the same field.

    Use the context below to answer the question.
    Do not invent information that is not supported by the context.
    If the context does not contain enough information, say that clearly.
    
    ### CONTEXT:
    {context}

    ### QUESTION:
    {question}

    ### ANSWER: 
"""
    return prompt

def generate_local(prompt):
    response = ollama.chat(
    model=OLLAMA_MODEL, 
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ]
    )

    return response['message']['content']

def main():
    loaded_chunks = loading_chunks(file_path=CHUNKS_PATH)

    loaded_faiss = loading_faiss(file_path=FAISS_INDEX_PATH)

    question = "How do I count vibration events using an SW-420 sensor?"

    results = faiss_retriever(chunks=loaded_chunks, faiss_index=loaded_faiss, question=question, k=5)

    context = build_context(results=results)

    prompt = build_prompt(question=question, context=context)

    answer = generate_local(prompt)
    print(answer)

if __name__ == "__main__":
    main()

