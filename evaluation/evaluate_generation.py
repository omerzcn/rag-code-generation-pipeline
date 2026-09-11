import sys
from pathlib import Path
import json
import ast
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import PATTERN_REQUIREMENTS_PATH, CHUNKS_PATH, FAISS_INDEX_PATH, MODEL_TRANSFORMER, RESULT_EVALUATION_PATH

from vector_store import loading_chunks, loading_faiss
from rag import generate_rag_answer
from langchain_pipeline.rag_chain import generate_langchain_rag_answer, build_lcel_chain
from langchain_pipeline.retriever import chunks_to_documents, SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS

def check_required_code(generated_code, required_code):
    missing = []
    for item in required_code:
        if item not in generated_code:
            missing.append(item)

    if missing:
        return {
            "passed": False,
            "missing": missing,
        }
    else:
        return {
            "passed": True,
            "missing": [],
        }

def check_forbidden_code(generated_code, forbidden_code):
    found_forbidden = []
    for item in forbidden_code:
        if item in generated_code:
            found_forbidden.append(item)
    if found_forbidden:
        return {
            "passed": False,
            "found_forbidden": found_forbidden,
            }
    else:
        return {
            "passed": True,
            "found_forbidden": [],
        }

def check_placeholders(generated_code, placeholders):
    missing_placeholders = []
    for placeholder in placeholders:
        if placeholder not in generated_code:
            missing_placeholders.append(placeholder)
    if missing_placeholders:
        return {
            "passed": False,
            "missing_placeholders": missing_placeholders,
        }
    else:
        return {
            "passed": True,
            "missing_placeholders": []
        }

def load_evaluation_cases(file_path):
    try:
        with open(file_path, "r") as file:
            cases = json.load(file)
            return cases
    except FileNotFoundError as e:
        print(f"Evaluation file not found: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")

def extract_python_code(generated_answer):
    start_marker = "```python"
    end_marker = "```"

    start_id = generated_answer.find(start_marker)
    if start_id == -1:
        return ""

    code_start = start_id + len(start_marker)

    end_id = generated_answer.find(end_marker, code_start)
    if end_id == -1:
        return ""

    return generated_answer[code_start:end_id].strip()

def replace_placeholders_for_syntax(code, placeholders):
    syntax_code = code
    for placeholder in placeholders:
        syntax_code = syntax_code.replace(placeholder, "17")
    return syntax_code

def check_python_syntax(syntax_code):
    try:
        ast.parse(syntax_code)
        return {
            "passed": True,
            "syntax_error": None,
        }
    except SyntaxError as e:
        return {
            "passed": False,
            "syntax_error": str(e)
        }

def check_no_fstrings(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            return {
                "passed": False,
                "fstring_found": True,
            }
    return {
        "passed": True,
        "fstring_found": False,
    }

def check_code_block(code):
    if code == "":
        return {
            "passed": False,
            "reason": "No Python code block found",
        }
    return {
        "passed": True,
        "reason": None,
    }

def evaluate_case(case, generator):
    try:
        generated_code = generator(case["question"])
    except Exception as e:
        return {
            "question": case["question"],
            "generated_code": "",
            "required_check": {
                "passed": False,
                "missing": case["required_code"],
            },
            "forbidden_check": {
                "passed": False,
                "found_forbidden": [],
            },
            "placeholder_check": {
                "passed": False,
                "missing_placeholders": case["placeholders"],
            },
            "code_block_check": {
                "passed": False,
                "reason": "Generation failed",
            },
            "syntax_check": {
                "passed": False,
                "syntax_error": "Generation failed",
            },
            "f_string_check": {
                "passed": False,
                "fstring_found": None,
            },
            "generation_error": str(e),
            "passed": False,
        }

    required_check = check_required_code(generated_code=generated_code, required_code=case["required_code"])
    forbidden_check = check_forbidden_code(generated_code=generated_code, forbidden_code=case["forbidden_code"])
    placeholder_check = check_placeholders(generated_code=generated_code, placeholders=case["placeholders"])

    extracted_code = extract_python_code(generated_answer=generated_code)

    code_block_check = check_code_block(code=extracted_code)


    if code_block_check["passed"]:
        syntax_code = replace_placeholders_for_syntax(code=extracted_code, placeholders=case["placeholders"])

        syntax_check = check_python_syntax(syntax_code=syntax_code)
        
        if syntax_check["passed"]:
            f_string_check = check_no_fstrings(code=syntax_code)
        else:
            f_string_check = {
                "passed": False,
                "fstring_found": None,
            }
    else:
        syntax_check = {
            "passed": False,
            "syntax_error": "No Python code block found",
        }
        f_string_check = {
            "passed": False,
            "fstring_found": None,
        }

    case_passed = (
        required_check["passed"]
        and forbidden_check["passed"]
        and placeholder_check["passed"]
        and syntax_check["passed"]
        and f_string_check["passed"]
        and code_block_check["passed"]
    )

    return {
        "question": case["question"],
        "generated_code": generated_code,
        "required_check": required_check,
        "forbidden_check": forbidden_check,
        "placeholder_check": placeholder_check,
        "code_block_check": code_block_check,
        "syntax_check": syntax_check,
        "f_string_check": f_string_check,
        "passed": case_passed,
    }

def evaluate_generation(cases, generator):
    passed_cases = 0
    case_results = []

    for case in cases:
        result = evaluate_case(
            case=case, generator=generator
        )
        case_results.append(result)   
        if result["passed"]:
            passed_cases += 1

    total_cases = len(cases)
    failed_cases = total_cases - passed_cases
    generation_pass_rate = passed_cases / total_cases

    return {
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "total_cases": total_cases,
        "pass_rate": generation_pass_rate,
        "case_results": case_results,
    }

def print_failed_cases(results):
    for result in results["case_results"]:
        if not result["passed"]:
            print("\nQuestion:")
            print(result["question"])
            print("Required:", result["required_check"])
            print("Forbidden:", result["forbidden_check"])
            print("Placeholders:", result["placeholder_check"])
            print("Code block:", result["code_block_check"])
            print("Syntax:", result["syntax_check"])
            print("F-strings:", result["f_string_check"])
            print("\nGenerated code:")
            print(result["generated_code"])

def save_generation_results(file_path, experiment_name, results):
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M")
    with open(file_path, "a") as file:
        file.write(f"## Experiment: {experiment_name} - [{current_time}]\n\n")
        file.write(f"- Passed cases: {results['passed_cases']}\n")
        file.write(f"- Failed cases: {results['failed_cases']}\n")
        file.write(f"- Total cases: {results['total_cases']}\n")
        file.write(f"- Pass rate: {results['pass_rate']:.1%}\n\n")

def main():
    cases = load_evaluation_cases(file_path=PATTERN_REQUIREMENTS_PATH)

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

    custom_results = evaluate_generation(cases=cases, generator=custom_generator)
    langchain_results = evaluate_generation(cases=cases, generator=lc_generator)

    print("\n## CUSTOM FAILURES")
    print_failed_cases(results=custom_results)

    print("\n## LANGCHAIN FAILURES")
    print_failed_cases(results=langchain_results)

    save_generation_results(
        file_path=RESULT_EVALUATION_PATH, experiment_name="Custom Generation Baseline", results=custom_results,
    )

    save_generation_results(
        file_path=RESULT_EVALUATION_PATH, experiment_name="LangChain Generation", results=langchain_results
    )

if __name__ == "__main__":
    main()
