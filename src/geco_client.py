import requests

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


def get_corpus_table(token: str, corpus_id: int):
    url = f"{BASE}/corpus/{corpus_id}/tabla"
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
