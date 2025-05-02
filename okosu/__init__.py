__version__ = "0.1.0"

import logging
import warnings
from speechbrain.utils.logger import setup_logging

# SpeechBrainのロギング設定
setup_logging(default_level="ERROR")

# okosuのロガーだけINFOレベルに設定
logging.getLogger("okosu").setLevel(logging.INFO)

# 各ライブラリのログレベルを設定
loggers = {
    "transformers": logging.CRITICAL,
    "transformers.modeling_utils": logging.CRITICAL,
    "transformers.generation.utils": logging.CRITICAL,
    "transformers.models.whisper.tokenization_whisper": logging.CRITICAL,
    "torch": logging.ERROR,
    "pyannote": logging.ERROR,
    "pywhispercpp": logging.WARNING,
    "pydub.converter": logging.WARNING,
    "speechbrain": logging.ERROR,
}

for logger_name, level in loggers.items():
    logging.getLogger(logger_name).setLevel(level)

# warningsモジュールの設定
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)