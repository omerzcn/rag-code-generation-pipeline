# RAG-Based IoT Code Generation Pipeline

A Retrieval-Augmented Generation (RAG) pipeline for generating reliable Python code for Raspberry Pi
and IoT tasks from a structured knowledge base of skill files.

The project implements the main components of a RAG system from scratch, including document processing,
chunking, embeddings, FAISS vector search, retrieval, pattern selection, evaluation, regression testing,
containerization and CI/CD deployment.

A key focus is improving the reliability of smaller local models by retrieving human-reviewed,
machine-readable code patterns instead of relying entirely on free-form LLM code generation.

## How It Works

Skill files are loaded from Markdown documents and converted into chunks.
Normal documentation uses character-based chunking, while machine-readable code patterns are kept as complete atomic chunks.

The chunks are embedded using SentenceTransformers and stored in a FAISS index.
For each user query, the system retrieves the most relevant candidates and searches them for reviewed machine patterns.

```text

question
    ↓
faiss_retriever(k=20)
    ↓
select_context_candidates()
    ↓
select_machine_pattern()
    ↓
pattern found?  
    └── yes -> extract_pattern_code() -> return code
    |
    └── no -> build_context() -> LLM -> return code

```

When a machine-readable pattern is found, its reviewed code is extracted directly rather than rewritten by the LLM.
The LLM is used as a fallback when no suitable machine pattern is available.

The RAG pipeline is exposed through a FastAPI layer.

The API provides a health endpoint and a generation endpoint that accepts validated JSON requests using Pydantic
and returns generated code as a JSON response.

To run the API locally:

```bash
uvicorn api.main:app --reload
```

Interactive Swagger documentation is available at:

http://127.0.0.1:8000/docs

## Key Engineering Decisions

During evaluation, several failure modes were identified:

- machine-readable patterns were sometimes split during normal chunking
- relevant patterns could appear lower in the retrieval results
- explanatory examples could compete with authoritative patterns
- the LLM could unnecessarily modify already reviewed code

The architecture was therefore changed to:

- keep machine-readable patterns as atomic chunks
- inspect a wider set of retrieval candidates
- distinguish reviewed patterns from normal documentation
- deterministically extract reviewed code when a pattern is selected
- use LLM generation as a fallback rather than the default path

These changes improved generation reliability from 66.7% to 88.9% on the current evaluation set.

## Evaluation

Retrieval and final code generation are evaluated separately.

| Metric | Result |
|---|---:|
| Retrieval Hit@1 | 20.0% |
| Retrieval Hit@3 | 73.3% |
| Retrieval Hit@5 | 80.0% |
| Initial generation pass rate | 66.7% |
| Current generation pass rate | **88.9%** |

The generation evaluation contains 9 representative Raspberry Pi and IoT tasks.
Outputs are checked for required and forbidden code, placeholder preservation, Python code blocks,
AST syntax validity, and project-specific rules such as avoiding f-strings.

An important finding was that better standalone retrieval metrics did not always produce better
end-to-end generation results. Retrieval metrics are therefore used as diagnostics
alongside generation evaluation rather than as the only measure of system quality.

Detailed evaluation experiments are available in
[evaluation/results.md](evaluation/results.md).

### Custom Pipeline vs. LangChain

| Metric | Custom | LangChain |
|---|---:|---:|
| Hit@1 | 20.0% | 20.0% |
| Hit@3 | 73.3% | 73.3% |
| Hit@5 | 80.0% | 80.0% |
| Generation pass rate | 88.9% | 88.9% |
| LLM fallback latency | 3.367 s | 3.123 s |

LangChain reproduced the retrieval and generation quality of the custom
pipeline while providing cleaner composition through LCEL. However, it also
introduced additional framework dependencies and abstraction overhead.

The custom pipeline remains the primary implementation because it is small,
deterministic, and directly debuggable. The LangChain implementation is kept
as a comparative implementation demonstrating framework integration.

## Known Limitation

One of the 9 generation cases currently fails for an RTSP single-snapshot request.
FAISS ranks a semantically similar camera_snapshot_interval pattern slightly above the intended snapshot pattern.

This is kept as a known limitation rather than optimizing specifically for a 100% benchmark score.
A future improvement could introduce second-stage reranking for similar patterns.

## Regression Testing & CI/CD

pytest covers retrieval/generation regression checks and FastAPI endpoint behavior.

Regression safeguards:

Generation pass rate >= 80%
Retrieval Hit@5 >= 70%

API tests cover:

- health endpoint
- valid generation requests
- invalid input validation
- internal server errors

GitHub Actions automatically runs the full test suite on pushes and pull requests to the main branch.

After a successful test run on the main branch, the CD workflow builds a new Docker image,
pushes it to Azure Container Registry, and deploys the tested commit to Azure Container Apps.

## Tech Stack

- Language: Python
- Embeddings: SentenceTransformers
- Vector Search: FAISS
- RAG Framework Comparison: LangChain + LCEL
- Local LLM: Qwen2.5-Coder:7b via Ollama
- Cloud LLMs: Azure OpenAI, OpenRouter
- API Framework: FastAPI + Pydantic
- Evaluation: Custom retrieval and generation evaluators + Python AST
- Testing: pytest
- CI/CD: GitHub Actions
- Containerization: Docker + Docker Compose
- Cloud: Microsoft Azure Container Apps + Azure Container Registry
- Authentication: GitHub Actions -> Azure via OIDC

## Setup

```bash
git clone https://github.com/omerzcn/rag-code-generation-pipeline.git
cd rag-code-generation-pipeline

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

For local LLM usage:

```bash
ollama pull qwen2.5-coder:7b
```

Run the evaluations:

```bash
python3 evaluation/evaluate_retrieval.py
python3 evaluation/evaluate_generation.py
python3 evaluation/evaluate_latency.py
```

Run tests:

```bash
python -m pytest -v
```

## Docker

The application can also be run as a Docker container using Docker Compose.

The Docker setup includes the FastAPI application, persisted FAISS index, retrieved chunks, and skill files.
Runtime configuration and secrets are provided through environment variables rather than being stored in the image.

Start the application:

```bash
docker compose up --build -d
```

Check the container status:

```bash
docker compose ps
```

The API is available at:

http://localhost:8000

Swagger documentation:

http://localhost:8000/docs

Stop the application:

```bash
docker compose down
```

For local LLM generation, Ollama must be running on the host with the required model available:

```bash
ollama pull qwen2.5-coder:7b
```

## Azure Deployment

The containerized API is deployed on Microsoft Azure.
A live deployment is running on Azure Container Apps.

GitHub
    ↓
GitHub Actions CI/CD
    ↓
Azure Container Registry
    ↓
Azure Container Apps
    ↓
FastAPI + RAG Pipeline
    ↓
Azure OpenAI

Deployment secrets are stored outside the Docker image using Azure Container Apps secrets,
and GitHub Actions authenticates to Azure using OIDC.
