import os
import re
import html
import httpx
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from openai import OpenAI
from vectorstore import embedding_model, chroma_client

load_dotenv()

medline_collection = chroma_client.get_or_create_collection(name="medline_knowledge")

MEDLINE_BASE = "https://wsearch.nlm.nih.gov/ws/query"

_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=30,
    max_retries=6,
)
_MODEL = "openai/gpt-oss-20b"


def clean_html(text: str) -> str:
    """Remove HTML tags from MedlinePlus text and tidy the whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)   # remove tags like <span class="qt0">
    text = html.unescape(text)             # turn &amp; etc. into normal characters
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_key_terms(summary: str, max_terms: int = 4) -> list[str]:
    """Ask the model which medical conditions this report summary points to.

    Returns an empty list if extraction fails — the pipeline continues
    without extra background rather than failing outright.
    """
    prompt = f"""Read this medical report summary and list the specific medical conditions, diseases, or health topics it points to (for example: "type 2 diabetes", "high cholesterol", "anemia", "hypothyroidism").

Report summary:
{summary}

Rules:
- Return at most {max_terms} items.
- Use short, common condition names, not individual lab test names like "A1C" or "creatinine".
- If the summary shows no specific condition, return nothing.
- Output ONLY a comma-separated list, nothing else. No numbering, no explanation, no markdown."""

    try:
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0,
            reasoning_effort="low",
        )
        raw = response.choices[0].message.content.strip()
        print(f"[medical_retrieval] raw extraction response: {raw!r}")
        terms = [t.strip() for t in raw.split(",") if t.strip()]
        return terms[:max_terms]
    except Exception as e:
        print(f"[medical_retrieval] term extraction failed: {e}")
        return []


def fetch_medline_topic(term: str) -> list[dict]:
    """Search MedlinePlus for a term, return top results with title + summary.

    Returns an empty list if MedlinePlus is unreachable — the pipeline
    continues without medical context rather than failing outright.
    """
    params = {"db": "healthTopics", "term": term}
    headers = {"User-Agent": "MediAssist-AI/1.0 (student project)"}

    for attempt in range(3):  # two retries
        try:
            response = httpx.get(
                MEDLINE_BASE,
                params=params,
                headers=headers,
                timeout=15.0,
            )
            response.raise_for_status()
            root = ET.fromstring(response.text)
            break
        except (httpx.HTTPError, ET.ParseError) as e:
            if attempt == 2:
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
    docs = results["documents"][0] if results["documents"] else []
    return [clean_html(d) for d in docs]