import os
from typing import Any, Dict

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore # fallback for Python < 3.11
from dotenv import load_dotenv

load_dotenv()

_config_cache: Dict[str, Any] = {}


def load_config(path: str = "config.toml") -> Dict[str, Any]:
    """設定ファイルを読み込む（セッション中は1回のみ）
    
    Args:
        path: 設定ファイルのパス
        
    Returns:
        Dict[str, Any]: 読み込んだ設定
    """
    global _config_cache
    if not _config_cache and os.path.exists(path):
        with open(path, "rb") as f:
            _config_cache = tomllib.load(f)
    return _config_cache


def get_setting(toml_path: str, env_var: str, default: Any) -> Any:
    """設定値を取得（環境変数 > TOML > デフォルト値の優先順）
    
    Args:
        toml_path: TOML内のパス（例: "general.model_path"）
        env_var: 環境変数名
        default: デフォルト値
        
    Returns:
        Any: 取得した設定値
    """
    # First try environment variable
    env_value = os.getenv(env_var)
    if env_value is not None:
        return env_value

    # Then try TOML config
    config = load_config()
    if config:
        # Split TOML path into sections
        sections = toml_path.split(".")
        value = config
        for section in sections:
            value = value.get(section, {})
        if value != {}:
            return value

    # Finally use default
    return default


def get_model_path() -> str:
    return get_setting("general.model_path", "MODEL_PATH", "models/ggml-kotoba-whisper-v2.0.bin")


def get_language() -> str:
    return get_setting("general.language", "LANGUAGE", "ja")


def get_backend_type() -> str:
    """使用するWhisperバックエンドの種類を取得
    
    Returns:
        str: バックエンドの種類（例: "whisper.cpp"）
    """
    return get_setting("general.backend", "BACKEND_TYPE", "whisper.cpp")


def get_output_format() -> str:
    return get_setting("general.output_format", "OUTPUT_FORMAT", "srt")


def get_vad_settings() -> dict:
    return {
        "threshold": float(get_setting("vad.threshold", "VAD_THRESHOLD", 0.30)),
        "min_speech_duration_ms": int(get_setting("vad.min_speech_duration_ms", "VAD_MIN_SPEECH_MS", 100)),
        "min_silence_duration_ms": int(get_setting("vad.min_silence_duration_ms", "VAD_MIN_SILENCE_MS", 300)),
        "speech_pad_ms": int(get_setting("vad.speech_pad_ms", "VAD_PAD_MS", 50)),
    }
