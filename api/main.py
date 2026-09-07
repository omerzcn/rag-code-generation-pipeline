from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from config import CHUNKS_PATH, FAISS_INDEX_PATH
from vector_store import loading_chunks, loading_faiss
from rag import generate_rag_answer

app = FastAPI()

loaded_chunks = loading_chunks(file_path=CHUNKS_PATH)
loaded_faiss = loading_faiss(file_path=FAISS_INDEX_PATH)

class GenerateRequest(BaseModel):
    question: str 

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        if not value.strip():
            raise ValueError("Question must not be empty")
        return value.strip()

class GenerateResponse(BaseModel):
    code: str
    status: str

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.post("/generate", response_model=GenerateResponse)
def generate_post(request: GenerateRequest):
    try:
        question = request.question
        answer = generate_rag_answer(
            question=question, loaded_chunks=loaded_chunks, loaded_faiss=loaded_faiss
        )
        return {
            "code": answer,
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
