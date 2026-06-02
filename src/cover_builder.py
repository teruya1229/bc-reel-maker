from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


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


def _shorten_title(title: str) -> str:
    cleaned = (title or "").strip()
    if "\n" in cleaned:
        return cleaned
    predefined = {
        "通常分解では落ちない汚れ": "通常分解では\n落ちない汚れ",
        "完全分解ビフォーアフター": "完全分解で\n見える変化",
        "完全分解でここまで変わる": "完全分解で\nここまで変わる",
        "分解して丁寧に洗浄": "分解して\n丁寧に洗浄",
        "作業工程をわかりやすく紹介": "分解して\n丁寧に洗浄",
        "安心につながる工程の見える化": "作業工程を\n見える化",
    }
    if cleaned in predefined:
        return predefined[cleaned]
    if len(cleaned) <= 14:
        return cleaned
    mid = max(6, min(10, len(cleaned) // 2))
    return f"{cleaned[:mid]}\n{cleaned[mid:]}"


def _make_soft_background(background_image_path: Path | None) -> Image.Image:
    base = Image.new("RGB", (WIDTH, HEIGHT), "#F6F2EA")
    draw = ImageDraw.Draw(base)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(250 - 12 * ratio)
        g = int(246 - 10 * ratio)
        b = int(238 - 8 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    if background_image_path and background_image_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
        try:
            bg = Image.open(background_image_path).convert("RGB")
            scale = max(WIDTH / bg.width, HEIGHT / bg.height)
            rs = bg.resize((int(bg.width * scale), int(bg.height * scale)))
            left = (rs.width - WIDTH) // 2
            top = (rs.height - HEIGHT) // 2
            rs = rs.crop((left, top, left + WIDTH, top + HEIGHT))
            rs = rs.filter(ImageFilter.GaussianBlur(radius=1.2))
            base = Image.blend(rs, base, alpha=0.72)
        except Exception:
            pass
    return base


def build_cover_image(
    output_path: Path,
    title: str,
    subtitle: str,
    brand_name: str,
    background_image_path: Path | None = None,
) -> Path:
    image = _make_soft_background(background_image_path)
    draw = ImageDraw.Draw(image)

    title_font = _load_font(116, bold=True)
    subtitle_font = _load_font(48, bold=False)
    small_font = _load_font(34, bold=False)

    compact_title = _shorten_title(title)
    title_lines = []
    for chunk in compact_title.splitlines():
        title_lines.extend(_wrap_text(draw, chunk, title_font, WIDTH - 160))
    subtitle_lines = _wrap_text(draw, subtitle, subtitle_font, WIDTH - 220) if subtitle else []

    total_h = len(title_lines) * 122 + len(subtitle_lines) * 72
    start_y = max(250, (HEIGHT - total_h) // 2 - 60)

    draw.rounded_rectangle([(90, start_y - 60), (WIDTH - 90, start_y + total_h + 100)], radius=34, fill=(255, 255, 255, 172))
    y = start_y
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        x = (WIDTH - tw) // 2
        draw.rectangle([(x - 12, y + 102), (x + tw + 12, y + 108)], fill="#F5D66C")
        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0, 82))
        draw.text((x, y), line, font=title_font, fill="#383838")
        y += 122

    for line in subtitle_lines:
        bbox = draw.textbbox((0, 0), line, font=subtitle_font)
        tw = bbox[2] - bbox[0]
        x = (WIDTH - tw) // 2
        draw.text((x + 1, y + 1), line, font=subtitle_font, fill=(0, 0, 0, 70))
        draw.text((x, y), line, font=subtitle_font, fill="#4A4A4A")
        y += 72

    draw.text((70, HEIGHT - 130), brand_name, font=small_font, fill="#555555")
    draw.text((70, HEIGHT - 82), "LINEで無料相談", font=small_font, fill="#555555")

    image.save(output_path)
    return output_path
