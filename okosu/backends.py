from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Type
from pywhispercpp.model import Model


@dataclass
class TranscriptionSegment:
    """文字起こし結果の1セグメントを表すデータクラス"""
    start: float
    end: float
    text: str
    confidence: Optional[float] = None
    words: Optional[List[Dict[str, Any]]] = None
    speaker: Optional[str] = None


class WhisperBackend(ABC):
    """Whisper系バックエンドの抽象基底クラス"""
    
    @abstractmethod
    def load_model(self, model_path: str, **kwargs) -> None:
        """モデルをロードする
        
        Args:
            model_path: モデルファイルのパス
            **kwargs: バックエンド固有の追加パラメータ
        """
        pass
        
    @abstractmethod
    def transcribe(self, audio_path: str, **kwargs) -> List[TranscriptionSegment]:
        """音声ファイルを文字起こしする
        
        Args:
            audio_path: 音声ファイルのパス
            **kwargs: バックエンド固有の追加パラメータ
            
        Returns:
            List[TranscriptionSegment]: 文字起こし結果のセグメントリスト
        """
        pass
        
    @abstractmethod
    def free(self) -> None:
        """モデルのメモリを解放する（必要な場合）"""
        pass


class WhisperCppBackend(WhisperBackend):
    """whisper.cpp用のバックエンド実装"""
    
    def __init__(self):
        self.model = None
        
    def load_model(self, model_path: str, **kwargs) -> None:
        """whisper.cppモデルをロードする
        
        Args:
            model_path: モデルファイルのパス
            **kwargs: 
                language: 言語指定（デフォルト: "ja"）
        """
        language = kwargs.get("language", "ja")
        self.model = Model(model_path, language=language)
        
    def transcribe(self, audio_path: str, **kwargs) -> List[TranscriptionSegment]:
        """音声ファイルを文字起こしする
        
        Args:
            audio_path: 音声ファイルのパス
            
        Returns:
            List[TranscriptionSegment]: 文字起こし結果のセグメントリスト
        """
        if self.model is None:
            raise RuntimeError("モデルがロードされていません。先にload_model()を呼び出してください。")
            
        chunks = self.model.transcribe(audio_path)
        return [
            TranscriptionSegment(
                start=seg.t0/1000,  # ミリ秒を秒に変換
                end=seg.t1/1000,
                text=seg.text,
                confidence=None  # whisper.cppは現状confidence未対応
            ) for seg in chunks
        ]
        
    def free(self) -> None:
        """モデルのメモリを解放する"""
        if self.model is not None:
            if hasattr(self.model, 'free') and callable(self.model.free):
                self.model.free()
            self.model = None


# 利用可能なバックエンドの定義
AVAILABLE_BACKENDS: Dict[str, Type[WhisperBackend]] = {
    "whisper.cpp": WhisperCppBackend,
    # 今後他のバックエンドを追加予定:
    # "faster-whisper": FasterWhisperBackend,
    # "transformers": TransformersBackend,
}


def create_whisper_backend(backend_type: str) -> WhisperBackend:
    """バックエンドのインスタンスを生成する
    
    Args:
        backend_type: バックエンドの種類（例: "whisper.cpp"）
        
    Returns:
        WhisperBackend: 指定されたバックエンドのインスタンス
        
    Raises:
        ValueError: サポートされていないバックエンドが指定された場合
    """
    if backend_type not in AVAILABLE_BACKENDS:
        raise ValueError(
            f"サポートされていないバックエンド: {backend_type}\n"
            f"利用可能なバックエンド: {', '.join(AVAILABLE_BACKENDS.keys())}"
        )
    return AVAILABLE_BACKENDS[backend_type]() 