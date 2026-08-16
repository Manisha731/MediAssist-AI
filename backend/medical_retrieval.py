import httpx
from vectorstore import embedding_model, chroma_client

medline_collection = chroma_client.get_or_create_collection(name="medline_knowledge")

MEDLINE_BASE = "https://wsearch.nlm.nih.gov/ws/query"


def fetch_medline_topic(term: str) -> list[dict]:
    """Search MedlinePlus for a term, return top results with title + summary."""
    params = {"db": "healthTopics", "term": term}
    response = httpx.get(MEDLINE_BASE, params=params)
    
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response.text)
    
    results = []
    for doc in root.findall(".//document")[:3]:  # top 3 results
        title = doc.find(".//content[@name='title']")
        summary = doc.find(".//content[@name='FullSummary']")
        results.append({
            "title": title.text if title is not None else "",
            "summary": summary.text if summary is not None else ""
        })
    return results


def store_medline_knowledge(term: str):
    """Fetch, chunk, embed, and store MedlinePlus content for a term."""
    topics = fetch_medline_topic(term)
    for i, topic in enumerate(topics):
        text = f"{topic['title']}\n{topic['summary']}"
        embedding = embedding_model.encode([text]).tolist()
        medline_collection.add(
            documents=[text],
            embeddings=embedding,
            ids=[f"{term}_{i}"]
        )
    return len(topics)


def retrieve_relevant_knowledge(query: str, n_results: int = 2) -> list[str]:
    """Query the stored MedlinePlus knowledge for relevant content."""
    query_embedding = embedding_model.encode([query]).tolist()
    results = medline_collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results["documents"][0] if results["documents"] else []