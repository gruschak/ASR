#!/usr/bin/env python3

import os
import asyncio
import websockets
import concurrent.futures
import functools
import logging
from typing import Tuple, Any
from vosk import Model, KaldiRecognizer
from env import get_env


def process_chunk(rec, message) -> Tuple[Any, bool]:
    if message == '{"eof" : 1}':
        return rec.FinalResult(), True
    elif rec.AcceptWaveform(message):
        return rec.Result(), False
    else:
        return rec.PartialResult(), False


async def recognize(websocket, path, env, model, pool, loop, connected):

    # Create the recognizer
    sample_rate = env.sample_rate
    max_alternatives = env.max_alternatives
    recognizer = KaldiRecognizer(model, sample_rate)
    recognizer.SetMaxAlternatives(max_alternatives)

    logging.info(f'Connection from {websocket.remote_address}')
    connected.add(websocket)

    try:

        while True:
            message = await websocket.recv()
            response, stop = await loop.run_in_executor(pool, process_chunk, recognizer, message)
            for ws in connected:
                await ws.send(response)

            if stop:
                break

    except websockets.ConnectionClosed as e:
        logging.info(f'ASR lost connection {websocket.remote_address}: {e!s}')
    finally:
        connected.remove(websocket)


def start_ws_server():

    # Enable logging if needed
    #
    # logger = logging.getLogger('websockets')
    # logger.setLevel(logging.INFO)
    # logger.addHandler(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO)

    # Gpu part, uncomment if vosk-api has gpu support
    #
    # from vosk import GpuInit, GpuInstantiate
    # GpuInit()
    # def thread_init():
    #     GpuInstantiate()
    # pool = concurrent.futures.ThreadPoolExecutor(initializer=thread_init)

    env = get_env()
    model = Model(env.model_path)
    pool = concurrent.futures.ThreadPoolExecutor((os.cpu_count() or 1))
    loop = asyncio.get_event_loop()
    connected = set()

    recognize_handler = functools.partial(recognize, env=env, model=model, pool=pool, loop=loop, connected=connected)
    start_server = websockets.serve(recognize_handler, env.ip_addr, env.port)

    logging.info(f'Listening on {env.ip_addr} {env.port}')
    loop.run_until_complete(start_server)
    loop.run_forever()


if __name__ == "__main__":
    start_ws_server()
