from pathlib import Path


def is_audio_file(path: Path) -> bool:
return path.suffix.lower() in {".wav", ".mp3", ".flac", ".ogg"}