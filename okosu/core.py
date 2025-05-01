import os
from pywhispercpp.model import Model
from pydub import AudioSegment
import logging

from okosu.vad import VoiceActivityDetector
from okosu.output import create_formatter
from okosu.config import get_model_path, get_output_format
from okosu.preprocessing import AudioPreprocessor
from okosu.utils import TempFileManager, ProgressManager, log_info, log_warning, suppress_output


def transcribe_audio(input_path: str, output_format: str = None) -> str:
    """Main pipeline: VAD segmentation + whisper.cpp transcription + formatted output.
    
    Args:
        input_path: 入力音声ファイルのパス
        output_format: 出力フォーマット（未指定の場合は設定ファイルから取得）
    
    Returns:
        str: 生成された出力ファイルのパス
    """
    # サードパーティライブラリのログレベルを制御
    logging.getLogger("pywhispercpp").setLevel(logging.WARNING)
    logging.getLogger("pydub.converter").setLevel(logging.WARNING)

    with TempFileManager() as temp_manager:
        # 1) Convert to WAV with preprocessing
        log_info("音声ファイルを前処理中...")
        preprocessor = AudioPreprocessor()
        wav_path = preprocessor.process(input_path, temp_manager)

        # 2) VAD segments with merging
        log_info("音声区間を検出中...")
        vad = VoiceActivityDetector()
        segments = vad.detect_speech_segments(wav_path)
        total_segments = len(segments)
        log_info(f"{total_segments}個の音声区間を検出しました")

        # 3) Load Whisper model and process
        log_info("Whisperモデルを読み込み中...")
        transcripts = []
        model = None  # モデル変数をブロック外で定義
        
        # Whisperモデルの読み込み
        with suppress_output():
            model_file = get_model_path()
            model = Model(model_file, language="ja")

        audio_full = AudioSegment.from_wav(wav_path)
        dur_full = len(audio_full) / 1000.0
        MARGIN = 0.25

        # 文字起こし処理
        with ProgressManager() as progress:
            progress.add_task(
                f"[cyan]文字起こし処理中... (0/{total_segments}区間)[/cyan]",
                total=total_segments
            )
            
            for i, ts in enumerate(segments):
                # 音声区間の処理
                start = max(0, ts["start"] - MARGIN)
                end = min(dur_full, ts["end"] + MARGIN)
                clip = audio_full[int(start*1000):int(end*1000)]
                temp_wav = temp_manager.create_temp_path(
                    prefix=f"segment_{i}_",
                    suffix=".wav"
                )
                clip.export(temp_wav, format="wav")

                # Whisper処理部分のみsuppress_output
                with suppress_output():
                    chunks = model.transcribe(temp_wav)
                if not chunks:
                    log_warning(f"区間 {i+1} で文字起こし結果が得られませんでした")
                for seg in chunks:
                    s = seg.t0/1000 + start
                    e = seg.t1/1000 + start
                    transcripts.append({"start": s, "end": e, "text": seg.text})

                # 進捗状況の更新（1区間完了）
                progress.update(
                    advance=1,
                    description=f"[cyan]文字起こし処理中... ({i+1}/{total_segments}区間)[/cyan]"
                )

        # モデルの明示的な解放を試みる
        with suppress_output():
            if hasattr(model, 'free') and callable(model.free):
                model.free()
            del model

        # 4) Format and write output
        log_info("出力ファイルを作成中...")
        format_type = output_format or get_output_format()
        formatter = create_formatter(format_type)
        
        base = os.path.splitext(os.path.basename(input_path))[0]
        out = os.path.join("outputs", f"{base}.{format_type}")
        result_path = formatter.format(transcripts, out)
        log_info(f"処理が完了しました: {result_path}")
        
        return result_path
