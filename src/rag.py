import os
from sentence_transformers import SentenceTransformer
import ollama

from qdrant_config import get_client, COLLECTION_NAME


class RAGSystem:
    def __init__(self, model_name="llama3.2"):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qdrant_client = get_client()
        self.llm_model = model_name
        self.ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        
    def search(self, query: str, limit: int = 5, corpus_filter: str = None):
        query_vector = self.embedding_model.encode(query).tolist()
        
        search_params = {
            "collection_name": COLLECTION_NAME,
            "query_vector": query_vector,
            "limit": limit
        }
        
        if corpus_filter:
            search_params["query_filter"] = {
                "must": [{"key": "corpus_name", "match": {"value": corpus_filter}}]
            }
        
        results = self.qdrant_client.search(**search_params)
        return results
    
    def generate_answer(self, query: str, limit: int = 5, corpus_filter: str = None):
        results = self.search(query, limit, corpus_filter)
        
        if not results:
            return "No relevant documents found."
        
        context = "\n\n".join([
            f"[{r.payload['corpus_name']} - {r.payload['document_filename']}]\n{r.payload['text']}"
            for r in results
        ])
        
        prompt = f"""Basándote en el siguiente contexto, responde la pregunta del usuario.

Contexto:
{context}

Pregunta: {query}

Respuesta:"""
        
        client = ollama.Client(host=f"http://{self.ollama_host}:11434")
        response = client.generate(model=self.llm_model, prompt=prompt)
        
        return {
            "answer": response["response"],
            "sources": [
                {
                    "corpus": r.payload["corpus_name"],
                    "document": r.payload["document_filename"],
                    "score": r.score
                }
                for r in results
            ]
        }


if __name__ == "__main__":
    rag = RAGSystem()
    
    query = "¿Qué información hay sobre el río?"
    result = rag.generate_answer(query)
    
    print(f"Query: {query}\n")
    print(f"Answer: {result['answer']}\n")
    print("Sources:")
    for src in result['sources']:
        print(f"  - {src['corpus']}: {src['document']} (score: {src['score']:.3f})")
