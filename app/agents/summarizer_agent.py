import os
from typing import List, Optional

# Try to import a generic LLM client wrapper if present; fallback to a simple placeholder
try:
    from app.integrations.llm_client import LLMClient
except Exception:
    LLMClient = None


class SummarizerAgent:
    def __init__(self):
        if LLMClient is not None:
            self.llm = LLMClient(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.llm = None

    def _find_file_path(self, class_name: str, filename: str) -> str | None:
        """Try to locate a file name under the class folder across common subfolders."""
        base = os.path.join("data", "classes", class_name)
        # direct path
        p = os.path.join(base, filename)
        if os.path.exists(p):
            return p

        # try notes (including category subfolders)
        notes_base = os.path.join(base, "notes")
        if os.path.exists(notes_base):
            for root, _, files in os.walk(notes_base):
                if filename in files:
                    return os.path.join(root, filename)

        # transcripts
        transcripts = os.path.join(base, "transcripts")
        if os.path.exists(transcripts):
            candidate = os.path.join(transcripts, filename)
            if os.path.exists(candidate):
                return candidate

        # summaries (pdfs)
        summaries = os.path.join(base, "summaries")
        if os.path.exists(summaries):
            candidate = os.path.join(summaries, filename)
            if os.path.exists(candidate):
                return candidate

        # audio folder
        audio = os.path.join(base, "audio")
        if os.path.exists(audio):
            candidate = os.path.join(audio, filename)
            if os.path.exists(candidate):
                return candidate

        return None

    def _load_file_text(self, path: str) -> str:
        """Extract text content from a supported file path (txt, pdf fallback)."""
        if not path:
            return ""
        lower = path.lower()
        try:
            if lower.endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            # PDF extraction is best-effort: try to use app.handlers.document_handlers if available
            try:
                from app.handlers.document_handlers import DocumentHandler
                return DocumentHandler.extract_text(path)
            except Exception:
                # Best-effort fallback: return empty or a small placeholder
                return f"[Binary file skipped: {os.path.basename(path)}]"
        except Exception:
            return ""

    def summarize(self, class_name: str, sources: List[str], query: Optional[str] = None, mode: str = "key_topics") -> str:
        """
        Summarize a list of source filenames (notes, transcripts, pdfs, audio) for a class.
        """
        texts: list[str] = []
        for src in sources:
            path = self._find_file_path(class_name, src)
            if not path:
                continue
            # If audio file, prefer to use existing transcript if present
            if path.lower().endswith(tuple([".mp3", ".wav", ".m4a"])):
                # look for a transcript with same stem
                stem = os.path.splitext(os.path.basename(path))[0]
                tpath = self._find_file_path(class_name, stem + ".txt")
                if tpath:
                    texts.append(self._load_file_text(tpath))
                    continue
                else:
                    # if no transcript, skip (or could call a transcriber)
                    texts.append(f"[Audio file skipped: {os.path.basename(path)}]")
                    continue

            # normal text/pdf handling
            texts.append(self._load_file_text(path))

        combined = "\n\n".join([t for t in texts if t])

        prompt = f"Summarize these class materials in {mode} style.\n"
        if query:
            prompt += f"User request: {query}\n\n"
        prompt += combined or "[No textual content found in selected sources]"

        if self.llm is not None:
            try:
                return self.llm.generate(prompt)
            except Exception as e:
                # Surface the error for debugging but return a safe message
                print(f"[LLM error] {e}")
                return f"[LLM error] Could not generate summary. Details: {e}"

        # fallback: simple preview when LLM is disabled
        if not combined:
            return "[No content available]"
        return "[LLM disabled - preview]\n" + (combined[:2000] + ("..." if len(combined) > 2000 else ""))
