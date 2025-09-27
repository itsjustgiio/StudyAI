"""
Button Handler Module
Central module that connects UI buttons to their respective implementation files.
This allows team members to work on different features independently.
"""

from typing import Any, Callable
import flet as ft
import os, sys, subprocess
from pathlib import Path

# Import all the handler modules
from app.handlers import (
    class_handlers,
    notes_handlers,
    document_handlers,
    transcription_handlers,
    ai_handlers,
    google_drive_handlers
)
from app.agents.summarizer_agent import SummarizerAgent
from app.agents.chat_agent import ChatAgent
from app.agents.flashcards_agent import FlashcardsAgent


def open_file(path: str):
    """Open file with the system default application"""
    if sys.platform.startswith("darwin"):  # macOS
        subprocess.call(("open", path))
    elif os.name == "nt":  # Windows
        os.startfile(path)
    elif os.name == "posix":  # Linux
        subprocess.call(("xdg-open", path))


class ButtonManager:
    """Manages all button callbacks and routes them to appropriate handlers"""

    def __init__(self, page: ft.Page):
        self.page = page
        # Snackbar color palette (calmer tones)
        # Error: muted maroon, Info: soft dark purple, Success: calm light green
        self.SNACK_ERROR = "#6A2830"      # muted maroon
        self.SNACK_INFO = "#5A3E7A"       # soft dark purple
        self.SNACK_SUCCESS = "#66A36C"    # calm light green
        # Shared settings (e.g., selected Whisper model)
        self.settings = {"whisper_model": "tiny"}

        # Initialize handlers (share class_handler across modules)
        self.class_handler = class_handlers.ClassHandler(page)
        self.notes_handler = notes_handlers.NotesHandler(page)
        self.document_handler = document_handlers.DocumentHandler(page)
        # Inject the shared class_handler into TranscriptionHandler so all modules share the same state
        self.transcription_handler = transcription_handlers.TranscriptionHandler(page, self.class_handler, settings=self.settings)
        self.ai_handler = ai_handlers.AIHandler(page)
        self.google_drive_handler = google_drive_handlers.GoogleDriveHandler(page)

        # Summarizer agent (lightweight)
        try:
            self.summarizer_agent = SummarizerAgent()
        except Exception:
            self.summarizer_agent = None
        # Chat agent for interactive summarizer/chat
        try:
            self.chat_agent = ChatAgent()
        except Exception:
            self.chat_agent = None
        # Flashcards agent
        try:
            self.flashcards_agent = FlashcardsAgent()
        except Exception:
            self.flashcards_agent = None

    def on_model_change(self, e: Any = None):
        """Update shared whisper model setting and forward event to AI handler."""
        try:
            if e and hasattr(e, 'control') and hasattr(e.control, 'value'):
                selected = e.control.value
                if selected:
                    self.settings['whisper_model'] = selected
                    # notify AI handler for its own model state (if implemented)
                    try:
                        if hasattr(self.ai_handler, 'on_model_change'):
                            self.ai_handler.on_model_change(e)
                    except Exception:
                        pass
                    # show small info
                    self.show_info(f"Whisper model set to: {selected}")
        except Exception:
            pass

    def get_callbacks(self) -> dict:
        """Returns dictionary of all button callbacks for the UI"""
        # Wrapper for document upload that accepts the FilePicker event and UI refs
        def _upload_document_wrapper(e, notes_ref=None, document_status_ref=None, class_name: str = "General"):
            try:
                # Ensure DocumentHandler knows current class for saving
                try:
                    self.document_handler.current_class = class_name or "General"
                except Exception:
                    pass

                # Call the lower-level handler which returns extracted text
                extracted = self.document_handler.upload_document(e)

                # If a notes_ref was passed from UI, populate it
                try:
                    if notes_ref and getattr(notes_ref, 'current', None) and isinstance(extracted, str):
                        notes_ref.current.value = extracted
                        notes_ref.current.update()
                except Exception:
                    pass

                # Update document status UI
                try:
                    if document_status_ref and getattr(document_status_ref, 'current', None):
                        document_status_ref.current.value = f"📄 Document loaded: {getattr(e, 'files', [None])[0].name if hasattr(e, 'files') and e.files else (getattr(e, 'name', '') or '')}"
                        document_status_ref.current.update()
                except Exception:
                    pass

                # Show a quick success snackbar
                try:
                    self.show_success("Document imported")
                except Exception:
                    pass

                return extracted
            except Exception as ex:
                try:
                    self.show_error(f"Failed to import document: {ex}")
                except Exception:
                    pass
                return ""

        callbacks = {
            # Class Management
            'add_class': self.class_handler.add_new_class,
            'switch_class': self.class_handler.switch_class,
            'get_current_class': self.class_handler.get_current_class,
            'list_classes': lambda: self.class_handler.classes,
            'delete_class': self.class_handler.delete_class,

            # Notes Management
            'create_note': self.notes_handler.create_note,   # 👈 NEW
            'upload_note_document': self.notes_handler.upload_note_document,
            'save_notes': self.notes_handler.save_notes,
            'load_notes': self.notes_handler.load_notes,
            'copy_notes': self.notes_handler.copy_notes,
            'clear_notes': self.notes_handler.clear_notes,

            # Document Management
            'upload_document': _upload_document_wrapper,
            'process_document': self.document_handler.process_document,
            'clear_document': self.document_handler.clear_document,

            # Transcription
            'start_recording': self.transcription_handler.start_recording,
            'stop_recording': self.transcription_handler.stop_recording,
            'upload_audio': self.transcription_handler.upload_audio,
            # 'transcribe_audio' removed: auto-transcription will trigger after upload/recording

            # AI Features
            'summarize_content': self.ai_handler.summarize_content,
            'generate_summary': self.summarizer_agent.summarize if self.summarizer_agent else (lambda *a, **k: ""),
            'ask_ai': self.ai_handler.ask_ai,
            'generate_quiz': self.ai_handler.generate_quiz,
            # Flashcards generation
            'generate_flashcards': (lambda notes, n: self.flashcards_agent.generate_flashcards(notes, n)) if self.flashcards_agent else (lambda *a, **k: []),
            # Model change: update shared whisper model setting and notify AI handler
            'model_change': self.on_model_change,
            # Provide notes text for UI agents (best-effort)
            'get_notes_text': (lambda: self._get_notes_text()) ,
            # expose getter for current whisper model
            'get_whisper_model': lambda: self.settings.get('whisper_model', 'tiny'),
            # Chat agent session management (wrapped to update UI)
            'start_session': (lambda class_name, files, chat_ref: self._start_session_ui(class_name, files, chat_ref)) if self.chat_agent else (lambda *a, **k: ""),
            'send_message': (lambda msg, chat_ref, input_ref: self._send_message_ui(msg, chat_ref, input_ref)) if self.chat_agent else (lambda *a, **k: ""),

            # Google Drive
            'connect_drive': self.google_drive_handler.connect_drive,
            'download_notes': self.google_drive_handler.download_notes,

            # File opening
            'open_pdf': open_file,
        }

        # 👇 Give the transcription handler access to all callbacks
        self.transcription_handler.callbacks = callbacks

        return callbacks

    def _get_notes_text(self) -> str:
        """Best-effort: return concatenated note text for the current class (Daily Notes)."""
        try:
            cls = getattr(self.class_handler, 'current_class', 'General') or 'General'
            base = Path('data/classes') / cls / 'notes' / 'Daily Notes'
            texts = []
            if base.exists() and base.is_dir():
                for p in base.iterdir():
                    if p.suffix.lower() in ('.txt', '.md'):
                        try:
                            texts.append(p.read_text(encoding='utf-8'))
                        except Exception:
                            continue
            return "\n\n".join(texts)
        except Exception:
            return ""

    # ------------------------------
    # Unified snackbar styling
    # ------------------------------
    def show_success(self, message: str):
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color="white"),
                bgcolor=self.SNACK_SUCCESS,
                duration=2000,
            )
        )

    def show_error(self, message: str):
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color="white"),
                bgcolor=self.SNACK_ERROR,
                duration=2000,
            )
        )

    def show_info(self, message: str):
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color="white"),
                bgcolor=self.SNACK_INFO,
                duration=2000,
            )
        )

    # ------------------------------
    # Chat UI helpers
    # ------------------------------
    def _start_session_ui(self, class_name: str, files: list | None, chat_ref):
        try:
            files = files or []
            intro = self.chat_agent.start_session(class_name, files)
            # append assistant intro to UI
            try:
                if chat_ref and getattr(chat_ref, 'current', None):
                    chat_ref.current.controls.append(ft.Row([ft.Container(ft.Text(intro), bgcolor="#FFFFFF", padding=ft.padding.all(12), border_radius=12)], alignment=ft.MainAxisAlignment.START))
                    chat_ref.current.update()
            except Exception:
                pass
            return intro
        except Exception as e:
            self.show_error(f"Failed to start session: {e}")
            return ""

    def _send_message_ui(self, msg: str, chat_ref, input_ref):
        try:
            if not msg or not msg.strip():
                return ""
            # append user message
            try:
                if chat_ref and getattr(chat_ref, 'current', None):
                    chat_ref.current.controls.append(ft.Row([ft.Container(ft.Text(msg), bgcolor=ft.colors.PRIMARY, padding=ft.padding.all(12), border_radius=12)], alignment=ft.MainAxisAlignment.END))
                    chat_ref.current.update()
            except Exception:
                pass

            # call agent
            resp = self.chat_agent.chat(msg)

            # append assistant response
            try:
                if chat_ref and getattr(chat_ref, 'current', None):
                    chat_ref.current.controls.append(ft.Row([ft.Container(ft.Text(resp), bgcolor="#FFFFFF", padding=ft.padding.all(12), border_radius=12)], alignment=ft.MainAxisAlignment.START))
                    chat_ref.current.update()
            except Exception:
                pass

            # clear input field
            try:
                if input_ref and getattr(input_ref, 'current', None):
                    input_ref.current.value = ""
                    input_ref.current.update()
            except Exception:
                pass

            return resp
        except Exception as e:
            self.show_error(f"Failed to send message: {e}")
            return ""
