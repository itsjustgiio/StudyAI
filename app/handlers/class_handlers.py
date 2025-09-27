# app/handlers/class_handlers.py
from __future__ import annotations

from pathlib import Path
from typing import Any
import flet as ft


class ClassHandler:
    """
    Minimal, working class manager.
    - Keeps a list of classes in data/classes/
    - Ensures a default 'General' class exists
    - Provides add / switch / delete helpers
    - Emits snackbar messages for UX
    """

    BASE = Path("data/classes")

    def __init__(self, page: ft.Page):
        self.page = page

        # Ensure base directory and default class exist
        self.BASE.mkdir(parents=True, exist_ok=True)

        self.classes = sorted([p.name for p in self.BASE.iterdir() if p.is_dir()])
        if not self.classes:
            (self.BASE / "General").mkdir(parents=True, exist_ok=True)
            self.classes = ["General"]

        self.current_class = self.classes[0]

    # ---------- helpers ----------

    def _show(self, msg: str, ok: bool = True) -> None:
        color = ft.colors.GREEN if ok else ft.colors.RED
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(msg), bgcolor=color))

    @staticmethod
    def _sanitize(name: str) -> str:
        """Make a filesystem-safe class name (very basic)."""
        keep = []
        for ch in name.strip():
            keep.append(ch if ch.isalnum() or ch in (" ", "_", "-") else "_")
        out = "".join(keep).strip()
        return out or "Untitled"

    # ---------- public API (used by UI/ButtonManager) ----------

    def get_current_class(self) -> str:
        return self.current_class

    def list_classes(self) -> list[str]:
        return list(self.classes)

    def add_new_class(self, e: Any = None, class_name: str | None = None) -> None:
        """Add a class by name; if called from UI event, read value from control."""
        if class_name is None and e is not None:
            class_name = getattr(e.control, "value", None)

        class_name = self._sanitize(class_name or "")
        if not class_name:
            self._show("⚠️ Please enter a class name!", ok=False)
            return

        if class_name in self.classes:
            self._show("⚠️ Class already exists", ok=False)
            return

        # Create the top-level class folder
        (self.BASE / class_name).mkdir(parents=True, exist_ok=True)

        # NEW: Scaffold audio/, transcripts/, summaries/ right away
        from app.audio import ensure_class_dir
        ensure_class_dir(class_name)

        # Update in-memory state
        self.classes.append(class_name)
        self.classes.sort()
        self.current_class = class_name

        self._show(f"✅ Created and switched to class: {class_name}")


    def switch_class(self, e: Any = None, class_name: str | None = None) -> None:
        """Switch currently active class."""
        if class_name is None and e is not None:
            class_name = getattr(e.control, "value", None)

        if class_name in self.classes:
            self.current_class = class_name
            self._show(f"✅ Switched to: {class_name}")
        else:
            self._show("⚠️ Invalid class selection", ok=False)

    def delete_class(self, e: Any = None, class_name: str | None = None) -> None:
        """
        Remove a class directory from the list (non-destructive by default).
        NOTE: To actually delete files, you could add shutil.rmtree here.
        """
        target = class_name or (self.current_class if self.current_class else None)
        if not target or target not in self.classes:
            self._show("⚠️ No such class", ok=False)
            return

        if len(self.classes) <= 1:
            self._show("⚠️ Cannot delete the last remaining class", ok=False)
            return

        # Remove from in-memory list (keep files for safety)
        self.classes.remove(target)
        # Switch to first remaining class
        self.current_class = self.classes[0]
        self._show(f"🗑️ Removed class: {target}. Active: {self.current_class}")
