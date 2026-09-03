from config import CHUNKS_PATH, FAISS_INDEX_PATH
from vector_store import loading_chunks, loading_faiss, faiss_retriever
from llm import generate_local, generate_api

def build_context(results):
    machine_patterns = []
    human_patterns = []
    other_chunks = []
    for r in results:
        if r["header"].startswith("### PATTERN:"):
            formatted_machine = f"{r['header']}\n{r['text']}"
            machine_patterns.append(formatted_machine)
        elif r["header"].startswith("### PATTERN "):
            formatted_human = f"{r['header']}\n{r['text']}"
            human_patterns.append(formatted_human)
        else:
            formatted_chunk = f"{r['header']}\n{r['text']}"
            other_chunks.append(formatted_chunk)

    if machine_patterns:
        context_parts = machine_patterns + other_chunks
    else:
        context_parts = human_patterns + other_chunks
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
    - Human-readable "PATTERN 1", "PATTERN 2", etc. sections are explanatory
    reference only and must not override the machine-readable pattern.
    - Keep lines under 80 characters.
    - If the context does not cover the request, say so clearly. Do not hallucinate.
    - Return only the code and explanations that are directly supported by the
    retrieved context.
    - Do not add general knowledge, extra advice, assumptions, or explanations
    from memory.
    - Follow the structure of the authoritative pattern faithfully, but do not
    include unrelated operations from the pattern.
    - Use the authoritative machine-readable pattern as the source of truth,
    but include only the parts required to answer the user's request.
    - Do not introduce code that is not present in that pattern.

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

def generate_rag_answer(question):
    loaded_chunks = loading_chunks(file_path=CHUNKS_PATH)
    loaded_faiss = loading_faiss(file_path=FAISS_INDEX_PATH)

    results = faiss_retriever(chunks=loaded_chunks, faiss_index=loaded_faiss, question=question, k=5)

    context = build_context(results=results)
    prompt = build_prompt(question=question, context=context)

    answer = generate_api(prompt)
    return answer

def main():
    question = "How do I move a servo motor to the center position?"

    answer = generate_rag_answer(question=question)

    print(answer)

if __name__ == "__main__":
    main()
