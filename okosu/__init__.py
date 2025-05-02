__version__ = "0.1.0"

import logging
import warnings
from speechbrain.utils.logger import setup_logging
import transformers

# transformersの警告を完全に抑制
transformers.logging.set_verbosity_error()

# SpeechBrainのロギング設定
setup_logging(default_level="ERROR")

# okosuのロガーだけINFOレベルに設定
logging.getLogger("okosu").setLevel(logging.INFO)

# 各ライブラリのログレベルを設定
loggers = {
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