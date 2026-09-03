import sys
from pathlib import Path
import json
import ast

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import PATTERN_REQUIREMENTS_PATH

from rag import generate_rag_answer

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

def evaluate_case(case):
    generated_code = generate_rag_answer(question=case["question"])

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

def main():
    cases = load_evaluation_cases(file_path=PATTERN_REQUIREMENTS_PATH)

    passed_cases = 0

    for case in cases:
        result = evaluate_case(case)

        print("\nQuestion:")
        print(result["question"])

        print("Required:", result["required_check"])
        print("Forbidden:", result["forbidden_check"])
        print("Placeholders:", result["placeholder_check"])
        print("Code block:", result["code_block_check"])
        print("Syntax:", result["syntax_check"])
        print("F-strings:", result["f_string_check"])

        if result["passed"]:
            print("Overall: PASS")
            passed_cases += 1
        else:
            print("Overall: FAIL")
            print("\nGenerated code:")
            print(result["generated_code"])

    total_cases = len(cases)

    generation_pass_rate = passed_cases / total_cases

    print(
        f"Generation Pass Rate: {str(round(generation_pass_rate * 100, 1))}%"
    )

if __name__ == "__main__":
    main()
