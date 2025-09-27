# ============================================================================
# StudyAI UI-ONLY VERSION
# ============================================================================
# This file contains ONLY UI components and layout - NO BUSINESS LOGIC
# 
# All button clicks are mapped to `lambda e: None` with TODO comments indicating
# where the actual functionality should be wired from main.py to manager modules:
# - app/transcription.py (start/stop streaming, captions)
# - app/summarizer.py (summaries, Q&A)
# - app/quiz_manager.py (quiz generation)
# - app/pdf_manager.py (import/export/list PDFs)
# - app/storage.py (local save/load)
# - app/agents.py (class management)
#
# Team members can implement their functionality in the respective manager files
# and wire them through main.py by replacing the `lambda e: None` callbacks.
# ============================================================================

from __future__ import annotations
import asyncio
import flet as ft

from .landing_page import create_landing_page
from pathlib import Path
import json
import datetime


# ============================================================================
# UI CONSTANTS
# ============================================================================

# Default content height for all main areas
# At runtime we compute a responsive `content_height` (sticky) based on the page
# window height so content areas shrink/expand when the app is resized.
DEFAULT_CONTENT_HEIGHT = 675  # Fallback fixed height for content areas

# ============================================================================
# STUB FUNCTIONS - UI PLACEHOLDERS ONLY
# These are kept only for UI demo purposes and should NOT be used in production
# ============================================================================

async def stub_summarize(text: str, mode: str) -> str:
    """UI PLACEHOLDER - Replace with app/summarizer.py integration"""
    return f"[UI PLACEHOLDER] {mode} summary for {len(text.split())} words."

async def stub_answer(question: str) -> str:
    """UI PLACEHOLDER - Replace with app/agents.py integration"""
    return f"[UI PLACEHOLDER] Answer to: {question}"

async def stub_make_quiz(source: str, n: int = 5) -> list[tuple[str, str]]:
    """UI PLACEHOLDER - Replace with app/quiz_manager.py integration"""
    return [(f"[UI PLACEHOLDER] Question {i+1}?", "Sample answer") for i in range(n)]

async def stub_start_transcription(callback):
    """UI PLACEHOLDER - Replace with app/transcription.py integration"""
    # Pretend to stream a few lines for UI demo
    import asyncio
    for i in range(3):
        await asyncio.sleep(0.4)
        await callback(f"[UI PLACEHOLDER] live caption line {i+1}")

async def stub_stop_transcription():
    """UI PLACEHOLDER - Replace with app/transcription.py integration"""
    pass


# ----------------------------
# UI entry point
# Exported function: build_ui(page)
# Your main.py should do:  ft.app(build_ui)
# ----------------------------

def build_ui(page: ft.Page, callbacks: dict | None = None):
    """Build UI with optional button callbacks from ButtonManager"""
    if callbacks is None:
        callbacks = {}  # Fallback to empty dict if no callbacks provided
    
    page.title = "StudyAI"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1400  # Larger default width
    page.window_height = 1000  # Larger default height
    page.window_min_width = 1000
    page.window_min_height = 700
    page.window_maximized = True  # Start maximized for full screen experience
    page.spacing = 0  # Remove any default spacing
    page.padding = 0  # Remove any default padding
    page.scroll = None  # Remove scroll to enable full vertical expansion
    page.auto_scroll = False  # Disable auto scroll for full control  
    page.vertical_alignment = ft.MainAxisAlignment.START  # Align content to top
    # Responsive (sticky) content height: compute from window height
    # Use a sensible minimum so small windows don't collapse the UI.
    content_height = max(300, int(page.window_height * 0.65)) if page.window_height else DEFAULT_CONTENT_HEIGHT

    # Refs for containers whose height should follow `content_height`
    notes_content_ref: ft.Ref[ft.Container] = ft.Ref[ft.Container]()
    trans_content_ref: ft.Ref[ft.Container] = ft.Ref[ft.Container]()
    ai_content_ref: ft.Ref[ft.Container] = ft.Ref[ft.Container]()
    audio_player_ref: ft.Ref[ft.Audio] = ft.Ref[ft.Audio]()
    now_playing_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()
    # Progress UI refs
    elapsed_time_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()
    total_time_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()
    progress_slider_ref: ft.Ref[ft.Slider] = ft.Ref[ft.Slider]()

    # Active class ref (tracks which class the chat is bound to)
    active_class: ft.Ref[str] = ft.Ref[str]()

    def _on_resize(e=None):
        """Recompute content_height and apply to main content containers."""
        nonlocal content_height
        try:
            content_height = max(300, int(page.window_height * 0.65))
        except Exception:
            content_height = DEFAULT_CONTENT_HEIGHT

        if notes_content_ref.current is not None:
            notes_content_ref.current.height = content_height
        if trans_content_ref.current is not None:
            trans_content_ref.current.height = content_height
        if ai_content_ref.current is not None:
            ai_content_ref.current.height = content_height

        try:
            page.update()
        except Exception:
            pass

    # Attach handler so Flet calls it on resize events
    page.on_resize = _on_resize
    
    # App state
    app_state = {"show_landing": True}
    
    # Main container that switches between landing and app
    main_container = ft.Container(expand=True)
    
    # Navigation functions (defined early so they can be used in app bar)
    def enter_main_app(e=None):
        """Navigate from landing page to main application"""
        app_state["show_landing"] = False
        page.update()
    
    def return_to_landing(e=None):
        """Navigate back to landing page from main app"""
        app_state["show_landing"] = True
        page.appbar = None  # Hide app bar
        main_container.content = create_landing_page(page, enter_main_app)
        page.update()
    
    # -------------------- Class Tree State --------------------
    class_tree_data = {
        "type": "root",  
        "children": {
            "General": {
                "type": "folder",
                "expanded": True,
                "children": {
                    "My Notes": {"type": "note", "notes": "", "transcriptions": [], "ai_history": []}
                }
            }
        }
    }
    current_selection = {"path": ["General", "My Notes"], "type": "note"}
    
    def save_current_data():
        """Save current content to the selected item - UI ONLY"""
        pass
    
    def load_data(path):
        """Load data for the selected item - UI ONLY"""
        pass
    
    # Custom Pastel Purple Theme Colors
    PASTEL_PURPLE = "#B19CD9"
    DARK_PURPLE = "#8B7AB8"
    SOFT_PURPLE = "#E6D9F0"
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#F8F6FA"
    TEXT_DARK = "#4A4A4A"

    # Tree-based class management UI components
    tree_container_ref = ft.Ref[ft.Column]()
    add_folder_dialog_ref = ft.Ref[ft.AlertDialog]()
    add_note_dialog_ref = ft.Ref[ft.AlertDialog]()
    new_folder_name_ref = ft.Ref[ft.TextField]()
    new_note_name_ref = ft.Ref[ft.TextField]()
    new_note_category_ref = ft.Ref[ft.Dropdown]()
    note_mode_ref = ft.Ref[ft.Dropdown]()
    note_file_picker_ref = ft.Ref[ft.FilePicker]()
    
    def get_item_at_path(tree_data, path):
        """Navigate to item at given path in tree"""
        current = tree_data
        for part in path:
            if "children" in current and part in current["children"]:
                current = current["children"][part]
            else:
                return None
        return current
    
    def on_tree_item_click(path, item_type):
        """Handle tree item selection"""
        def handler(e):
            current_selection["path"] = path.copy()
            current_selection["type"] = item_type

            # NEW: sync sidebar click with ClassHandler
            if item_type == "folder" and callbacks.get("switch_class"):
                callbacks["switch_class"](class_name=path[0])

            save_current_data()
            load_data(path)
            build_tree_ui()
            page.update()
        return handler
    
    def toggle_folder(path):
        """Toggle folder expanded/collapsed state"""
        def handler(e):
            item = get_item_at_path(class_tree_data, path)
            if item and item["type"] == "folder":
                item["expanded"] = not item.get("expanded", False)
                build_tree_ui()  # Refresh tree
                page.update()
        return handler
    
    def build_tree_ui():
        # Keep expanded/collapsed state between calls
        expanded_state = getattr(build_tree_ui, "expanded_state", {})
        build_tree_ui.expanded_state = expanded_state  # persist dictionary

        # Ask backend for class list
        classes_cb = callbacks.get("list_classes", lambda: [])
        try:
            classes = classes_cb() or []
        except Exception:
            classes = []

        items: list[ft.Control] = []

        # Ensure selection is valid
        if classes:
            current_cls = current_selection.get("path", [None])[0]
            if current_cls not in classes:
                current_selection["path"] = [classes[0]]
                current_selection["type"] = "folder"
                if callbacks.get("switch_class"):
                    callbacks["switch_class"](class_name=classes[0])

        for class_name in classes:
            is_selected = (
                current_selection.get("path")
                and current_selection["path"][0] == class_name
            )

            expanded = expanded_state.get(class_name, True)

            # --- Class row with expand/collapse chevron ---
            row = ft.Row(
                [
                    ft.Icon(
                        ft.icons.ARROW_DROP_DOWN if expanded else ft.icons.ARROW_RIGHT,
                        size=16,
                        color=TEXT_DARK,
                    ),
                    ft.Icon(
                        ft.icons.FOLDER_OPEN if expanded else ft.icons.FOLDER,
                        size=16,
                        color=PASTEL_PURPLE if is_selected else TEXT_DARK,
                    ),
                    ft.Text(
                        class_name,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=PASTEL_PURPLE if is_selected else TEXT_DARK,
                    ),
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.START,
            )

            def on_folder_click(e, cls=class_name):
                # toggle expand/collapse
                expanded_state[cls] = not expanded_state.get(cls, True)
                # update selection so this folder highlights purple
                current_selection["path"] = [cls]
                current_selection["type"] = "folder"
                if callbacks.get("switch_class"):
                    callbacks["switch_class"](class_name=cls)
                build_tree_ui()
                page.update()

            items.append(
                ft.Container(
                    row,
                    on_click=on_folder_click,   # ↗ use new handler
                    padding=ft.padding.symmetric(vertical=4, horizontal=4),
                )
)

            # --- Show subfiles only if expanded ---
            if expanded:
                children: list[ft.Control] = []
                class_path = Path("data/classes") / class_name

                # 🎵 Audio folder
                audio_path = class_path / "audio"
                if audio_path.exists():
                    audio_files = [
                        f for f in audio_path.glob("*.*")
                        if f.suffix.lower() in [".mp3", ".wav", ".m4a", ".flac", ".ogg"]
                    ]
                    if audio_files:
                        # Track expand state per subfolder
                        audio_expanded = expanded_state.get(f"{class_name}_audio", False)

                        def toggle_audio(e, cls=class_name):
                            expanded_state[f"{cls}_audio"] = not expanded_state.get(f"{cls}_audio", True)
                            build_tree_ui()
                            page.update()

                        # Audio folder row
                        children.append(
                            ft.Container(
                                ft.Row([
                                    ft.Icon(
                                        ft.icons.ARROW_DROP_DOWN if audio_expanded else ft.icons.ARROW_RIGHT,
                                        size=14, color=TEXT_DARK
                                    ),
                                    ft.Icon(
                                        ft.icons.FOLDER_OPEN if audio_expanded else ft.icons.FOLDER,
                                        size=14, color=TEXT_DARK
                                    ),
                                    ft.Text("Audio", size=12, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ]),
                                on_click=toggle_audio,
                                padding=ft.padding.only(top=4, bottom=2),
                            )
                        )

                        # Audio files (only if expanded)
                        if audio_expanded:
                            for f in audio_files:
                                children.append(
                                    ft.Container(
                                        ft.Row([
                                            ft.Icon(ft.icons.AUDIOTRACK, size=14, color=TEXT_DARK),
                                            ft.Text(f.name, size=12, color=TEXT_DARK),
                                        ]),
                                        padding=ft.padding.only(left=20, top=2, bottom=2),
                                        on_click=lambda e, p=f: callbacks.get("open_audio", lambda _: None)(str(p)),
                                    )
                                )

                # 🗂 Summaries folder
                summaries_path = class_path / "summaries"
                if summaries_path.exists():
                    pdf_files = list(summaries_path.glob("*.pdf"))
                    if pdf_files:
                        summaries_expanded = expanded_state.get(f"{class_name}_summaries", False)

                        def toggle_summaries(e, cls=class_name):
                            expanded_state[f"{cls}_summaries"] = not expanded_state.get(f"{cls}_summaries", True)
                            build_tree_ui()
                            page.update()

                        children.append(
                            ft.Container(
                                ft.Row([
                                    ft.Icon(
                                        ft.icons.ARROW_DROP_DOWN if summaries_expanded else ft.icons.ARROW_RIGHT,
                                        size=14, color=TEXT_DARK
                                    ),
                                    ft.Icon(
                                        ft.icons.FOLDER_OPEN if summaries_expanded else ft.icons.FOLDER,
                                        size=14, color=TEXT_DARK
                                    ),
                                    ft.Text("Summaries", size=12, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ]),
                                on_click=toggle_summaries,
                                padding=ft.padding.only(top=4, bottom=2),
                            )
                        )

                        if summaries_expanded:
                            for f in pdf_files:
                                children.append(
                                    ft.Container(
                                        ft.Row([
                                            ft.Icon(ft.icons.PICTURE_AS_PDF, size=14, color=TEXT_DARK),
                                            ft.Text(f.name, size=12, color=TEXT_DARK),
                                        ]),
                                        padding=ft.padding.only(left=20, top=2, bottom=2),
                                        on_click=lambda e, p=f: callbacks.get("open_pdf", lambda _: None)(str(p)),
                                    )
                                )

                # 🗒️ Notes folder (categorized)
                notes_path = class_path / "notes"
                if notes_path.exists():
                    # Gather categories (directories) and loose .txt files
                    categories = [p for p in notes_path.iterdir() if p.is_dir()]
                    notes_files = [p for p in notes_path.glob("*.txt")]
                    if categories or notes_files:
                        notes_expanded = expanded_state.get(f"{class_name}_notes", False)

                        def toggle_notes(e, cls=class_name):
                            expanded_state[f"{cls}_notes"] = not expanded_state.get(f"{cls}_notes", True)
                            build_tree_ui()
                            page.update()

                        children.append(
                            ft.Container(
                                ft.Row([
                                    ft.Icon(
                                        ft.icons.ARROW_DROP_DOWN if notes_expanded else ft.icons.ARROW_RIGHT,
                                        size=14, color=TEXT_DARK
                                    ),
                                    ft.Icon(
                                        ft.icons.FOLDER_OPEN if notes_expanded else ft.icons.FOLDER,
                                        size=14, color=TEXT_DARK
                                    ),
                                    ft.Text("Notes", size=12, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ]),
                                on_click=toggle_notes,
                                padding=ft.padding.only(top=4, bottom=2),
                            )
                        )

                        if notes_expanded:
                            # Category folders
                            for cat in sorted(categories, key=lambda p: p.name.lower()):
                                cat_name = cat.name
                                cat_expanded = expanded_state.get(f"{class_name}_notes_{cat_name}", False)

                                def make_toggle(cat_name_inner, cls=class_name):
                                    def _t(e):
                                        expanded_state[f"{cls}_notes_{cat_name_inner}"] = not expanded_state.get(f"{cls}_notes_{cat_name_inner}", True)
                                        build_tree_ui()
                                        page.update()
                                    return _t

                                children.append(
                                    ft.Container(
                                        ft.Row([
                                            ft.Icon(ft.icons.ARROW_DROP_DOWN if cat_expanded else ft.icons.ARROW_RIGHT, size=14, color=TEXT_DARK),
                                            ft.Icon(ft.icons.FOLDER_OPEN if cat_expanded else ft.icons.FOLDER, size=14, color=TEXT_DARK),
                                            ft.Text(cat_name, size=12, color=TEXT_DARK),
                                        ]),
                                        padding=ft.padding.only(left=12, top=2, bottom=2),
                                        on_click=make_toggle(cat_name),
                                    )
                                )

                                if cat_expanded:
                                    for nf in sorted(list(cat.glob("*.txt")), key=lambda p: p.name.lower()):
                                        children.append(
                                            ft.Container(
                                                ft.Row([
                                                    ft.Icon(ft.icons.NOTE, size=14, color=TEXT_DARK),
                                                    ft.Text(nf.name, size=12, color=TEXT_DARK),
                                                ]),
                                                padding=ft.padding.only(left=28, top=2, bottom=2),
                                                on_click=lambda e, p=nf: (
                                                    notes_ref.current and setattr(notes_ref.current, "value", open(p, "r", encoding="utf-8").read()),
                                                    notes_ref.current and notes_ref.current.update(),
                                                    page.update()
                                                ),
                                            )
                                        )

                            # Also show loose note files directly under notes/ (no category)
                            for nf in sorted(notes_files, key=lambda p: p.name.lower()):
                                children.append(
                                    ft.Container(
                                        ft.Row([
                                            ft.Icon(ft.icons.NOTE, size=14, color=TEXT_DARK),
                                            ft.Text(nf.name, size=12, color=TEXT_DARK),
                                        ]),
                                        padding=ft.padding.only(left=20, top=2, bottom=2),
                                        on_click=lambda e, p=nf: (
                                            notes_ref.current and setattr(notes_ref.current, "value", open(p, "r", encoding="utf-8").read()),
                                            notes_ref.current and notes_ref.current.update(),
                                            page.update()
                                        ),
                                    )
                                )

                if children:
                    # Nest all subfolders/files under this class folder
                    items.append(
                        ft.Container(
                            ft.Column(children, spacing=2),
                            padding=ft.padding.only(left=28),
                        )
                    )

    # ✅ Update the sidebar container
        if tree_container_ref.current:
            tree_container_ref.current.controls = items


    # Helper to populate class selector and notes checklist
    def refresh_summarizer_class_notes():
        try:
            classes = callbacks.get('list_classes', lambda: [])() or []
        except Exception:
            classes = []
        # update class dropdown options
        opts = []
        for c in classes:
            opts.append(ft.dropdown.Option(c))
        try:
            class_select_ref.current.options = opts
            class_select_ref.current.update()
        except Exception:
            pass

        # If a class is selected, populate its notes
        sel = None
        try:
            sel = class_select_ref.current.value
        except Exception:
            sel = None
        if sel:
            notes_controls = []
            base = Path("data/classes") / sel / "notes"
            if base.exists():
                for p in base.rglob("*.txt"):
                    # Create a checkbox for each note file; store the relative path in data attribute
                    try:
                        cb = ft.Checkbox(label=p.name, value=False, width=220)
                        # attach a custom attribute to carry full path
                        setattr(cb, 'note_path', str(p))
                        notes_controls.append(cb)
                    except Exception:
                        pass
            try:
                if notes_check_ref.current:
                    notes_check_ref.current.controls.clear()
                    notes_check_ref.current.controls.extend(notes_controls)
                    notes_check_ref.current.update()
            except Exception:
                pass
            # Also populate files selector for summarizer chat (notes, transcripts, pdf placeholders)
            try:
                files_controls = []
                files_base = Path("data/classes") / sel
                # notes
                notes_dir = files_base / "notes"
                if notes_dir.exists():
                    for p in notes_dir.rglob("*.txt"):
                        try:
                            cb = ft.Checkbox(label=f"notes/{p.name}", value=False, width=340)
                            setattr(cb, 'file_path', str(p))
                            files_controls.append(cb)
                        except Exception:
                            pass
                # transcripts
                trans_dir = files_base / "transcripts"
                if trans_dir.exists():
                    for p in trans_dir.rglob("*.txt"):
                        try:
                            cb = ft.Checkbox(label=f"transcripts/{p.name}", value=False, width=340)
                            setattr(cb, 'file_path', str(p))
                            files_controls.append(cb)
                        except Exception:
                            pass
                # PDFs (placeholder entries)
                pdf_dir = files_base / "pdfs"
                if pdf_dir.exists():
                    for p in pdf_dir.rglob("*.pdf"):
                        try:
                            cb = ft.Checkbox(label=f"pdfs/{p.name}", value=False, width=340)
                            setattr(cb, 'file_path', str(p))
                            files_controls.append(cb)
                        except Exception:
                            pass

                if files_selector_ref.current:
                    files_selector_ref.current.controls.clear()
                    files_selector_ref.current.controls.extend(files_controls)
                    files_selector_ref.current.update()
            except Exception:
                pass


    
    def add_folder_action(e):
        folder_name = new_folder_name_ref.current.value.strip()
        if not folder_name:
            return

        # Create the class on disk + backend
        if callbacks.get("add_class"):
            callbacks["add_class"](class_name=folder_name)

        # Close dialog and reset input
        if add_folder_dialog_ref.current:
            add_folder_dialog_ref.current.open = False
        if new_folder_name_ref.current:
            new_folder_name_ref.current.value = ""

        # Refresh sidebar
        build_tree_ui()

        # Notify user
        page.snack_bar = ft.SnackBar(ft.Text(f"✅ Created new folder: {folder_name}"), bgcolor="#66A36C")
        page.snack_bar.open = True
        page.update()

    def add_note_action(e):
        """Add a new note to the selected folder"""
        note_name = new_note_name_ref.current.value.strip()
        if note_name:
            # Find the selected folder or use General as default
            selected_path = current_selection["path"]
            if current_selection["type"] == "note" and len(selected_path) > 1:
                # If note is selected, add to its parent folder
                parent_path = selected_path[:-1]
            elif current_selection["type"] == "folder":
                # If folder is selected, add to it
                parent_path = selected_path
            else:
                # Default to General folder
                parent_path = ["General"]

            parent_item = get_item_at_path(class_tree_data, parent_path)
            if parent_item and parent_item["type"] == "folder":
                # Update in-memory tree for immediate UI feedback
                parent_item["children"][note_name] = {
                    "type": "note",
                    "notes": "",
                    "transcriptions": [],
                    "ai_history": []
                }
                parent_item["expanded"] = True  # Expand to show new note

                # --- Persist note to disk using NotesHandler with category or upload file ---
                class_name = parent_path[0]  # top-level class folder
                category = (new_note_category_ref.current.value
                            if new_note_category_ref.current and getattr(new_note_category_ref.current, 'value', None)
                            else "Daily Notes")

                # Determine mode: Text vs Upload
                mode = "Text"
                if note_mode_ref.current:
                    try:
                        mode = getattr(note_mode_ref.current, 'value', 'Text') or 'Text'
                    except Exception:
                        mode = 'Text'

                try:
                    if mode == "Upload":
                        # If file picker has a result, use it; otherwise open file picker UI
                        picked = None
                        try:
                            # FilePicker stores files in .result.files when used
                            fp = note_file_picker_ref.current
                            if fp and getattr(fp, 'result', None) and getattr(fp.result, 'files', None):
                                picked = fp.result.files[0].path
                        except Exception:
                            picked = None

                        if not picked:
                            # Open the file picker using pick_files so we can restrict extensions.
                            if note_file_picker_ref.current:
                                try:
                                    note_file_picker_ref.current.pick_files(
                                        allow_multiple=False,
                                        allowed_extensions=["pdf", "pptx", "docx"],
                                    )
                                    page.update()
                                except Exception:
                                    # Fallback to opening the picker if pick_files isn't available
                                    try:
                                        note_file_picker_ref.current.open = True
                                        page.update()
                                    except Exception:
                                        pass
                            raise RuntimeError("Please select a file to upload")

                        # Upload the selected file into notes
                        if callbacks.get('upload_note_document'):
                            callbacks['upload_note_document'](class_name=class_name, category=category, file_path=picked)
                    else:
                        # Text note
                        if callbacks.get("create_note"):
                            callbacks["create_note"](class_name=class_name,
                                                       note_name=note_name,
                                                       category=category,
                                                       content="")
                except Exception as err:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"⚠️ Failed to save note: {err}"),
                        bgcolor="#6A2830"
                    )
                    page.snack_bar.open = True

                # Close dialog and reset input
                add_note_dialog_ref.current.open = False
                new_note_name_ref.current.value = ""
                if new_note_category_ref.current:
                    try:
                        new_note_category_ref.current.value = "Daily Notes"
                        new_note_category_ref.current.update()
                    except Exception:
                        pass
                # reset mode dropdown
                if note_mode_ref.current:
                    try:
                        note_mode_ref.current.value = "Text"
                        note_mode_ref.current.update()
                    except Exception:
                        pass

                # Refresh sidebar
                build_tree_ui()

                # Notify user (include category)
                display_cat = category if 'category' in locals() else "Daily Notes"
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ Added note: {note_name} ({display_cat})"), bgcolor="#66A36C")
                page.snack_bar.open = True
                page.update()
        
    # Dialog for adding folders
    add_folder_dialog = ft.AlertDialog(
        ref=add_folder_dialog_ref,
        modal=True,
    title=ft.Text("Add New Folder"),
        content=ft.Container(
            ft.Column([
                ft.Text("Enter the folder name:", size=14),
                ft.TextField(
                    ref=new_folder_name_ref,
                    hint_text="e.g., Computer Science",
                    autofocus=True,
                    on_submit=add_folder_action,
                    width=280,
                ),
            ], spacing=15, tight=True),
            width=300,
            height=120,
            padding=ft.padding.all(10),
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(add_folder_dialog_ref.current, 'open', False) or page.update()),
            ft.ElevatedButton("Add Folder", on_click=add_folder_action, style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Dialog for adding notes
    add_note_dialog = ft.AlertDialog(
        ref=add_note_dialog_ref,
        modal=True,
    title=ft.Text("Add New Note"),
        content=ft.Container(
            ft.Column([
                ft.Text("Enter the note name:", size=14),
                ft.TextField(
                    ref=new_note_name_ref,
                    hint_text="e.g., Lecture 1 Notes",
                    autofocus=True,
                    on_submit=add_note_action,
                    width=280,
                ),
                ft.Dropdown(
                    ref=note_mode_ref,
                    value="Text",
                    width=280,
                    options=[
                        ft.dropdown.Option("Text"),
                        ft.dropdown.Option("Upload"),
                    ],
                    bgcolor=WHITE,
                    color=TEXT_DARK,
                    border_color=PASTEL_PURPLE,
                    border_radius=8,
                    content_padding=ft.padding.all(8),
                ),
                ft.Dropdown(
                    ref=new_note_category_ref,
                    value="Daily Notes",
                    width=280,
                    options=[
                        ft.dropdown.Option("Syllabus"),
                        ft.dropdown.Option("Textbook"),
                        ft.dropdown.Option("Daily Notes"),
                        ft.dropdown.Option("Other"),
                    ],
                    bgcolor=WHITE,
                    color=TEXT_DARK,
                    border_color=PASTEL_PURPLE,
                    border_radius=8,
                    content_padding=ft.padding.all(8),
                ),
            ], spacing=12, tight=True),
            width=300,
            height=170,
            padding=ft.padding.all(10),
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(add_note_dialog_ref.current, 'open', False) or page.update()),
            ft.ElevatedButton("Add Note", on_click=add_note_action, style=ft.ButtonStyle(bgcolor=DARK_PURPLE)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Tree container
    tree_container = ft.Column(ref=tree_container_ref, spacing=2, tight=True)
    
    # Action buttons
    add_folder_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.icons.CREATE_NEW_FOLDER, size=16),
            ft.Text("Add Folder", size=12)
        ], spacing=4, tight=True),
        on_click=lambda e: setattr(add_folder_dialog_ref.current, 'open', True) or page.update(),
        style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE, color=WHITE),
        height=32,
        width=120,
    )
    
    add_note_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.icons.NOTE_ADD, size=16),
            ft.Text("Add Note", size=12)
        ], spacing=4, tight=True),
        on_click=lambda e: setattr(add_note_dialog_ref.current, 'open', True) or page.update(),
        style=ft.ButtonStyle(bgcolor=DARK_PURPLE, color=WHITE),
        height=32,
        width=120,
    )

    # Refs & state
    nav_index = 0  # 0: Notes, 1: Transcribe, 2: AI
    notes_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    live_transcription_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    file_transcription_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    # Attach notes_ref to handler
        # Notes reference handled by ButtonManager in main.py
    trans_live_ref: ft.Ref[ft.ListView] = ft.Ref[ft.ListView]()
    sum_output_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()
    sum_mode_ref: ft.Ref[ft.Dropdown] = ft.Ref[ft.Dropdown]()
    ask_input_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    ask_output_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()
    quiz_n_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    quiz_list_ref: ft.Ref[ft.ListView] = ft.Ref[ft.ListView]()
    upload_results_ref: ft.Ref[ft.ListView] = ft.Ref[ft.ListView]()
    document_status_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()



    # Google Drive button for top navigation
    google_drive_btn = ft.ElevatedButton(
        "Google Drive",
        icon=ft.icons.CLOUD,
        style=ft.ButtonStyle(bgcolor="#4285F4", color=ft.colors.WHITE),  # Google blue color
        on_click=callbacks.get('connect_drive', lambda e: None),
    )

    # Back to Landing button
    back_to_landing_btn = ft.IconButton(
        icon=ft.icons.HOME,
        tooltip="Back to Landing Page",
        on_click=return_to_landing,
        icon_color=WHITE,
    )
    
    app_bar = ft.AppBar(
        title=ft.Text("StudyAI", size=24, weight=ft.FontWeight.BOLD),
        center_title=False,
        bgcolor=PASTEL_PURPLE,
        color=WHITE,
        actions=[
            google_drive_btn,
        ],
    )

    # ---------------- Sidebar (NavigationRail)
    # Create a simple container that will hold the current view
    main_content = ft.Container(expand=True)
    nav_container_ref = ft.Ref[ft.Container]()
    
    # Navigation logic is now handled by nav_button_click functions

    # Create custom navigation buttons instead of NavigationRail
    current_nav = {"selected": 0}
    
    # Navigation handler will be defined after all views are created
    def nav_button_click(index):
        """Navigation button click handler - FUNCTIONAL"""
        def handler(_):
            current_nav["selected"] = index
            # Views will be referenced after they're defined
            page.update()
        return handler
    
    # Top navigation bar buttons - horizontal layout
    nav_buttons = [
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.NOTE_ALT, size=18),
                ft.Text("Notes", weight=ft.FontWeight.W_500, size=14)
            ], spacing=6),
            on_click=nav_button_click(0),
            style=ft.ButtonStyle(
                bgcolor=PASTEL_PURPLE,
                color=ft.colors.ON_PRIMARY,
            ),
            height=40,
        ),
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.MIC, size=18),
                ft.Text("Transcribe", weight=ft.FontWeight.W_500, size=14)
            ], spacing=6),
            on_click=nav_button_click(1),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.SURFACE_VARIANT,
                color=ft.colors.ON_SURFACE,
            ),
            height=40,
        ),
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.SMART_TOY, size=18),
                ft.Text("AI Assistant", weight=ft.FontWeight.W_500, size=14)
            ], spacing=6),
            on_click=nav_button_click(2),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.SURFACE_VARIANT,
                color=ft.colors.ON_SURFACE,
            ),
            height=40,
        ),
    ]
    
    # Mode tabs (moved to content column)
    mode_tabs = ft.Container(
        content=ft.Row(
            nav_buttons,
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor=WHITE,
        padding=ft.padding.only(top=12, bottom=12),  # No left/right padding, inherits from parent
        border=ft.border.only(bottom=ft.BorderSide(2, PASTEL_PURPLE)),
        height=64,
        margin=ft.margin.all(0),  # Ensure no stray margins
    )
    
    # Purple divider between sidebar and content
    divider = ft.Container(
        width=2,
        bgcolor=PASTEL_PURPLE,
    )
    
    # Left sidebar with Home button and Class section
    back_to_landing_nav_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.icons.HOME, size=18),
            ft.Text("Home", weight=ft.FontWeight.W_500, size=14)
        ], spacing=6),
        on_click=return_to_landing,
        style=ft.ButtonStyle(
            bgcolor=PASTEL_PURPLE,
            color=ft.colors.ON_PRIMARY,
        ),
        width=220,
        height=40,
    )
    
    # Sidebar column content
    sidebar_column = ft.Column([
        ft.Container(
            back_to_landing_nav_btn,
            padding=ft.padding.only(top=12, bottom=12),
        ),
        ft.Divider(color=PASTEL_PURPLE, height=1),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Classes & Notes", size=14, color=TEXT_DARK, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=8),
                ft.Row([
                    add_folder_btn,
                    add_note_btn,
                ], spacing=6, alignment=ft.MainAxisAlignment.START),
                ft.Container(height=8),
                ft.Container(
                    tree_container,
                    expand=True,  # fills remaining vertical space
                    bgcolor=WHITE,
                    border_radius=8,
                    border=ft.border.all(1, PASTEL_PURPLE),
                    padding=ft.padding.all(8),
                ),
                ft.Container(height=8),  # 👈 small gap
                # Audio Player widget for sidebar (centered, fixed size, controls + volume)
                ft.Container(
                    ft.Column([
                        ft.Text("🎵 Audio Player", size=12, weight=ft.FontWeight.BOLD, color=TEXT_DARK, text_align=ft.TextAlign.CENTER),
                        ft.Text("No file playing", ref=now_playing_ref, size=11, italic=True, color=TEXT_DARK, text_align=ft.TextAlign.CENTER),

                        # Top bar: progress/time scrubber
                        ft.Row([
                            ft.Text("0:00", ref=elapsed_time_ref, size=11, color=TEXT_DARK),
                            ft.Slider(
                                ref=progress_slider_ref,
                                min=0,
                                max=100,
                                value=0,
                                width=150,
                                on_change=lambda e: audio_player_ref.current and getattr(audio_player_ref.current, "seek", lambda v: None)(e.control.value),
                            ),
                            ft.Text("--:--", ref=total_time_ref, size=11, color=TEXT_DARK),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),

                        # Middle: playback buttons
                        ft.Row([
                            ft.IconButton(icon=ft.icons.REPLAY_10, tooltip="Back 10s",
                                          on_click=lambda e: audio_player_ref.current and audio_player_ref.current.seek(audio_player_ref.current.get_current_position() - 10),
                                          icon_color=PASTEL_PURPLE),
                            ft.IconButton(icon=ft.icons.PLAY_ARROW, tooltip="Play",
                                          on_click=lambda e: audio_player_ref.current and audio_player_ref.current.play(),
                                          icon_color=PASTEL_PURPLE),
                            ft.IconButton(icon=ft.icons.PAUSE, tooltip="Pause",
                                          on_click=lambda e: audio_player_ref.current and audio_player_ref.current.pause(),
                                          icon_color=PASTEL_PURPLE),
                            ft.IconButton(icon=ft.icons.STOP, tooltip="Stop",
                                          on_click=lambda e: audio_player_ref.current and audio_player_ref.current.stop(),
                                          icon_color=PASTEL_PURPLE),
                            ft.IconButton(icon=ft.icons.FORWARD_10, tooltip="Forward 10s",
                                          on_click=lambda e: audio_player_ref.current and audio_player_ref.current.seek(audio_player_ref.current.get_current_position() + 10),
                                          icon_color=PASTEL_PURPLE),
                        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),

                        # Bottom bar: volume control
                        ft.Row([
                            ft.Icon(ft.icons.VOLUME_DOWN, size=16, color=TEXT_DARK),
                            ft.Slider(
                                min=0,
                                max=1,
                                divisions=10,
                                value=0.7,
                                width=150,
                                on_change=lambda e: audio_player_ref.current and setattr(audio_player_ref.current, "volume", e.control.value),
                            ),
                            ft.Icon(ft.icons.VOLUME_UP, size=16, color=TEXT_DARK),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),

                        # Hidden audio backend
                        ft.Audio(
                            ref=audio_player_ref,
                            autoplay=False,
                            volume=0.7,
                        ),
                    ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.all(8),
                    bgcolor=SOFT_PURPLE,
                    border_radius=8,
                    height=160,   # fixed size
                    alignment=ft.alignment.center,   # centers the block in sidebar
                ),
            ], spacing=0, tight=True),
            padding=ft.padding.only(top=0, bottom=12),
        ),
    ], spacing=0, tight=True)
    
    # Sidebar container with specified structure
    sidebar = ft.Container(
        width=280,
        alignment=ft.alignment.top_left,
        padding=ft.padding.only(left=12, right=12),
        content=sidebar_column,
        bgcolor=LIGHT_GRAY,
        margin=ft.margin.all(0),  # Remove stray margins
    )

    # Document upload functionality
    current_document = {"file": None, "content": ""}
    
    def handle_document_upload(file):
        """Handle PDF/DOC file selection and processing - UI ONLY"""
        # TODO: Wire in main.py to call app/pdf_manager.py (import/export/list PDFs)
        pass

    # Document file picker
    # Document picker will delegate processing to the DocumentHandler provided in callbacks.
    # When a file is picked the handler will be called with the FilePicker event and UI refs.
    document_picker = ft.FilePicker(
        on_result=lambda e: callbacks.get('upload_document', lambda *a, **k: None)(
            e, notes_ref, document_status_ref, callbacks.get('get_current_class', lambda: "General")()
        )
    )

    # Notes view
    document_status = ft.Text(
        ref=document_status_ref,
        value="No document loaded",
        size=12,
        color=ft.colors.ON_SURFACE,
        italic=True,
    )
    
    toolbar = ft.Row(
        controls=[
            ft.Text(" Notes", size=18, weight=ft.FontWeight.BOLD, color=PASTEL_PURPLE),
            ft.Container(expand=True),  # Spacer
            ft.Container(document_status, padding=ft.padding.only(right=10)),
            ft.ElevatedButton(
                "Upload Document",
                icon=ft.icons.UPLOAD_FILE,
                style=ft.ButtonStyle(bgcolor=DARK_PURPLE, color=ft.colors.ON_PRIMARY),
                on_click=lambda e: document_picker.pick_files(
                    allow_multiple=False,
                    allowed_extensions=["pdf", "docx", "txt", "jpg", "jpeg", "png"]
                ),
            ),
            ft.ElevatedButton(
                "Clear",
                icon=ft.icons.CLEAR,
                style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE, color=ft.colors.ON_PRIMARY),
                on_click=lambda e: None,  # TODO: was `lambda _: (clear notes and document)` -> wire in main.py to call app/pdf_manager.py (import/export/list PDFs)
            ),
            ft.IconButton(
                ft.icons.CONTENT_COPY,
                tooltip="Copy notes",
                icon_color=PASTEL_PURPLE,
                on_click=callbacks.get('copy_notes', lambda e: None),
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # State for notes guidance visibility
    notes_guidance_visible = {"visible": True}
    
    # Guidance text container reference (not just the text)
    notes_guidance_container_ref = ft.Ref[ft.Container]()
    
    def on_notes_change(e):
        """Handle notes text change to hide/show guidance"""
        if notes_ref.current and notes_guidance_container_ref.current:
            has_text = bool(notes_ref.current.value and notes_ref.current.value.strip())
            notes_guidance_container_ref.current.visible = not has_text
            notes_guidance_visible["visible"] = not has_text
            page.update()
    
    notes_editor = ft.TextField(
        ref=notes_ref,
        multiline=True,
        min_lines=50,  # Allow natural expansion within fixed container
        max_lines=None,  # No line limit - container height controls size
        expand=True,
        border=ft.InputBorder.NONE,  # Remove border to prevent double borders
        content_padding=ft.padding.all(8),  # Minimal padding to fit within container
        text_size=14,
        bgcolor=ft.colors.TRANSPARENT,  # Make background transparent
        width=None,  # Let container control width
        height=None,  # Let container control height
        on_change=on_notes_change,  # Add change handler
    )
    
    # Guidance text overlay - must match TextField positioning exactly
    notes_guidance = ft.Text(
        value="Type your lecture notes here...\n\nTips:\n- Use bullet points for key concepts\n- Organize thoughts clearly\n- The AI will analyze this content",
        size=14,  # Match TextField text_size exactly
        color=ft.colors.OUTLINE,
        font_family=None,  # Use default font like TextField
        weight=ft.FontWeight.NORMAL,  # Match TextField font weight
        selectable=False,  # Make it non-selectable so it doesn't interfere
        text_align=ft.TextAlign.LEFT,  # Ensure left alignment like TextField
    )
    
    # Guidance container positioned to match TextField's actual text cursor position
    notes_guidance_container = ft.Container(
        ref=notes_guidance_container_ref,
        content=notes_guidance,
        padding=ft.padding.only(left=8, right=8, top=21, bottom=8),  # Add extra top padding to align with cursor
        alignment=ft.alignment.top_left,  # Top-left alignment to match TextField
        disabled=True,  # Make it non-interactive so clicks pass through
        visible=True,  # Initially visible
        expand=True,  # Match TextField expand behavior
    )
    
    # Stack to overlay guidance text under textfield - both elements fill the same space
    notes_editor_stack = ft.Stack([
        # Guidance text positioned behind the textfield
        notes_guidance_container,
        # TextField on top to receive all user interaction
        notes_editor,
    ])

    # --- Audio Player Setup ---
    # (audio_player_ref is declared earlier near other refs)
    def play_audio(path: str):
        if audio_player_ref.current:
            audio_player_ref.current.src = path
            audio_player_ref.current.autoplay = True  # start playing on click
            audio_player_ref.current.update()

        if now_playing_ref.current:
            import os
            now_playing_ref.current.value = f"▶️ Now Playing: {os.path.basename(path)}"
            now_playing_ref.current.update()

    # Helper: format seconds to M:SS
    def _format_time(seconds: float) -> str:
        try:
            s = int(round(seconds))
            m = s // 60
            s = s % 60
            return f"{m}:{s:02d}"
        except Exception:
            return "--:--"

    # Update progress UI from audio player
    def update_progress():
        audio = audio_player_ref.current
        if not audio:
            return
        # Safe getters for duration/position
        try:
            duration = getattr(audio, "get_duration", lambda: None)()
        except Exception:
            duration = None
        try:
            pos = getattr(audio, "get_current_position", lambda: 0)()
        except Exception:
            pos = 0

        # Update elapsed label
        if elapsed_time_ref.current:
            elapsed_time_ref.current.value = _format_time(pos or 0)
            try:
                elapsed_time_ref.current.update()
            except Exception:
                pass

        # Update total label
        if total_time_ref.current:
            total_time_ref.current.value = _format_time(duration) if duration else "--:--"
            try:
                total_time_ref.current.update()
            except Exception:
                pass

        # Update slider
        if progress_slider_ref.current:
            try:
                if duration and duration > 0:
                    progress_slider_ref.current.max = duration
                progress_slider_ref.current.value = pos or 0
                progress_slider_ref.current.update()
            except Exception:
                pass

    # Start a repeating asyncio task to refresh progress every second
    async def _progress_loop():
        while True:
            try:
                update_progress()
            except Exception:
                pass
            await asyncio.sleep(1)

    # Kick off loop (non-blocking) only if an event loop is already running
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_progress_loop())
    except RuntimeError:
        # No running loop in this import context — skip starting the background task
        pass
    except Exception:
        pass

    # Register into callbacks so sidebar clicks work
    callbacks.update({
    "open_audio": play_audio,
    "display_transcript": lambda name, snippet, path=None: (
        upload_results_ref.current.controls.insert(
            0,
            ft.Container(
                ft.Row([
                    ft.Icon(ft.icons.DESCRIPTION, size=14, color=TEXT_DARK),
                    ft.Text(f"{name}", size=12, color=TEXT_DARK, weight=ft.FontWeight.BOLD),
                ], spacing=6),
                # 👆 Instead of open_file, load transcript into notes editor
                on_click=lambda e, p=path: (
                    notes_ref.current and setattr(notes_ref.current, "value", open(p, "r", encoding="utf-8").read()),
                    notes_ref.current.update(),
                    page.update()
                ),
                padding=ft.padding.only(left=4, top=2, bottom=2),
            )
        ),
        upload_results_ref.current.update(),
        page.update()
        )   
    })

    # --- Notes view with audio player docked ---
    notes_view = ft.Container(
        ft.Column([
            # Header section - standardized height to match other tabs
            ft.Container(
                toolbar, 
                padding=ft.padding.only(bottom=15),
                height=60,  # Fixed header height matching other tabs
            ),
                        # Main content area - expands to fill all available space  
            ft.Container(
                notes_editor_stack,
                expand=True,  # Dynamic scaling with user's screen size
                padding=ft.padding.all(8),  # Internal padding between border and textbox
                border=ft.border.all(2, PASTEL_PURPLE),
                border_radius=12,
                bgcolor=WHITE,
            ),
            # Status area - consistent with other tabs
        ], spacing=0, expand=True),  # Allow inner containers to expand
        expand=True,
        border=ft.border.all(2, PASTEL_PURPLE),
        border_radius=12,
        padding=ft.padding.all(16),
        bgcolor=SOFT_PURPLE,
    )

    # Transcription view
    trans_running = {"on": False}

    async def handle_transcription_line(line: str):
        """Handle transcription line - UI ONLY"""
        # TODO: Wire in main.py to call app/transcription.py
        pass

    async def start_trans(_):
        """Start transcription - UI ONLY"""
        # TODO: Wire in main.py to call app/transcription.py (start/stop streaming, captions)
        pass

    async def stop_trans(_):
        """Stop transcription - UI ONLY"""
        # TODO: Wire in main.py to call app/transcription.py (start/stop streaming, captions)
        pass

    # Audio upload handlers
    current_audio_file = {"file": None}
    
    
    def handle_audio_upload(file):
        """Handle audio file selection - UI ONLY"""
        # TODO: Wire in main.py to call app/transcription.py
        pass
    
    async def transcribe_audio_file(_):
        """Transcribe the uploaded audio file - UI ONLY"""
        # TODO: Wire in main.py to call app/transcription.py
        pass

    trans_header = ft.Row([
    ft.Row([ft.Icon(ft.icons.MIC, color=PASTEL_PURPLE), ft.Text("Transcription", size=18, weight=ft.FontWeight.BOLD)], spacing=8),
        ft.Container(expand=True),
        ft.Text("Status: Ready", size=12, color=ft.colors.ON_SURFACE),
    ])

    start_btn = ft.ElevatedButton(
        "Start Recording", 
        icon=ft.icons.MIC, 
        on_click=callbacks.get('start_recording', lambda e: None),
        style=ft.ButtonStyle(
            bgcolor=PASTEL_PURPLE,
            color=ft.colors.ON_PRIMARY,
            padding=ft.padding.symmetric(vertical=12, horizontal=18),
        )
    )
    stop_btn = ft.OutlinedButton(
        "Stop Recording", 
        icon=ft.icons.STOP, 
        on_click=callbacks.get('stop_recording', lambda e: None),
        style=ft.ButtonStyle(
            bgcolor=DARK_PURPLE,
            color=ft.colors.ON_PRIMARY,
        )
    )

    trans_controls = ft.Row([
        start_btn,
        stop_btn,
        ft.Container(expand=True),
    ], spacing=10)

    trans_live = ft.ListView(
        ref=trans_live_ref, 
        expand=True, 
        spacing=4, 
        padding=ft.padding.all(12), 
        auto_scroll=True
    )

    # Audio upload section
    file_picker = ft.FilePicker(
        on_result=lambda e: callbacks.get("upload_audio", lambda ev: None)(e)
    )

    # Note document picker (for Upload mode in Add Note dialog)
    def _note_picker_result(e):
        try:
            if note_file_picker_ref.current is not None:
                setattr(note_file_picker_ref.current, 'result', e)
            # show a small confirmation
            try:
                page.snack_bar = ft.SnackBar(ft.Text(f"Selected file: {e.files[0].name}"), bgcolor=PASTEL_PURPLE)
                page.snack_bar.open = True
            except Exception:
                pass
            page.update()
        except Exception:
            pass

    note_file_picker = ft.FilePicker(
        ref=note_file_picker_ref,
        on_result=_note_picker_result,
    )
    
    # Model size dropdown
    model_size_ref = ft.Ref[ft.Dropdown]()
    model_size_dropdown = ft.Dropdown(
        ref=model_size_ref,
        width=140,
        value="base",
        options=[
            ft.dropdown.Option("tiny"),
            ft.dropdown.Option("base"),
            ft.dropdown.Option("small"),
            ft.dropdown.Option("medium"),
            ft.dropdown.Option("large"),
        ],
        label="Model Size",
        bgcolor=WHITE,
        color=ft.colors.BLACK,
        border_color=PASTEL_PURPLE,
        content_padding=ft.padding.all(10),
        text_style=ft.TextStyle(size=14),
        border_radius=8,
        on_change=callbacks.get('model_change', lambda e: None),
    )
    
    upload_status_ref = ft.Ref[ft.Text]()
    upload_status = ft.Text(
        ref=upload_status_ref,
        size=12,
        color=ft.colors.ON_SURFACE,
    )
    
    upload_btn = ft.ElevatedButton(
    "Upload Audio File",
    icon=ft.icons.UPLOAD_FILE,
    on_click=lambda e: file_picker.pick_files(
        allowed_extensions=["mp3", "wav", "m4a", "flac", "ogg", "mp4", "mov", "mkv"]
    ),
    style=ft.ButtonStyle(
        bgcolor=PASTEL_PURPLE,
        color=ft.colors.ON_PRIMARY,
        padding=ft.padding.symmetric(vertical=12, horizontal=18),
    ),
    )
    
    transcribe_btn = ft.ElevatedButton(
        "Transcribe Audio",
        icon=ft.icons.TRANSCRIBE,
    on_click=lambda e: None,  # TODO: was `transcribe_audio_file` -> wire in main.py to call app/transcription.py (start/stop streaming, captions)
        disabled=True,
        style=ft.ButtonStyle(
            bgcolor=DARK_PURPLE,
            color=ft.colors.ON_PRIMARY,
        )
    )
    
    upload_controls = ft.Column([
        ft.Row([
            upload_btn,
            model_size_dropdown,
            ft.Container(expand=True),
        ], spacing=10),
        ft.Container(upload_status, padding=ft.padding.only(top=8)),
    ], spacing=8)
    
    upload_results = ft.ListView(
        ref=upload_results_ref,
        expand=True,
        spacing=4,
        padding=ft.padding.all(12),
    )

    # Live Transcription tab content
    live_transcription_tab = ft.Column([
        # Header row with inline controls
        ft.Container(
            ft.Row([
                ft.Row([
                    ft.Icon(ft.icons.MIC, color=PASTEL_PURPLE, size=20),
                    ft.Text("Live Transcription", size=16, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Container(expand=True),
                start_btn,
                stop_btn,
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            padding=ft.padding.all(16),
            height=60,
        ),
        ft.Container(height=8),
        # Transcription output section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.SUBTITLES, color=PASTEL_PURPLE, size=16),
                    ft.Text("Live Transcription Output:", weight=ft.FontWeight.W_500),
                ], spacing=8),
                ft.Container(height=8),
                # Live transcription streaming list (shows partial segments)
                ft.Container(
                    trans_live,
                    expand=False,
                    height=200,
                    border=ft.border.all(1, PASTEL_PURPLE),
                    border_radius=8,
                    bgcolor=WHITE,
                ),
                ft.Container(height=8),
                # Read-only multiline TextField for assembled live transcription (larger, styled)
                ft.Container(
                    ft.Column([
                        ft.Text("📝 Live Transcript", size=16, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ft.TextField(
                            ref=live_transcription_ref,
                            multiline=True,
                            expand=True,
                            read_only=True,
                            max_lines=None,
                            height=400,
                            width=800,
                            text_size=14,
                            hint_text="Your live transcription will appear here...",
                            border=ft.InputBorder.OUTLINE,
                            border_radius=12,
                            content_padding=ft.padding.all(12),
                            bgcolor=ft.colors.WHITE,
                            # TextField does not accept a `scroll` kwarg; container handles scrolling
                        )
                    ], expand=True, spacing=8),
                    expand=True,
                    padding=ft.padding.all(8),
                    border=ft.border.all(1, PASTEL_PURPLE),
                    border_radius=8,
                    bgcolor=SOFT_PURPLE,
                ),
            ]),
            padding=ft.padding.all(12),
            expand=True,
        ),
    ], spacing=0)

    # Audio File Upload tab content
    audio_upload_tab = ft.Column([
        # Controls section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.UPLOAD_FILE, color=PASTEL_PURPLE, size=20),
                    ft.Text("Audio File Upload", size=16, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Text("Upload audio files for batch transcription processing", size=12, color=ft.colors.OUTLINE),
                ft.Container(height=10),
                ft.Container(upload_controls, height=80),
            ]),
            padding=ft.padding.all(16),
            height=130,
        ),
        ft.Container(height=15),
        # Upload results section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.LIST_ALT, color=PASTEL_PURPLE, size=16),
                    ft.Text("Transcription Results:", weight=ft.FontWeight.W_500),
                ], spacing=8),
                ft.Container(height=8),
                # File upload results list (shows processed files)
                ft.Container(
                    upload_results,
                    expand=False,
                    height=180,
                    border=ft.border.all(1, PASTEL_PURPLE),
                    border_radius=8,
                    bgcolor=WHITE,
                ),
                ft.Container(height=8),
                # Note: removed redundant final transcription text area to avoid duplicate boxes
            ]),
            padding=ft.padding.all(12),
            expand=True,
        ),
    ], spacing=0)

    # Transcription tabs
    transcription_tabs = ft.Tabs(
        tabs=[
            ft.Tab(text="Live Recording", icon=ft.icons.MIC, content=live_transcription_tab),
            ft.Tab(text="File Upload", icon=ft.icons.UPLOAD_FILE, content=audio_upload_tab),
        ],
        selected_index=0,
        expand=True,
        tab_alignment=ft.TabAlignment.START,
    )

    # Uniform transcription view - standardized to match other tabs
    trans_view = ft.Container(
        ft.Column([
            # Header section - standardized height to match other tabs
            ft.Container(
                trans_header, 
                padding=ft.padding.only(bottom=15),
                height=60,  # Fixed header height matching other tabs
            ),
            # Main content area - expands to fill all available space
            ft.Container(
                transcription_tabs,
                expand=True,  # Dynamic scaling with user's screen size
                border=ft.border.all(2, PASTEL_PURPLE),
                border_radius=12,
                bgcolor=WHITE,
            ),
            # Status area - consistent with other tabs
        ], spacing=0, expand=True),  # Allow inner containers to expand
        expand=True,
        border=ft.border.all(2, PASTEL_PURPLE),
        border_radius=12,
        padding=ft.padding.all(16),
        bgcolor=SOFT_PURPLE,
    )
    sum_mode = ft.Dropdown(
        ref=sum_mode_ref,
        width=220,
        value="Topics",
        options=[
            ft.dropdown.Option("Topics", "Key Topics"),
            ft.dropdown.Option("Q&A", "Q&A Format"),
            ft.dropdown.Option("Detailed", "Detailed Summary")
        ],
        border_radius=8,
        bgcolor=WHITE,
        color=ft.colors.BLACK,
        border_color=PASTEL_PURPLE,
        content_padding=ft.padding.all(12),
        text_style=ft.TextStyle(size=14),
    )
    sum_btn = ft.ElevatedButton(
        "Generate Summary",
        icon=ft.icons.SUMMARIZE,
        style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE, color=ft.colors.ON_PRIMARY)
    )

    # Class selector and notes checklist
    class_select_ref = ft.Ref[ft.Dropdown]()
    # CheckboxGroup does not exist in flet - use a Column of Checkbox controls instead
    notes_check_ref = ft.Ref[ft.Column]()
    class_select = ft.Dropdown(ref=class_select_ref, width=220, value=None, options=[], bgcolor=WHITE, border_color=PASTEL_PURPLE)
    notes_check = ft.Column(ref=notes_check_ref, controls=[], spacing=6)

    # Enhanced output: scrollable text area
    sum_out = ft.TextField(
        ref=sum_output_ref,
        multiline=True,
        read_only=True,
        expand=True,
        text_size=14,
        border=ft.InputBorder.OUTLINE,
        border_radius=8,
        content_padding=ft.padding.all(12),
        bgcolor=WHITE,
        hint_text="Summary will appear here...",
        hint_style=ft.TextStyle(color=ft.colors.OUTLINE, italic=True),
    )

    # Helper functions for transcription UI
    def append_live_transcription(text: str):
        try:
            if live_transcription_ref.current:
                current = live_transcription_ref.current.value or ""
                if current:
                    live_transcription_ref.current.value = current + "\n" + text
                else:
                    live_transcription_ref.current.value = text
                live_transcription_ref.current.update()
        except Exception:
            pass

    def set_file_transcription(text: str):
        try:
            if file_transcription_ref.current:
                file_transcription_ref.current.value = text
                file_transcription_ref.current.update()
        except Exception:
            pass

    # Loading spinner for transcription tasks
    loading_spinner = ft.ProgressRing(visible=False)

    def start_loading():
        try:
            loading_spinner.visible = True
            loading_spinner.update()
        except Exception:
            pass

    def stop_loading():
        try:
            loading_spinner.visible = False
            loading_spinner.update()
        except Exception:
            pass

    # Expose transcription helper callbacks to external handlers via callbacks dict
    try:
        callbacks.update({
            "append_live_transcription": append_live_transcription,
            "set_file_transcription": set_file_transcription,
            "start_loading": start_loading,
            "stop_loading": stop_loading,
        })
    except Exception:
        pass

    async def do_summarize(_):
        """Generate summary - UI ONLY"""
        # TODO: Wire in main.py to call app/summarizer.py (summaries, Q&A)
        pass

    def _generate_summary(e):
        # Gather inputs
        cls = None
        try:
            cls = class_select_ref.current.value
        except Exception:
            cls = None

        selected_notes = []
        try:
            if notes_check_ref.current:
                # collect checked checkboxes and return their stored note_path
                for ctl in getattr(notes_check_ref.current, 'controls', []) or []:
                    try:
                        if getattr(ctl, 'value', False):
                            path = getattr(ctl, 'note_path', None)
                            if path:
                                selected_notes.append(path)
                            else:
                                # fallback to label if note_path missing
                                selected_notes.append(getattr(ctl, 'label', ''))
                    except Exception:
                        continue
        except Exception:
            selected_notes = []

        mode_val = getattr(sum_mode, 'value', 'Topics')
        q = ""
        try:
            q = ask_input_ref.current.value or ""
        except Exception:
            q = ""

        # Call backend summarizer via callbacks (blocking call)
        gen_cb = callbacks.get('generate_summary')
        if gen_cb and cls and selected_notes:
            try:
                result = gen_cb(class_name=cls, notes=selected_notes, query=q, mode=mode_val)
                # put result into output
                if sum_output_ref.current:
                    sum_output_ref.current.value = result
                    sum_output_ref.current.update()
            except Exception as err:
                page.snack_bar = ft.SnackBar(ft.Text(f"❌ Summarization failed: {err}"), bgcolor="#6A2830")
                page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Please select a class and at least one note."), bgcolor="#6A2830")
            page.snack_bar.open = True

    sum_btn.on_click = _generate_summary

    # --- Summarizer Chat Interface ---
    # Replaces the previous one-shot summary UI with an interactive chat
    class_selector_ref = ft.Ref[ft.Dropdown]()
    files_selector_ref = ft.Ref[ft.Column]()
    chat_column_ref = ft.Ref[ft.Column]()
    chat_input_ref = ft.Ref[ft.TextField]()
    # Header ref for AI chat so we can update the title with active class
    ai_chat_header = ft.Ref[ft.Text]()

    # Top controls: class selector, multi-select files, start session
    # Handlers for Start Session (bind class only) and Send (auto-start on first send)
    def start_session_handler(e=None):
        # Determine selected class from dropdown
        try:
            selected = class_selector_ref.current.value if class_selector_ref and class_selector_ref.current else None
        except Exception:
            selected = None

        if selected:
            # bind active class
            try:
                active_class.current = selected
            except Exception:
                pass

            # Try to persist selection using provided callback if available
            try:
                save_cb = callbacks.get('save_to_local_storage')
                if callable(save_cb):
                    save_cb('active_class', selected)
                else:
                    # Fallback: persist to class_data.json (best-effort)
                    try:
                        cd_path = Path('class_data.json')
                        if cd_path.exists():
                            data = json.loads(cd_path.read_text(encoding='utf-8'))
                        else:
                            data = {}
                        data.setdefault('current_classes', {})
                        data['current_classes']['selected'] = selected
                        cd_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
                    except Exception:
                        pass
            except Exception:
                pass

            # Update header if present
            try:
                if ai_chat_header and getattr(ai_chat_header, 'current', None):
                    ai_chat_header.current.value = f"AI Study Chat — {selected}"
                    ai_chat_header.current.update()
            except Exception:
                pass

            # Give backend a chance to switch class
            try:
                if callbacks.get('switch_class'):
                    callbacks.get('switch_class')(class_name=selected)
            except Exception:
                pass

            # Show snackbar
            try:
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ Class set to {selected}"))
                page.snack_bar.open = True
            except Exception:
                pass
            try:
                page.update()
            except Exception:
                pass
            return
        else:
            try:
                page.snack_bar = ft.SnackBar(ft.Text("⚠ Please select a class first!"))
                page.snack_bar.open = True
                page.update()
            except Exception:
                pass
            return

    def send_message_handler(e):
        # guard: require active class
        try:
            if not getattr(active_class, 'current', None):
                page.snack_bar = ft.SnackBar(ft.Text("⚠ Please select a class first!"))
                page.snack_bar.open = True
                page.update()
                return
        except Exception:
            page.snack_bar = ft.SnackBar(ft.Text("⚠ Please select a class first!"))
            page.snack_bar.open = True
            try:
                page.update()
            except Exception:
                pass
            return

        # Extract message text
        try:
            msg = chat_input_ref.current.value if chat_input_ref and chat_input_ref.current else ""
        except Exception:
            msg = ""

        if not msg or not msg.strip():
            return

        # Auto-start session on first send by calling backend start_session callback
        try:
            start_cb = callbacks.get('start_session')
            if callable(start_cb):
                # collect checked files
                try:
                    files = [getattr(cb, 'file_path', getattr(cb, 'label', None)) for cb in (files_selector_ref.current.controls if files_selector_ref.current else []) if getattr(cb, 'value', False)]
                except Exception:
                    files = []
                # call backend start_session with bound class
                try:
                    start_cb(active_class.current, files, chat_column_ref)
                except Exception:
                    pass
        except Exception:
            pass

        # Call backend send_message and capture assistant reply (if any)
        assistant_reply = None
        try:
            send_cb = callbacks.get('send_message')
            if callable(send_cb):
                assistant_reply = send_cb(msg, chat_column_ref, chat_input_ref)
        except Exception:
            assistant_reply = None

        # Save the user message and assistant reply to disk (per-class) using existing callbacks if available
        try:
            save_cb = callbacks.get('save_ai_message')
            if callable(save_cb):
                # Let the backend handle persistence for both user and assistant
                try:
                    save_cb(active_class.current, {'role': 'user', 'text': msg})
                    if assistant_reply:
                        save_cb(active_class.current, {'role': 'assistant', 'text': assistant_reply})
                except Exception:
                    pass
            else:
                # Fallback: append to data/classes/<class>/ai_sessions/chat_log.json
                try:
                    base = Path('data/classes') / active_class.current / 'ai_sessions'
                    base.mkdir(parents=True, exist_ok=True)
                    log_file = base / 'chat_log.json'
                    entry_user = {'timestamp': datetime.datetime.utcnow().isoformat()+'Z', 'role': 'user', 'text': msg}
                    arr = json.loads(log_file.read_text(encoding='utf-8') or '[]') if log_file.exists() else []
                    arr.append(entry_user)
                    if assistant_reply:
                        entry_assist = {'timestamp': datetime.datetime.utcnow().isoformat()+'Z', 'role': 'assistant', 'text': assistant_reply}
                        arr.append(entry_assist)
                    log_file.write_text(json.dumps(arr, indent=2), encoding='utf-8')
                except Exception:
                    pass
        except Exception:
            pass

        # clear input and update UI
        try:
            if chat_input_ref and getattr(chat_input_ref, 'current', None):
                chat_input_ref.current.value = ""
                chat_input_ref.current.update()
        except Exception:
            pass

        try:
            page.update()
        except Exception:
            pass

    top_controls = ft.Row(
        controls=[
            ft.Dropdown(
                ref=class_selector_ref,
                label="Select Class",
                options=[],
                width=220,
                bgcolor=WHITE,
                border_color=PASTEL_PURPLE,
            ),
            ft.Container(
                ft.Column(ref=files_selector_ref, controls=[], spacing=6),
                width=380,
                height=120,
            ),
            ft.ElevatedButton(
                "Start Session",
                icon=ft.icons.PLAY_CIRCLE_OUTLINE,
                on_click=start_session_handler,
                style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE, color=ft.colors.ON_PRIMARY, padding=ft.padding.symmetric(vertical=10, horizontal=16)),
            ),
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    # Chat window
    chat_window = ft.Container(
        ft.Column(ref=chat_column_ref, spacing=12, expand=True),
        border=ft.border.all(1, "#E3DFF5"),
        border_radius=12,
        padding=12,
        expand=True,
        bgcolor=SOFT_PURPLE,
    )

    # Input row
    input_row = ft.Row(
        controls=[
            ft.TextField(ref=chat_input_ref, hint_text="Ask me about your notes...", expand=True, multiline=False),
            ft.IconButton(
                icon=ft.icons.SEND,
                tooltip="Send",
                on_click=send_message_handler,
                style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE),
            )
        ],
        spacing=8,
    )

    def add_chat_message(chat_col_ref, message: str, sender: str = "assistant"):
        # create a bubble; assistant on left (soft purple), user on right (pastel purple)
        if not chat_col_ref or not getattr(chat_col_ref, 'current', None):
            return
        bubble_color = "#FFFFFF" if sender == "assistant" else PASTEL_PURPLE
        text_color = ft.colors.BLACK if sender == "assistant" else ft.colors.ON_PRIMARY
        align = ft.MainAxisAlignment.START if sender == "assistant" else ft.MainAxisAlignment.END
        bubble = ft.Container(
            ft.Text(message, color=text_color),
            bgcolor=bubble_color,
            padding=ft.padding.all(12),
            border_radius=12,
            width=520,
        )
        chat_col_ref.current.controls.append(ft.Row([bubble], alignment=align))
        try:
            chat_col_ref.current.update()
        except Exception:
            pass

    # Build tab column
    summarizer_tab = ft.Column([
        ft.Row([ft.Icon(ft.icons.SUMMARIZE, color=PASTEL_PURPLE), ft.Text("AI Study Chat", ref=ai_chat_header, size=18, weight=ft.FontWeight.BOLD)], spacing=8),
        ft.Container(top_controls, padding=ft.padding.all(8)),
        chat_window,
        ft.Container(input_row, padding=ft.padding.only(top=8)),
    ], expand=True, spacing=12)

    # Study Buddy tab
    ask_in = ft.TextField(
        ref=ask_input_ref, 
        expand=True, 
        label="Ask a question about your notes",
        hint_text="e.g., What are the main concepts? Explain this topic...",
        border_radius=8,
        content_padding=ft.padding.all(12),
    )
    ask_btn = ft.ElevatedButton(
        "Ask AI", 
        icon=ft.icons.QUESTION_ANSWER,
        style=ft.ButtonStyle(bgcolor=DARK_PURPLE, color=ft.colors.ON_PRIMARY)
    )
    ask_out = ft.TextField(
        ref=ask_output_ref, 
        multiline=True,
        read_only=True,
        expand=True,
        text_size=14,
        border=ft.InputBorder.OUTLINE,
        border_radius=8,
        content_padding=ft.padding.all(12),
        bgcolor=WHITE,
        hint_text="AI response will appear here...",
        hint_style=ft.TextStyle(color=ft.colors.OUTLINE, italic=True),
    )

    async def do_ask(_):
        """Ask AI question - UI ONLY"""
        # TODO: Wire in main.py to call appropriate manager via main.py
        pass

    ask_btn.on_click = lambda e: None  # TODO: was `do_ask` -> wire in main.py to call appropriate manager via main.py

    study_tab = ft.Column([
        # Question section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.PSYCHOLOGY, color=PASTEL_PURPLE, size=20),
                    ft.Text("Study Buddy", size=16, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Text("Ask questions about your notes and get AI-powered answers", size=12, color=ft.colors.OUTLINE),
                ft.Container(height=10),
                ft.Row([ask_in, ask_btn], spacing=10),
            ]),
            padding=ft.padding.all(16),
            height=130,
        ),
        ft.Container(height=15),
        # Response section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.CHAT_BUBBLE_OUTLINE, color=PASTEL_PURPLE, size=16),
                    ft.Text("AI Response:", weight=ft.FontWeight.W_500),
                ], spacing=8),
                ft.Container(height=8),
                ft.Container(
                    ask_out,
                    expand=True,
                ),
            ]),
            padding=ft.padding.all(12),
            expand=True,
        ),
    ], spacing=0)

    # Quiz Master tab
    quiz_n = ft.TextField(
        ref=quiz_n_ref, 
        width=140, 
        value="5", 
        label="Questions",
        border_radius=8,
        text_align=ft.TextAlign.CENTER,
        bgcolor=WHITE,
        color=ft.colors.BLACK,
        border_color=PASTEL_PURPLE,
        content_padding=ft.padding.all(12),
        text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_500),
    )
    quiz_btn = ft.ElevatedButton(
        "Generate Quiz", 
        icon=ft.icons.QUIZ,
        style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE, color=ft.colors.ON_PRIMARY)
    )
    quiz_list = ft.ListView(
        ref=quiz_list_ref, 
        expand=True, 
        spacing=15, 
        padding=ft.padding.all(16),
        auto_scroll=True,
    )

    async def do_quiz(_):
        """Generate quiz - UI ONLY"""
        # TODO: Wire in main.py to call app/quiz_manager.py (quiz generation)
        pass

    quiz_btn.on_click = lambda e: None  # TODO: was `do_quiz` -> wire in main.py to call app/quiz_manager.py (quiz generation)

    quiz_tab = ft.Column([
        # Controls section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.QUIZ, color=PASTEL_PURPLE, size=20),
                    ft.Text("Quiz Master", size=16, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Text("Generate practice questions from your notes", size=12, color=ft.colors.OUTLINE),
                ft.Container(height=10),
                ft.Row([
                    ft.Text("Number of questions:", weight=ft.FontWeight.W_500),
                    quiz_n,
                    ft.Container(expand=True),
                    quiz_btn
                ], alignment=ft.MainAxisAlignment.START, spacing=15),
            ]),
            padding=ft.padding.all(16),
            height=130,
        ),
        ft.Container(height=15),
        # Quiz questions section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.LIST_ALT, color=PASTEL_PURPLE, size=16),
                    ft.Text("Generated Quiz Questions:", weight=ft.FontWeight.W_500),
                ], spacing=8),
                ft.Container(height=8),
                ft.Container(
                    quiz_list,
                    expand=True,
                    border=ft.border.all(2, PASTEL_PURPLE),
                    border_radius=8,
                    bgcolor=WHITE,
                ),
            ]),
            padding=ft.padding.all(12),
            expand=True,
        ),
    ], spacing=0)

    # --- Flashcards tab ---
    flash_count_ref = ft.Ref[ft.TextField]()
    flash_card_text_ref = ft.Ref[ft.Text]()
    flash_card_container_ref = ft.Ref[ft.Container]()
    flash_prev_ref = ft.Ref[ft.ElevatedButton]()
    flash_next_ref = ft.Ref[ft.ElevatedButton]()

    # State holders
    flash_state = {
        'cards': [],
        'index': 0,
        'flipped': False,
    }

    def update_flash_ui():
        try:
            cards = flash_state['cards'] or []
            idx = flash_state['index']
            flipped = flash_state['flipped']
            if not cards:
                flash_card_text_ref.current.value = "⚡ No flashcards yet. Click 'Generate Flashcards' to start."
                flash_prev_ref.current.disabled = True
                flash_next_ref.current.disabled = True
            else:
                card = cards[idx]
                flash_card_text_ref.current.value = card['answer'] if flipped else card['question']
                flash_prev_ref.current.disabled = (idx == 0)
                flash_next_ref.current.disabled = (idx >= len(cards)-1)
            flash_card_text_ref.current.update()
            flash_prev_ref.current.update()
            flash_next_ref.current.update()
        except Exception:
            pass

    def flip_flash(e=None):
        try:
            if not flash_state['cards']:
                return
            flash_state['flipped'] = not flash_state['flipped']
            update_flash_ui()
        except Exception:
            pass

    def show_prev(e=None):
        try:
            if flash_state['index'] > 0:
                flash_state['index'] -= 1
                flash_state['flipped'] = False
                update_flash_ui()
        except Exception:
            pass

    def show_next(e=None):
        try:
            if flash_state['index'] < (len(flash_state['cards']) - 1):
                flash_state['index'] += 1
                flash_state['flipped'] = False
                update_flash_ui()
        except Exception:
            pass

    def generate_flashcards_ui(e=None):
        # Read number
        try:
            n = int(flash_count_ref.current.value) if flash_count_ref and flash_count_ref.current else 5
        except Exception:
            n = 5
        # Get notes via callback
        notes_cb = callbacks.get('get_notes_text') or (lambda: "")
        try:
            notes = notes_cb() or ""
        except Exception:
            notes = ""

        gen_cb = callbacks.get('generate_flashcards')
        cards = []
        try:
            if callable(gen_cb):
                cards = gen_cb(notes, n) or []
        except Exception:
            cards = []

        if not cards:
            try:
                page.show_snack_bar(ft.SnackBar(ft.Text("⚠️ Could not generate flashcards. Try again.")))
            except Exception:
                pass
            return

        flash_state['cards'] = cards
        flash_state['index'] = 0
        flash_state['flipped'] = False
        update_flash_ui()

    flash_count = ft.TextField(ref=flash_count_ref, value="5", width=150, label="How many flashcards do you want?", border_radius=8)
    flash_card_text = ft.Text(ref=flash_card_text_ref, value="⚡ No flashcards yet. Click 'Generate Flashcards' to start.", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    flash_card_container = ft.Container(ref=flash_card_container_ref, content=flash_card_text, width=800, height=280, alignment=ft.alignment.center, border_radius=16, bgcolor=SOFT_PURPLE, ink=True, on_click=flip_flash, padding=ft.padding.all(24))
    flash_prev = ft.ElevatedButton("Previous", ref=flash_prev_ref, on_click=show_prev, disabled=True)
    flash_next = ft.ElevatedButton("Next", ref=flash_next_ref, on_click=show_next, disabled=True)
    flash_gen = ft.ElevatedButton("Generate Flashcards", on_click=generate_flashcards_ui, style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE, color=ft.colors.ON_PRIMARY))

    flashcards_tab = ft.Column([
        ft.Row([ft.Icon(ft.icons.CREDIT_CARD, color=PASTEL_PURPLE), ft.Text("Flashcards", size=18, weight=ft.FontWeight.BOLD)], spacing=8),
        ft.Container(ft.Row([flash_count, flash_gen], spacing=12), padding=ft.padding.all(8)),
        ft.Container(flash_card_container, padding=ft.padding.only(top=12, bottom=12)),
        ft.Row([flash_prev, flash_next], alignment=ft.MainAxisAlignment.CENTER, spacing=40)
    ], expand=True, spacing=12)

    tabs = ft.Tabs(
        tabs=[
                ft.Tab(text="Summarizer", icon=ft.icons.NOTE_ALT, content=summarizer_tab),
                ft.Tab(text="Study Buddy", icon=ft.icons.SCHOOL, content=study_tab),
                ft.Tab(text="Quiz Master", icon=ft.icons.HELP_OUTLINE, content=quiz_tab),
                ft.Tab(text="🃏 Flashcards", icon=ft.icons.CREDIT_CARD, content=flashcards_tab),
        ],
        selected_index=0,
        expand=True,  # Let tabs expand to fill available space
        tab_alignment=ft.TabAlignment.START,
    )

    ai_view = ft.Container(
        ft.Column([
            # Header section - standardized height to match other tabs
            ft.Container(
                ft.Row([
                    ft.Row([ft.Icon(ft.icons.SMART_TOY, color=PASTEL_PURPLE), ft.Text("AI Assistant", size=18, weight=ft.FontWeight.BOLD)], spacing=8),
                    ft.Container(expand=True),
                    ft.Text("Powered by AI", size=12, color=ft.colors.ON_SURFACE, italic=True),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.only(bottom=15),
                height=60,  # Fixed header height matching other tabs
            ),
            # Main content area - expands to fill all available space
            ft.Container(
                tabs,
                expand=True,  # Dynamic scaling with user's screen size
                border=ft.border.all(2, PASTEL_PURPLE),
                border_radius=12,
                bgcolor=WHITE,
            ),
            # Status area - consistent with other tabs
        ], spacing=0, expand=True),  # Allow inner containers to expand
        expand=True,
        border=ft.border.all(2, PASTEL_PURPLE),
        border_radius=12,
        padding=ft.padding.all(16),
        bgcolor=SOFT_PURPLE,
    )

    # Now that all views are defined, create the proper navigation handler
    def create_nav_handler(index):
        """Create navigation handler with proper view references"""
        def handler(_):
            current_nav["selected"] = index
            if index == 0:
                main_content.content = notes_view
            elif index == 1:
                main_content.content = trans_view
            else:
                main_content.content = ai_view
            
            # Update button styles
            for i, btn in enumerate(nav_buttons):
                btn.style = ft.ButtonStyle(
                    bgcolor=PASTEL_PURPLE if i == index else ft.colors.SURFACE_VARIANT,
                    color=ft.colors.ON_PRIMARY if i == index else ft.colors.ON_SURFACE,
                )
            page.update()
        return handler

    # Update navigation button handlers with proper references
    nav_buttons[0].on_click = create_nav_handler(0)
    nav_buttons[1].on_click = create_nav_handler(1)
    nav_buttons[2].on_click = create_nav_handler(2)

    main_content.content = notes_view  # Content handled directly, no wrapper needed


    
    # Content column with mode tabs and main content
    content_column = ft.Column([
        mode_tabs,  # Navigation buttons moved here
        ft.Container(
            main_content,
            expand=True,  # Allow full expansion
        ),
    ], spacing=0, expand=True)
    
    # Content container with specified structure (wrapped in Column for scrolling)
    content = ft.Container(
        expand=True,
        alignment=ft.alignment.top_left,
        padding=ft.padding.only(left=24, right=24, top=0),  # Specified padding
        content=ft.Column(
            [content_column],
            expand=True,  # Remove scroll to allow full expansion
        ),
        bgcolor=WHITE,
        margin=ft.margin.all(0),  # Remove stray margins
    )
    
    # Main app layout with proper Row structure
    main_app_content = ft.Column([
        ft.Row(
            controls=[sidebar, divider, content],
            spacing=0,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,  # Align to top
        ),
    ], spacing=0, expand=True)
    
    main_app_layout = main_app_content

    # Complete the enter_main_app function now that we have all components
    def complete_enter_main_app(e=None):
        """Navigate from landing page to main application"""
        app_state["show_landing"] = False
        page.appbar = app_bar  # Show app bar with back button
        main_container.content = main_app_layout
        page.update()
    
    # Replace the enter_main_app function reference
    enter_main_app = complete_enter_main_app
    
    # Show landing page initially
    if app_state["show_landing"]:
        page.appbar = None  # Hide app bar on landing page
        main_container.content = create_landing_page(page, enter_main_app)
    else:
        page.appbar = app_bar
        main_container.content = main_app_layout

    # Initialize tree UI
    build_tree_ui()
    # Populate summarizer class and notes selectors
    try:
        refresh_summarizer_class_notes()
    except Exception:
        pass
    

    
    # Add overlays and components to page
    page.overlay.extend([file_picker, note_file_picker, add_folder_dialog, add_note_dialog, document_picker])
    page.add(main_container)


# End of file