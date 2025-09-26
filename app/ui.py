from __future__ import annotations
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
    page.window_height = 800
    page.window_min_width = 1000
    page.window_min_height = 600
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 0

    # --- Refs & state
    nav_index = 0  # 0: Notes, 1: Transcribe, 2: AI
    notes_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    trans_live_ref: ft.Ref[ft.ListView] = ft.Ref[ft.ListView]()
    sum_output_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()
    sum_mode_ref: ft.Ref[ft.Dropdown] = ft.Ref[ft.Dropdown]()
    ask_input_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    ask_output_ref: ft.Ref[ft.Text] = ft.Ref[ft.Text]()
    quiz_n_ref: ft.Ref[ft.TextField] = ft.Ref[ft.TextField]()
    quiz_list_ref: ft.Ref[ft.ListView] = ft.Ref[ft.ListView]()

    # --- Theme toggle
    def toggle_theme(_):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        page.update()

    theme_switch = ft.IconButton(
        icon=ft.icons.DARK_MODE,
        tooltip="Toggle theme",
        on_click=toggle_theme,
    )

    page.appbar = ft.AppBar(
        title=ft.Text("StudyAI", size=20, weight=ft.FontWeight.BOLD),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[theme_switch],
    )

    # ---------------- Sidebar (NavigationRail)
    # Create a simple container that will hold the current view
    main_content = ft.Container(expand=True)
    
    # Navigation logic is now handled by nav_button_click functions

    # Create custom navigation buttons instead of NavigationRail
    current_nav = {"selected": 0}
    
    def nav_button_click(index):
        def handler(_):
            current_nav["selected"] = index
            if index == 0:
                main_content.content = ft.Container(notes_view, expand=True, padding=ft.padding.all(20))
            elif index == 1:
                main_content.content = ft.Container(trans_view, expand=True, padding=ft.padding.all(20))
            else:
                main_content.content = ft.Container(ai_view, expand=True, padding=ft.padding.all(20))
            # Update button styles
            for i, btn in enumerate(nav_buttons):
                btn.style = ft.ButtonStyle(
                    bgcolor=ft.colors.PRIMARY if i == index else ft.colors.TRANSPARENT,
                    color=ft.colors.ON_PRIMARY if i == index else ft.colors.ON_SURFACE,
                )
            page.update()
        return handler
    
    nav_buttons = [
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.NOTE_ALT),
                ft.Text("Notes")
            ], spacing=8),
            on_click=nav_button_click(0),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.PRIMARY,
                color=ft.colors.ON_PRIMARY,
            ),
            width=160,
        ),
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.MIC),
                ft.Text("Transcribe")
            ], spacing=8),
            on_click=nav_button_click(1),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.TRANSPARENT,
                color=ft.colors.ON_SURFACE,
            ),
            width=160,
        ),
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.SMART_TOY),
                ft.Text("AI Assistant")
            ], spacing=8),
            on_click=nav_button_click(2),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.TRANSPARENT,
                color=ft.colors.ON_SURFACE,
            ),
            width=160,
        ),
    ]
    
    nav = ft.Column(
        nav_buttons,
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,  # Don't expand to fill all available space
    )

    # Notes view
    toolbar = ft.Row(
        controls=[
            ft.Text("📝 Notes", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),  # Spacer
            ft.ElevatedButton(
                "Clear",
                icon=ft.icons.CLEAR,
                on_click=lambda _: (setattr(notes_ref.current, "value", ""), page.update()),
            ),
            ft.IconButton(
                ft.icons.CONTENT_COPY,
                tooltip="Copy notes",
                on_click=lambda _: page.set_clipboard(notes_ref.current.value or ""),
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    notes_editor = ft.TextField(
        ref=notes_ref,
        multiline=True,
        min_lines=25,
        expand=True,
        hint_text="Type your lecture notes here...\n\nTips:\n• Use bullet points for key concepts\n• Organize thoughts clearly\n• The AI will analyze this content",
        hint_style=ft.TextStyle(color=ft.colors.OUTLINE),
        border=ft.InputBorder.OUTLINE,
        content_padding=ft.padding.all(16),
        text_size=14,
    )

    notes_view = ft.Container(
        ft.Column([
            ft.Container(toolbar, padding=ft.padding.only(bottom=10)),
            ft.Container(
                notes_editor, 
                expand=True,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=8,
                padding=ft.padding.all(8),
            ),
        ], expand=True, spacing=0),
        expand=True,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=8,
        padding=ft.padding.all(16),
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    # Transcription view
    trans_running = {"on": False}

    async def handle_transcription_line(line: str):
        trans_live_ref.current.controls.append(
            ft.Container(
                ft.Text(line, size=14),
                padding=ft.padding.all(8),
                margin=ft.margin.only(bottom=4),
                bgcolor=ft.colors.SURFACE_VARIANT,
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

    trans_header = ft.Row([
        ft.Text("🎙️ Live Transcription", size=18, weight=ft.FontWeight.BOLD),
        ft.Container(expand=True),
        ft.Text("Status: Ready", size=12, color=ft.colors.OUTLINE),
    ])

    start_btn = ft.ElevatedButton(
        "Start Recording", 
        icon=ft.icons.MIC, 
        on_click=start_trans,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
        )
    )
    stop_btn = ft.OutlinedButton(
        "Stop Recording", 
        icon=ft.icons.STOP, 
        on_click=stop_trans, 
        disabled=True,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
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

    trans_view = ft.Container(
        ft.Column([
            ft.Container(trans_header, padding=ft.padding.only(bottom=10)),
            ft.Container(trans_controls, padding=ft.padding.only(bottom=15)),
            ft.Container(
                trans_live, 
                expand=True,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=8,
                bgcolor=ft.colors.SURFACE,
            ),
        ], expand=True, spacing=0),
        expand=True,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=8,
        padding=ft.padding.all(16),
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    sum_mode = ft.Dropdown(
        ref=sum_mode_ref,
        width=200,
        value="Topics",
        options=[
            ft.dropdown.Option("Topics", "📝 Key Topics"),
            ft.dropdown.Option("Q&A", "❓ Q&A Format"),
            ft.dropdown.Option("Detailed", "📋 Detailed Summary")
        ],
        border_radius=8,
    )
    sum_btn = ft.ElevatedButton(
        "Generate Summary", 
        icon=ft.icons.SUMMARIZE,
        style=ft.ButtonStyle(bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
    )
    sum_out = ft.Text(
        ref=sum_output_ref, 
        selectable=True,
        size=14,
    )

    async def do_summarize(_):
        text = notes_ref.current.value or ""
        if not text.strip():
            page.snack_bar = ft.SnackBar(ft.Text("📝 Please add some notes first!"))
            page.snack_bar.open = True
            page.update()
            return
        mode = sum_mode_ref.current.value
        sum_btn.disabled = True
        sum_btn.text = "Generating..."
        page.update()
        result = await stub_summarize(text, mode)
        sum_output_ref.current.value = result
        sum_btn.disabled = False
        sum_btn.text = "Generate Summary"
        page.update()

    sum_btn.on_click = do_summarize

    summarizer_tab = ft.Column([
        ft.Container(
            ft.Column([
                ft.Text("📝 AI Summarizer", size=16, weight=ft.FontWeight.BOLD),
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
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            bgcolor=ft.colors.SURFACE,
        ),
        ft.Container(height=15),
        ft.Container(
            ft.Column([
                ft.Text("Summary Output:", weight=ft.FontWeight.W_500),
                ft.Container(height=5),
                sum_out,
            ]),
            padding=ft.padding.all(16),
            expand=True,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            bgcolor=ft.colors.SURFACE_VARIANT,
        ),
    ], expand=True, spacing=0)

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
        style=ft.ButtonStyle(bgcolor=ft.colors.PURPLE, color=ft.colors.WHITE)
    )
    ask_out = ft.Text(
        ref=ask_output_ref, 
        selectable=True,
        size=14,
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
        ans = await stub_answer(q)
        ask_output_ref.current.value = ans
        ask_btn.disabled = False
        ask_btn.text = "Ask AI"
        page.update()

    ask_btn.on_click = do_ask

    study_tab = ft.Column([
        ft.Container(
            ft.Column([
                ft.Text("🤖 Study Buddy", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Ask questions about your notes and get AI-powered answers", size=12, color=ft.colors.OUTLINE),
                ft.Container(height=10),
                ft.Row([ask_in, ask_btn], spacing=10),
            ]),
            padding=ft.padding.all(16),
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            bgcolor=ft.colors.SURFACE,
        ),
        ft.Container(height=15),
        ft.Container(
            ft.Column([
                ft.Text("AI Response:", weight=ft.FontWeight.W_500),
                ft.Container(height=5),
                ask_out,
            ]),
            padding=ft.padding.all(16),
            expand=True,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            bgcolor=ft.colors.SURFACE_VARIANT,
        ),
    ], expand=True, spacing=0)

    # Quiz Master tab
    quiz_n = ft.TextField(
        ref=quiz_n_ref, 
        width=120, 
        value="5", 
        label="Questions",
        border_radius=8,
        text_align=ft.TextAlign.CENTER,
    )
    quiz_btn = ft.ElevatedButton(
        "Generate Quiz", 
        icon=ft.icons.QUIZ,
        style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE, color=ft.colors.WHITE)
    )
    quiz_list = ft.ListView(
        ref=quiz_list_ref, 
        expand=True, 
        spacing=12, 
        padding=ft.padding.all(12)
    )

    async def do_quiz(_):
        notes_text = notes_ref.current.value or ""
        if not notes_text.strip():
            page.snack_bar = ft.SnackBar(ft.Text("📝 Please add some notes first!"))
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
        qa = await stub_make_quiz(notes_text, n)
        quiz_list_ref.current.controls.clear()
        for i, (q, a) in enumerate(qa, 1):
            quiz_list_ref.current.controls.append(
                ft.Container(
                    ft.Column([
                        ft.Text(
                            f"Question {i}", 
                            size=12, 
                            weight=ft.FontWeight.BOLD, 
                            color=ft.colors.PRIMARY
                        ),
                        ft.Container(height=5),
                        ft.Text(q, size=14, weight=ft.FontWeight.W_500),
                        ft.Container(height=8),
                        ft.Text("Answer:", size=12, color=ft.colors.OUTLINE),
                        ft.Text(a, size=13),
                    ], spacing=0),
                    padding=ft.padding.all(16),
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=8,
                    bgcolor=ft.colors.SURFACE,
                )
            )
        quiz_btn.disabled = False
        quiz_btn.text = "Generate Quiz"
        quiz_list_ref.current.update()

    quiz_btn.on_click = do_quiz

    quiz_tab = ft.Column([
        ft.Container(
            ft.Column([
                ft.Text("🎯 Quiz Master", size=16, weight=ft.FontWeight.BOLD),
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
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            bgcolor=ft.colors.SURFACE,
        ),
        ft.Container(height=15),
        ft.Container(
            quiz_list,
            expand=True,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            bgcolor=ft.colors.SURFACE_VARIANT,
        ),
    ], expand=True, spacing=0)

    tabs = ft.Tabs(
        tabs=[
            ft.Tab(text="📝 Summarizer", content=summarizer_tab),
            ft.Tab(text="🤖 Study Buddy", content=study_tab),
            ft.Tab(text="🎯 Quiz Master", content=quiz_tab),
        ],
        selected_index=0,
        height=400,  
    )

    ai_view = ft.Container(
        ft.Column([
            ft.Container(
                ft.Text("🤖 AI Assistant", size=18, weight=ft.FontWeight.BOLD),
                padding=ft.padding.only(bottom=15)
            ),
            tabs
        ], spacing=0),
        expand=True,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=8,
        padding=ft.padding.all(16),
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    main_content.content = ft.Container(notes_view, expand=True, padding=ft.padding.all(20))

    layout = ft.Row([
        ft.Container(
            nav,
            width=200,
            height=page.window_height - 100 if page.window_height else 700,  # Fixed height
            bgcolor=ft.colors.SURFACE_VARIANT, 
            padding=ft.padding.all(12),
            alignment=ft.alignment.top_left,  
        ),
        ft.VerticalDivider(width=1, color=ft.colors.OUTLINE),
        ft.Container(
            main_content,
            expand=True,
            alignment=ft.alignment.top_left,  
        ),
    ], expand=True, spacing=0, alignment=ft.MainAxisAlignment.START)

    page.add(layout)


# End of file
