from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1080
HEIGHT = 1920


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                Path("C:/Windows/Fonts/meiryob.ttc"),
                Path("C:/Windows/Fonts/msgothic.ttc"),
            ]
        )
    else:
        candidates.extend(
            [
                Path("C:/Windows/Fonts/meiryo.ttc"),
                Path("C:/Windows/Fonts/msgothic.ttc"),
            ]
        )

    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = list(text)
    lines: list[str] = []
    current = ""
    for char in words:
        test = current + char
        width = draw.textbbox((0, 0), test, font=font)[2]
        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def build_cover_image(
    output_path: Path,
    title: str,
    subtitle: str,
    brand_name: str,
) -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#FFFFFF")
    draw = ImageDraw.Draw(image)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(255 - 9 * ratio)
        g = int(255 - 13 * ratio)
        b = int(255 - 21 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    title_font = _load_font(84, bold=True)
    subtitle_font = _load_font(50, bold=False)
    small_font = _load_font(36, bold=False)

    title_lines = _wrap_text(draw, title, title_font, WIDTH - 180)
    subtitle_lines = _wrap_text(draw, subtitle, subtitle_font, WIDTH - 220) if subtitle else []

    total_h = len(title_lines) * 100 + len(subtitle_lines) * 68
    start_y = max(300, (HEIGHT - total_h) // 2 - 140)

    y = start_y
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        x = (WIDTH - tw) // 2
        draw.rectangle([(x - 16, y + 88), (x + tw + 16, y + 92)], fill="#F5D66C")
        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0, 80))
        draw.text((x, y), line, font=title_font, fill="#FFFFFF")
        y += 100

    for line in subtitle_lines:
        bbox = draw.textbbox((0, 0), line, font=subtitle_font)
        tw = bbox[2] - bbox[0]
        x = (WIDTH - tw) // 2
        draw.text((x + 1, y + 1), line, font=subtitle_font, fill=(0, 0, 0, 65))
        draw.text((x, y), line, font=subtitle_font, fill="#FFFFFF")
        y += 68

    draw.text((70, HEIGHT - 120), brand_name, font=small_font, fill="#FFFFFF")
    draw.text((70, HEIGHT - 72), "LINEで無料相談", font=small_font, fill="#FFFFFF")

    image.save(output_path)
    return output_path
