"""LLM client wrapper.
Tries to use google.generativeai (Gemini). Falls back to a simple dummy client
that echoes prompts when the SDK is not available.
"""
import os
import logging
from typing import Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False


class LLMClient:
    """Simple wrapper exposing generate(prompt) -> str

    If the Gemini SDK is available, calls it. Otherwise provides a local
    deterministic fallback for development.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-mini"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model_name = model
        if GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                # model can be a string name used by the wrapper later
                self._model = model
            except Exception as e:
                logging.getLogger(__name__).exception("Failed to configure Gemini client: %s", e)
                self._model = None
        else:
            self._model = None

    def generate(self, prompt: str) -> str:
        if GENAI_AVAILABLE and self._model:
            try:
                # Using the GenerativeModel convenience wrapper if present
                model = genai.get_model(self._model) if hasattr(genai, 'get_model') else None
                if model is not None:
                    # Newer SDKs may have different call shapes; attempt best-effort
                    resp = model.generate(prompt)
                    if hasattr(resp, 'text'):
                        return resp.text
                    return str(resp)
                # Fallback attempt using older helper
                resp = genai.generate_text(model=self._model, input=prompt)
                # Try to extract text
                if isinstance(resp, dict) and 'candidates' in resp and resp['candidates']:
                    return resp['candidates'][0].get('content', '')
                return str(resp)
            except Exception as e:
                logging.getLogger(__name__).exception("Gemini generate failed: %s", e)
                raise

        # Fallback: return a deterministic preview so UI works offline
        preview = prompt[:2000]
        return "[LLM disabled - local preview]\n" + (preview + ("..." if len(prompt) > 2000 else ""))
