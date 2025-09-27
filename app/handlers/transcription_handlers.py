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
        # Use the shared class handler instead of creating a new one here
        self.class_handler = class_handler
        self.transcriber = Transcriber(model_size="tiny")  # load once
        self.is_recording = False
        self.current_recording = None

    def upload_audio(self, e: ft.FilePickerResultEvent):
        """Save audio file into class folder, run Whisper, save transcript (sentence split), then summarize."""
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

            # 2.5. Format for readability (split by punctuation)
            sentences = re.split(r'(?<=[.!?]) +', text)
            text = "\n".join(sentences)

            # 3. Save transcript alongside audio
            class_dir = Path("data/classes") / class_name / "transcripts"
            class_dir.mkdir(parents=True, exist_ok=True)
            transcript_path = class_dir / (Path(file.name).stem + ".txt")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(text)

            self._show_message(f"✅ Saved transcript: {transcript_path.name}")
            print(f"[INFO] Transcript saved to {transcript_path}")

            # 4. Summarize transcript into summaries folder
            try:
                summary_path = summarizer.summarize_file(
                    transcript_path,  # input transcript
                    None,             # output ignored (summarizer builds metadata filename)
                    class_name=class_name
                )
                self._show_message(f"📄 Summary generated: {Path(summary_path).name}")
                print(f"[INFO] Summary saved to {summary_path}")
            except Exception as err:
                self._show_message(f"⚠️ Summarization failed: {err}", success=False)

        except Exception as err:
            self._show_message(f"❌ Error: {err}", success=False)

    # ------------------------
    # Stubs so UI buttons don’t break
    # ------------------------

    def start_recording(self, e: ft.ControlEvent = None):
        if not self.is_recording:
            self.is_recording = True
            self._show_message("🎤 Start recording (stub) - not yet implemented")
        else:
            self._show_message("⚠️ Already recording", success=False)

    def stop_recording(self, e: ft.ControlEvent = None):
        if self.is_recording:
            self.is_recording = False
            self._show_message("⏹️ Stop recording (stub) - not yet implemented")
        else:
            self._show_message("⚠️ Not currently recording!", success=False)
    
    # NOTE: Manual transcribe_audio method removed. Auto-transcription will be
    # triggered automatically after upload or recording stop by future logic.
    
    def upload_audio(self, e: Any = None):
        """
        Handle uploading audio file for transcription
        
        TODO: Implement the following:
        1. Show file picker for audio files
        2. Validate audio format and size
        3. Load audio file
        4. Display audio player controls
        5. Prepare for transcription
        """
        # Placeholder implementation
        self._show_message("📂 Upload Audio - Ready for implementation!")
        
        # Example implementation:
        # audio_formats = ['.wav', '.mp3', '.m4a', '.flac']
        # file_path = self._show_file_picker(audio_formats)
        # if file_path:
        #     if self._validate_audio_file(file_path):
        #         self._load_audio_file(file_path)
        #         self._show_audio_player(file_path)
        #         self._show_message(f"✅ Audio loaded: {file_path}")
        #     else:
        #         self._show_message("❌ Invalid audio file", success=False)
    
    def play_audio(self, e: Any = None):
        """
        Handle playing audio file
        
        TODO: Implement the following:
        1. Check if audio file is loaded
        2. Initialize audio playback
        3. Start playing audio
        4. Update playback UI controls
        5. Handle playback errors
        """
        # Placeholder implementation
        self._show_message("▶️ Play Audio - Ready for implementation!")
    
    def pause_audio(self, e: Any = None):
        """
        Handle pausing audio playback
        
        TODO: Implement the following:
        1. Pause current audio playback
        2. Update UI controls
        3. Save playback position
        """
        # Placeholder implementation
        self._show_message("⏸️ Pause Audio - Ready for implementation!")
    
    def _show_message(self, message: str, success: bool = True):
        color = ft.colors.GREEN if success else ft.colors.RED
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(message), bgcolor=color))
