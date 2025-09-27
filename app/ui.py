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
    return None


# ----------------------------
# UI entry point
# Exported function: build_ui(page)
# Your main.py should do:  ft.app(build_ui)
# ----------------------------

def build_ui(page: ft.Page, callbacks=None):
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
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 0
    
    # App state
    app_state = {"show_landing": True}
    
    # Main container that switches between landing and app
    main_container = ft.Container(expand=True)
    
    # Navigation functions (defined early so they can be used in app bar)
    def enter_main_app(e=None):
        """Navigate from landing page to main application"""
        app_state["show_landing"] = False
        # App bar and content will be set after they're defined
        page.update()
    
    def return_to_landing(e=None):
        """Navigate back to landing page from main app"""
        app_state["show_landing"] = True
        page.appbar = None  # Hide app bar
        main_container.content = create_landing_page(page, enter_main_app)
        page.update()
    
    # Class management system
    current_classes = {"classes": ["General"], "selected": "General"}
    class_data = {"General": {"notes": "", "transcriptions": [], "ai_history": []}}
    
    def save_current_class_data():
        """Save current content to the selected class - UI ONLY"""
        # TODO: Wire in main.py to call appropriate class manager
        pass
    
    def load_class_data(class_name):
        """Load data for the selected class - UI ONLY"""
        # TODO: Wire in main.py to call appropriate class manager
        pass
    
    # Remove dynamic resize handler to prevent navigation movement
    # Navigation will now stay fixed in position regardless of content changes
    
    # Custom Pastel Purple Theme Colors
    PASTEL_PURPLE = "#B19CD9"      # Light pastel purple
    DARK_PURPLE = "#8B7AB8"        # Darker purple for accents
    SOFT_PURPLE = "#E6D9F0"        # Very light purple background
    WHITE = "#FFFFFF"              # Pure white
    LIGHT_GRAY = "#F8F6FA"         # Very light gray with purple tint
    TEXT_DARK = "#4A4A4A"          # Dark gray for text

    # Class management UI components
    class_dropdown_ref = ft.Ref[ft.Dropdown]()
    add_class_dialog_ref = ft.Ref[ft.AlertDialog]()
    new_class_name_ref = ft.Ref[ft.TextField]()
    
    def on_class_change(e):
        """Handle class selection change - UI ONLY"""
        # TODO: Wire in main.py to call appropriate class manager
        pass
    class_dropdown = ft.Dropdown(
        ref=class_dropdown_ref,
        width=150,
        value="General",
        options=[ft.dropdown.Option("General")],
        on_change=on_class_change,
        text_style=ft.TextStyle(size=14, color=ft.colors.BLACK),
        bgcolor=WHITE,
        color=ft.colors.BLACK,  # Text color for selected value
    )
    
    def close_add_class_dialog(e):
        add_class_dialog_ref.current.open = False
        new_class_name_ref.current.value = ""
        page.update()
    def add_new_class(e):
        """Add a new class"""
        class_name = new_class_name_ref.current.value.strip()
        if class_name and class_name not in current_classes["classes"]:
            # Add to classes list
            current_classes["classes"].append(class_name)
            class_data[class_name] = {"notes": "", "transcriptions": [], "ai_history": []}
            
            # Update dropdown options
            class_dropdown_ref.current.options = [
                ft.dropdown.Option(cls) for cls in current_classes["classes"]
            ]
            
            # Switch to new class
            save_current_class_data()
            current_classes["selected"] = class_name
            class_dropdown_ref.current.value = class_name
            load_class_data(class_name)
            
            # Close dialog and show success message
            add_class_dialog_ref.current.open = False
            new_class_name_ref.current.value = ""
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ Added new class: {class_name}"))
            page.snack_bar.open = True
            page.update()
        elif class_name in current_classes["classes"]:
            # Show error but don't close dialog
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Class already exists!"))
            page.snack_bar.open = True
            page.update()
        elif not class_name:
            # Show error for empty name but don't close dialog
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Please enter a class name!"))
            page.snack_bar.open = True
            page.update()
    def open_add_class_dialog(e):
        new_class_name_ref.current.value = ""  # Clear the field when opening
        add_class_dialog_ref.current.open = True
        page.update()
    add_class_dialog = ft.AlertDialog(
        ref=add_class_dialog_ref,
        modal=True,
        title=ft.Text("📚 Add New Class"),
        content=ft.Container(
            ft.Column([
                ft.Text("Enter the name of your new class:", size=14),
                ft.TextField(
                    ref=new_class_name_ref,
                    hint_text="e.g., Computer Science 101",
                    autofocus=True,
                    on_submit=add_new_class,
                    width=280,
                ),
            ], spacing=15, tight=True),
            width=300,
            height=120,  # Fixed compact height
            padding=ft.padding.all(10),
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: None),  # TODO: was `close_add_class_dialog` → wire in main.py to call appropriate manager via main.py  # TODO: was `close_add_class_dialog` → wire in main.py to call appropriate manager via main.py
            ft.ElevatedButton("Add Class", on_click=lambda e: None, style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE)),  # TODO: was `add_new_class` → wire in main.py to call appropriate manager via main.py  # TODO: was `add_new_class` → wire in main.py to call appropriate manager via main.py
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    add_class_btn = ft.IconButton(
        icon=ft.icons.ADD,
        tooltip="Add New Class",
        on_click=open_add_class_dialog,  # TODO: was `open_add_class_dialog` → wire in main.py to call appropriate manager via main.py
        icon_color=WHITE,
    )

    # Refs & state
    nav_index = 0  # 0: Notes, 1: Transcribe, 2: AI
    notes_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
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
                ft.Text("Class:", size=14, color=TEXT_DARK, weight=ft.FontWeight.W_500),
                ft.Container(height=8),
                ft.Row([
                    class_dropdown,
                    add_class_btn,
                ], spacing=8, alignment=ft.MainAxisAlignment.START),
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
    document_picker = ft.FilePicker(
        on_result=lambda e: handle_document_upload(e.files[0] if e.files else None)
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
            ft.Text("📝 Notes", size=18, weight=ft.FontWeight.BOLD, color=PASTEL_PURPLE),
            ft.Container(expand=True),  # Spacer
            ft.Container(document_status, padding=ft.padding.only(right=10)),
            ft.ElevatedButton(
                "Upload Document",
                icon=ft.icons.UPLOAD_FILE,
                style=ft.ButtonStyle(bgcolor=DARK_PURPLE, color=ft.colors.ON_PRIMARY),
                on_click=callbacks.get('upload_document', lambda e: None),
            ),
            ft.ElevatedButton(
                "Clear",
                icon=ft.icons.CLEAR,
                style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE, color=ft.colors.ON_PRIMARY),
                on_click=lambda e: None,  # TODO: was `lambda _: (clear notes and document)` → wire in main.py to call app/pdf_manager.py (import/export/list PDFs)
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

    notes_editor = ft.TextField(
        ref=notes_ref,
        multiline=True,
        min_lines=1,  # Allow natural expansion within fixed container
        max_lines=None,  # No line limit - container height controls size
        expand=True,
        hint_text="Type your lecture notes here...\n\nTips:\n• Use bullet points for key concepts\n• Organize thoughts clearly\n• The AI will analyze this content",
        hint_style=ft.TextStyle(color=ft.colors.OUTLINE),
        border=ft.InputBorder.NONE,  # Remove border to prevent double borders
        content_padding=ft.padding.all(8),  # Minimal padding to fit within container
        text_size=14,
        bgcolor=ft.colors.TRANSPARENT,  # Make background transparent
        width=None,  # Let container control width
        height=None,  # Let container control height
    )

    notes_view = ft.Container(
        ft.Column([
            # Header section - standardized height to match other tabs
            ft.Container(
                toolbar, 
                padding=ft.padding.only(bottom=15),
                height=60,  # Fixed header height matching other tabs
            ),
            # Main content area - fixed height for consistency
            ft.Container(
                notes_editor,
                height=500,  # Fixed height to fit properly within border
                padding=ft.padding.all(8),  # Internal padding between border and textbox
                border=ft.border.all(2, PASTEL_PURPLE),
                border_radius=12,
                bgcolor=WHITE,
            ),
            # Status area - consistent with other tabs
            ft.Container(
                ft.Row([
                    ft.Icon(ft.icons.INFO_OUTLINE, size=16, color=PASTEL_PURPLE),
                    ft.Text("💡 Tip: Use bullet points and clear headings for better AI analysis", 
                           size=12, color=ft.colors.ON_SURFACE, italic=True),
                ], spacing=8),
                padding=ft.padding.all(10),
                height=40,  # Fixed tip area height
                border_radius=8,
                bgcolor=ft.colors.SURFACE_VARIANT,
                margin=ft.margin.only(top=15),
            ),
        ], spacing=0),
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
        ft.Text("🎙️ Transcription", size=18, weight=ft.FontWeight.BOLD, color=PASTEL_PURPLE),
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
        ft.Text("💡 Demo: Will show sample transcription", size=12, italic=True)
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
        on_result=lambda e: handle_audio_upload(e.files[0] if e.files else None)
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
    )
    
    upload_status_ref = ft.Ref[ft.Text]()
    upload_status = ft.Text(
        ref=upload_status_ref,
        value="No file selected",
        size=12,
        color=ft.colors.ON_SURFACE,
    )
    
    upload_btn = ft.ElevatedButton(
        "Upload Audio File",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda e: None,  # TODO: was `lambda _: file_picker.pick_files(allowed_extensions=["mp3", "wav", "m4a", "flac", "ogg"])` → wire in main.py to call app/pdf_manager.py (import/export/list PDFs)
        style=ft.ButtonStyle(
            bgcolor=PASTEL_PURPLE,
            color=ft.colors.ON_PRIMARY,
        )
    )
    
    transcribe_btn = ft.ElevatedButton(
        "Transcribe Audio",
        icon=ft.icons.TRANSCRIBE,
        on_click=lambda e: None,  # TODO: was `transcribe_audio_file` → wire in main.py to call app/transcription.py (start/stop streaming, captions)
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
            transcribe_btn,
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
        # Controls section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.MIC, color=PASTEL_PURPLE, size=20),
                    ft.Text("Live Transcription", size=16, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Text("Record audio in real-time and get live transcription", size=12, color=ft.colors.OUTLINE),
                ft.Container(height=10),
                ft.Container(trans_controls, height=50),
            ]),
            padding=ft.padding.all(16),
            height=130,
        ),
        ft.Container(height=15),
        # Transcription output section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.SUBTITLES, color=PASTEL_PURPLE, size=16),
                    ft.Text("Live Transcription Output:", weight=ft.FontWeight.W_500),
                ], spacing=8),
                ft.Container(height=8),
                ft.Container(
                    trans_live,
                    expand=True,
                    border=ft.border.all(1, PASTEL_PURPLE),
                    border_radius=8,
                    bgcolor=WHITE,
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
                ft.Container(
                    upload_results,
                    expand=True,
                    border=ft.border.all(1, PASTEL_PURPLE),
                    border_radius=8,
                    bgcolor=WHITE,
                ),
            ]),
            padding=ft.padding.all(12),
            expand=True,
        ),
    ], spacing=0)

    # Transcription tabs
    transcription_tabs = ft.Tabs(
        tabs=[
            ft.Tab(text="🎙️ Live Recording", content=live_transcription_tab),
            ft.Tab(text="📁 File Upload", content=audio_upload_tab),
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
            # Main content area - fixed height for consistency
            ft.Container(
                transcription_tabs,
                height=500,  # Fixed height to match other tabs
                border=ft.border.all(2, PASTEL_PURPLE),
                border_radius=12,
                bgcolor=WHITE,
            ),
            # Status area - consistent with other tabs
            ft.Container(
                ft.Row([
                    ft.Icon(ft.icons.INFO_OUTLINE, size=16, color=PASTEL_PURPLE),
                    ft.Text("💡 Tip: Use live recording or upload audio files for transcription", 
                           size=12, color=ft.colors.ON_SURFACE, italic=True),
                ], spacing=8),
                padding=ft.padding.all(10),
                height=40,  # Fixed tip area height
                border_radius=8,
                bgcolor=ft.colors.SURFACE_VARIANT,
                margin=ft.margin.only(top=15),
            ),
        ], spacing=0),
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
            ft.dropdown.Option("Topics", "📝 Key Topics"),
            ft.dropdown.Option("Q&A", "❓ Q&A Format"),
            ft.dropdown.Option("Detailed", "📋 Detailed Summary")
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

    async def do_summarize(_):
        """Generate summary - UI ONLY"""
        # TODO: Wire in main.py to call app/summarizer.py (summaries, Q&A)
        pass

    sum_btn.on_click = callbacks.get('summarize_content', lambda e: None)

    summarizer_tab = ft.Column([
        # Controls section  
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.SUMMARIZE, color=PASTEL_PURPLE, size=20),
                    ft.Text("AI Summarizer", size=16, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Text("Transform your notes into structured summaries", size=12, color=ft.colors.OUTLINE),
                ft.Container(height=10),
                ft.Row([
                    ft.Text("Summary Mode:", weight=ft.FontWeight.W_500),
                    sum_mode,
                    ft.Container(expand=True),
                    sum_btn
                ], alignment=ft.MainAxisAlignment.START, spacing=15),
            ]),
            padding=ft.padding.all(16),
            height=130,
        ),
        ft.Container(height=15),
        # Output section
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.ARTICLE, color=PASTEL_PURPLE, size=16),
                    ft.Text("Summary Output:", weight=ft.FontWeight.W_500),
                ], spacing=8),
                ft.Container(height=8),
                ft.Container(
                    sum_out,
                    expand=True,
                ),
            ]),
            padding=ft.padding.all(12),
            expand=True,
        ),
    ], spacing=0)

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

    ask_btn.on_click = lambda e: None  # TODO: was `do_ask` → wire in main.py to call appropriate manager via main.py

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

    quiz_btn.on_click = lambda e: None  # TODO: was `do_quiz` → wire in main.py to call app/quiz_manager.py (quiz generation)

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

    tabs = ft.Tabs(
        tabs=[
            ft.Tab(text="📝 Summarizer", content=summarizer_tab),
            ft.Tab(text="🤖 Study Buddy", content=study_tab),
            ft.Tab(text="🎯 Quiz Master", content=quiz_tab),
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
                    ft.Text("🤖 AI Assistant", size=18, weight=ft.FontWeight.BOLD, color=PASTEL_PURPLE),
                    ft.Container(expand=True),
                    ft.Text("Powered by AI", size=12, color=ft.colors.ON_SURFACE, italic=True),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.only(bottom=15),
                height=60,  # Fixed header height matching other tabs
            ),
            # Main content area - fixed height for consistency
            ft.Container(
                tabs,
                height=500,  # Fixed height to match other tabs
                border=ft.border.all(2, PASTEL_PURPLE),
                border_radius=12,
                bgcolor=WHITE,
            ),
            # Status area - consistent with other tabs
            ft.Container(
                ft.Row([
                    ft.Icon(ft.icons.INFO_OUTLINE, size=16, color=PASTEL_PURPLE),
                    ft.Text("💡 Tip: Use the tabs above to analyze your notes with AI tools", 
                           size=12, color=ft.colors.ON_SURFACE, italic=True),
                ], spacing=8),
                padding=ft.padding.all(10),
                height=40,  # Fixed tip area height
                border_radius=8,
                bgcolor=ft.colors.SURFACE_VARIANT,
                margin=ft.margin.only(top=15),
            ),
        ], spacing=0),
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
            padding=ft.padding.only(top=0, bottom=12),  # No left/right padding, inherits from parent
            expand=True,
        ),
    ], spacing=0, expand=True)
    
    # Content container with specified structure (wrapped in Column for scrolling)
    content = ft.Container(
        expand=True,
        alignment=ft.alignment.top_left,
        padding=ft.padding.only(left=24, right=24, top=0),  # Specified padding
        content=ft.Column(
            [content_column],
            scroll=ft.ScrollMode.AUTO,  # Enable scrolling if needed
            expand=True,
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

    # Add overlays and components to page
    page.overlay.extend([file_picker, add_class_dialog, document_picker])
    page.add(main_container)


# End of file