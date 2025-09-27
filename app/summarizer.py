from pathlib import Path
from datetime import datetime
import json
from integrations import gemini_api
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    ListFlowable, ListItem, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


# Strict summarizer template with "mark unsure" rule
_TEMPLATE = """You are a structured academic summarizer.
Your job is ONLY to extract and organize information. No fluff, no style.

STRICT RULES:
- Use plain text only. NO Markdown, no bold, no special symbols.
- TL;DR must be ONE sentence, max 20 words.
- Evidence must have no more than 8 bullet points.
- If a name/date is unclear or uncertain, write it as [unclear] instead of guessing.
- Remove filler: jokes, branding, rhetorical phrases, repeated words.
- Glossary only if a key term is explicitly defined in the source; skip otherwise.
- Keep sentences short and factual.

OUTPUT FORMAT (always use this structure, nothing else):
Title: <short descriptive title>
TL;DR: <1 sentence, max 20 words>
Discussion:
- <bullet fact 1>
- <bullet fact 2>
- ...
Implications:
- <bullet implication 1>
- <bullet implication 2>
Advice/Actions:
- <bullet action 1>
- <bullet action 2>
Glossary:
- <term — short definition> (only if clearly defined; otherwise omit section)

SOURCE MATERIAL:
\"\"\"{text}\"\"\""""


def summarize_text(text: str) -> str:
    """Summarize text using strict academic rules."""
    prompt = _TEMPLATE.format(text=text)
    return gemini_api.generate_text(
        prompt,
        generation_config={
            "temperature": 0.25,
            "top_p": 0.9,
            "max_output_tokens": 900,
        },
    ).strip()


def save_summary_txt(summary: str, output_path: Path) -> None:
    """Save the summary into a plain .txt file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")


def _load_class_metadata(class_name: str) -> dict | None:
    """Load metadata for a given class from class_data.json or data/class_data.json."""
    if not class_name:
        return None

    candidates = [Path("class_data.json"), Path("data/class_data.json")]
    for p in candidates:
        try:
            if not p.exists():
                continue
            data = json.loads(p.read_text(encoding="utf-8"))
            meta = None

            if isinstance(data, dict):
                if "classes" in data and isinstance(data["classes"], dict):
                    meta = data["classes"].get(class_name)
                if meta is None:  # fallback
                    meta = data.get(class_name)

            if isinstance(meta, dict):
                out = {
                    "course_name": meta.get("course_name") or class_name,
                    "class_code": meta.get("class_code") or class_name,
                    "lecture_title": meta.get("lecture_title", ""),
                    "date": meta.get("date") or datetime.now().strftime("%m/%d/%y"),
                }
                return out
        except Exception as e:
            print(f"⚠️ Error reading {p}: {e}")

    return {
        "course_name": class_name,
        "class_code": class_name,
        "lecture_title": "",
        "date": datetime.now().strftime("%m/%d/%y"),
    }


def save_summary_pdf(summary: str, output_path: Path, metadata: dict | None = None) -> None:
    """Save the summary text into a styled PDF."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"],
                                 fontSize=20, spaceAfter=4, alignment=1)
    header_style = ParagraphStyle("HeaderStyle", parent=styles["Heading2"],
                                  fontSize=14, spaceBefore=12, spaceAfter=6)
    body_style = styles["Normal"]

    # Parse summary
    lines = summary.splitlines()
    bullets = []
    tldr_line = None
    title_text = None

    for line in lines:
        if not line.strip():
            continue
        if line.startswith("Title:"):
            title_text = line.replace("Title:", "").strip()
        elif line.startswith("TL;DR:"):
            tldr_line = line.replace("TL;DR:", "").strip()

    # Title
    if title_text:
        story.append(Paragraph(title_text, title_style))

    # Course left / Date right
    course = metadata.get("course_name", "") if metadata else ""
    date_str = metadata.get("date", datetime.now().strftime("%m/%d/%y")) if metadata else datetime.now().strftime("%m/%d/%y")

    header_data = [[f"Course: {course}", date_str]]
    header_table = Table(header_data, colWidths=[3.5 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    #story.append(Spacer(1, 0.15 * inch))

    # Body
    bullets = []
    for line in lines:
        if not line.strip() or line.startswith("Title:") or line.startswith("TL;DR:"):
            continue
        if line.endswith(":") and not line.startswith("-"):
            if bullets:
                story.append(ListFlowable([ListItem(Paragraph(b[2:].strip(), body_style)) for b in bullets], bulletType='bullet'))
                story.append(Spacer(1, 0.15 * inch))
                bullets = []
            story.append(Paragraph(line.strip(), header_style))
        elif line.startswith("-"):
            bullets.append(line)
        else:
            story.append(Paragraph(line.strip(), body_style))

    if bullets:
        story.append(ListFlowable([ListItem(Paragraph(b[2:].strip(), body_style)) for b in bullets], bulletType='bullet'))

    if tldr_line:
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("Conclusion / TL;DR", header_style))
        story.append(Paragraph(tldr_line, body_style))

    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.drawString(40, 20, "Generated by LectureAI")
        canvas.drawRightString(550, 20, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)


def summarize_file(input_txt: Path, output_txt: Path, class_name: str = "") -> None:
    """
    Summarize transcript → save .txt + .pdf
    Filenames are metadata-driven: <Course>_<MM-DD-YY>
    """
    if not input_txt.exists():
        raise FileNotFoundError(f"Transcript not found: {input_txt}")

    raw_text = input_txt.read_text(encoding="utf-8")
    summary = summarize_text(raw_text)

    # Load metadata
    if class_name:
        metadata = _load_class_metadata(class_name)
    else:
        try:
            data = json.loads(Path("class_data.json").read_text(encoding="utf-8"))
            selected = data.get("current_classes", {}).get("selected")
            metadata = _load_class_metadata(selected)
        except Exception:
            metadata = {"course_name": "General", "date": datetime.now().strftime("%m/%d/%y")}

    # Build filename from metadata
    course = metadata.get("course_name", "General").replace(" ", "_")
    date_str = datetime.now().strftime("%m-%d-%y")
    base_dir = Path(f"data/classes/{course}/summaries")
    base_dir.mkdir(parents=True, exist_ok=True)

    txt_filename = f"{course}_{date_str}.txt"
    pdf_filename = f"{course}_{date_str}.pdf"

    save_summary_txt(summary, base_dir / txt_filename)
    save_summary_pdf(summary, base_dir / pdf_filename, metadata)

    print(f"📝 Summary (text) generated: {base_dir/txt_filename}")
    print(f"📄 Summary (PDF) generated: {base_dir/pdf_filename}")
