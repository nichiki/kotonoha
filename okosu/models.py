from enum import Enum
from pathlib import Path
from typing import Tuple
from huggingface_hub import hf_hub_download
from okosu.utils import log_info


class KotobaModel(Enum):
    """利用可能なKotobaモデル一覧"""
    # 通常版
    V2_0 = "kotoba-whisper-v2.0"
    V2_1 = "kotoba-whisper-v2.1"
    V2_2 = "kotoba-whisper-v2.2"
    # 最適化版
    V2_0_GGML = "kotoba-whisper-v2.0-ggml"     # whisper.cpp用
    V2_0_FASTER = "kotoba-whisper-v2.0-faster"  # faster-whisper用

    @property
    def backend_type(self) -> str:
        """このモデルに対応するバックエンド"""
        if self.value.endswith("-ggml"):
            return "whisper.cpp"
        elif self.value.endswith("-faster"):
            return "faster-whisper"
        return "transformers"

    @property
    def filename(self) -> str:
        """モデルのファイル名"""
        if self.backend_type == "whisper.cpp":
            # -ggmlを除いたベース名を使用
            base_name = self.value.replace("-ggml", "")
            return f"ggml-{base_name}.bin"
        elif self.backend_type == "faster-whisper":
            return "model.bin"
        elif self.backend_type == "transformers":
            return "model.safetensors"
        return self.value

    @property
    def repo_id(self) -> str:
        """HuggingFaceのリポジトリID"""
        return f"kotoba-tech/{self.value}"


class KotobaModelManager:
    """Kotoba-Whisperモデルの管理クラス"""
    
    def __init__(self, model: KotobaModel = KotobaModel.V2_0_GGML):
        self.model = model
        
    def ensure_model(self) -> Tuple[str, str]:
        """モデルの存在確認とダウンロード
        Returns:
            Tuple[str, str]: (バックエンドタイプ, モデルパスまたはリポジトリID)
        """
        if self.model.backend_type in ("faster-whisper", "transformers"):
            # transformers, faster-whisperはリポジトリIDをそのまま返す
            return self.model.backend_type, self.model.repo_id
        else:
            model_path = self._download_model()
            return self.model.backend_type, model_path

    def _download_model(self) -> Path:
        """HuggingFaceからモデルをダウンロード（キャッシュ優先、ログはダウンロード時のみ）"""
        try:
            # まずキャッシュのみで探す
            downloaded_path = hf_hub_download(
                repo_id=self.model.repo_id,
                filename=self.model.filename,
                local_files_only=True
            )
        except Exception:
            # なければダウンロード
            log_info(f"モデル {self.model.value} をダウンロード中...")
            downloaded_path = hf_hub_download(
                repo_id=self.model.repo_id,
                filename=self.model.filename,
                local_files_only=False
            )
            log_info(f"モデルのダウンロードが完了しました: {downloaded_path}")
        return Path(downloaded_path)

# モデルごとのバックエンド種別・推奨パラメータセット（init_options: モデル生成時, infer_options: 推論時）
MODEL_REGISTRY = {
    "kotoba-whisper-v2.2": {
        "backend": "transformers",
        "init_options": {
            "batch_size": 8,
            "trust_remote_code": True,
            "model_kwargs": {"attn_implementation": "sdpa"},
        },
        "infer_options": {
            "chunk_length_s": 15,
            # 例: "num_speakers": 3,
        }
    },
    "kotoba-whisper-v2.1": {
        "backend": "transformers",
        "init_options": {
            "batch_size": 16,
            "trust_remote_code": True,
            "punctuator": True,
            "model_kwargs": {"attn_implementation": "sdpa"},
        },
        "infer_options": {
            "chunk_length_s": 15,
            "return_timestamps": True,
            "generate_kwargs": {"language": "ja", "task": "transcribe"},
        }
    },
    "kotoba-whisper-v2.0": {
        "backend": "transformers",
        "init_options": {
            "model_kwargs": {"attn_implementation": "sdpa"},
        },
        "infer_options": {
            "return_timestamps": True,
            "generate_kwargs": {"language": "ja", "task": "transcribe"},
        }
    },
    "kotoba-whisper-v2.0-faster": {
        "backend": "faster-whisper",
        "init_options": {
            "compute_type": "auto",
        },
        "infer_options": {
            "chunk_length": 15,
            "language": "ja",
            "condition_on_previous_text": False,
        }
    },
    "kotoba-whisper-v2.0-ggml": {
        "backend": "whisper.cpp",
        "init_options": {
            "language": "ja",
        },
        "infer_options": {}
    },
} 