from __future__ import annotations

from typing import Any


def _pick(values: list[str], fallback: str) -> str:
    if values:
        return values[0]
    return fallback


def build_captions(
    theme_template: dict[str, Any],
    brand_config: dict[str, Any],
    title: str,
    subtitle: str,
    cta: str,
) -> dict[str, str]:
    brand_name = brand_config["brand_name"]
    line_url = brand_config["line_url"]
    hashtags = " ".join(theme_template.get("hashtags", []))

    ig_intro = _pick(
        theme_template.get("instagram_intro", []),
        "家族が吸う空気を見直したい方へ。",
    )
    yt_intro = _pick(
        theme_template.get("youtube_intro", []),
        "エアコンの風が気になる方に向けた短い紹介です。",
    )
    tiktok_intro = _pick(
        theme_template.get("tiktok_intro", []),
        "空気が気になる方へ。",
    )

    subtitle_line = f"{subtitle}\n" if subtitle else ""

    instagram = (
        f"{ig_intro}\n"
        f"{title}\n"
        f"{subtitle_line}"
        "不安を煽らず、必要な施工を丁寧にご案内します。\n\n"
        f"{cta}\n"
        f"LINE相談はこちら: {line_url}\n"
        f"{hashtags}".strip()
    )

    youtube = (
        f"タイトル: {title}\n\n"
        "説明文:\n"
        f"{yt_intro}\n"
        f"{subtitle if subtitle else '室内の空気環境をやさしく整えるお手伝いをしています。'}\n"
        f"{cta}\n\n"
        "タグ候補:\n"
        "#エアコンクリーニング #沖縄 #家族の空気 #BCサービス"
    )

    tiktok = (
        f"{tiktok_intro}\n"
        f"{title}\n"
        f"{subtitle if subtitle else '毎日使うエアコンの風を見直しませんか。'}\n"
        f"{cta}\n"
        f"LINE相談: {line_url}\n"
        "#沖縄 #エアコンクリーニング #子育て家庭"
    )

    return {
        "instagram.txt": instagram,
        "youtube_shorts.txt": youtube,
        "tiktok.txt": tiktok,
        "platform_notice.txt": f"{brand_name} 投稿テンプレート一式",
    }
