#!/usr/bin/env python3

import asyncio
import os

import websockets
import sys
from pyaudio import PyAudio, Stream, paInt16
from contextlib import asynccontextmanager, contextmanager, AsyncExitStack
from typing import AsyncGenerator, Generator


@contextmanager
def _pyaudio() -> Generator[PyAudio, None, None]:
    p = PyAudio()
    try:
        yield p
    finally:
        print('Terminating PyAudio object')
        p.terminate()


@contextmanager
def _pyaudio_open_stream(p: PyAudio, *args, **kwargs) -> Generator[Stream, None, None]:
    s = p.open(*args, **kwargs)
    try:
        yield s
    finally:
        print('Closing PyAudio Stream')
        s.close()


@asynccontextmanager
async def _polite_websocket(ws: websockets.WebSocketClientProtocol) -> AsyncGenerator[websockets.WebSocketClientProtocol, None]:
    try:
        yield ws
    finally:
        print('Terminating connection')
        await ws.send('{"eof" : 1}')
        print(await ws.recv())


async def run_test(uri):

    async with AsyncExitStack() as stack:
        ws = await stack.enter_async_context(websockets.connect(uri))
        print(f'Connected to {uri}')
        print('Type Ctrl-C to exit')
        ws = await stack.enter_async_context(_polite_websocket(ws))
        p = stack.enter_context(_pyaudio())
        s = stack.enter_context(_pyaudio_open_stream(
            p,
            format=paInt16,
            channels=1,
            rate=int(os.getenv("SAMPLE_RATE", 16000)),
            input=True,
            frames_per_buffer=int(os.getenv("FRAMES_PER_BUFFER", 8000))
        ))
        while True:
            data = s.read(8000)
            if len(data) == 0:
                break
            await ws.send(data)
            print(await ws.recv())


if __name__ == '__main__':

    if len(sys.argv) == 2:
        server_uri = sys.argv[1]
    else:
        server_uri = 'localhost:2700'

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            run_test('ws://' + server_uri)
        )
    except (KeyboardInterrupt, Exception) as e:
        loop.stop()
        loop.run_until_complete(
            loop.shutdown_asyncgens()
        )
        if isinstance(e, KeyboardInterrupt):
            print('Bye!')
            exit(0)
        else:
            print(f'Oops! {e}')
            exit(1)
