from config import CHUNKS_PATH, FAISS_INDEX_PATH
from vector_store import loading_chunks, loading_faiss, faiss_retriever
from llm import generate

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

def select_context_candidates(results):
    machine_patterns = []
    other_chunks = []

    for result in results:
        if result["header"].startswith("### PATTERN:"):
            machine_patterns.append(result)
        else:
            other_chunks.append(result)
    return machine_patterns[:1] + other_chunks[:4]

def select_machine_pattern(results):
    machine_patterns = []
    for result in results:
        if result["header"].startswith("### PATTERN:"):
            machine_patterns.append(result)

    if machine_patterns:
        return machine_patterns[0] 
    return None

def extract_pattern_code(pattern_result):
    text = pattern_result["text"]
    code_marker = "### CODE:"
    start = text.find(code_marker)
    if start == -1:
        return None
    code = text[start + len(code_marker):].strip()
    return code
    
def generate_rag_answer(question, loaded_chunks, loaded_faiss):
    results = faiss_retriever(chunks=loaded_chunks, faiss_index=loaded_faiss, question=question, k=20)

    # Machine pattern selection
    selected_pattern = select_machine_pattern(results=results)
    if selected_pattern is not None:
        code = extract_pattern_code(pattern_result=selected_pattern)
        if code is not None:
            return "```python\n" + code + "\n```"

    # Fallback to let model create, if there was no machine pattern
    selected_results = select_context_candidates(results=results)
    context = build_context(results=selected_results)

    prompt = build_prompt(question=question, context=context)

    return generate(prompt)

def main():
    loaded_chunks = loading_chunks(file_path=CHUNKS_PATH)
    loaded_faiss = loading_faiss(file_path=FAISS_INDEX_PATH)

    question = "What does IoT mean?"

    answer = generate_rag_answer(question=question, loaded_chunks=loaded_chunks, loaded_faiss=loaded_faiss)

    print(answer)

if __name__ == "__main__":
    main()
