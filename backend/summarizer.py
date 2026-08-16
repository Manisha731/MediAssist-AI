import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.5-flash-lite")


def summarize_report(chunks: list[str]) -> str:
    full_text = "\n\n".join(chunks)
    prompt = f"""You are a medical report summarizer. Summarize the following medical report in plain, patient-friendly language. Highlight any abnormal values clearly.

Report content:
{full_text}

Summary:"""
    
    response = model.generate_content(prompt)
    return response.text