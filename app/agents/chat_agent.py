import threading
from typing import List
from pathlib import Path

# Simple ChatAgent skeleton that loads files and maintains history
class ChatAgent:
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.history: List[dict] = []  # list of {'role': 'user'|'assistant', 'content': str}
        self.loaded_texts: List[str] = []
        self.class_name = None
        self.files = []

    def start_session(self, class_name: str, file_paths: List[str] | None = None):
        self.history = []
        self.loaded_texts = []
        self.class_name = class_name
        self.files = file_paths or []
        # Load text contents from files (txt, transcripts). For PDFs or others you'd integrate a parser.
        for p in self.files:
            try:
                path = Path(p)
                if path.exists() and path.suffix.lower() in ['.txt', '.md']:
                    self.loaded_texts.append(path.read_text(encoding='utf-8'))
                else:
                    # For other types, just record filename as placeholder
                    self.loaded_texts.append(f"[Loaded file: {path.name}]")
            except Exception:
                self.loaded_texts.append(f"[Failed to load: {p}]")

        # Intro message
        intro = "Hi! I\'ve loaded your selected notes. Do you want a summary, key topics, or quiz-style questions?"
        self.history.append({'role': 'assistant', 'content': intro})
        return intro

    def chat(self, user_message: str) -> str:
        # Append user message
        self.history.append({'role': 'user', 'content': user_message})

        # Build prompt from history + loaded_texts (very simple concatenation for now)
        context = "\n\n".join(self.loaded_texts[-5:])  # include last few loaded texts
        prompt = f"Context:\n{context}\n\nUser: {user_message}\nAssistant:" 

        # If llm client present, call it (expected to be blocking); otherwise, return a mocked reply
        if self.llm:
            try:
                response = self.llm.call(prompt)
            except Exception as e:
                response = f"[LLM error: {e}]"
        else:
            # Mocked response (simple echo + hint)
            response = f"[Mock reply] I understood: \"{user_message}\". I can summarize, extract key topics, or make quiz questions."

        # Append assistant response
        self.history.append({'role': 'assistant', 'content': response})
        return response

    def get_history(self) -> List[dict]:
        return self.history
