from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_rejects_empty_question():
    response = client.post(
        "/generate",
        json={"question": "   "}
    )
    assert response.status_code == 422

def test_generate_valid_question(monkeypatch):
    def fake_generate_rag_answer(question, loaded_chunks, loaded_faiss):
        return "fake generated code"

    monkeypatch.setattr(
        "api.main.generate_rag_answer",
        fake_generate_rag_answer
    )

    response = client.post(
        "/generate",
        json={"question": "Read an HC-SR04 sensor"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "code": "fake generated code",
        "status": "success"
    }

def test_generate_internal_error(monkeypatch):
    def fake_generate_rag_answer(question, loaded_chunks, loaded_faiss):
        raise RuntimeError("Generation failed")

    monkeypatch.setattr(
        "api.main.generate_rag_answer",
        fake_generate_rag_answer
    )

    response = client.post(
        "/generate",
        json={"question": "Read a sensor"}
    )
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Generation failed"
    }
