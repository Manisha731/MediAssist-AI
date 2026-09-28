import os, time
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"), transport="rest")
model = genai.GenerativeModel("gemini-3.5-flash-lite")

start = time.time()
response = model.generate_content("Say hello in one short sentence.")
print(response.text)
print(f"Took {time.time() - start:.1f} seconds")