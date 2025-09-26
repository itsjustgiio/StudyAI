from __future__ import annotations
import asyncio
import flet as ft


async def stub_summarize(text: str, mode: str) -> str:
    return f"[stub] {mode} summary for {len(text.split())} words."

async def stub_answer(question: str) -> str:
    return f"[stub] Answer to: {question}"

async def stub_make_quiz(source: str, n: int = 5) -> list[tuple[str, str]]:
    return [(f"Question {i+1}?", "Sample answer") for i in range(n)]

async def stub_start_transcription(callback):
    # Pretend to stream a few lines
    import asyncio
    for i in range(3):
        await asyncio.sleep(0.4)
        await callback(f"(stub) live caption line {i+1}")

async def stub_stop_transcription():
    return None


# ----------------------------
# UI entry point
# Exported function: build_ui(page)
# Your main.py should do:  ft.app(build_ui)
# ----------------------------

def build_ui(page: ft.Page):
    page.title = "StudyAI"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 900  # Increased height for larger notes area
    page.window_min_width = 1000
    page.window_min_height = 700  # Increased minimum height
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 0
    
    # Class management system
    current_classes = {"classes": ["General"], "selected": "General"}
    class_data = {"General": {"notes": "", "transcriptions": [], "ai_history": []}}
    
    def save_current_class_data():
        """Save current content to the selected class"""
        current_class = current_classes["selected"]
        if notes_ref.current and hasattr(notes_ref.current, 'value'):
            class_data[current_class]["notes"] = notes_ref.current.value or ""
    
    def load_class_data(class_name):
        """Load data for the selected class"""
        if class_name in class_data:
            # Load notes
            if notes_ref.current and hasattr(notes_ref.current, 'value'):
                notes_ref.current.value = class_data[class_name]["notes"]
                notes_ref.current.update()
            # Clear transcription and AI history for new class (only if they exist and are on page)
            try:
                if trans_live_ref.current and hasattr(trans_live_ref.current, 'controls'):
                    trans_live_ref.current.controls.clear()
                    trans_live_ref.current.update()
            except:
                pass  # Ignore if not on page yet
            try:
                if upload_results_ref.current and hasattr(upload_results_ref.current, 'controls'):
                    upload_results_ref.current.controls.clear()
                    upload_results_ref.current.update()
            except:
                pass  # Ignore if not on page yet
    
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
        """Handle class selection change"""
        save_current_class_data()  # Save current class data
        current_classes["selected"] = e.control.value
        load_class_data(e.control.value)  # Load new class data
        page.snack_bar = ft.SnackBar(ft.Text(f"📚 Switched to class: {e.control.value}"))
        page.snack_bar.open = True
        page.update()
    
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
            ft.TextButton("Cancel", on_click=close_add_class_dialog),
            ft.ElevatedButton("Add Class", on_click=add_new_class, style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    add_class_btn = ft.IconButton(
        icon=ft.icons.ADD,
        tooltip="Add New Class",
        on_click=open_add_class_dialog,
        icon_color=WHITE,
    )

    # Refs & state
    nav_index = 0  # 0: Notes, 1: Transcribe, 2: AI
    notes_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    trans_live_ref: ft.Ref[ft.ListView] = ft.Ref[ft.ListView]()
    sum_output_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()
    sum_mode_ref: ft.Ref[ft.Dropdown] = ft.Ref[ft.Dropdown]()
    ask_input_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    ask_output_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()
    quiz_n_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    quiz_list_ref: ft.Ref[ft.ListView] = ft.Ref[ft.ListView]()
    upload_results_ref: ft.Ref[ft.ListView] = ft.Ref[ft.ListView]()
    document_status_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()



    app_bar = ft.AppBar(
        title=ft.Text("StudyAI", size=24, weight=ft.FontWeight.BOLD),
        center_title=False,
        bgcolor=PASTEL_PURPLE,
        color=WHITE,
        actions=[
            ft.Text("Class:", size=14, color=WHITE),
            class_dropdown,
            add_class_btn,
        ],
    )

    # ---------------- Sidebar (NavigationRail)
    # Create a simple container that will hold the current view
    main_content = ft.Container(expand=True)
    nav_container_ref = ft.Ref[ft.Container]()
    
    # Navigation logic is now handled by nav_button_click functions

    # Create custom navigation buttons instead of NavigationRail
    current_nav = {"selected": 0}
    
    def nav_button_click(index):
        def handler(_):
            current_nav["selected"] = index
            if index == 0:
                main_content.content = ft.Container(notes_view, expand=True, padding=ft.padding.all(10))
            elif index == 1:
                main_content.content = ft.Container(trans_view, expand=True, padding=ft.padding.all(10))
            else:
                main_content.content = ft.Container(ai_view, expand=True, padding=ft.padding.all(10))
            
            # Update button styles
            for i, btn in enumerate(nav_buttons):
                btn.style = ft.ButtonStyle(
                    bgcolor=PASTEL_PURPLE if i == index else ft.colors.SURFACE_VARIANT,
                    color=ft.colors.ON_PRIMARY if i == index else ft.colors.ON_SURFACE,
                )
            page.update()
        return handler
    
    nav_buttons = [
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.NOTE_ALT),
                ft.Text("Notes", weight=ft.FontWeight.W_500)
            ], spacing=8),
            on_click=nav_button_click(0),
            style=ft.ButtonStyle(
                bgcolor=PASTEL_PURPLE,
                color=ft.colors.ON_PRIMARY,
            ),
            width=160,
        ),
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.MIC),
                ft.Text("Transcribe", weight=ft.FontWeight.W_500)
            ], spacing=8),
            on_click=nav_button_click(1),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.SURFACE_VARIANT,
                color=ft.colors.ON_SURFACE,
            ),
            width=160,
        ),
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.SMART_TOY),
                ft.Text("AI Assistant", weight=ft.FontWeight.W_500)
            ], spacing=8),
            on_click=nav_button_click(2),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.SURFACE_VARIANT,
                color=ft.colors.ON_SURFACE,
            ),
            width=160,
        ),
    ]
    
    nav = ft.Column(
        nav_buttons,
        spacing=10,
        alignment=ft.MainAxisAlignment.START,  # Start from top, we'll position with container
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,  # Don't expand, keep compact
    )

    # Document upload functionality
    current_document = {"file": None, "content": ""}
    
    def handle_document_upload(file):
        """Handle PDF/DOC file selection and processing"""
        if file:
            current_document["file"] = file
            document_status_ref.current.value = f"📄 Loaded: {file.name}"
            
            # TODO: Extract text content from PDF/DOC file
            # This is a placeholder - your team will implement actual file parsing
            if file.name.lower().endswith('.pdf'):
                extracted_text = f"[PDF Content from {file.name}]\n\nThis is placeholder text extracted from the PDF file. Your team will implement actual PDF text extraction using libraries like PyPDF2 or pdfplumber.\n\nSample content that would be extracted from the document..."
            elif file.name.lower().endswith(('.doc', '.docx')):
                extracted_text = f"[DOC Content from {file.name}]\n\nThis is placeholder text extracted from the Word document. Your team will implement actual DOC text extraction using libraries like python-docx.\n\nSample content that would be extracted from the document..."
            else:
                extracted_text = f"[Document Content from {file.name}]\n\nUnsupported file type. Please upload PDF or DOC files."
            
            current_document["content"] = extracted_text
            
            # Add extracted content to notes
            current_notes = notes_ref.current.value or ""
            if current_notes:
                notes_ref.current.value = current_notes + "\n\n" + extracted_text
            else:
                notes_ref.current.value = extracted_text
                
            notes_ref.current.update()
            document_status_ref.current.update()
            
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ Document content added to notes: {file.name}"))
            page.snack_bar.open = True
            page.update()
        else:
            current_document["file"] = None
            current_document["content"] = ""
            document_status_ref.current.value = "No document loaded"
            document_status_ref.current.update()

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
                on_click=lambda _: document_picker.pick_files(
                    allowed_extensions=["pdf", "doc", "docx"]
                ),
            ),
            ft.ElevatedButton(
                "Clear",
                icon=ft.icons.CLEAR,
                style=ft.ButtonStyle(bgcolor=PASTEL_PURPLE, color=ft.colors.ON_PRIMARY),
                on_click=lambda _: (
                    setattr(notes_ref.current, "value", ""),
                    setattr(current_document, "file", None),
                    setattr(current_document, "content", ""),
                    setattr(document_status_ref.current, "value", "No document loaded"),
                    document_status_ref.current.update(),
                    page.update()
                ),
            ),
            ft.IconButton(
                ft.icons.CONTENT_COPY,
                tooltip="Copy notes",
                icon_color=PASTEL_PURPLE,
                on_click=lambda _: page.set_clipboard(notes_ref.current.value or ""),
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
        trans_live_ref.current.controls.append(
            ft.Container(
                ft.Text(line, size=14),
                padding=ft.padding.all(8),
                margin=ft.margin.only(bottom=4),
                bgcolor=SOFT_PURPLE,
                border_radius=6,
            )
        )
        trans_live_ref.current.update()

    async def start_trans(_):
        if trans_running["on"]:
            return
        trans_running["on"] = True
        start_btn.disabled = True
        stop_btn.disabled = False
        page.snack_bar = ft.SnackBar(ft.Text("🎙️ Starting transcription (demo mode)"))
        page.snack_bar.open = True
        page.update()
        await stub_start_transcription(handle_transcription_line)

    async def stop_trans(_):
        if not trans_running["on"]:
            return
        trans_running["on"] = False
        await stub_stop_transcription()
        start_btn.disabled = False
        stop_btn.disabled = True
        page.snack_bar = ft.SnackBar(ft.Text("⏹️ Stopped transcription"))
        page.snack_bar.open = True
        page.update()

    # Audio upload handlers
    current_audio_file = {"file": None}
    
    def handle_audio_upload(file):
        """Handle audio file selection"""
        if file:
            current_audio_file["file"] = file
            upload_status_ref.current.value = f"Selected: {file.name}"
            transcribe_btn.disabled = False
        else:
            current_audio_file["file"] = None
            upload_status_ref.current.value = "No file selected"
            transcribe_btn.disabled = True
        upload_status_ref.current.update()
        transcribe_btn.update()
    
    async def transcribe_audio_file(_):
        """Transcribe the uploaded audio file"""
        if not current_audio_file["file"]:
            return
            
        # Clear previous results
        upload_results_ref.current.controls.clear()
        
        # Show processing status
        upload_results_ref.current.controls.append(
            ft.Container(
                ft.Text("🔄 Processing audio file...", size=14, color=PASTEL_PURPLE),
                padding=ft.padding.all(8),
                bgcolor=SOFT_PURPLE,
                border_radius=6,
            )
        )
        upload_results_ref.current.update()
        
        # TODO: Implement actual audio transcription
        model_size = model_size_ref.current.value
        file_name = current_audio_file["file"].name
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Show sample result
        upload_results_ref.current.controls.clear()
        upload_results_ref.current.controls.extend([
            ft.Container(
                ft.Text(f"✅ Transcription complete using {model_size} model", size=14, weight=ft.FontWeight.BOLD),
                padding=ft.padding.all(8),
                bgcolor=SOFT_PURPLE,
                border_radius=6,
            ),
            ft.Container(
                ft.Text(f"File: {file_name}", size=12, italic=True),
                padding=ft.padding.all(8),
            ),
            ft.Container(
                ft.Text("Sample transcription result would appear here. This is a placeholder for the actual transcription that will be implemented by your team's audio processing module.", 
                       size=14),
                padding=ft.padding.all(8),
                bgcolor=WHITE,
                border=ft.border.all(1, PASTEL_PURPLE),
                border_radius=6,
            ),
        ])
        upload_results_ref.current.update()

    trans_header = ft.Row([
        ft.Text("🎙️ Transcription", size=18, weight=ft.FontWeight.BOLD, color=PASTEL_PURPLE),
        ft.Container(expand=True),
        ft.Text("Status: Ready", size=12, color=ft.colors.ON_SURFACE),
    ])

    start_btn = ft.ElevatedButton(
        "Start Recording", 
        icon=ft.icons.MIC, 
        on_click=start_trans,
        style=ft.ButtonStyle(
            bgcolor=PASTEL_PURPLE,
            color=ft.colors.ON_PRIMARY,
        )
    )
    stop_btn = ft.OutlinedButton(
        "Stop Recording", 
        icon=ft.icons.STOP, 
        on_click=stop_trans, 
        disabled=True,
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
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["mp3", "wav", "m4a", "flac", "ogg"]
        ),
        style=ft.ButtonStyle(
            bgcolor=PASTEL_PURPLE,
            color=ft.colors.ON_PRIMARY,
        )
    )
    
    transcribe_btn = ft.ElevatedButton(
        "Transcribe Audio",
        icon=ft.icons.TRANSCRIBE,
        on_click=transcribe_audio_file,
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
                ft.Column([
                    # Live transcription section (top half)
                    ft.Container(
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.MIC, color=PASTEL_PURPLE, size=16),
                                ft.Text("Live Transcription", size=14, weight=ft.FontWeight.BOLD, color=PASTEL_PURPLE),
                            ], spacing=8),
                            ft.Container(height=8),
                            ft.Container(trans_controls, height=50),  # Compact controls
                            ft.Container(height=8),
                            ft.Container(
                                trans_live,
                                expand=True,
                                border=ft.border.all(1, PASTEL_PURPLE),
                                border_radius=8,
                                bgcolor=WHITE,
                            ),
                        ], spacing=0),
                        height=245,  # Increased to split evenly (245 + 5 + 245 = 495, leaving 5px for container padding)
                        padding=ft.padding.all(12),
                        border=ft.border.all(2, PASTEL_PURPLE),
                        border_radius=12,
                        bgcolor=SOFT_PURPLE,
                    ),
                    
                    ft.Container(height=5),  # Minimal spacing between sections
                    
                    # Audio upload section (bottom half)
                    ft.Container(
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.UPLOAD_FILE, color=PASTEL_PURPLE, size=16),
                                ft.Text("Audio File Upload", size=14, weight=ft.FontWeight.BOLD, color=PASTEL_PURPLE),
                            ], spacing=8),
                            ft.Container(height=8),
                            ft.Container(upload_controls, height=80),  # Upload controls
                            ft.Container(height=8),
                            ft.Container(
                                upload_results,
                                expand=True,
                                border=ft.border.all(1, PASTEL_PURPLE),
                                border_radius=8,
                                bgcolor=WHITE,
                            ),
                        ], spacing=0),
                        height=245,  # Same height for perfect split
                        padding=ft.padding.all(12),
                        border=ft.border.all(2, PASTEL_PURPLE),
                        border_radius=12,
                        bgcolor=SOFT_PURPLE,
                    ),
                ], spacing=0),
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
        text = notes_ref.current.value or ""
        document_content = current_document.get("content", "")
        
        # Combine notes and document content
        combined_text = ""
        if text.strip():
            combined_text += text.strip()
        if document_content.strip():
            if combined_text:
                combined_text += "\n\n" + document_content.strip()
            else:
                combined_text = document_content.strip()
        
        if not combined_text.strip():
            page.snack_bar = ft.SnackBar(ft.Text("📝 Please add some notes or upload a document first!"))
            page.snack_bar.open = True
            page.update()
            return
            
        mode = sum_mode_ref.current.value
        sum_btn.disabled = True
        sum_btn.text = "Generating..."
        page.update()
        
        # Enhanced prompt to indicate source
        source_info = ""
        if current_document.get("file"):
            source_info = f" (including content from {current_document['file'].name})"
        
        result = await stub_summarize(combined_text, mode)
        result += source_info
        sum_output_ref.current.value = result
        sum_btn.disabled = False
        sum_btn.text = "Generate Summary"
        page.update()

    sum_btn.on_click = do_summarize

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
        q = ask_input_ref.current.value or ""
        if not q.strip():
            page.snack_bar = ft.SnackBar(ft.Text("❓ Please enter a question first!"))
            page.snack_bar.open = True
            page.update()
            return
            
        ask_btn.disabled = True
        ask_btn.text = "Thinking..."
        page.update()
        
        # Enhanced question with context from notes and documents
        context = ""
        notes_text = notes_ref.current.value or ""
        document_content = current_document.get("content", "")
        
        if notes_text.strip() or document_content.strip():
            context += "\nContext from notes and documents:\n"
            if notes_text.strip():
                context += f"Notes: {notes_text.strip()}\n"
            if document_content.strip():
                doc_name = current_document.get("file", {}).get("name", "uploaded document")
                context += f"Document ({doc_name}): {document_content.strip()}\n"
        
        enhanced_question = q + context
        ans = await stub_answer(enhanced_question)
        
        # Add source information to response
        if current_document.get("file"):
            ans += f"\n\n(Answer generated using context from your notes and {current_document['file'].name})"
        elif notes_text.strip():
            ans += f"\n\n(Answer generated using context from your notes)"
        
        ask_output_ref.current.value = ans
        ask_btn.disabled = False
        ask_btn.text = "Ask AI"
        page.update()

    ask_btn.on_click = do_ask

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
        notes_text = notes_ref.current.value or ""
        document_content = current_document.get("content", "")
        
        # Combine notes and document content
        combined_text = ""
        if notes_text.strip():
            combined_text += notes_text.strip()
        if document_content.strip():
            if combined_text:
                combined_text += "\n\n" + document_content.strip()
            else:
                combined_text = document_content.strip()
        
        if not combined_text.strip():
            page.snack_bar = ft.SnackBar(ft.Text("📝 Please add some notes or upload a document first!"))
            page.snack_bar.open = True
            page.update()
            return
            
        try:
            n = max(1, min(20, int(quiz_n_ref.current.value)))
        except Exception:
            n = 5
        quiz_btn.disabled = True
        quiz_btn.text = "Generating..."
        page.update()
        qa = await stub_make_quiz(combined_text, n)
        quiz_list_ref.current.controls.clear()
        for i, (q, a) in enumerate(qa, 1):
            quiz_list_ref.current.controls.append(
                ft.Container(
                    ft.Column([
                        ft.Container(
                            ft.Text(
                                f"Question {i}", 
                                size=14, 
                                weight=ft.FontWeight.BOLD, 
                                color=WHITE
                            ),
                            padding=ft.padding.all(8),
                            bgcolor=PASTEL_PURPLE,
                            border_radius=6,
                            margin=ft.margin.only(bottom=10),
                        ),
                        ft.Text(q, size=14, weight=ft.FontWeight.W_500, color=ft.colors.BLACK),
                        ft.Container(height=12),
                        ft.Container(
                            ft.Text("Answer:", size=12, weight=ft.FontWeight.BOLD, color=DARK_PURPLE),
                            padding=ft.padding.only(bottom=5),
                        ),
                        ft.Text(a, size=13, color=ft.colors.ON_SURFACE),
                    ], spacing=0),
                    padding=ft.padding.all(18),
                    border=ft.border.all(2, PASTEL_PURPLE),
                    border_radius=12,
                    bgcolor=WHITE,
                    margin=ft.margin.only(bottom=8),
                )
            )
        quiz_btn.disabled = False
        quiz_btn.text = "Generate Quiz"
        quiz_list_ref.current.update()

    quiz_btn.on_click = do_quiz

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

    main_content.content = ft.Container(notes_view, expand=True, padding=ft.padding.all(10))

    # Create navigation container with truly fixed center-left positioning
    nav_container = ft.Container(
        ref=nav_container_ref,
        content=ft.Column([
            ft.Container(expand=True),  # Top spacer - pushes nav to center
            nav,  # Navigation buttons in the center
            ft.Container(expand=True),  # Bottom spacer - keeps nav centered
        ]),
        width=200,
        height=900,  # Fixed height that matches window height
        bgcolor=LIGHT_GRAY,
        padding=ft.padding.all(12),
    )

    layout = ft.Row([
        nav_container,
        ft.VerticalDivider(width=2, color=PASTEL_PURPLE),
        ft.Container(
            main_content,
            expand=True,
            alignment=ft.alignment.top_left,  # Ensure content starts at top
            bgcolor=WHITE,
        ),
    ], expand=True, spacing=0, alignment=ft.MainAxisAlignment.START)

    # Add overlays and components to page
    page.appbar = app_bar
    page.overlay.extend([file_picker, add_class_dialog, document_picker])
    page.add(layout)


# End of file
