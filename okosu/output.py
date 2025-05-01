import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict


class TranscriptionFormatter(ABC):
    """文字起こし結果の出力フォーマッタの基底クラス"""
    
    @abstractmethod
    def format(self, transcripts: List[Dict], output_path: str) -> str:
        """文字起こし結果を指定されたフォーマットで出力する
        
        Args:
            transcripts: 文字起こし結果のリスト。各要素は {"start": float, "end": float, "text": str}
            output_path: 出力先のパス
            
        Returns:
            str: 実際に出力されたファイルのパス
        """
        pass


class SRTFormatter(TranscriptionFormatter):
    """SRT形式での出力を行うフォーマッタ"""
    
    def format(self, transcripts: List[Dict], output_path: str) -> str:
        # 出力ディレクトリの作成
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(output_path, "w", encoding="utf-8") as f:
            for idx, seg in enumerate(transcripts, start=1):
                start = self._format_timestamp(seg["start"])
                end = self._format_timestamp(seg["end"])
                text = seg.get("text", "").strip()
                speaker = seg.get("speaker")
                if speaker:
                    text = f"{speaker}：{text}"
                f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
                
        return output_path
    
    def _format_timestamp(self, seconds: float) -> str:
        """秒数をSRTタイムスタンプ形式（HH:MM:SS,mmm）に変換"""
        millis = int((seconds - int(seconds)) * 1000)
        total_seconds = int(seconds)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


class PlainTextFormatter(TranscriptionFormatter):
    """プレーンテキスト形式での出力を行うフォーマッタ"""
    
    def format(self, transcripts: List[Dict], output_path: str) -> str:
        # 拡張子を.txtに変更
        output_path = str(Path(output_path).with_suffix('.txt'))
        
        # 出力ディレクトリの作成
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            for seg in transcripts:
                text = seg.get("text", "").strip()
                speaker = seg.get("speaker")
                if speaker:
                    text = f"{speaker}：{text}"
                f.write(f"{text}\n")
        
        return output_path


def create_formatter(format_type: str = "srt") -> TranscriptionFormatter:
    """フォーマッタのファクトリ関数
    
    Args:
        format_type: 出力フォーマットの種類 ("srt", "txt" など)
    
    Returns:
        TranscriptionFormatter: 対応するフォーマッタのインスタンス
    """
    formatters = {
        "srt": SRTFormatter,
        "txt": PlainTextFormatter,
    }
    
    formatter_class = formatters.get(format_type.lower())
    if formatter_class is None:
        raise ValueError(f"Unsupported format type: {format_type}")
        
    return formatter_class()
