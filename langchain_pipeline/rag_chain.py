import sys
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT, MODEL_TRANSFORMER, CHUNKS_PATH
from rag import build_context, select_context_candidates, select_machine_pattern, extract_pattern_code
from vector_store import loading_chunks
from langchain_pipeline.retriever import chunks_to_documents, SentenceTransformerEmbeddings, langchain_retriever

def build_langchain_prompt():
    prompt = """
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
    return ChatPromptTemplate.from_template(prompt)

def build_lcel_chain():
    prompt = build_langchain_prompt()

    model = ChatOpenAI(
        model=AZURE_OPENAI_DEPLOYMENT,
        api_key=AZURE_OPENAI_KEY,
        base_url=AZURE_OPENAI_ENDPOINT,
    )
    parser = StrOutputParser()

    chain = prompt | model | parser 
    return chain

def generate_langchain_rag_answer(vector_store, question, chain):
    results = langchain_retriever(
        vector_store=vector_store, question=question, k=20,
    )

    selected_pattern = select_machine_pattern(results=results)
    if selected_pattern is not None:
        code = extract_pattern_code(
            pattern_result=selected_pattern
        )
        if code is not None:
            return "```python\n" + code + "\n```"

    selected_results = select_context_candidates(results=results)
    context = build_context(results=selected_results)

    return chain.invoke({
        "context": context,
        "question": question,
    })

def main():
    chain = build_lcel_chain()

    loaded_chunks = loading_chunks(file_path=CHUNKS_PATH)
    documents = chunks_to_documents(chunks=loaded_chunks)
    embeddings = SentenceTransformerEmbeddings(model=MODEL_TRANSFORMER)
    
    vector_store = FAISS.from_documents(
        documents=documents,
        embedding=embeddings
    )
    question = "What does IoT mean?"
    answer = generate_langchain_rag_answer(vector_store=vector_store, question=question, chain=chain)

    print(answer)

if __name__ == "__main__":
    main()
