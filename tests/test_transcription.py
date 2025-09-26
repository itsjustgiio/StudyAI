from app.transcription import Transcriber
import os

SAMPLE_FILE = "data/transcripts/samples/sample.mp3"

def test_transcription_not_empty():
    assert os.path.exists(SAMPLE_FILE), f"Missing file: {SAMPLE_FILE}"
    transcriber = Transcriber("tiny")
    text = transcriber.transcribe_file(SAMPLE_FILE)
    print("\n✅ Transcription result:\n", text)
    assert text.strip() != "", "Transcription is empty!"