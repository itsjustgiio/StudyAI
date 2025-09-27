# app/integrations/gemini_api.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

def generate_text(prompt: str, generation_config: dict | None = None) -> str:
    """
    Try multiple Gemini models until one succeeds.
    You can pass generation_config, e.g. {"temperature": 0.3, "max_output_tokens": 800}
    """
    candidate_models = [
        "models/gemini-2.0-flash",
        "models/gemini-2.5-flash-preview",
        "models/gemini-1.5-pro",
    ]

    generation_config = generation_config or {
        "temperature": 0.3,
        "top_p": 0.9,
        "max_output_tokens": 800,
    }

    last_error = None
    for model_name in candidate_models:
        try:
            print(f"⚡ Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(prompt, generation_config=generation_config)
            if resp and getattr(resp, "text", None):
                return resp.text.strip()
        except Exception as e:
            print(f"⚠️ Gemini API error with {model_name}: {e}")
            last_error = e

    return f"Error: Could not generate summary. Last error: {last_error}"
