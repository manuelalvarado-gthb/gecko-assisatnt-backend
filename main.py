import requests

BASE = "https://devsys.iingen.unam.mx/geco4/proyectos/apidocs"


def get_token(username: str, password: str):
    """Obtiene un token JWT del API GECO."""
    url = f"{BASE}/get-token"
    data = {"username": username, "password": password}

    resp = requests.post(url, data=data)
    resp.raise_for_status()
    token = resp.json().get("token")
    return token


def get_headers(token: str):
    """Headers necesarios para todas las llamadas."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }


def get_user_corpus(token: str):
    """Lista todos los corpus que el usuario puede consultar."""
    url = f"{BASE}/corpus/"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    return resp.json()


def get_corpus_metadata(token: str, corpus_id: int):
    """Obtiene metadatos del corpus."""
    url = f"{BASE}/corpus/{corpus_id}"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    return resp.json()


def get_corpus_documents(token: str, corpus_id: int):
    """Listado de documentos de un corpus."""
    url = f"{BASE}/corpus/{corpus_id}"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    return resp.json()


def get_corpus_table(token: str, corpus_id: int):
    """Tabla completa: documentos + metadatos por documento."""
    url = f"{BASE}/corpus/{corpus_id}/tabla"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------
# USE CASE COMPLETO
# --------------------------------------------------------

if __name__ == "__main__":
    # 1) Obtener token usando tus credenciales
    token = get_token("gsierram", "Tamara2005")
    print("\nTOKEN OBTENIDO:\n", token, "\n")

    # 2) Corpus accesibles al usuario
    corpus = get_user_corpus(token)
    print("CORPUS DISPONIBLES:\n", corpus, "\n")

    # EJEMPLO: elegir automáticamente el primero del listado
    proyectos = corpus["data"]["proyectos"]
    corpus_id = proyectos[0]["id"]
    print(f"Usando corpus ID = {corpus_id}\n")

    # 3) Obtener metadatos del corpus
    metadata = get_corpus_metadata(token, corpus_id)
    print("METADATOS DEL CORPUS:\n", metadata, "\n")

    # 4) Obtener documentos del corpus
    docs = get_corpus_documents(token, corpus_id)
    print("DOCUMENTOS DEL CORPUS:\n", docs, "\n")

    # 5) Obtener tabla general (metadatos + documentos)
    tabla = get_corpus_table(token, corpus_id)
    print("TABLA COMPLETA DEL CORPUS:\n", tabla, "\n")