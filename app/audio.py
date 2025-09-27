# app/audio.py
import shutil
from pathlib import Path

BASE_DIR = Path("data/classes")

def ensure_class_dir(class_name: str):
    """Ensure the directory structure for a given class exists."""
    class_dir = BASE_DIR / class_name
    (class_dir / "audio").mkdir(parents=True, exist_ok=True)
    (class_dir / "transcripts").mkdir(parents=True, exist_ok=True)
    (class_dir / "summaries").mkdir(parents=True, exist_ok=True)
    return class_dir

def save_audio_file(temp_path: str, filename: str, class_name: str) -> str:
    """Save an uploaded audio file into the correct class folder."""
    class_dir = ensure_class_dir(class_name)

    if not filename.lower().endswith(".mp3"):
        raise ValueError("Only .mp3 files are supported right now.")

    dest_path = class_dir / "audio" / filename
    shutil.copy(temp_path, dest_path)

    return str(dest_path)

def list_audio_files(class_name: str) -> list[str]:
    """List audio files for a given class."""
    class_dir = ensure_class_dir(class_name)
    return [f.name for f in (class_dir / "audio").glob("*.mp3")]

def delete_audio_file(filename: str, class_name: str) -> bool:
    """Delete an audio file from a given class folder."""
    file_path = ensure_class_dir(class_name) / "audio" / filename
    if file_path.exists():
        file_path.unlink()
        return True
    return False
