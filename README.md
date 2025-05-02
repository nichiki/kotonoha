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
  - JSON形式（詳細な情報を含む）

- **使いやすい設定システム**
  - CLI引数
  - 環境変数（.env）
  - 設定ファイル（config.toml）
  - 優先順位：CLI引数 > .env > config.toml > デフォルト

## 📚 モデルの種類と特徴

Kotoba-Whisperには複数のバージョンが用意されており、用途に応じて選択できます：

### モデルバージョンの違い

- **v2.0**: 基本的な文字起こしモデル
  - [Transformers版](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.0)
  - [faster-whisper版](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.0-faster)
  - [whisper.cpp版（GGML）](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.0-ggml)

- **v2.1**: [句読点付与機能付きモデル](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.1)
  - 文字起こし結果に自動で句読点を追加
  - Transformersバックエンドのみ対応

- **v2.2**: [話者分離機能付きモデル](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.2)
  - 話者の自動分離機能を搭載
  - 句読点付与機能も内包（※chunk単位での句読点付与は未対応）
  - Transformersバックエンドのみ対応

### 話者分離機能の利用について（v2.2）

v2.2の話者分離機能を使用するには、以下の追加設定が必要です：

1. 必要なモデル
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)

2. 設定手順
   1. HuggingFaceで上記モデルの利用規約に同意
   2. HuggingFace APIトークンを取得（[トークン作成ページ](https://huggingface.co/settings/tokens)）
   3. プロジェクトの`.env.example`ファイルを`.env`にコピー
   4. `.env`ファイル内の`HF_TOKEN=YOUR_HF_TOKEN_HERE`を実際のトークンに書き換え

### パフォーマンスと選択ガイド

- **Mac環境**
  - whisper.cpp版（GGML）が最も高速
  - Apple Silicon搭載機では特に効果的

- **NVIDIA GPU搭載環境**
  - faster-whisper版が高いパフォーマンスを発揮
  - 必要に応じてv2.1やv2.2の高度な機能を使用可能
  - ※Windows環境での動作検証中

### 推奨環境

- **CPU環境**: whisper.cpp版を推奨
  - メモリ使用量が少なく、CPU最適化された実装
  - 特にMac環境では高速

- **GPU環境**: faster-whisper版を推奨
  - NVIDIA GPUでの高速な推論が可能
  - CUDA 11.8以上を推奨

### トラブルシューティング

- モデルのダウンロードに失敗する場合
  - HuggingFaceのトークンが正しく設定されているか確認
  - インターネット接続を確認
  - プロキシ環境の場合は適切な設定が必要

- 話者分離が動作しない場合
  - 必要なモデルの利用規約への同意確認
  - `.env`ファイルの設定確認
  - 音声ファイルの品質確認（極端に短い、ノイズが多いなど）

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
[general]
model_path = "models/ggml-kotoba-whisper-v2.0.bin"
language = "ja"
output_format = "srt"  # srt, txt, json
backend = "whisper.cpp"  # whisper.cpp, transformers

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

### 設定システムの詳細

設定は3層構造になっており、より柔軟な運用が可能です：

1. **CLI引数**: 最も優先度が高く、一時的な設定変更に
2. **環境変数**（.env）: API keyなどの機密情報の管理に
3. **設定ファイル**（config.toml）: プロジェクト固有の設定に

`config.toml`の設定例：

```toml
[general]
model_path = "models/ggml-kotoba-whisper-v2.0.bin"
language = "ja"
output_format = "srt"  # srt, txt, json
backend = "whisper.cpp"  # whisper.cpp, transformers

[vad]
threshold = 0.30
min_speech_duration_ms = 100
min_silence_duration_ms = 300
speech_pad_ms = 50
```

### エラー対処とログ

- エラーメッセージは日本語で表示
- 詳細なログ出力により問題の特定が容易
- 処理の進捗状況をリアルタイムで表示
