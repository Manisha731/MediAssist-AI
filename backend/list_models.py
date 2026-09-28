import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=30,
)

ids = sorted(m.id for m in client.models.list().data)
print(f"{len(ids)} models available\n")

# Print only likely candidates so the list stays readable
keywords = ["nemotron", "llama", "gemma", "mistral", "qwen", "deepseek", "kimi", "gpt-oss"]
for model_id in ids:
    if any(k in model_id.lower() for k in keywords):
        print(model_id)