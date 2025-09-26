"""
Button Handler Module
Central module that connects UI buttons to their respective implementation files.
This allows team members to work on different features independently.
"""

from typing import Any, Callable
import flet as ft

# Import all the handler modules
from app.handlers import (
    class_handlers,
    notes_handlers,
    document_handlers,
    transcription_handlers,
    ai_handlers,
    google_drive_handlers
)


class ButtonManager:
    """Manages all button callbacks and routes them to appropriate handlers"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.class_handler = class_handlers.ClassHandler(page)
        self.notes_handler = notes_handlers.NotesHandler(page)
        self.document_handler = document_handlers.DocumentHandler(page)
        self.transcription_handler = transcription_handlers.TranscriptionHandler(page)
        self.ai_handler = ai_handlers.AIHandler(page)
        self.google_drive_handler = google_drive_handlers.GoogleDriveHandler(page)
    
    def get_callbacks(self) -> dict:
        """Returns dictionary of all button callbacks for the UI"""
        return {
            # Class Management
            'add_class': self.class_handler.add_new_class,
            'switch_class': self.class_handler.switch_class,
            'delete_class': self.class_handler.delete_class,
            
            # Notes Management
            'save_notes': self.notes_handler.save_notes,
            'load_notes': self.notes_handler.load_notes,
            'copy_notes': self.notes_handler.copy_notes,
            'clear_notes': self.notes_handler.clear_notes,
            
            # Document Management
            'upload_document': self.document_handler.upload_document,
            'process_document': self.document_handler.process_document,
            'clear_document': self.document_handler.clear_document,
            
            # Transcription
            'start_recording': self.transcription_handler.start_recording,
            'stop_recording': self.transcription_handler.stop_recording,
            'upload_audio': self.transcription_handler.upload_audio,
            'transcribe_audio': self.transcription_handler.transcribe_audio,
            
            # AI Features
            'summarize_content': self.ai_handler.summarize_content,
            'ask_ai': self.ai_handler.ask_ai,
            'generate_quiz': self.ai_handler.generate_quiz,
            
            # Google Drive
            'connect_drive': self.google_drive_handler.connect_drive,
            'upload_notes': self.google_drive_handler.upload_notes,
            'download_notes': self.google_drive_handler.download_notes,
            'sync_files': self.google_drive_handler.sync_files,
        }
    
    def show_success(self, message: str):
        """Show success message to user"""
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.GREEN)
        )
    
    def show_error(self, message: str):
        """Show error message to user"""
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.RED)
        )
    
    def show_info(self, message: str):
        """Show info message to user"""
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.BLUE)
        )