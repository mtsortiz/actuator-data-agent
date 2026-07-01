# Intelligent Actuator Data Agent
This project consists of a microservice based on FastAPI that implements an ai agent specialized in the Series 76 electric actuators. The agent is designed to hold natural conversations, retrieve precise technical specifications, and make product recommendations based on client requirements.

## Desing Choices and Service Architecture
The system architecture was designed following a modular, efficient, and decoupled approach, adhering to the following guidelines:
- Agent Orchestration Framework: 
    - Powered by LangChain. Using thread_scope memory persitence to maintain conversation context via the `trhead_id` parameter.
- Data Extraction and Processing:
    - Data extraction handled via google ai studio API.
    - Pydantic schema to guarantee consistent output
- Hybrid Data Storage (SQLite + ChromaDB):
    - Technical tables from the pdf are stored in a local SQLite database.
    - Conceptual context from the summary pdf is chunked and stored in a local ChromaDB vector using `text-embbedings-3-small`. The agent queries this vector store to answer business oriented questions using the `query_business_context` tool.
- Web Server:
    -Endpoint built on FastAPI with Pydantic validation.

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed on your machine.
- (Optional) Python 3.11 or uv package manager
### Environment Variables
1. Copy the .env.example file to create a .env file in the root directory: ```cp .env.example .env ``` 
2. Open the .env file and replace the placeholder values with yor keys

### Data Processing and Ingestion Pipeline
- *Important: Preprocessed database files are already included in the repository. Running the script is only necessary if you add new raw files or want to rebuild databases.* 
- The project features a data preprocessing pipeline that parses the raw pdf into sqlite and chromadb databases in `data/processed/` before running the server.
To run the data ingestion: 
    - Using uv: 
        ```bash 
        uv run python scripts/ingests.py
        ```
    - Using standard python: 
        ```bash
        python scripts/ingests.py
        ```

## How to Run
The app is fully containerized with Docker.
### 1. Build and Run the Container
Run the following command in the root directory to compile the Docker image and start the FastAPI server: 
```bash
docker-compose up --build -d
``` 
The server will start running in the background on port 8000 (`http://localhost:8000`).

### 2. Verify the Server Status
You can access the API documentation with Swagger by navigating to `http://localhost:8000/docs`.

## API Testing and Endpoint Usage
The endpoint to interact with the agent is `POST /api/conversation`. You can test it using the following commands:
- Option A: using `curl` (terminal/bash)
    ```bash
    curl -X POST "http://localhost:8000/api/conversation" \
    -H "Content-Type: application/json" \
    -d '{"query": "Recommend me a weatherproof actuator operating at 110V with at least 150 Nm torque.", "thread_id": "session-123"}'
    ```
- Option B: usinf powershell
    ```powershell
    Invoke-RestMethod -Uri "http://localhost:8000/api/conversation" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"query": "Recommend me a weatherproof actuator operating at 110V with at least 150 Nm torque.", "thread_id": "session-123"}'
    ```

#### Expected Server Response:
```json
{
  "answer": "I recommend the model **762A00-11300000/A**. It has a Weatherproof     enclosure, operates at 110V (Single Phase), and delivers 150 Nm of On/Off output torque (130 Nm of modulating torque) with a motor power of 40 Watts. Alternatively, you could consider...",
  "thread_id": "session-123",
  "sources": [
    "Tool: query_by_specs"
  ]
}
```