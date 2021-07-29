import os
import dataclasses


@dataclasses.dataclass
class ASREnv:
    """
    Переменные окружения ASR-сервера
    """
    ip_addr: str          # VOSK-server IP address
    port: int               # VOSK-server IP port
    model_path: str         # VOSK model directory name
    sample_rate: float      # VOSK sample rate
    max_alternatives: int


def get_env() -> ASREnv:

    env = ASREnv(
        ip_addr=os.environ.get("VOSK_SERVER_IP_ADDR", "0.0.0.0"),
        port=int(os.environ.get("VOSK_SERVER_PORT", 2700)),
        model_path=os.environ.get("VOSK_MODEL_DIR", "model"),
        sample_rate=float(os.environ.get("VOSK_SAMPLE_RATE", 16000)),
        max_alternatives=int(os.environ.get("VOSK_ALTERNATIVES", 0)),
    )
    return env
