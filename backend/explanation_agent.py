import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.5-flash-lite")


def generate_patient_explanation(summary: str, drug_interactions: list = None, medical_context: list = None) -> str:
    """Combine outputs from other agents into one clear, patient-friendly explanation."""
    
    interaction_text = ""
    if drug_interactions:
        interaction_text = "\n\nMedication interaction findings:\n"
        for item in drug_interactions:
            interaction_text += f"- {item.get('input_name')}: {item.get('drug_interactions', 'No data')}\n"
    
    context_text = ""
    if medical_context:
        context_text = "\n\nAdditional medical background:\n" + "\n".join(medical_context)
    
    prompt = f"""You are explaining a medical report to a patient with no medical background. Be warm, clear, and reassuring where appropriate, but honest about anything that needs follow-up.

Report summary:
{summary}
{interaction_text}
{context_text}

Write a final, easy-to-understand explanation for the patient. End with a clear disclaimer that this is not a substitute for professional medical advice."""

    response = model.generate_content(prompt)
    return response.text