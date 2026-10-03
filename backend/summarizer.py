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
        reasoning_effort="low",
    )
    return strip_markdown(response.choices[0].message.content)