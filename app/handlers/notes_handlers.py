"""
Notes Management Handler
Handles all notes-related button functionality.
"""

import flet as ft
from typing import Any
from pathlib import Path
import datetime


class NotesHandler:
    """Handles notes management operations"""

    def __init__(self, page: ft.Page):
        self.page = page

    # ------------------------------
    # NEW: Create a note on disk
    # ------------------------------
    def create_note(self, class_name: str, note_name: str, category: str = "Daily Notes", content: str = "") -> str:
        """
        Create a new note file under data/classes/<class_name>/notes/<category>/<note_name>.txt
        Returns the full file path as a string.
        """
        try:
            # sanitize category as a folder name (very basic)
            cat = "".join(ch if ch.isalnum() or ch in (" ", "_", "-") else "_" for ch in (category or "Daily Notes")).strip() or "Daily Notes"
            base_dir = Path("data/classes") / class_name / "notes" / cat
            base_dir.mkdir(parents=True, exist_ok=True)

            # Ensure .txt extension
            if not note_name.lower().endswith(".txt"):
                note_name = f"{note_name}.txt"

            note_path = base_dir / note_name
            note_path.write_text(content, encoding="utf-8")

            self._show_message(f"✅ Note created: {note_path}")
            return str(note_path)

        except Exception as e:
            self._show_message(f"❌ Failed to create note: {e}", success=False)
            return ""

    # ------------------------------
    # Upload a document into notes category (pdf, pptx, docx)
    # ------------------------------
    def upload_note_document(self, class_name: str, category: str, file_path: str) -> str:
        """
        Copy an uploaded file (pdf, pptx, docx) into the class notes/<category> folder.
        Returns the saved file path as string, or empty string on failure.
        """
        try:
            # sanitize category
            cat = "".join(ch if ch.isalnum() or ch in (" ", "_", "-") else "_" for ch in (category or "Daily Notes")).strip() or "Daily Notes"
            base_dir = Path("data/classes") / class_name / "notes" / cat
            base_dir.mkdir(parents=True, exist_ok=True)

            import shutil
            target_path = base_dir / Path(file_path).name
            shutil.copy(file_path, target_path)

            self._show_message(f"✅ Uploaded {target_path.name} to {cat}")
            return str(target_path)

        except Exception as e:
            self._show_message(f"❌ Failed to upload document: {e}", success=False)
            return ""

    # ------------------------------
    # Existing placeholder methods
    # ------------------------------
    def save_notes(self, e: Any = None):
        self._show_message("💾 Save Notes - Ready for implementation!")

    def load_notes(self, e: Any = None):
        self._show_message("📂 Load Notes - Ready for implementation!")

    def copy_notes(self, e: Any = None):
        self._show_message("📋 Copy Notes - Ready for implementation!")

    def clear_notes(self, e: Any = None):
        self._show_message("🗑️ Clear Notes - Ready for implementation!")

    # ------------------------------
    # Helpers
    # ------------------------------
    def _show_message(self, message: str, success: bool = True):
        """Helper method to show messages"""
        # Calmer snackbar palette: success -> calm light green, error -> muted maroon
        color = "#66A36C" if success else "#6A2830"
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=color)
        )
