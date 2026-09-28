import os, time
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=60,
    max_retries=0,   # fail fast instead of retrying silently
)

MODEL = "nvidia/nemotron-3-super-120b-a12b"

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

SUMMARY = "Blood sugar (HbA1c 8.1%, fasting glucose 168) is high, cholesterol markers are off (LDL and triglycerides high, HDL low), and creatinine is mildly high. Hemoglobin is normal."

INTERACTIONS = """

Medication interaction findings:
- warfarin: Concurrent use with NSAIDs may increase the risk of bleeding.
- ibuprofen: May increase the anticoagulant effect of warfarin and raise bleeding risk.
"""

SUMMARIZER = f"""You are a medical report summarizer. Summarize the following medical report in plain, patient-friendly language. Highlight any abnormal values clearly.

Report content:
{REPORT}

Summary:"""

SUMMARIZER_PLAIN = SUMMARIZER.replace(
    "Summary:", "Use plain text only: no tables and no markdown symbols like ** or #. Use short paragraphs and simple dashes for lists.\n\nSummary:")

EXPLAINER = f"""You are explaining a medical report to a patient with no medical background. Be warm, clear, and reassuring where appropriate, but honest about anything that needs follow-up.

Report summary:
{SUMMARY}
{INTERACTIONS}


Write a final, easy-to-understand explanation for the patient. End with a clear disclaimer that this is not a substitute for professional medical advice."""

def run(label, prompt, show=True):
    start = time.time()
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.3,
        )
        secs = time.time() - start
        print(f"[{label}] {secs:.1f}s")
        if show:
            print(resp.choices[0].message.content)
            print()
    except Exception as e:
        print(f"[{label}] FAILED after {time.time() - start:.1f}s: {e}")

# Speed consistency: same summarizer prompt 3 times
for i in range(3):
    run(f"summarizer run {i + 1}", SUMMARIZER, show=False)

print("\n===== SUMMARIZER, PLAIN TEXT VERSION =====")
run("summarizer plain", SUMMARIZER_PLAIN)

print("===== EXPLANATION AGENT =====")
run("explainer", EXPLAINER)