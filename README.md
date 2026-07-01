# Intelligent Actuator Data Agent

This project implements a FastAPI microservice that exposes an AI agent specialized in Series 76 electric actuators. The agent supports conversational technical assistance with two core capabilities:

- Specific data retrieval by Base Part Number.
- Product recommendation from user technical requirements.

The implementation is aligned with the assessment scenario and uses LangChain tools over locally processed data.

## Design Choices and Service Architecture

### 1. Agent orchestration
- Framework: LangChain.
- Conversation state: `thread_id`-based continuity using LangGraph `MemorySaver` as checkpointer.
- Tool-first behavior: the agent is instructed to query tools for technical answers.

### 2. Data extraction and preprocessing
- Raw technical tables are extracted from the provided PDF using Google AI Studio (`gemini-2.5-flash`) with a strict Pydantic schema.
- A preprocessing pipeline transforms extracted rows into structured tabular format.

### 3. Hybrid storage strategy (SQLite + ChromaDB)
- Structured technical data is stored in local SQLite (`data/processed/electric_data_table.db`).
- Business/contextual document content is chunked and stored in local ChromaDB (`data/processed/chroma_db`).
- Embeddings are generated with OpenAI (`text-embedding-3-small`).

### 4. API layer
- Backend: FastAPI.
- Endpoint: `POST /api/conversation`.
- Request/response models are validated with Pydantic.

## Repository Inputs and Data Files

Raw files expected by the ingestion script:
- `data/raw/series_76_tables.pdf`
- `data/raw/series_76_summary.pdf`

Processed outputs generated/used by the service:
- `data/processed/electric_data_table.db`
- `data/processed/chroma_db/`


## Setup Instructions

### Prerequisites
- Docker + Docker Compose.
- Optional local runtime: Python 3.11 and `uv`.

### Environment Variables
1. Create `.env` from `.env.example`.

Linux/macOS:
```bash
cp .env.example .env
```

Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

2. Set real values in `.env`:
- `OPENAI_API_KEY` (required for runtime embeddings/tool context retrieval).
- `GOOGLE_API_KEY` (required only when running ingestion pipeline).

## Data Processing Pipeline

Script: `scripts/ingests.py`

What it does:
- Extracts structured actuator rows from `series_76_tables.pdf`.
- Cleans and normalizes numeric columns.
- Writes `electric_data_table` into SQLite.
- Extracts, chunks, embeds, and stores summary context in ChromaDB.

Run with `uv`:
```bash
uv run python scripts/ingests.py
```

Run with standard Python:
```bash
python scripts/ingests.py
```

*IMPORTANT: processed data is already included in this repository for quick evaluation. Re-running ingestion is only needed if you want to rebuild artifacts.*

## How to Run (Docker)

From repository root:
```bash
docker-compose up --build -d
```

Service URL:
- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

Stop service:
```bash
docker-compose down
```

## API Usage

Endpoint:
- `POST /api/conversation`

Request body:
```json
{
    "query": "Recommend me a weatherproof actuator operating at 110V with at least 150 Nm torque.",
    "thread_id": "session-123"
}
```

Notes:
- `thread_id` is optional. If omitted, the API creates one.
- Reusing the same `thread_id` keeps conversation continuity.

Example with curl:
```bash
curl -X POST "http://localhost:8000/api/conversation" \
    -H "Content-Type: application/json" \
    -d '{"query":"Recommend me a weatherproof actuator operating at 110V with at least 150 Nm torque.","thread_id":"session-123"}'
```

Example with PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/conversation" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"query":"Recommend me a weatherproof actuator operating at 110V with at least 150 Nm torque.","thread_id":"session-123"}'
```

Expected response shape:
```json
{
    "answer": "I recommend model ...",
    "thread_id": "session-123",
    "sources": [
        "Tool: query_by_specs"
    ]
}
```

## Non-Happy Path Test Cases

These cases are useful to validate robustness beyond the happy path.

### 1. Missing required field (`query`)
Command:
```bash
curl -X POST "http://localhost:8000/api/conversation" \
    -H "Content-Type: application/json" \
    -d '{"thread_id":"fail-001"}'
```

Expected:
- HTTP `422 Unprocessable Entity`
- Validation error indicating `query` is required.

### 2. Empty query string
Command:
```bash
curl -X POST "http://localhost:8000/api/conversation" \
    -H "Content-Type: application/json" \
    -d '{"query":"","thread_id":"fail-002"}'
```

Expected:
- HTTP `422 Unprocessable Entity`
- Validation error for minimum query length.

### 3. Malformed JSON body
Command:
```bash
curl -X POST "http://localhost:8000/api/conversation" \
    -H "Content-Type: application/json" \
    -d '{"query":"test", "thread_id":"fail-003"'
```

Expected:
- HTTP `422 Unprocessable Entity`
- JSON parsing error in request body.

### 4. Non-existent part number (functional negative case)
Command:
```bash
curl -X POST "http://localhost:8000/api/conversation" \
    -H "Content-Type: application/json" \
    -d '{"query":"Give me details for base part number DOES-NOT-EXIST-999","thread_id":"fail-004"}'
```

Expected:
- HTTP `200 OK`
- Agent response indicating no matching actuator was found.


# Design Notes: How I Built It
I built this incrementally. As I explored the data and understood the requirements better, I adjusted the approach to keep it reliable, easy to validate, and reasonably cost-efficient.

### Storing the technical tables
The data extracted from series_76_tables.pdf is highly structured, mostly exact values like base_part_number and numeric specs. That pointed toward a relational database rather than a vector store, so I went with SQLite. It is simple, and it fits the kind of exact-match lookups this table needs.

### Improving the extraction pipeline
This took a couple of iterations. At first, some motor_power values came out duplicated, while others were missing. Looking into the generated data, I found the issue: my normalization step was not consistently identifying each row.

I fixed this by using base_part_number as the primary identifier for each record and adjusting the cleaning logic around it. After that change, the dataset became much more consistent.

### Choosing how to handle the summary PDF
My first instinct was to keep the summary text in memory. The document is small, and that would have been enough for this assessment. I ended up implementing a RAG pipeline with ChromaDB instead. It adds some complexity, but it retrieves relevant context more reliably and scales better if more documentation gets added later.

I used text-embedding-3-small for embeddings to keep costs low while maintaining good retrieval quality.

### Keeping API costs under control
I tried to avoid spending the provided OpenAI budget on experimentation. Most of the early iterations were built and tested with free tokens on Google AI Studio. Once I was satisfied, I moved to the OpenAI API for final end-to-end validation.
