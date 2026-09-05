from ingest import load_documents
from config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP

def split_by_characters(documents:list[dict[str, str]], chunk_size:int, chunk_overlap:int) -> list[dict[str, str]]:
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap must be >= 0 and smaller than chunk size")
    chunks = []
    for file in documents:
        filename = file["filename"]
        text = file["text"]
        i = 0
        text_length = len(text)
        while i < text_length:
            chunks.append({
                "filename": filename,
                "text": text[i:i+chunk_size]
            })
            i += (chunk_size-chunk_overlap)
    return chunks

def split_by_headers(documents:list[dict[str, str]]) -> list[dict[str, str]]:
    sections = []
    for file in documents:
        current_filename = file["filename"]
        current_header = None
        current_text = []

        lines = file["text"].splitlines()
        for line in lines:
            if line.startswith("#"):
                if (
                    current_header is not None and current_header.startswith("### PATTERN:")
                    and (line.startswith("### SLOTS:") or line.startswith("### CODE:"))
                ):
                    current_text.append(line)
                else:
                    if current_header is not None:
                        sections.append({
                            "filename": current_filename,
                            "header": current_header,
                            "text": "\n".join(current_text),
                        })
                    current_filename = file["filename"]
                    current_header = line
                    current_text = []
            else:
                current_text.append(line)
        if current_header is not None:
            sections.append({
                "filename": current_filename,
                "header": current_header,
                "text": "\n".join(current_text),
            })
    return sections

def chunk_sections(sections:list[dict[str, str]], chunk_size:int, chunk_overlap:int) -> list[dict[str, str]]:
    chunks = []
    for section in sections:
        current_filename = section["filename"]
        current_header = section["header"]
        current_text = section["text"]

        if current_header.startswith("### PATTERN:"):
            chunks.append({
                "filename": current_filename,
                "header": current_header,
                "text": current_text,
            })

        elif len(current_text) <= chunk_size:
            chunks.append({
                "filename": current_filename,
                "header": current_header,
                "text": current_text,
            })
        else:
            new_chunk = split_by_characters([section], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            ordered_chunks = []
            for chunk in new_chunk:
                ordered_chunks.append({
                    "filename": chunk["filename"],
                    "header": current_header,
                    "text": chunk["text"],
                })
            chunks.extend(ordered_chunks)
    return chunks

def build_chunks(data_path:str, chunk_size:int, chunk_overlap:int) -> list[dict[str, str]]:
    documents = load_documents(data_path)
    sections = split_by_headers(documents)
    return chunk_sections(sections, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

def main():
    try:
        chunks = build_chunks(data_path=DATA_DIR, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        print(chunks)
    except ValueError as e:
        print(f"Validation Error: {e}")

if __name__ == "__main__":
    main()
