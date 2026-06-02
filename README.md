# BCサービス Instagramリール量産ツール (MVP)

## このツールの目的
現場で撮影した写真・動画素材とBGMを使って、BCサービス向けのSNS投稿素材を半自動で量産するローカルツールです。  
MVPでは「自由編集」よりも「決まった型に流し込む」運用を優先しています。

## 必要環境
- Python 3.11 以上
- Windows 10/11 (他OSでも動作する可能性あり)
- ffmpeg (ローカルインストール + PATH設定)

## ffmpeg の前提
本ツールは動画生成を `ffmpeg` で行います。  
`ffmpeg` が未導入、または PATH 未設定の場合はアプリ内に日本語エラーを表示します。

## インストール方法
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## 起動方法
```powershell
streamlit run app.py
```

## 入力方法
1. テーマを選択
2. タイトル / サブテキスト / CTA を入力
3. BGM (mp3) をアップロード
4. 素材 (写真・動画) を 3〜8個アップロード
5. 任意で左上キャラ画像をアップロード
6. 投稿先を選択して「生成する」を押す

## 出力先
生成結果は以下に保存されます。
- `output/YYYYMMDD_HHMMSS/`

主な出力:
- `reel.mp4` (1080x1920 縦動画)
- `cover.png` (表紙画像)
- `instagram.txt`
- `youtube_shorts.txt`
- `tiktok.txt`
- `assets/` (入力素材コピー)

## 今回のMVPでできること
- テーマ選択型の投稿素材生成
- 写真/動画混在素材からの縦動画生成
- BGMトリム + 軽いフェード
- 最後にCTAスライドを自動挿入
- 表紙画像の自動生成
- 投稿文テンプレートの自動出力
- ffmpeg未導入時の分かりやすいエラー表示

## 今回のMVPでまだできないこと
- Instagram / YouTube / TikTok への自動投稿
- 素材順のドラッグ&ドロップ並べ替え
- 音声に合わせた自動カット最適化
- 高度なテロップ演出・字幕編集
- 商用デザインテンプレの複数切り替え

## 将来拡張案
- Instagram API投稿
- 音声連動カット
- 自動シーン提案
- キャラアニメ化
- バッチ処理

## 補足
- テンプレート設定は `config/brand_config.json` と `config/content_templates.json` で管理します。
- サンプル素材は `sample_assets/` を利用してください。
