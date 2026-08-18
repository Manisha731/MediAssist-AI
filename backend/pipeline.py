from io import BytesIO
from pypdf import PdfReader

from vectorstore import store_chunks
from summarizer import summarize_report
from drug_interaction import check_drug_interactions
from medical_retrieval import retrieve_relevant_knowledge
from explanation_agent import generate_patient_explanation


def extract_drug_names_from_text(text: str) -> list[str]:
    """Very simple placeholder: real version would use NLP/regex to pull medication names
    from the report. For now, this can be passed in separately by the caller."""
    return []


def run_full_pipeline(pdf_bytes: bytes, filename: str, drug_names: list[str] = None) -> dict:
    # Step 1: Extract text from PDF
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()

    # Step 2: Chunk and store in Chroma
    from main import chunk_text  # reuse existing chunking function
    chunks = chunk_text(extracted_text)
    store_chunks(chunks, report_id=filename)

    # Step 3: Report Summarizer agent
    summary = summarize_report(chunks)

    # Step 4: Drug Interaction Agent (only if drug names were provided)
    drug_results = []
    if drug_names:
        drug_results = check_drug_interactions(drug_names)

    # Step 5: Medical Knowledge Retrieval Agent (use summary as the query)
    medical_context = retrieve_relevant_knowledge(summary)

    # Step 6: Patient Explanation Agent (combines everything)
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