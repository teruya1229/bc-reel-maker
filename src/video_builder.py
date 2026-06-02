from __future__ import annotations

import math
import subprocess
from pathlib import Path
from typing import Any

from src.utils import escape_drawtext, is_image_file


VIDEO_W = 1080
VIDEO_H = 1920
FPS = 30
CTA_SLIDE_DURATION = 3.0
CHAR_VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".avi", ".mkv"}


def _run_ffmpeg(command: list[str]) -> None:
    proc = subprocess.run(command, capture_output=True)
    if proc.returncode != 0:
        stderr_text = (proc.stderr or b"").decode("utf-8", errors="ignore").strip()
        if not stderr_text:
            stderr_text = (proc.stderr or b"").decode("cp932", errors="ignore").strip()
        raise RuntimeError(stderr_text or "ffmpeg の実行に失敗しました。")


def _build_timeline(media_paths: list[Path]) -> list[Path]:
    # 目安24秒になるよう、素材が少ない場合は循環して補完する
    min_segments = 6
    segment_count = max(len(media_paths), min_segments)
    timeline: list[Path] = []
    idx = 0
    while len(timeline) < segment_count:
        timeline.append(media_paths[idx % len(media_paths)])
        idx += 1
    return timeline


def _segment_duration(segment_count: int) -> float:
    return max(3.0, min(5.0, 24.0 / segment_count))


def _video_filter() -> str:
    return (
        "scale='if(gt(a,9/16),-2,1080)':'if(gt(a,9/16),1920,-2)',"
        "crop=1080:1920,setsar=1,fps=30"
    )


def _image_filter(duration: float) -> str:
    frame_count = int(math.ceil(duration * FPS))
    return (
        "scale='if(gt(a,9/16),-2,1080)':'if(gt(a,9/16),1920,-2)',"
        "crop=1080:1920,zoompan="
        f"z='min(zoom+0.0008,1.10)':d={frame_count}:s=1080x1920:fps=30"
    )


def _make_segment(src: Path, dst: Path, duration: float) -> None:
    if is_image_file(src):
        command = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(src),
            "-t",
            f"{duration:.2f}",
            "-vf",
            _image_filter(duration),
            "-pix_fmt",
            "yuv420p",
            str(dst),
        ]
    else:
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-t",
            f"{duration:.2f}",
            "-vf",
            _video_filter(),
            "-an",
            "-pix_fmt",
            "yuv420p",
            str(dst),
        ]
    _run_ffmpeg(command)


def _resolve_cta_lines(cta: str) -> tuple[str, str]:
    cleaned = (cta or "").strip()
    default_cta = "気になる方はLINEで無料相談"
    if not cleaned:
        cleaned = default_cta
    if "\n" in cleaned:
        parts = [line.strip() for line in cleaned.splitlines() if line.strip()]
        if len(parts) >= 2:
            return parts[0], parts[1]
    if cleaned == default_cta:
        return "気になる方は", "LINEで無料相談"
    return cleaned, ""


def _make_cta_slide(path: Path, cta: str, brand_name: str, duration: float = CTA_SLIDE_DURATION) -> None:
    main_1, main_2 = _resolve_cta_lines(cta)
    text_main_1 = escape_drawtext(main_1)
    text_main_2 = escape_drawtext(main_2)
    text_brand = escape_drawtext(brand_name)
    text_sub = escape_drawtext("家族が吸う空気を見直すきっかけに")
    fontfile = "C\\:/Windows/Fonts/meiryo.ttc"
    vf = (
        "color=c=#F6F2EA:s=1080x1920:d={dur}[bg];"
        "[bg]drawbox=x=iw*0.24:y=ih*0.47:w=iw*0.52:h=5:color=#F5D66C@0.95:t=fill,"
        "drawtext=fontfile='{font}':text='{main1}':fontcolor=#4A4A4A:fontsize=66:"
        "x=(w-text_w)/2:y=(h-text_h)/2-95:shadowx=2:shadowy=2:shadowcolor=black@0.20,"
        "drawtext=fontfile='{font}':text='{main2}':fontcolor=#4A4A4A:fontsize=70:"
        "x=(w-text_w)/2:y=(h-text_h)/2-10:shadowx=2:shadowy=2:shadowcolor=black@0.20,"
        "drawtext=fontfile='{font}':text='{brand}':fontcolor=white:fontsize=42:"
        "x=(w-text_w)/2:y=(h-text_h)/2+90:shadowx=2:shadowy=2:shadowcolor=black@0.35,"
        "drawtext=fontfile='{font}':text='{sub}':fontcolor=#6B6B6B:fontsize=36:"
        "x=(w-text_w)/2:y=h*0.84"
    ).format(
        dur=duration,
        font=fontfile,
        main1=text_main_1,
        main2=text_main_2,
        brand=text_brand,
        sub=text_sub,
    )

    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            vf,
            "-t",
            f"{duration:.2f}",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ]
    )


def _concat_videos(video_paths: list[Path], output_path: Path, work_dir: Path) -> None:
    concat_path = work_dir / "concat.txt"
    concat_lines = [f"file '{video.as_posix()}'" for video in video_paths]
    concat_path.write_text("\n".join(concat_lines), encoding="utf-8")
    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c",
            "copy",
            str(output_path),
        ]
    )


def _overlay_and_mix(
    src_video: Path,
    bgm_path: Path,
    output_path: Path,
    duration: float,
    bubbles: list[str],
    character_path: Path | None,
) -> None:
    fontfile = "C\\:/Windows/Fonts/meiryo.ttc"
    def _compact(text: str) -> str:
        cleaned = (text or "").replace("。", "").replace("、", "").strip()
        if len(cleaned) <= 16:
            return cleaned
        return f"{cleaned[:8]}\n{cleaned[8:16]}"

    bubble1 = escape_drawtext(_compact(bubbles[0])) if bubbles else ""
    bubble2 = escape_drawtext(_compact(bubbles[1])) if len(bubbles) > 1 else ""

    draw_chain = (
        f"[0:v]drawtext=fontfile='{fontfile}':text='{bubble1}':"
        "fontcolor=white:fontsize=56:shadowx=2:shadowy=2:shadowcolor=black@0.35:"
        "x=(w-text_w)/2:y=h*0.70:enable='between(t,1,6)',"
        f"drawbox=x=iw*0.35:y=ih*0.745:w=iw*0.30:h=4:color=#F5D66C@0.95:t=fill:enable='between(t,1,6)',"
        f"drawtext=fontfile='{fontfile}':text='{bubble2}':"
        "fontcolor=white:fontsize=56:shadowx=2:shadowy=2:shadowcolor=black@0.35:"
        "x=(w-text_w)/2:y=h*0.70:enable='between(t,9,14)',"
        "drawbox=x=iw*0.35:y=ih*0.745:w=iw*0.30:h=4:color=#F5D66C@0.95:t=fill:enable='between(t,9,14)'[vt]"
    )

    command: list[str] = ["ffmpeg", "-y", "-i", str(src_video), "-stream_loop", "-1", "-i", str(bgm_path)]

    if character_path:
        char_is_video = character_path.suffix.lower() in CHAR_VIDEO_SUFFIXES
        if char_is_video:
            command.extend(["-stream_loop", "-1", "-i", str(character_path)])
        elif is_image_file(character_path):
            command.extend(["-loop", "1", "-i", str(character_path)])
        else:
            command.extend(["-i", str(character_path)])

        char_visible_end = max(duration - CTA_SLIDE_DURATION, 0.1)
        filter_complex = (
            f"{draw_chain};"
            "[vt]drawbox=x=32:y=72:w=232:h=232:color=white@0.42:t=fill[vtbg];"
            "[2:v]scale=216:-1,setsar=1,fps=30[char];"
            "[vtbg][char]overlay=40:80:enable='between(t,0,{char_end})'[vout];"
            "[1:a]atrim=0:{dur},afade=t=in:st=0:d=0.8,afade=t=out:st={fade_start}:d=1[aout]"
        ).format(
            dur=f"{duration:.2f}",
            char_end=f"{char_visible_end:.2f}",
            fade_start=max(duration - 1.2, 0.1),
        )
    else:
        filter_complex = (
            f"{draw_chain};"
            "[vt]copy[vout];"
            "[1:a]atrim=0:{dur},afade=t=in:st=0:d=0.8,afade=t=out:st={fade_start}:d=1[aout]"
        ).format(dur=f"{duration:.2f}", fade_start=max(duration - 1.2, 0.1))

    command.extend(
        [
            "-filter_complex",
            filter_complex,
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-pix_fmt",
            "yuv420p",
            "-t",
            f"{duration:.2f}",
            str(output_path),
        ]
    )
    _run_ffmpeg(command)


def build_reel_video(
    media_paths: list[Path],
    bgm_path: Path,
    output_path: Path,
    work_dir: Path,
    cta_text: str,
    brand_name: str,
    bubble_texts: list[str],
    character_path: Path | None = None,
) -> tuple[Path, float]:
    timeline = _build_timeline(media_paths)
    seg_duration = _segment_duration(len(timeline))
    segments: list[Path] = []

    for i, media_path in enumerate(timeline, start=1):
        segment_path = work_dir / f"segment_{i:02d}.mp4"
        _make_segment(media_path, segment_path, seg_duration)
        segments.append(segment_path)

    cta_path = work_dir / "cta.mp4"
    _make_cta_slide(cta_path, cta_text, brand_name, duration=CTA_SLIDE_DURATION)
    segments.append(cta_path)

    stitched = work_dir / "stitched.mp4"
    _concat_videos(segments, stitched, work_dir)

    total_duration = len(timeline) * seg_duration + CTA_SLIDE_DURATION
    _overlay_and_mix(
        src_video=stitched,
        bgm_path=bgm_path,
        output_path=output_path,
        duration=total_duration,
        bubbles=bubble_texts[:2],
        character_path=character_path,
    )
    return output_path, total_duration
