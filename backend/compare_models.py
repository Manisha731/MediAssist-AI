import os, time
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=60,
)

MODELS = [
    "nvidia/nemotron-3.5-lightning-30b-a3b",
    "nvidia/nemotron-3-super-120b-a12b",
    "moonshotai/kimi-k3",
    "google/gemma-4-31b-it",
]

# Made-up test data, not a real patient
REPORT = """SYNTHETIC LAB REPORT - Test Patient A
HbA1c: 8.1 % (ref <5.7) HIGH
Fasting Glucose: 168 mg/dL (ref 70-99) HIGH
Total Cholesterol: 245 mg/dL (ref <200) HIGH
LDL: 162 mg/dL (ref <100) HIGH
HDL: 34 mg/dL (ref >40) LOW
Triglycerides: 210 mg/dL (ref <150) HIGH
Creatinine: 1.6 mg/dL (ref 0.7-1.3) HIGH
Hemoglobin: 14.2 g/dL (ref 13.5-17.5) NORMAL"""

prompt = f"""You are a medical report summarizer. Summarize the following medical report in plain, patient-friendly language. Highlight any abnormal values clearly.

Report content:
{REPORT}

Summary:"""

for model in MODELS:
    print("=" * 60)
    print(model)
    start = time.time()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=900,
            temperature=0.3,
        )
        print(f"Time: {time.time() - start:.1f}s")
        print(resp.choices[0].message.content)
    except Exception as e:
        print(f"FAILED after {time.time() - start:.1f}s: {e}")
    print()