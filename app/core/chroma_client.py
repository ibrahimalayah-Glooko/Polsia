from app.config import settings

_collection = None


def get_collection():
    """Lazily create and cache the ChromaDB memory collection."""
    global _collection
    if _collection is None:
        import chromadb

        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        _collection = client.get_or_create_collection("memory")
    return _collection
