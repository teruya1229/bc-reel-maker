from __future__ import annotations

from typing import Any


def _pick(values: list[str], fallback: str) -> str:
    if values:
        return values[0]
    return fallback


def _theme_hashtags(theme_name: str) -> list[str]:
    base = [
        "#エアコンクリーニング",
        "#完全分解クリーニング",
        "#エアコン完全分解",
        "#沖縄",
        "#沖縄南部",
        "#南城市",
        "#子育て家庭",
        "#家族が吸う空気",
        "#エアコンの風が気になる",
        "#BCサービス",
    ]
    per_theme: dict[str, list[str]] = {
        "通常分解では落ちない汚れ編": ["#エアコンの汚れ", "#カビ対策"],
        "梅雨のニオイ編": ["#梅雨対策", "#ニオイ対策"],
        "赤ちゃんが吸う空気編": ["#赤ちゃんのいる暮らし", "#室内空気"],
        "料金補足案内編": ["#事前見積もり", "#安心価格"],
    }
    extras = per_theme.get(theme_name, [])
    tags = base[:-2] + extras + base[-2:]
    # 重複を削除しつつ最大12個に調整
    deduped = list(dict.fromkeys(tags))
    return deduped[:12]


def build_captions(
    theme_template: dict[str, Any],
    brand_config: dict[str, Any],
    title: str,
    subtitle: str,
    cta: str,
    theme_name: str = "",
) -> dict[str, str]:
    brand_name = brand_config["brand_name"]
    line_url = brand_config["line_url"]
    hashtags = "\n".join(_theme_hashtags(theme_name))

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

    instagram_cta = "気になる方は、LINEでお気軽にご相談ください。"
    youtube_cta = "気になる方はLINEで無料相談できます。"
    tiktok_cta = "気になる方はLINEで相談OKです。"

    instagram = (
        f"{ig_intro}\n\n"
        f"今回の動画は、\n{title}\n"
        f"{subtitle_line}"
        "通常分解だけでは見えにくい内部の状態を、短く分かりやすくまとめています。\n\n"
        "不安を煽るのではなく、必要な施工を丁寧にご案内しています。\n\n"
        f"{cta}\n"
        f"{instagram_cta}\n\n"
        f"LINE相談はこちら\n{line_url}\n\n"
        f"{hashtags}".strip()
    )

    youtube = (
        f"タイトル: {title}\n\n"
        "説明文:\n"
        f"{yt_intro}\n"
        f"{subtitle if subtitle else '家族が吸う空気を見直すきっかけに。'}\n"
        "通常分解との違いが分かるように、内部の状態を短く紹介しています。\n"
        f"{cta}\n"
        f"{youtube_cta}\n\n"
        "タグ候補:\n"
        f"{' '.join(_theme_hashtags(theme_name)[:8])}"
    )

    tiktok = (
        f"{tiktok_intro}\n"
        f"{title}\n"
        f"{subtitle if subtitle else '毎日使うエアコンの風を見直すきっかけに。'}\n"
        "内部の汚れが気になる方へ\n"
        "必要な施工を丁寧にご案内します\n"
        f"{cta}\n"
        f"{tiktok_cta}\n"
        f"LINE相談: {line_url}\n"
        f"{' '.join(_theme_hashtags(theme_name)[:6])}"
    )

    return {
        "instagram.txt": instagram,
        "youtube_shorts.txt": youtube,
        "tiktok.txt": tiktok,
        "platform_notice.txt": f"{brand_name} 投稿テンプレート一式",
    }
