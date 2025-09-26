"""
StudyAI Landing Page
"""

import flet as ft


def create_landing_page(page: ft.Page, on_get_started):    
    # Color scheme
    PASTEL_PURPLE = "#B19CD9"
    DARK_PURPLE = "#8B7AB8"
    SOFT_PURPLE = "#E6D9F0"
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#F8F6FA"
    TEXT_DARK = "#4A4A4A"
    
    # Get responsive sizing based on window dimensions
    def get_responsive_sizes():
        window_width = page.window_width or 1200
        window_height = page.window_height or 800
        
        # Scale factors based on window size
        scale_factor = min(window_width / 1200, window_height / 800)
        
        return {
            'logo_size': max(80, int(100 * scale_factor)),
            'title_size': max(48, int(72 * scale_factor)),
            'subtitle_size': max(18, int(24 * scale_factor)),
            'tagline_size': max(16, int(20 * scale_factor)),
            'button_text_size': max(16, int(20 * scale_factor)),
            'icon_size': max(18, int(24 * scale_factor)),
            'scroll_text_size': max(12, int(14 * scale_factor)),
            'scroll_icon_size': max(30, int(40 * scale_factor)),
            'tagline_width': max(500, int(700 * scale_factor)),
            'spacing_small': max(8, int(10 * scale_factor)),
            'spacing_medium': max(20, int(25 * scale_factor)),
            'spacing_large': max(32, int(40 * scale_factor)),
            'spacing_xlarge': max(45, int(60 * scale_factor)),
        }
    
    sizes = get_responsive_sizes()
    
    # Full viewport hero section - takes exactly 100vh
    hero_section = ft.Container(
        content=ft.Column([
            # Main hero content - centered in viewport
            ft.Container(
                content=ft.Column([
                    # Logo on top - responsive size
                    ft.Icon(
                        ft.icons.SCHOOL,
                        size=sizes['logo_size'],
                        color=PASTEL_PURPLE,
                    ),
                    
                    ft.Container(height=sizes['spacing_medium']),  # Responsive spacing
                    
                    # Title - responsive size
                    ft.Text(
                        "StudyAI",
                        size=sizes['title_size'],
                        weight=ft.FontWeight.BOLD,
                        color=DARK_PURPLE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    
                    ft.Container(height=sizes['spacing_small']),  # Responsive spacing
                    
                    # Subtitle - responsive size
                    ft.Text(
                        "AI-Powered Study Assistant",
                        size=sizes['subtitle_size'],
                        color=TEXT_DARK,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    
                    ft.Container(height=sizes['spacing_large']),  # Responsive spacing
                    
                    # Tagline - responsive size and width
                    ft.Text(
                        "Transform your learning experience with intelligent note-taking,\\ntranscription, and AI-powered study tools",
                        size=sizes['tagline_size'],
                        color=TEXT_DARK,
                        text_align=ft.TextAlign.CENTER,
                        width=sizes['tagline_width'],
                    ),
                    
                    ft.Container(height=sizes['spacing_large']),  # Responsive spacing
                    
                    # Get Started button - responsive size
                    ft.ElevatedButton(
                        content=ft.Text("Get Started", size=sizes['button_text_size'], weight=ft.FontWeight.BOLD),
                        on_click=on_get_started,
                        style=ft.ButtonStyle(
                            bgcolor=PASTEL_PURPLE,
                            color=WHITE,
                            padding=ft.padding.symmetric(
                                horizontal=max(40, int(50 * min(page.window_width or 1200, page.window_height or 800) / 1000)),
                                vertical=max(15, int(20 * min(page.window_width or 1200, page.window_height or 800) / 1000))
                            ),
                            shape=ft.RoundedRectangleBorder(radius=30),
                        ),
                        height=max(50, int(60 * min(page.window_width or 1200, page.window_height or 800) / 1000)),
                        width=max(200, int(240 * min(page.window_width or 1200, page.window_height or 800) / 1000)),
                    ),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,  # Use container heights for precise spacing
                alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            ),
            
            # Scroll indicator at bottom of viewport
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Scroll down to explore features",
                        size=sizes['scroll_text_size'],
                        color=TEXT_DARK,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=sizes['spacing_small']),
                    # Animated scroll arrow
                    ft.Icon(
                        ft.icons.KEYBOARD_ARROW_DOWN,
                        size=sizes['scroll_icon_size'],
                        color=PASTEL_PURPLE,
                    ),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                spacing=0,
                tight=True,
                ),
                padding=ft.padding.only(bottom=30),
                alignment=ft.alignment.bottom_center,
            ),
        ],
        spacing=0,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=WHITE,
        width=None,  # Full viewport width
        height=page.window_height or 800,  # Full viewport height (100vh equivalent)
        alignment=ft.alignment.center,
    )
    
    # Features section
    features = [
        {
            "icon": ft.icons.NOTE_ALT,
            "title": "Smart Notes",
            "description": "Organize your thoughts with intelligent note-taking tools and class management"
        },
        {
            "icon": ft.icons.MIC,
            "title": "Live Transcription", 
            "description": "Record lectures and convert speech to text automatically with AI transcription"
        },
        {
            "icon": ft.icons.UPLOAD_FILE,
            "title": "Document Processing",
            "description": "Upload PDFs and documents to extract text and integrate with your notes"
        },
        {
            "icon": ft.icons.SMART_TOY,
            "title": "AI Assistant",
            "description": "Get summaries, ask questions, and generate quizzes from your study materials"
        },
        {
            "icon": ft.icons.CLOUD,
            "title": "Google Drive Sync",
            "description": "Seamlessly sync and backup your notes and documents to Google Drive"
        },
        {
            "icon": ft.icons.QUIZ,
            "title": "Interactive Quizzes",
            "description": "Generate practice questions automatically from your notes and documents"
        },
    ]
    
    feature_cards = []
    for i in range(0, len(features), 2):  # Create rows of 2 cards each
        row_cards = []
        for j in range(2):
            if i + j < len(features):
                feature = features[i + j]
                card = ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            feature["icon"],
                            size=40,
                            color=PASTEL_PURPLE,
                        ),
                        ft.Text(
                            feature["title"],
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=DARK_PURPLE,
                        ),
                        ft.Text(
                            feature["description"],
                            size=14,
                            color=TEXT_DARK,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10),
                    bgcolor=SOFT_PURPLE,
                    padding=ft.padding.all(20),
                    border_radius=15,
                    width=280,
                    height=180,
                    border=ft.border.all(2, PASTEL_PURPLE),
                )
                row_cards.append(card)
        
        if row_cards:
            feature_cards.append(
                ft.Row(
                    row_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                )
            )
    
    features_section = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    "🚀 Powerful Features",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_PURPLE,
                    text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(height=30),  # Increased spacing
            ft.Container(
                content=ft.Column(feature_cards, spacing=25),  # Increased spacing between rows
                alignment=ft.alignment.center,
            ),
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=WHITE,
        padding=ft.padding.all(50),  # Increased padding
        border_radius=20,
        margin=ft.margin.symmetric(horizontal=40, vertical=20),  # Centered margins
        alignment=ft.alignment.center,
        expand=True,  # Take full screen height
    )
    
    # How to use section
    steps = [
        {
            "number": "1",
            "title": "Create Your Classes",
            "description": "Add and organize your different subjects and courses"
        },
        {
            "number": "2", 
            "title": "Take Notes & Record",
            "description": "Write notes manually or use live transcription during lectures"
        },
        {
            "number": "3",
            "title": "Upload Documents",
            "description": "Add PDFs, slides, and documents to supplement your notes"
        },
        {
            "number": "4",
            "title": "Get AI Insights",
            "description": "Generate summaries, ask questions, and create practice quizzes"
        },
    ]
    
    step_items = []
    for step in steps:
        step_item = ft.Row([
            # Step number circle
            ft.Container(
                content=ft.Text(
                    step["number"],
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=WHITE,
                ),
                bgcolor=PASTEL_PURPLE,
                width=50,
                height=50,
                border_radius=25,
                alignment=ft.alignment.center,
            ),
            
            # Step content
            ft.Column([
                ft.Text(
                    step["title"],
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_PURPLE,
                ),
                ft.Text(
                    step["description"],
                    size=14,
                    color=TEXT_DARK,
                ),
            ], spacing=5),
        ], spacing=20, alignment=ft.MainAxisAlignment.START)
        
        step_items.append(step_item)
    
    how_to_section = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    "📚 How to Get Started",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_PURPLE,
                    text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(height=30),  # Increased spacing
            
            # Steps container for better centering
            ft.Container(
                content=ft.Column(step_items, spacing=30),  # Increased spacing
                alignment=ft.alignment.center,
                width=600,  # Fixed width for consistent layout
            ),
            
            ft.Container(height=40),  # Increased spacing
            
            # Secondary CTA - perfectly centered
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Text("Start Studying", size=16, weight=ft.FontWeight.BOLD),
                    on_click=on_get_started,
                    style=ft.ButtonStyle(
                        bgcolor=DARK_PURPLE,
                        color=WHITE,
                        padding=ft.padding.symmetric(horizontal=30, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=20),
                    ),
                    height=45,
                    width=180,
                ),
                alignment=ft.alignment.center,
            ),
            
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=LIGHT_GRAY,
        padding=ft.padding.all(50),  # Increased padding
        border_radius=20,
        margin=ft.margin.symmetric(horizontal=40, vertical=20),  # Centered margins
        alignment=ft.alignment.center,
        expand=True,  # Take full screen height
    )
    
    # Footer - perfectly centered
    footer = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Divider(color=PASTEL_PURPLE, height=2),
                width=800,  # Fixed width for consistent divider
                alignment=ft.alignment.center,
            ),
            ft.Container(height=10),
            # Center the footer content on small screens, space between on larger screens
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        "© 2025 StudyAI - Empowering Students with AI",
                        size=12,
                        color=TEXT_DARK,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Row([
                        ft.Icon(ft.icons.FAVORITE, size=12, color=ft.colors.RED),
                        ft.Text("Built with", size=12, color=TEXT_DARK),
                        ft.Text("Flet", size=12, color=PASTEL_PURPLE, weight=ft.FontWeight.BOLD),
                    ], spacing=5),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                width=800,  # Fixed width for consistent layout
                alignment=ft.alignment.center,
            ),
        ], 
        spacing=5, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.padding.all(30),
        alignment=ft.alignment.center,
        expand=True,  # Take full screen height
        bgcolor=WHITE,  # Add background color for consistency
    )
    
    # Main landing page layout - each section takes full screen
    landing_page = ft.Column([
        hero_section,
        features_section,
        how_to_section,
        footer,
    ], spacing=0, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # Update sizes and hero height when window changes
    def on_resize(e):
        nonlocal sizes, hero_section
        sizes = get_responsive_sizes()
        # Update hero section height to match new viewport height
        hero_section.height = page.window_height or 800
        page.update()
    
    page.on_resize = on_resize
    
    return ft.Container(
        content=landing_page,
        bgcolor=LIGHT_GRAY,
        width=None,  # Full viewport width
        height=None,  # Full viewport height
        expand=True,
        alignment=ft.alignment.center,
    )