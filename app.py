from __future__ import annotations

import traceback
from pathlib import Path

import streamlit as st

from src.caption_builder import build_captions
from src.cover_builder import build_cover_image
from src.utils import (
    CONFIG_DIR,
    ensure_directory,
    load_json,
    save_bytes,
    timestamped_output_dir,
    check_ffmpeg_available,
)
from src.video_builder import build_reel_video


st.set_page_config(page_title="BCサービス リール量産ツール", page_icon="🎬", layout="centered")
st.title("BCサービス Instagramリール量産ツール (MVP)")
st.caption("素材とBGMを入れるだけで、縦動画・表紙・投稿文テンプレをまとめて生成します。")

brand_config = load_json(CONFIG_DIR / "brand_config.json")
content_templates = load_json(CONFIG_DIR / "content_templates.json")
theme_names = list(content_templates["themes"].keys())

ffmpeg_ok, ffmpeg_info = check_ffmpeg_available()
if ffmpeg_ok:
    st.success(f"ffmpeg 検出済み: {ffmpeg_info}")
else:
    st.error(ffmpeg_info)

with st.form("reel_form"):
    st.subheader("1) テーマと文言")
    theme = st.selectbox("テーマを選択", options=theme_names)
    title = st.text_input("任意タイトル", value="")
    subtitle = st.text_input("任意サブテキスト", value="")
    cta = st.text_input("CTA文言", value=brand_config["default_cta"])
    platforms = st.multiselect(
        "投稿先を選択",
        ["Instagram", "YouTube Shorts", "TikTok"],
        default=["Instagram", "YouTube Shorts", "TikTok"],
    )

    st.subheader("2) 素材アップロード")
    bgm_file = st.file_uploader("BGMファイル (mp3)", type=["mp3"])
    media_files = st.file_uploader(
        "写真または動画素材 (3〜8個)",
        type=["jpg", "jpeg", "png", "webp", "mp4", "mov", "avi", "mkv"],
        accept_multiple_files=True,
    )
    character_file = st.file_uploader("左上キャラ画像 (任意, png推奨)", type=["png", "jpg", "jpeg", "webp"])

    st.subheader("3) 入力内容プレビュー")
    st.write(f"選択テーマ: **{theme}**")
    if media_files:
        st.write("素材の並び順 (アップロード順):")
        for idx, media in enumerate(media_files, start=1):
            st.write(f"{idx}. {media.name}")
    else:
        st.info("素材をアップロードするとここに並び順が表示されます。")

    submit = st.form_submit_button("生成する")

if submit:
    if not ffmpeg_ok:
        st.error("ffmpeg が利用できないため生成できません。README の手順で設定してください。")
        st.stop()

    errors: list[str] = []
    if not title.strip():
        errors.append("任意タイトルは必須です。")
    if not bgm_file:
        errors.append("BGMファイル(mp3)を指定してください。")
    if not media_files or len(media_files) < 3 or len(media_files) > 8:
        errors.append("素材は3〜8個の範囲でアップロードしてください。")
    if not platforms:
        errors.append("投稿先を1つ以上選択してください。")

    if errors:
        for err in errors:
            st.error(err)
        st.stop()

    theme_template = content_templates["themes"][theme]
    theme_template = {
        **theme_template,
        "hashtags": content_templates.get("hashtags", []),
    }

    output_dir = timestamped_output_dir()
    work_dir = ensure_directory(output_dir / "_work")
    asset_dir = ensure_directory(output_dir / "assets")

    try:
        bgm_path = save_bytes(asset_dir / f"bgm_{bgm_file.name}", bgm_file.getvalue())

        media_paths: list[Path] = []
        for i, media in enumerate(media_files, start=1):
            suffix = Path(media.name).suffix.lower()
            media_path = save_bytes(asset_dir / f"media_{i:02d}{suffix}", media.getvalue())
            media_paths.append(media_path)

        character_path: Path | None = None
        if character_file:
            char_suffix = Path(character_file.name).suffix.lower()
            character_path = save_bytes(asset_dir / f"character{char_suffix}", character_file.getvalue())

        cover_path = output_dir / "cover.png"
        build_cover_image(
            output_path=cover_path,
            title=title,
            subtitle=subtitle,
            brand_name=brand_config["brand_name"],
        )

        reel_path = output_dir / "reel.mp4"
        bubble_texts = theme_template.get("bubble_texts", [])
        used_cta = cta if cta.strip() else brand_config["default_cta"]
        video_path, duration = build_reel_video(
            media_paths=media_paths,
            bgm_path=bgm_path,
            output_path=reel_path,
            work_dir=work_dir,
            cta_text=used_cta,
            brand_name=brand_config["brand_name"],
            bubble_texts=bubble_texts,
            character_path=character_path,
        )

        caption_files = build_captions(
            theme_template=theme_template,
            brand_config=brand_config,
            title=title,
            subtitle=subtitle,
            cta=used_cta,
        )

        for filename, body in caption_files.items():
            if filename.startswith("platform_"):
                continue
            (output_dir / filename).write_text(body, encoding="utf-8")

        st.success("生成が完了しました。")
        st.write(f"出力先: `{output_dir}`")
        st.write(f"動画尺(目安): {duration:.1f}秒")
        st.write(f"- 動画: `{video_path.name}`")
        st.write(f"- 表紙: `{cover_path.name}`")
        st.write("- 投稿文: `instagram.txt` / `youtube_shorts.txt` / `tiktok.txt`")
        st.info(
            "MVP仕様のため投稿先別に文体を出力していますが、選択プラットフォームに関係なくファイルは全て生成します。"
        )
    except Exception as exc:  # noqa: BLE001
        st.error("生成中にエラーが発生しました。入力ファイル形式や ffmpeg 設定を確認してください。")
        st.code(f"{exc}\n\n{traceback.format_exc()}", language="text")
