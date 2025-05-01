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
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        self.model = model
        
    def ensure_model(self) -> Tuple[str, Path]:
        """モデルの存在確認とダウンロード
        
        Returns:
            Tuple[str, Path]: (バックエンドタイプ, モデルパス)
        """
        # モデル名をファイル名に含める
        local_filename = f"{self.model.value}_{self.model.filename}"
        model_path = self.models_dir / local_filename
        
        if not model_path.exists():
            self._download_model(model_path)
            
        return self.model.backend_type, model_path

    def _download_model(self, model_path: Path) -> None:
        """HuggingFaceからモデルをダウンロード"""
        log_info(f"モデル {self.model.value} をダウンロード中...")
        
        try:
            # HuggingFace Hubからダウンロード
            downloaded_path = hf_hub_download(
                repo_id=self.model.repo_id,
                filename=self.model.filename  # HFのリポジトリ内のファイル名はそのまま
            )
            # ダウンロードしたファイルを適切な場所にコピー
            model_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(downloaded_path, model_path)
            
            log_info(f"モデルのダウンロードが完了しました: {model_path}")
            
        except Exception as e:
            raise RuntimeError(f"モデルのダウンロードに失敗しました: {str(e)}") 