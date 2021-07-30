#!/usr/bin/env python3

"""
Это автономный модуль, который не использует сетевые соединения
или коммуникации между службами. Он самостоятельно организует VOSK-сервис
и направляет ему данные из потока, получаемого от микрофона.
Для работы с ALSA через PortAudio применяется библиотека sounddevice.
"""

import logging
import os
import queue
import sounddevice as sd
import vosk
import sys

from asr_server.asr_env import get_env

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)
q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        logging.debug(f'{status=}')
    q.put(bytes(indata))


if __name__ == "__main__":

    env = get_env()

    try:
        if not os.path.exists(env.model_path):
            logging.error(f'{env.model_path=} not found')
            sys.exit("Acoustic-Language Model was not found")
        if env.samplerate is None:
            device_info = sd.query_devices(kind='input')
            env.samplerate = int(device_info['default_samplerate'])

        model = vosk.Model(env.model_path)

        with sd.RawInputStream(samplerate=env.samplerate, blocksize=4000, dtype='int16', channels=1,
                               callback=callback):
            logging.info('------------------ Press Ctrl+C to stop the recording ------------------')
            recognizer = vosk.KaldiRecognizer(model, env.samplerate)

            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    logging.info(recognizer.Result())
                else:
                    logging.info(recognizer.PartialResult())

    except KeyboardInterrupt:
        logging.info('\nDone')
        sys.exit(0)
    except Exception as e:
        logging.exception(f'{e}')
        sys.exit(f'{type(e).__name__} : {e}')
