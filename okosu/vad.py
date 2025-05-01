from silero_vad import load_silero_vad, read_audio, get_speech_timestamps as vad_ts
from okosu.config import get_vad_settings


class VoiceActivityDetector:
    def __init__(self, min_segment_duration: float = 2.0):
        self.settings = get_vad_settings()
        self.min_segment_duration = min_segment_duration
        self.model = load_silero_vad(onnx=True)

    def detect_speech_segments(self, wav_path: str) -> list[dict]:
        """音声ファイルから発話区間を検出し、短い区間をマージして返す"""
        # VADで発話区間を検出
        wav = read_audio(wav_path, sampling_rate=16000)
        segments = vad_ts(
            wav,
            self.model,
            sampling_rate=16000,
            return_seconds=True,
            threshold=self.settings["threshold"],
            min_speech_duration_ms=self.settings["min_speech_duration_ms"],
            min_silence_duration_ms=self.settings["min_silence_duration_ms"],
            speech_pad_ms=self.settings["speech_pad_ms"],
        )

        # 短い区間のマージ処理
        return self._merge_short_segments(segments)

    def _merge_short_segments(self, segments: list[dict]) -> list[dict]:
        """短い発話区間を結合する"""
        merged = []
        buffer = None

        for ts in segments:
            dur = ts["end"] - ts["start"]
            if dur >= self.min_segment_duration:
                if buffer and buffer["end"] - buffer["start"] >= self.min_segment_duration:
                    merged.append(buffer)
                buffer = None
                merged.append(ts)
            else:
                if buffer is None:
                    buffer = ts.copy()
                else:
                    buffer["end"] = ts["end"]

        if buffer:
            if buffer["end"] - buffer["start"] < self.min_segment_duration:
                buffer["end"] = buffer["start"] + self.min_segment_duration
            merged.append(buffer)

        return merged
