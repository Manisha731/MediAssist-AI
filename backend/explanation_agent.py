import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=90,
    max_retries=6,
)

MODEL = "openai/gpt-oss-20b"


def strip_markdown(text: str) -> str:
    """Remove common markdown symbols the model sometimes adds despite instructions."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)   # **bold** -> bold
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)  # leading # headers
    text = text.replace("*", "")                   # stray asterisks (bullets, etc.)
    return text


def find_cross_mentions(drug_interactions: list) -> list[str]:
    """Check whether one drug's interaction text names another drug the patient entered."""
    notes = []
    if not drug_interactions or len(drug_interactions) < 2:
        return notes

    for i, first in enumerate(drug_interactions):
        text = str(first.get("drug_interactions") or "").lower()
        for j, second in enumerate(drug_interactions):
            if i == j:
                continue
            other_name = str(second.get("input_name") or "").strip().lower()
            if other_name and other_name in text:
                notes.append(
                    f"IMPORTANT: The interaction information for {first.get('input_name')} "
                    f"specifically names {second.get('input_name')}. These two medicines "
                    f"were both entered by the patient."
                )
    return notes


def generate_patient_explanation(summary: str, drug_interactions: list = None, medical_context: list = None) -> str:
    """Combine outputs from other agents into one clear, patient-friendly explanation."""

    interaction_text = ""
    if drug_interactions:
        interaction_text = "\n\nMedication interaction findings:\n"
        for item in drug_interactions:
            data = item.get("drug_interactions", "No data")
            if str(data).strip().lower().startswith("no interaction data"):
                data = ("No interaction section was available for this medicine in the data source. "
                        "This does NOT mean it is safe to combine with other medicines.")
            interaction_text += f"- {item.get('input_name')}: {data}\n"

        cross_notes = find_cross_mentions(drug_interactions)
        if cross_notes:
            interaction_text += "\nCross-check between the patient's medicines:\n"
            for note in cross_notes:
                interaction_text += f"- {note}\n"

    context_text = ""
    if medical_context:
        context_text = "\n\nAdditional medical background:\n" + "\n".join(medical_context)

    prompt = f"""You are explaining a medical report to a patient with no medical background. Be warm, clear, and reassuring where appropriate, but honest about anything that needs follow-up.

Report summary:
{summary}
{interaction_text}
{context_text}

Rules:
- Use only the information provided above. Do not add new diagnoses, and do not soften or exaggerate what the report says.
- Do not recommend specific medications, doses, or alternative drugs. If medications interact, explain the risk in plain words and tell the patient to ask their doctor or pharmacist before changing anything.
- If a cross-check note says one medicine's information names another medicine the patient takes, explain that risk clearly, using what that information says, and tell the patient not to combine them without asking their doctor or pharmacist.
- Never say or imply that a medicine is safe just because no interaction data was found.
- Do not give diet or exercise plans. You may say lifestyle and treatment options are worth discussing with their doctor.
- Use plain text only: no tables and no markdown symbols like ** or #. Use short paragraphs and simple dashes for lists.
- Keep it under 350 words.

Write the final explanation directly to the patient. Do not include any planning or reasoning. End with a clear disclaimer that this is not a substitute for professional medical advice."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0,
        reasoning_effort="low",
    )
    return strip_markdown(response.choices[0].message.content)