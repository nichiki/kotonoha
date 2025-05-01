# 🎯 Okosu

Okosuは、ローカル環境で動作する柔軟かつ高速な音声文字起こしツールです。複数のWhisperベースのバックエンド（whisper.cpp, Transformers, faster-whisper）に対応し、環境に応じて最適なパフォーマンスを提供します。

## ✨ 特徴

- **マルチバックエンド対応**
  - whisper.cpp: 高速な推論が可能なC++実装
  - Transformers: HuggingFace Transformersライブラリベースの実装（v2.0-2.2対応）
  - faster-whisper: 高速な推論と軽量化を両立した実装

- **高度な音声処理**
  - Silero VADによる発話区間検出
  - 短い無音区間の自動結合
  - 16kHz mono形式への自動変換

- **柔軟な出力形式**
  - SRT形式（字幕ファイル）
  - プレーンテキスト

- **使いやすい設定システム**
  - CLI引数
  - 環境変数（.env）
  - 設定ファイル（config.toml）

## 🚀 クイックスタート

### インストール

```bash
# uv（推奨）
uv venv
source .venv/bin/activate  # Linux/macOS
# または
.venv\Scripts\activate  # Windows

uv pip install -e .

# または pip
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# または
.venv\Scripts\activate  # Windows

pip install .
```

### 基本的な使い方

```bash
# 基本的な文字起こし（SRT形式で出力）
okosu transcribe input.mp3

# 出力フォーマットの指定
okosu transcribe input.mp3 -f txt  # テキスト形式
okosu transcribe input.mp3 -f srt  # SRT形式

# バージョン確認
okosu version
```

## ⚙️ 設定

`config.toml`を使用して詳細な設定が可能です：

```toml
[model]
name = "kotoba-whisper-v2.2"  # 使用するモデル名

[general]
output_format = "srt"  # srt, txt

[vad]
threshold = 0.30
min_speech_duration_ms = 100
min_silence_duration_ms = 300
speech_pad_ms = 50
```

## 🛠 開発環境

- Python 3.12+
- 依存パッケージ管理: pip または uv
- テスト: pytest（予定）
- CI/CD: GitHub Actions（予定）

## 📦 主な依存パッケージ

- typer: CLIインターフェース
- rich: ターミナル出力の装飾
- transformers: Whisperモデルの実行
- pywhispercpp: whisper.cpp Python バインディング
- faster-whisper: 高速Whisper実装
- silero-vad: 音声区間検出
- pydub: 音声ファイル処理

## 🗺 ロードマップ

- [x] TranscriptionSegmentクラスの導入
- [x] faster-whisperバックエンドの追加
- [x] 話者分離機能の実装
- [ ] GUIインターフェース（PySide6）の開発
- [ ] パフォーマンス最適化

## 📝 ライセンス

MITライセンス
