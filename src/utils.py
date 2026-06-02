from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "output"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def timestamped_output_dir() -> Path:
    folder = OUTPUT_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_directory(folder)
    return folder


def save_bytes(path: Path, data: bytes) -> Path:
    ensure_directory(path.parent)
    path.write_bytes(data)
    return path


def check_ffmpeg_available() -> tuple[bool, str]:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        return (
            False,
            "ffmpeg が見つかりません。インストール後、PATH を通してから再実行してください。",
        )

    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True, ffmpeg_path
    except subprocess.CalledProcessError as exc:
        return False, f"ffmpeg の起動に失敗しました: {exc.stderr}"


def is_image_file(path: Path) -> bool:
    return path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}


def is_video_file(path: Path) -> bool:
    return path.suffix.lower() in {".mp4", ".mov", ".m4v", ".avi", ".mkv"}


def escape_drawtext(text: str) -> str:
    escaped = text.replace("\\", "\\\\")
    escaped = escaped.replace(":", r"\:")
    escaped = escaped.replace("'", r"\'")
    escaped = escaped.replace(",", r"\,")
    return escaped
