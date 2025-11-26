from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import sys
sys.path.append('/app/src')

from src.rag import RAGSystem
from src.ingestion import ingest_corpus

app = FastAPI(title="GECO RAG API")
rag_system = None


class QueryRequest(BaseModel):
    query: str
    limit: int = 5
    corpus_filter: Optional[str] = None


class IngestRequest(BaseModel):
    username: str
    password: str


class DocumentIngestRequest(BaseModel):
    corpus_id: int
    corpus_name: str
    corpus_public: bool
    corpus_colabora: bool
    document_id: int
    document_filename: str
    content: str
    metadata: dict = {}


def get_rag_system():
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system


@app.post("/ingest")
async def trigger_ingestion(request: IngestRequest):
    try:
        ingest_corpus(request.username, request.password)
        return {"status": "success", "message": "Ingestion completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/document")
async def ingest_single_document(request: DocumentIngestRequest):
    """Ingest or update a single document"""
    try:
        from sentence_transformers import SentenceTransformer
        from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
        from src.qdrant_config import get_client, COLLECTION_NAME
        from src.ingestion import chunk_text
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        client = get_client()
        
        # Delete existing chunks for this document
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(key="corpus_id", match=MatchValue(value=request.corpus_id)),
                    FieldCondition(key="document_id", match=MatchValue(value=request.document_id))
                ]
            )
        )
        
        # Get next available ID
        collection_info = client.get_collection(COLLECTION_NAME)
        next_id = collection_info.points_count
        
        # Chunk and embed
        chunks = chunk_text(request.content)
        points = []
        
        for chunk_idx, chunk in enumerate(chunks):
            embedding = model.encode(chunk).tolist()
            
            payload = {
                "corpus_id": request.corpus_id,
                "corpus_name": request.corpus_name,
                "corpus_public": request.corpus_public,
                "corpus_colabora": request.corpus_colabora,
                "document_id": request.document_id,
                "document_filename": request.document_filename,
                "chunk_index": chunk_idx,
                "text": chunk,
                **request.metadata
            }
            
            points.append(PointStruct(
                id=next_id + chunk_idx,
                vector=embedding,
                payload=payload
            ))
        
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        
        return {
            "status": "success",
            "document_id": request.document_id,
            "chunks_created": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/document/{corpus_id}/{document_id}")
async def delete_document(corpus_id: int, document_id: int):
    """Delete all chunks of a document"""
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        from src.qdrant_config import get_client, COLLECTION_NAME
        
        client = get_client()
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(key="corpus_id", match=MatchValue(value=corpus_id)),
                    FieldCondition(key="document_id", match=MatchValue(value=document_id))
                ]
            )
        )
        
        return {
            "status": "success",
            "message": f"Document {document_id} from corpus {corpus_id} deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search(request: QueryRequest):
    try:
        results = get_rag_system().search(
            request.query, 
            request.limit, 
            request.corpus_filter
        )
        return {
            "results": [
                {
                    "text": r.payload["text"],
                    "corpus": r.payload["corpus_name"],
                    "document": r.payload["document_filename"],
                    "score": r.score,
                    "metadata": {k: v for k, v in r.payload.items() 
                               if k not in ["text", "corpus_name", "document_filename"]}
                }
                for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query(request: QueryRequest):
    try:
        result = get_rag_system().generate_answer(
            request.query, 
            request.limit, 
            request.corpus_filter
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
