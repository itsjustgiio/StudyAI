#!/usr/bin/env python3
"""
StudyAI - AI-Powered Study Assistant
Main entry point for the Flet-based UI application.
"""

import flet as ft
from app.ui import build_ui

def main():
    """Launch the StudyAI application."""
    ft.app(target=build_ui, name="StudyAI", assets_dir="assets")

if __name__ == "__main__":
    main()
