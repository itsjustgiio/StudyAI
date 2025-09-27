from pathlib import Path
from app import summarizer


def test_summarizer():
    # Input transcript path
    input_txt = Path("data/classes/General/transcripts/sample.mp3.txt")

    # Load metadata directly (so test is in sync with summarizer logic)
    metadata = summarizer._load_class_metadata("General")

    course = metadata.get("course_name", "General").replace(" ", "_")
    date_str = metadata.get("date") or "unknown-date"

    summary_dir = Path(f"data/classes/{course}/summaries")
    expected_txt = summary_dir / f"{course}_{date_str.replace('/', '-')}.txt"
    expected_pdf = summary_dir / f"{course}_{date_str.replace('/', '-')}.pdf"

    # Run summarization
    summarizer.summarize_file(input_txt, None, class_name=course)

    # Verify outputs exist
    assert expected_txt.exists(), f"Summary text file was not generated at {expected_txt}"
    assert expected_pdf.exists(), f"Summary PDF file was not generated at {expected_pdf}"
