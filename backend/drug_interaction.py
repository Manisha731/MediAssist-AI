import httpx

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"
OPENFDA_BASE = "https://api.fda.gov/drug/label.json"


def get_generic_name(drug_name: str) -> str:
    """Convert a brand/messy drug name to its generic ingredient name using RxNorm."""
    url = f"{RXNORM_BASE}/rxcui.json"
    response = httpx.get(url, params={"name": drug_name})
    data = response.json()
    
    rxcui_list = data.get("idGroup", {}).get("rxnormId")
    if not rxcui_list:
        return drug_name  # fallback: couldn't resolve, use original name
    
    rxcui = rxcui_list[0]
    related_url = f"{RXNORM_BASE}/rxcui/{rxcui}/related.json"
    related_response = httpx.get(related_url, params={"tty": "IN"})
    related_data = related_response.json()
    
    concept_groups = related_data.get("relatedGroup", {}).get("conceptGroup", [])
    for group in concept_groups:
        if group.get("tty") == "IN" and "conceptProperties" in group:
            return group["conceptProperties"][0]["name"]
    
    return drug_name


def get_drug_interactions(generic_name: str) -> dict:
    """Fetch openFDA label data for a drug, focused on interactions."""
    query = f'openfda.generic_name:"{generic_name.upper()}"'
    response = httpx.get(OPENFDA_BASE, params={"search": query, "limit": 1})
    
    if response.status_code != 200:
        return {"found": False, "reason": "No FDA label data found (may not be a prescription drug)"}
    
    data = response.json()
    results = data.get("results", [])
    if not results:
        return {"found": False, "reason": "No results"}
    
    result = results[0]
    return {
        "found": True,
        "drug_interactions": result.get("drug_interactions", ["No interaction data listed"])[0]
    }


def check_drug_interactions(drug_names: list[str]) -> list[dict]:
    """For a list of drug names, resolve each to generic name and fetch interaction data."""
    results = []
    for drug in drug_names:
        generic = get_generic_name(drug)
        interaction_data = get_drug_interactions(generic)
        results.append({
            "input_name": drug,
            "generic_name": generic,
            **interaction_data
        })
    return results