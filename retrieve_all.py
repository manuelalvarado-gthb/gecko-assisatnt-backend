import requests
import json
import os

BASE = "https://devsys.iingen.unam.mx/geco4/proyectos/apidocs"


def get_token(username: str, password: str):
    url = f"{BASE}/get-token"
    resp = requests.post(url, data={"username": username, "password": password})
    resp.raise_for_status()
    return resp.json().get("token")


def get_headers(token: str):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }


def get_user_corpus(token: str):
    url = f"{BASE}/corpus/"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    return resp.json()


def get_corpus_documents(token: str, corpus_id: int):
    url = f"{BASE}/corpus/{corpus_id}"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    return resp.json()


def get_document_content(token: str, corpus_id: int, doc_id: int):
    url = f"{BASE}/corpus/{corpus_id}/{doc_id}"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    return resp.json()


def retrieve_all(username: str, password: str, output_dir: str = "corpus_data"):
    os.makedirs(output_dir, exist_ok=True)
    
    token = get_token(username, password)
    print(f"Token obtained: {token[:20]}...\n")
    
    corpus_list = get_user_corpus(token)
    proyectos = corpus_list["data"]["proyectos"]
    print(f"Found {len(proyectos)} corpus\n")
    
    for proyecto in proyectos:
        corpus_id = proyecto["id"]
        corpus_name = proyecto["nombre"]
        print(f"Processing: {corpus_name} (ID: {corpus_id})")
        
        corpus_dir = os.path.join(output_dir, f"{corpus_id}_{corpus_name.replace('/', '_')}")
        os.makedirs(corpus_dir, exist_ok=True)
        
        docs = get_corpus_documents(token, corpus_id)
        documents = docs["data"]
        print(f"  Found {len(documents)} documents")
        
        for doc in documents:
            doc_id = doc["id"]
            doc_name = doc["archivo"]
            has_rights = doc["derechos"]
            
            print(f"    - {doc_name} (ID: {doc_id}, Rights: {has_rights})")
            
            try:
                content = get_document_content(token, corpus_id, doc_id)
                
                doc_file = os.path.join(corpus_dir, f"{doc_id}_{doc_name}")
                with open(doc_file, "w", encoding="utf-8") as f:
                    if "data" in content:
                        f.write(content["data"])
                    else:
                        json.dump(content, f, indent=2, ensure_ascii=False)
                
                print(f"      ✓ Saved to {doc_file}")
            except Exception as e:
                print(f"      ✗ Error: {e}")
        
        print()
    
    print(f"All data saved to {output_dir}/")


if __name__ == "__main__":
    retrieve_all("gsierram", "Tamara2005")
