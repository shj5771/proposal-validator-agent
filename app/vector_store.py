import json
from pathlib import Path
from app.core.database import get_chroma_client
from app.core.embedding import get_embedding_function

COLLECTION_NAME = "proposal_validation_guidelines"

def _get_collection():
    client = get_chroma_client()
    embedding_fn = get_embedding_function()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

def seed_if_empty():
    collection = _get_collection()
    if collection.count() > 0:
        return

    data_path = Path(__file__).parent.parent / "data" / "architecture_guidelines.json"
    if not data_path.exists():
        return

    with open(data_path, encoding="utf-8") as f:
        docs = json.load(f)

    collection.add(
        ids=[d["id"] for d in docs],
        documents=[f"{d['title']}\n{d['content']}" for d in docs],
        metadatas=[{"category": d["category"]} for d in docs],
    )

def search_documents(query: str, n_results: int = 3) -> list[dict]:
    collection = _get_collection()
    if collection.count() == 0:
        return []

    results = collection.query(query_texts=[query], n_results=n_results)
    documents = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            documents.append({
                "content": doc,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None,
            })
    return documents