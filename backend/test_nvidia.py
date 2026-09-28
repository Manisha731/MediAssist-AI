import os, time
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=90,
)

MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
QUESTION = "Explain in two sentences why a high A1C matters, in plain language."

def run(label, messages, **params):
    start = time.time()
    resp = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=1024, **params)
    print(f"--- {label} ({time.time() - start:.1f}s) ---")
    print(resp.choices[0].message.content)
    print()

# Reasoning OFF (recommended settings: greedy)
run("reasoning OFF",
    [{"role": "system", "content": "/no_think"},
     {"role": "user", "content": QUESTION}],
    temperature=0)

# Reasoning ON (default, recommended settings)
run("reasoning ON",
    [{"role": "user", "content": QUESTION}],
    temperature=0.6, top_p=0.95)