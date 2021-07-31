import os
import dataclasses


@dataclasses.dataclass
class ClientEnv:
    """
    Переменные окружения ASR-клиента
    """
    ip_addr: str           # VOSK-server IP address
    port: int              # VOSK-server IP port
    samplerate: float      # Client audio samplerate
    blocksize: int         # The number of frames passed to the stream callback function


def get_env() -> ClientEnv:

    env = ClientEnv(
        ip_addr=os.environ.get("VOSK_SERVER_IP_ADDR", "localhost"),
        port=int(os.environ.get("VOSK_SERVER_PORT", 2700)),
        samplerate=float(os.environ.get("SAMPLERATE", 0)),
        blocksize=int(os.environ.get("BLOCKSIZE", 4000)),
    )
    return env
