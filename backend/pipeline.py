from io import BytesIO
from pypdf import PdfReader

from vectorstore import store_chunks
from summarizer import summarize_report
from drug_interaction import check_drug_interactions
from medical_retrieval import store_medline_knowledge, retrieve_relevant_knowledge, extract_key_terms
from explanation_agent import generate_patient_explanation


def run_full_pipeline(pdf_bytes: bytes, filename: str, drug_names: list[str] = None) -> dict:
    # Step 1: Extract text from PDF
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()

    # Step 2: Chunk and store in Chroma
    from main import chunk_text
    chunks = chunk_text(extracted_text)
    store_chunks(chunks, report_id=filename)

    # Step 3: Report Summarizer agent
    summary = summarize_report(chunks)

    # Step 4: Drug Interaction Agent
    drug_results = []
    if drug_names:
        drug_results = check_drug_interactions(drug_names)

   # Step 5: Medical Knowledge Retrieval Agent
    key_terms = extract_key_terms(summary)
    print(f"[pipeline] extracted terms: {key_terms}")
    for term in key_terms:
        store_medline_knowledge(term)  # cached after first successful fetch

    try:
        medical_context = retrieve_relevant_knowledge(summary)
    except Exception as e:
        print(f"[pipeline] knowledge retrieval failed: {e}")
        medical_context = []

    # Step 6: Patient Explanation Agent
    final_explanation = generate_patient_explanation(
        summary=summary,
        drug_interactions=drug_results,
        medical_context=medical_context
    )

    return {
        "filename": filename,
        "summary": summary,
        "drug_interactions": drug_results,
        "medical_context": medical_context,
        "final_explanation": final_explanation
    }