import json
from typing import List, Dict
from app.integrations.llm_client import LLMClient


class FlashcardsAgent:
    """Generate flashcards (question/answer pairs) from notes using an LLM client."""

    def __init__(self, llm_client: LLMClient | None = None):
        # Use provided client or create a default one
        try:
            self.client = llm_client or LLMClient()
        except Exception:
            self.client = None

    def generate_flashcards(self, notes: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Ask the LLM to generate `count` flashcards from `notes` and return a list of
        {"question": str, "answer": str} dictionaries. Returns an empty list on error.
        """
        prompt = f"""
You are a flashcard generator.
Create {count} study flashcards from these notes.
Format your response STRICTLY as a JSON array of objects with fields "question" and "answer".

Notes:
{notes}
"""

        try:
            if self.client:
                resp = self.client.generate_text(prompt)
            else:
                # fallback mock response
                resp = json.dumps([
                    {"question": "What is a placeholder?", "answer": "A placeholder is a mock answer."}
                ])

            # Try to extract JSON from the response
            data = json.loads(resp)
            out: List[Dict[str, str]] = []
            for item in data:
                if isinstance(item, dict) and 'question' in item and 'answer' in item:
                    out.append({'question': str(item['question']), 'answer': str(item['answer'])})
            return out
        except json.JSONDecodeError:
            return []
        except Exception:
            return []
