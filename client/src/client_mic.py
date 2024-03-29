#!/usr/bin/env python3

"""
Для работы с ALSA через PortAudio применяется библиотека sounddevice.
"""

import logging
import queue
import sounddevice as sd
import sys
import asyncio
import websockets
import json
import pprint

from client_env import get_env

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
que = queue.Queue()
env = get_env()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        logging.debug(f'{status=}')
    que.put(bytes(indata))


async def link_queue_to_ws(q: queue.Queue, ws_uri=f"ws://{env.ip_addr}:{env.port}"):
    """ Осуществляет подключение к websocket-серверу и перебрасывание
        поступающих в очередь данных в серверный сокет. """
    async with websockets.connect(ws_uri) as websocket:

        while True:
            data = q.get()
            await websocket.send(data)
            # logging.info(f'> {len(data)}')

            received_data = await websocket.recv()
            msg = json.loads(received_data)
            if msg.get("text"):
                logging.info(f'< {msg["text"]=}')


if __name__ == "__main__":

    samplerate = env.samplerate
    try:
        device_info = sd.query_devices(kind="input")
        logging.info('\n' + pprint.pformat(device_info))
        logging.info("*" * 80)

        if not samplerate:
            samplerate = int(device_info["default_samplerate"])

        with sd.RawInputStream(
                samplerate=samplerate,
                blocksize=env.blocksize,
                dtype='int16',
                channels=1,
                callback=callback
        ):
            logging.info(f'Started with {samplerate=}')
            logging.info('------------------ Press Ctrl+C to stop the recording ------------------')
            asyncio.get_event_loop().run_until_complete(link_queue_to_ws(que))
    except KeyboardInterrupt:
        logging.info('\nDone')
        sys.exit(0)
    except Exception as e:
        logging.exception(f'{e}')
        sys.exit(f'{type(e).__name__} : {e}')
