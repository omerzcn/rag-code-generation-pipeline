from pathlib import Path

from config import DATA_DIR

def load_documents(data_path) -> list[dict[str, str]]:
    results = []
    for file in data_path.rglob("*.md"):
        if file.is_file():
            results.append({
                "filename": str(file.relative_to(data_path)),
                "text": file.read_text(encoding="utf-8")
            }) 
    return results

def main():
    print(load_documents(data_path=DATA_DIR))

if __name__ == "__main__":
    main()
