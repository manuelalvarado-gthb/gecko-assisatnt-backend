# GECO RAG System

Complete pipeline for ingesting GECO corpus documents into Qdrant vector database and querying with RAG using Ollama.

## Architecture

- **Qdrant**: Vector database for storing document embeddings
- **Ollama**: Local LLM for generating answers
- **Ingestion Service**: Python service for fetching and embedding GECO documents
- **FastAPI**: REST API for search and RAG queries

## Setup

### 1. Start Services

```bash
docker-compose up -d
```

### 2. Pull Ollama Model

```bash
docker exec -it gecko_assistant-ollama-1 ollama pull llama3.2
```

### 3. Run Ingestion

```bash
docker exec -it gecko_assistant-ingestion-1 python src/ingestion.py
```

Or via API:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"username": "gsierram", "password": "Tamara2005"}'
```

## Usage

### Start API Server

```bash
docker exec -it gecko_assistant-ingestion-1 python src/api.py
```

### Full Ingestion (All Corpus)

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"username": "gsierram", "password": "Tamara2005"}'
```

### Ingest/Update Single Document

```bash
curl -X POST http://localhost:8000/ingest/document \
  -H "Content-Type: application/json" \
  -d '{
    "corpus_id": 999,
    "corpus_name": "My Corpus",
    "corpus_public": true,
    "corpus_colabora": false,
    "document_id": 1,
    "document_filename": "document.txt",
    "content": "Document text content here...",
    "metadata": {"Autor": "Name", "Año": "2025"}
  }'
```

### Delete Document

```bash
curl -X DELETE http://localhost:8000/document/{corpus_id}/{document_id}
```

### Search Documents

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "río tiempo agua", "limit": 5}'
```

### RAG Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Qué información hay sobre el río?", "limit": 5}'
```

### Filter by Corpus

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "medicina", "corpus_filter": "Corpus de medicina"}'
```

## Local Development

### Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Locally

```bash
# Set environment variables
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
export OLLAMA_HOST=localhost
export GECO_USERNAME=gsierram
export GECO_PASSWORD=Tamara2005

# Run ingestion
python src/ingestion.py

# Run API
python src/api.py

# Test RAG
python src/rag.py
```

## Data Schema

Each vector point contains:

```json
{
  "corpus_id": 29,
  "corpus_name": "ejemplo de corpus",
  "corpus_public": true,
  "corpus_colabora": false,
  "document_id": 2218,
  "document_filename": "Mirar el río hecho de tiempo y agua.txt",
  "chunk_index": 0,
  "text": "chunk content...",
  "Lengua": "español",
  "Título principal": "...",
  "Autor": "...",
  "Año": "2022"
}
```

## Services

- Qdrant UI: http://localhost:6333/dashboard
- API Docs: http://localhost:8000/docs
- Ollama: http://localhost:11434
