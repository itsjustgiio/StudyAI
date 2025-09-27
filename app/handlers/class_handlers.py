import flet as ft
from typing import Any
from pathlib import Path


class ClassHandler:
    """Handles class management operations"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_class = "General"
        self.classes = ["General"]

        # Ensure base folder exists
        base_dir = Path("data/classes")
        base_dir.mkdir(parents=True, exist_ok=True)
        (base_dir / self.current_class).mkdir(parents=True, exist_ok=True)

    def get_current_class(self) -> str:
        return self.current_class
    def add_new_class(self, e: Any = None, class_name: str | None = None):
        """Add a new class by name (from UI or event)."""
        if class_name is None:
            # fallback if called with event only
            class_name = getattr(e.control, "value", None) if e else None
        if not class_name:
            self._show_message("⚠️ Please enter a class name!", success=False)
            return

        if class_name in self.classes:
            self._show_message("⚠️ Class already exists", success=False)
            return

        class_dir = Path("data/classes") / class_name
        class_dir.mkdir(parents=True, exist_ok=True)

        self.classes.append(class_name)
        self.current_class = class_name
        self._show_message(f"✅ Created and switched to class: {class_name}")

    def switch_class(self, e: Any = None, class_name: str | None = None):
        """Switch active class by name (from UI or event)."""
        if class_name is None:
            class_name = getattr(e.control, "value", None) if e else None

        if class_name and class_name in self.classes:
            self.current_class = class_name
            self._show_message(f"✅ Switched to: {class_name}")
        else:
            self._show_message("⚠️ Invalid class selection", success=False)

    def delete_class(self, e: Any = None):
        if len(self.classes) <= 1:
            self._show_message("⚠️ Cannot delete the last remaining class", success=False)
            return

        to_delete = self.current_class
        try:
            self.classes.remove(to_delete)
            self.current_class = self.classes[0]
            self._show_message(f"🗑️ Deleted class: {to_delete}, switched to {self.current_class}")
        except Exception as err:
            self._show_message(f"❌ Failed to delete class: {err}", success=False)

    def _show_message(self, message: str, success: bool = True):
        color = ft.colors.GREEN if success else ft.colors.RED
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(message), bgcolor=color))
