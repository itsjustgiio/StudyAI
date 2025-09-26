import warnings
import whisper
from pathlib import Path
import argparse
import os

# Suppress CPU FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

class Transcriber:
    def __init__(self, model_size="tiny"):
        print(f"🔄 Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size, device="cpu")

    def transcribe_file(self, filepath: str) -> str:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        result = self.model.transcribe(str(path), fp16=False)  # fp16=False for CPU
        return result["text"]


if __name__ == "__main__":
    # CLI argumentspython app/transcription.py --model tiny --file data/transcripts/samples/sample.mp3 --save

    parser = argparse.ArgumentParser(description="Whisper Audio Transcriber")
    parser.add_argument(
        "--model",
        type=str,
        default="tiny",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Choose which Whisper model to use (default: tiny)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="data/transcripts/samples/sample.mp3",
        help="Path to the audio file"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the transcription to a .txt file in data/transcripts/outputs/"
    )
    args = parser.parse_args()

    # Run transcription
    transcriber = Transcriber(args.model)
    text = transcriber.transcribe_file(args.file)

    print("\n✅ Transcription result:\n")
    print(text)

    # Optionally save
    if args.save:
        output_dir = Path("data/transcripts/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / (Path(args.file).stem + f"_{args.model}.txt")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"\n💾 Transcription saved to: {output_file}")