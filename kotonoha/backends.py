from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Type
from pywhispercpp.model import Model
from faster_whisper import WhisperModel
from transformers import pipeline
import torch
import transformers


@dataclass
class TranscriptionSegment:
    """文字起こし結果の1セグメントを表すデータクラス"""
    start: float
    end: float
    text: str
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
                disable_log: ログ出力を無効化（デフォルト: True）
        """
        model_kwargs = kwargs.copy()  # kwargsのコピーを作成
        
        # ログ制御用のパラメータを取り出す
        disable_log = model_kwargs.pop("disable_log", True)
        
        # whisper.cppでは不要なパラメータを除外
        model_kwargs.pop("device", None)  # deviceパラメータは使用しない
        
        # ログ出力を制御
        if disable_log:
            # redirect_whispercpp_logs_toをNoneに設定してログを完全に抑制
            model_kwargs["redirect_whispercpp_logs_to"] = None
            # print_progressをFalseに設定してモデルの進捗出力を抑制
            model_kwargs["print_progress"] = False
            model_kwargs["print_realtime"] = False
            
        self.model = Model(model_path, **model_kwargs)
        
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
                speaker=None
            ) for seg in chunks
        ]
        
    def free(self) -> None:
        """モデルのメモリを解放する"""
        if self.model is not None:
            if hasattr(self.model, 'free') and callable(self.model.free):
                self.model.free()
            self.model = None


class FasterWhisperBackend(WhisperBackend):
    """faster-whisper用のバックエンド実装"""
    def __init__(self):
        self.model = None

    def load_model(self, model_path: str, **kwargs) -> None:
        # model_pathはHuggingFace HubのリポジトリIDを想定
        # 例: "kotoba-tech/kotoba-whisper-v2.0-faster"
        device = kwargs.get("device", "cpu")
        compute_type = kwargs.get("compute_type", "auto")
        self.model = WhisperModel(model_path, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: str, **kwargs) -> List[TranscriptionSegment]:
        if self.model is None:
            raise RuntimeError("モデルがロードされていません。先にload_model()を呼び出してください。")
        language = kwargs.get("language", "ja")
        chunk_length = kwargs.get("chunk_length", 15)
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            chunk_length=chunk_length,
            condition_on_previous_text=kwargs.get("condition_on_previous_text", False)
        )
        result = []
        for seg in segments:
            result.append(TranscriptionSegment(
                start=seg.start,
                end=seg.end,
                text=seg.text,
                speaker=None
            ))
        return result

    def free(self) -> None:
        self.model = None


class TransformersBackend(WhisperBackend):
    """transformers用のバックエンド実装"""
    def __init__(self):
        self.pipe = None

    def load_model(self, model_path: str, **kwargs) -> None:
        # model_pathはhf_hub_downloadで取得したキャッシュパス
        device = kwargs.get("device", "cpu")
        batch_size = kwargs.get("batch_size", 8)
        model_kwargs = kwargs.get("model_kwargs", {})
        torch_dtype = kwargs.get("torch_dtype", torch.float32)
        trust_remote_code = kwargs.get("trust_remote_code", True)
        version = tuple(map(int, transformers.__version__.split(".")[:2]))
        if version == (2, 0):
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=model_path,
                torch_dtype=torch_dtype,
                device=device,
                model_kwargs=model_kwargs,
                batch_size=batch_size,
                trust_remote_code=trust_remote_code,
            )
        else:
            self.pipe = pipeline(
                model=model_path,
                torch_dtype=torch_dtype,
                device=device,
                model_kwargs=model_kwargs,
                batch_size=batch_size,
                trust_remote_code=trust_remote_code,
            )

    def transcribe(self, audio_path: str, **kwargs) -> List[TranscriptionSegment]:
        if self.pipe is None:
            raise RuntimeError("モデルがロードされていません。先にload_model()を呼び出してください。")
        chunk_length_s = kwargs.get("chunk_length_s", 15)
        # pipe()の呼び出し
        result = self.pipe(audio_path, chunk_length_s=chunk_length_s, **{k: v for k, v in kwargs.items() if k != "chunk_length_s"})
        segments = []
        # transformersの出力形式に応じてパース
        if "chunks" in result:
            for seg in result["chunks"]:
                segments.append(TranscriptionSegment(
                    start=seg["timestamp"][0],
                    end=seg["timestamp"][1],
                    text=seg["text"],
                    speaker=seg.get("speaker_id")
                ))
        elif "text" in result:
            # chunk情報がない場合は全体を1セグメントとして扱う
            segments.append(TranscriptionSegment(
                start=0.0,
                end=0.0,
                text=result["text"],
                speaker=None
            ))
        else:
            # 予期しない出力形式
            raise RuntimeError(f"transformersの出力形式が不明: {result}")
        return segments

    def free(self) -> None:
        self.pipe = None


# 利用可能なバックエンドの定義
AVAILABLE_BACKENDS: Dict[str, Type[WhisperBackend]] = {
    "whisper.cpp": WhisperCppBackend,
    "faster-whisper": FasterWhisperBackend,
    "transformers": TransformersBackend,
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