from pydub import AudioSegment
from pathlib import Path
from typing import Protocol


class TempManagerProtocol(Protocol):
    """一時ファイル管理のためのプロトコル定義"""
    def create_temp_path(self, prefix: str, suffix: str) -> str: ...


class AudioPreprocessor:
    def __init__(self, target_sample_rate: int = 16000):
        self.target_sample_rate = target_sample_rate

    def process(self, input_path: str, temp_manager: TempManagerProtocol) -> str:
        """音声ファイルに対して一連の前処理を実行
        
        Args:
            input_path: 入力音声ファイルのパス
            temp_manager: 一時ファイル管理オブジェクト
            
        Returns:
            str: 処理済み音声ファイルのパス
            
        処理内容:
            1. WAV形式への変換
            2. サンプリングレートの統一
            3. モノラル化
        """
        audio = AudioSegment.from_file(input_path)
        input_stem = Path(input_path).stem
        wav_path = temp_manager.create_temp_path(
            prefix=f"{input_stem}_",
            suffix="_converted.wav"
        )
        
        # サンプリングレートとチャンネル数の変換
        audio = (
            audio
            .set_frame_rate(self.target_sample_rate)
            .set_channels(1)
        )
        
        # WAV形式で保存
        audio.export(wav_path, format="wav")
        return wav_path 