📝 プロジェクト概要：Okosu

📌 プロジェクト名

Okosu — Whisper系音声モデルを用いた音声文字起こしツール（CLI & GUI両対応予定）

🎯 目的
	•	ローカル環境で動作する、柔軟かつ高速な文字起こしツールを提供すること。
	•	実行環境に応じて適切なバックエンド（whisper.cpp, faster-whisper, Transformersなど）を自動的に選択し、精度・速度・機能のバランスを最適化する。
	•	将来的にはGUI（PySide6想定）も提供し、非技術ユーザーにも使いやすくする。

⸻

🏗 現状の実装状況

✅ 実装済み機能
	•	CLIツール（okosu）の基盤実装
	•	入力ファイルの読み込み、WAV変換（16kHz, mono）
	•	Silero VAD による発話区間抽出＋短区間の結合
	•	whisper.cpp バックエンドによる音声文字起こし（Kotoba v2.0固定）
	•	Transformers バックエンドの実装（v2.0-2.2対応）
	•	出力フォーマット（SRT, TXT, JSON）のインターフェース実装
	•	設定の三層構造（CLI引数 > .env > config.toml）
	•	進捗表示（rich）の実装と最適化

⚙ 開発環境
	•	macOS（ローカル開発）
	•	Python 3.12 + uv による仮想環境管理
	•	CLIは Typer によって構築
	•	whisper.cppは kotoba-whisper-v2.0（ローカルbin）を使用

📦 使用パッケージ
	•	pywhispercpp
	•	silero-vad
	•	transformers
	•	torch
	•	huggingface_hub
	•	python-dotenv
	•	tomllib（Python 3.11+）
	•	typer, pydub, rich

⸻

🧭 今後の方針・設計指針

📋 優先度付きタスク

✅ 実装済み
	•	バックエンド抽象化層の実装
		- BaseWhisperBackendインターフェース定義
		- 既存のwhisper.cpp実装の移行
		- バックエンド動的選択機能
	•	CLIオプション
		- 出力フォーマット選択（srt, txt, json）
		- バックエンド選択（whisper.cpp, transformers）
	•	Transformersバックエンド対応
		- v2.0-2.2のバージョン互換性対応
		- 出力フォーマットの統一化

🔥 高優先度
	•	TranscriptionSegmentクラスの導入
		- @dataclass化による型安全性の確保
		- speaker, confidenceなどの拡張フィールド対応
		- 既存コードの段階的移行
	•	CLIオプションの拡張
		- VAD無効化オプション
		- モデル自動ダウンロード機能
		- 言語指定オプション

🔄 中優先度
	•	Hugging Faceモデル自動DL機能
		- トークン認証対応
		- キャッシュ管理
	•	faster-whisperバックエンドの追加
	•	話者分離機能の基盤実装
	•	パフォーマンス最適化
		- マルチスレッド処理の改善
		- GPU利用の効率化

🌱 低優先度
	•	GUIプロトタイプ（CLI安定後）
	•	テストケースの拡充
	•	国際化対応
		- エラーメッセージ
		- ドキュメント

💡 追加提案

1. エラーハンドリング強化
	•	OkosuError基底クラス
	•	ModelLoadError, TranscriptionError等の具体的例外
	•	エラーメッセージの国際化対応

2. ログ出力の整理
	•	ログレベルの動的制御
	•	ファイルログオプション
	•	構造化ログの検討

3. キャッシュ機能
	•	VAD結果のキャッシュ
	•	中間結果の保存
	•	処理の再開機能

⸻

📝 設定方式

優先順位：
CLI引数 > .env > config.toml > デフォルト

config.toml 例：

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

[cache]  # 今後追加予定
enabled = true
directory = ".cache/okosu"
max_size_mb = 1000

⸻

このドキュメントは開発の進捗に応じて継続的に更新されます。