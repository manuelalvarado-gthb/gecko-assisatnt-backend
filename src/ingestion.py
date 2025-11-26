import os
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct
from tqdm import tqdm

from geco_client import (
    get_token, get_user_corpus, get_corpus_table, 
    get_corpus_documents, get_document_content
)
from qdrant_config import get_client, init_collection, COLLECTION_NAME


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def ingest_corpus(username: str, password: str):
    print("Initializing embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Connecting to Qdrant...")
    client = get_client()
    init_collection(client, vector_size=384)
    
    print("Getting GECO token...")
    token = get_token(username, password)
    
    print("Fetching corpus list...")
    corpus_list = get_user_corpus(token)
    proyectos = corpus_list["data"]["proyectos"]
    
    print(f"\nFound {len(proyectos)} corpus to process\n")
    
    point_id = 0
    
    for proyecto in proyectos:
        corpus_id = proyecto["id"]
        corpus_name = proyecto["nombre"]
        corpus_public = proyecto["publico"]
        corpus_colabora = proyecto["colabora"]
        
        print(f"Processing corpus: {corpus_name} (ID: {corpus_id})")
        
        try:
            table_data = get_corpus_table(token, corpus_id)
            metadatos_info = table_data["data"]["metadatos"]
            tabla = table_data["data"]["tabla"]
            
            metadatos_map = {m[0]: m[1] for m in metadatos_info}
            
            for doc_row in tqdm(tabla, desc=f"  Documents"):
                doc_id = doc_row[0]
                doc_filename = doc_row[1]
                doc_metadatos = doc_row[2]
                
                metadata_dict = {
                    metadatos_map.get(m[0], f"meta_{m[0]}"): m[1] 
                    for m in doc_metadatos
                }
                
                try:
                    content_resp = get_document_content(token, corpus_id, doc_id)
                    content = content_resp.get("data", "")
                    
                    if not content or not isinstance(content, str):
                        continue
                    
                    chunks = chunk_text(content)
                    
                    for chunk_idx, chunk in enumerate(chunks):
                        embedding = model.encode(chunk).tolist()
                        
                        payload = {
                            "corpus_id": corpus_id,
                            "corpus_name": corpus_name,
                            "corpus_public": corpus_public,
                            "corpus_colabora": corpus_colabora,
                            "document_id": doc_id,
                            "document_filename": doc_filename,
                            "chunk_index": chunk_idx,
                            "text": chunk,
                            **metadata_dict
                        }
                        
                        point = PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload=payload
                        )
                        
                        client.upsert(
                            collection_name=COLLECTION_NAME,
                            points=[point]
                        )
                        
                        point_id += 1
                        
                except Exception as e:
                    print(f"    Error processing document {doc_id}: {e}")
                    continue
                    
        except Exception as e:
            print(f"  Error processing corpus {corpus_id}: {e}")
            continue
    
    print(f"\n✓ Ingestion complete! Total points: {point_id}")


if __name__ == "__main__":
    username = os.getenv("GECO_USERNAME", "gsierram")
    password = os.getenv("GECO_PASSWORD", "Tamara2005")
    ingest_corpus(username, password)
