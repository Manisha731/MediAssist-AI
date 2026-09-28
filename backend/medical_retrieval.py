import httpx
import xml.etree.ElementTree as ET
from vectorstore import embedding_model, chroma_client

medline_collection = chroma_client.get_or_create_collection(name="medline_knowledge")

MEDLINE_BASE = "https://wsearch.nlm.nih.gov/ws/query"


def fetch_medline_topic(term: str) -> list[dict]:
    """Search MedlinePlus for a term, return top results with title + summary.

    Returns an empty list if MedlinePlus is unreachable — the pipeline
    continues without medical context rather than failing outright.
    """
    params = {"db": "healthTopics", "term": term}
    headers = {"User-Agent": "MediAssist-AI/1.0 (student project)"}

    for attempt in range(2):  # one retry
        try:
            response = httpx.get(
                MEDLINE_BASE,
                params=params,
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            root = ET.fromstring(response.text)
            break
        except (httpx.HTTPError, ET.ParseError) as e:
            if attempt == 1:
                print(f"[medical_retrieval] MedlinePlus unavailable for '{term}': {e}")
                return []

    results = []
    for doc in root.findall(".//document")[:3]:  # top 3 results
        title = doc.find(".//content[@name='title']")
        summary = doc.find(".//content[@name='FullSummary']")
        results.append({
            "title": title.text if title is not None else "",
            "summary": summary.text if summary is not None else ""
        })
    return results


def store_medline_knowledge(term: str) -> int:
    """Fetch, chunk, embed, and store MedlinePlus content for a term.

    Skips the network call entirely if this term is already in Chroma.
    """
    existing = medline_collection.get(ids=[f"{term}_0"])
    if existing["ids"]:
        return 0  # already cached from a previous run

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