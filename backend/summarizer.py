import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=90,
    max_retries=3,  # retries automatically on 503 / 429 errors
)

MODEL = "nvidia/nemotron-3-super-120b-a12b"


def summarize_report(chunks: list[str]) -> str:
    full_text = "\n\n".join(chunks)
    prompt = f"""You are a medical report summarizer. Summarize the following medical report in plain, patient-friendly language. Highlight any abnormal values clearly.

Use only information that appears in the report. Do not add diagnoses.
Use plain text only: no tables and no markdown symbols like ** or #. Use short paragraphs and simple dashes for lists.

Report content:
{full_text}

Summary:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.3,
    )
    return response.choices[0].message.content