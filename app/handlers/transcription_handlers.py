"""
Button Handler Module
Central module that connects UI buttons to their respective implementation files.
This allows team members to work on different features independently.
"""

from app import audio
from app.transcription import Transcriber
from app.handlers.class_handlers import ClassHandler
from app import summarizer
import flet as ft
from pathlib import Path
import re
from typing import Any


class TranscriptionHandler:
    def __init__(self, page: ft.Page, class_handler: ClassHandler):
        """Transcription handler now uses an injected shared ClassHandler.

        Args:
            page: flet page
            class_handler: shared ClassHandler instance (injected by ButtonManager)
        """
        self.page = page
        self.class_handler = class_handler
        self.transcriber = Transcriber(model_size="tiny")  # load once
        self.is_recording = False
        self.current_recording = None
        # Will be attached in ButtonManager.get_callbacks()
        self.callbacks: dict[str, Any] | None = None

    def upload_audio(self, e: ft.FilePickerResultEvent):
        """Save audio file into class folder, run Whisper, save transcript, then summarize."""
        if not e.files:
            self._show_message("⚠️ No file selected", success=False)
            return

        file = e.files[0]
        class_name = self.class_handler.get_current_class()

        try:
            # 1. Save audio file
            saved_audio = audio.save_audio_file(file.path, file.name, class_name)

            # 2. Transcribe with Whisper
            text = self.transcriber.transcribe_file(saved_audio)

            # 2.5. Format for readability (split into sentences)
            sentences = re.split(r'(?<=[.!?]) +', text)
            text = "\n".join(sentences)

            # 3. Save transcript alongside audio
            class_dir = Path("data/classes") / class_name / "transcripts"
            class_dir.mkdir(parents=True, exist_ok=True)
            transcript_path = class_dir / (Path(file.name).stem + ".txt")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(text)

            self._show_message(f"Saved transcript: {transcript_path.name}", success=True)
            print(f"[INFO] Transcript saved to {transcript_path}")

            # 3.5. Update UI panel with clickable entry
            if self.callbacks and "display_transcript" in self.callbacks:
                snippet = text[:100] + ("..." if len(text) > 100 else "")
                self.callbacks["display_transcript"](
                    transcript_path.name, snippet, str(transcript_path)
                )

            # 4. Summarize transcript into summaries folder
            try:
                summary_path = summarizer.summarize_file(
                    transcript_path,  # input transcript
                    None,             # output ignored (summarizer builds metadata filename)
                    class_name=class_name
                )
                self._show_message(f"Summary generated: {Path(summary_path).name}", success=True)
                print(f"[INFO] Summary saved to {summary_path}")
            except Exception as err:
                self._show_message(f"Summarization failed: {err}", success=False)

        except Exception as err:
            self._show_message(f"Error: {err}", success=False)

    # ------------------------
    # Recording stubs
    # ------------------------

    def start_recording(self, e: ft.ControlEvent = None):
        if not self.is_recording:
            self.is_recording = True
            self._show_message("🎤 Start recording (stub)", success=True)
        else:
            self._show_message("Already recording", success=False)

    def stop_recording(self, e: ft.ControlEvent = None):
        if self.is_recording:
            self.is_recording = False
            self._show_message("⏹️ Stop recording (stub)", success=True)
        else:
            self._show_message("Not currently recording", success=False)

    def play_audio(self, e: Any = None):
        """Stub: Handle playing audio file"""
        self._show_message("▶️ Play Audio - Ready for implementation!", success=True)

    def pause_audio(self, e: Any = None):
        """Stub: Handle pausing audio playback"""
        self._show_message("⏸️ Pause Audio - Ready for implementation!", success=True)

    # ------------------------
    # Unified message style
    # ------------------------

    def _show_message(self, message: str, success: bool = True):
        """Show styled snackbar notifications"""
        bgcolor = "#4B2E83" if success else "#800020"  # dark purple / maroon
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color="white"),
                bgcolor=bgcolor,
                duration=2000,
            )
        )