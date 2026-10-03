import os, time
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=60,
    max_retries=3,
)

MODEL = "openai/gpt-oss-20b"

start = time.time()
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "In 2 sentences, explain in plain language why high LDL cholesterol matters."}],
    max_tokens=500,
    reasoning_effort="low",
)
print(f"Took {time.time() - start:.1f}s")
print("--- content ---")
print(resp.choices[0].message.content)
reasoning = getattr(resp.choices[0].message, "reasoning_content", None)
if reasoning:
    print("--- reasoning_content (should NOT show up in your app's output) ---")
    print(reasoning[:300])