
"""
Class Management Handler
Handles all class-related button functionality for the StudyAI UI.
This module is intentionally UI-aware: it receives refs from ui.py and mutates
those controls directly so we don't need the rest of the app to be present.

It provides safe no-op fallbacks for any missing refs.

Public API:
    - ClassHandler(page, *, class_dropdown_ref, add_class_dialog_ref,
                   new_class_name_ref, notes_ref)
    - on_class_change(event)
    - open_add_class_dialog(event)
    - close_add_class_dialog(event)
    - add_new_class(event)
    - save_current_class_data()
"""

from typing import Dict, Any, Optional, List
import flet as ft


def _safe_get(ref: Optional[ft.Ref]):
    return ref.current if ref is not None else None


class ClassHandler:
    def __init__(
        self,
        page: ft.Page,
        *,
        class_dropdown_ref: Optional[ft.Ref] = None,
        add_class_dialog_ref: Optional[ft.Ref] = None,
        new_class_name_ref: Optional[ft.Ref] = None,
        notes_ref: Optional[ft.Ref] = None,
    ):
        self.page = page
        self.class_dropdown_ref = class_dropdown_ref
        self.add_class_dialog_ref = add_class_dialog_ref
        self.new_class_name_ref = new_class_name_ref
        self.notes_ref = notes_ref

        # In-memory store (UI session only)
        self.classes: List[str] = ["General"]
        self.selected: str = "General"
        self.data: Dict[str, Dict[str, Any]] = {
            "General": {"notes": "", "transcriptions": [], "ai_history": []}
        }

        # Initialize dropdown if present
        dd = _safe_get(self.class_dropdown_ref)
        if dd is not None:
            dd.options = [ft.dropdown.Option("General")]
            dd.value = "General"

    # ---------------------------
    # Dialog controls
    # ---------------------------
    def open_add_class_dialog(self, _=None):
        dlg = _safe_get(self.add_class_dialog_ref)
        if dlg is not None:
            dlg.open = True
            self.page.update()

    def close_add_class_dialog(self, _=None):
        dlg = _safe_get(self.add_class_dialog_ref)
        if dlg is not None:
            dlg.open = False
            self.page.update()

    # ---------------------------
    # Core actions
    # ---------------------------
    def _validate_class_name(self, name: str) -> Optional[str]:
        name = (name or "").strip()
        if not name:
            return "Please enter a class name."
        if any(ch in name for ch in "<>:/\\|?*\"'\n\t"):
            return "Class name has invalid characters."
        if name in self.classes:
            return "Class already exists."
        if len(name) > 40:
            return "Class name too long (max 40)."        
        return None

    def add_new_class(self, _=None):
        tf = _safe_get(self.new_class_name_ref)
        name = (tf.value if tf is not None else "").strip()
        err = self._validate_class_name(name)
        if err:
            # surface error unobtrusively
            try:
                self.page.snack_bar = ft.SnackBar(ft.Text(err))
                self.page.snack_bar.open = True
                self.page.update()
            except Exception:
                pass
            return

        # Create class
        self.classes.append(name)
        self.data[name] = {"notes": "", "transcriptions": [], "ai_history": []}
        self.selected = name

        # Update dropdown
        dd = _safe_get(self.class_dropdown_ref)
        if dd is not None:
            dd.options = [ft.dropdown.Option(c) for c in self.classes]
            dd.value = name

        # Close dialog and clear input
        dlg = _safe_get(self.add_class_dialog_ref)
        if dlg is not None:
            dlg.open = False
        if tf is not None:
            tf.value = ""

        self.page.update()

    def save_current_class_data(self):
        # Save notes text into current class
        notes = _safe_get(self.notes_ref)
        if self.selected not in self.data:
            self.data[self.selected] = {"notes": "", "transcriptions": [], "ai_history": []}
        if notes is not None:
            self.data[self.selected]["notes"] = notes.value or ""

    def on_class_change(self, e=None):
        # Persist current data first
        self.save_current_class_data()

        dd = _safe_get(self.class_dropdown_ref)
        if dd is None:
            return

        new_name = (dd.value or "General").strip()
        if new_name not in self.classes:
            # If user typed a new value manually (editable dropdown), normalize
            if new_name:
                self.classes.append(new_name)
                self.data.setdefault(new_name, {"notes": "", "transcriptions": [], "ai_history": []})
            else:
                new_name = "General"

        self.selected = new_name

        # Load notes into editor
        notes = _safe_get(self.notes_ref)
        if notes is not None:
            notes.value = self.data.get(new_name, {}).get("notes", "")

        self.page.update()
