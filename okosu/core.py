import os
from pydub import AudioSegment
import logging
import warnings
import torch

from okosu.vad import VoiceActivityDetector
from okosu.output import create_formatter
from okosu.config import get_model_name, get_output_format
from okosu.preprocessing import AudioPreprocessor
from okosu.utils import TempFileManager, ProgressManager, log_info, log_warning
from okosu.backends import create_whisper_backend
from okosu.models import KotobaModel, KotobaModelManager, MODEL_REGISTRY


def _get_model_enum(model_name: str) -> KotobaModel:
    """モデル名からKotobaModelの列挙型を取得"""
    for model in KotobaModel:
        if model.value == model_name:
            return model
    raise ValueError(f"サポートされていないモデル: {model_name}")


def transcribe_audio(input_path: str, output_format: str = None) -> str:
    """Main pipeline: VAD segmentation + whisper transcription + formatted output.
    
    Args:
        input_path: 入力音声ファイルのパス
        output_format: 出力フォーマット（未指定の場合は設定ファイルから取得）
    
    Returns:
        str: 生成された出力ファイルのパス
    """
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
        backend = None
        
        # モデルの準備
        model_name = get_model_name()
        model = _get_model_enum(model_name)
        model_manager = KotobaModelManager(model)
        backend_type, model_path = model_manager.ensure_model()
        # MODEL_REGISTRYから推奨オプションを取得
        init_options = MODEL_REGISTRY.get(model_name, {}).get("init_options", {}).copy()
        infer_options = MODEL_REGISTRY.get(model_name, {}).get("infer_options", {}).copy()

        log_info(f"モデル: {model_name} ({backend_type})")

        # 動的パラメータの決定
        if "torch_dtype" in init_options:
            init_options["torch_dtype"] = torch.float16 if torch.cuda.is_available() else torch.float32
        if "device" not in init_options and backend_type != "whisper.cpp":
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            init_options["device"] = device
            log_info(f"デバイス: {device}")
        elif backend_type == "whisper.cpp":
            log_info("デバイス: cpu (whisper.cpp)")
        
        # バックエンドの初期化
        backend = create_whisper_backend(backend_type)
        backend.load_model(str(model_path), **init_options)

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

                # Whisper処理
                result_segments = backend.transcribe(temp_wav, **infer_options)
                if not result_segments:
                    log_warning(f"区間 {i+1} で文字起こし結果が得られませんでした")
                    continue
                    
                for seg in result_segments:
                    # バックエンドから返されるセグメントは既に適切な形式
                    transcripts.append({
                        "start": seg.start + start,
                        "end": seg.end + start,
                        "text": seg.text,
                        "speaker": seg.speaker
                    })

                # 進捗状況の更新（1区間完了）
                progress.update(
                    advance=1,
                    description=f"[cyan]文字起こし処理中... ({i+1}/{total_segments}区間)[/cyan]"
                )

        # バックエンドの明示的な解放
        if backend is not None:
            backend.free()
        del backend

        # 4) Sort and format output
        transcripts.sort(key=lambda x: x["start"])
        log_info("出力ファイルを作成中...")
        format_type = output_format or get_output_format()
        formatter = create_formatter(format_type)
        
        base = os.path.splitext(os.path.basename(input_path))[0]
        out = os.path.join("outputs", f"{base}.{format_type}")
        result_path = formatter.format(transcripts, out)
        log_info(f"処理が完了しました: {result_path}")
        
        return result_path
