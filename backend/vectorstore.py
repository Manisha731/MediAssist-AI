import chromadb
from sentence_transformers import SentenceTransformer

chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="report_chunks")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def store_chunks(chunks: list[str], report_id: str):
    embeddings = embedding_model.encode(chunks).tolist()
    ids = [f"{report_id}_chunk_{i}" for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )
    return len(chunks)