#!/usr/bin/env python3
"""
StudyAI - AI-Powered Study Assistant
Main entry point for the Flet-based UI application.
"""
import os
import logging
import flet as ft
from app.ui import build_ui
from app.button_manager import ButtonManager

# Suppress TensorFlow/absl and gRPC debug spam
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # hides INFO & WARNING logs from TF/absl
logging.getLogger("absl").setLevel(logging.ERROR)
logging.getLogger("grpc").setLevel(logging.ERROR)

def create_connected_ui(page: ft.Page):
    """Create UI with connected button handlers"""
    # Initialize the button manager with all handlers
    button_manager = ButtonManager(page)
    
    # Get all the button callbacks from the manager
    callbacks = button_manager.get_callbacks()
    
    # Build the UI and connect the callbacks
    return build_ui(page, callbacks)

def main():
    """Launch the StudyAI application."""
    ft.app(target=create_connected_ui, name="StudyAI", assets_dir="assets")

if __name__ == "__main__":
    main()
