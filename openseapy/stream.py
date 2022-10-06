# -*- coding: utf-8 -*-
import asyncio
import json
from functools import wraps

import websockets
from loguru import logger
from websockets.exceptions import ConnectionClosedOK

from . import utils
from .base import OpenSeaBase
from .event import OpenSeaEvent
from .event_api import OpenSeaEventAPI
from .models.stream import Message
from .models.types import EventType


def with_ws(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        while not hasattr(self, "ws") or getattr(self, "ws") is None:
            await asyncio.sleep(0.2)

        return await f(self, *args, **kwargs)

    return wrapper


class OpenSeaStream(OpenSeaBase, OpenSeaEvent, OpenSeaEventAPI):
    def __init__(self, api_key: str, test: bool, log_level: str):
        OpenSeaBase.__init__(self, api_key, test, log_level)
        OpenSeaEvent.__init__(self)
        OpenSeaEventAPI.__init__(self)

        testnet = "testnets-" if test else ""
        self.url = (
            f"wss://{testnet}stream.openseabeta.com/socket/websocket?token={api_key}"
        )
        self._keep_alive_interval = 25

    async def start(self, loop=None):
        if loop is None:
            loop = asyncio

        loop.create_task(self._recv_task())
        loop.create_task(self._keep_alive_task())

    async def _recv_task(self):
        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    self.ws = ws

                    while True:
                        res = await ws.recv()
                        res = json.loads(res)
                        res["event"] = EventType(res["event"])

                        if self.log_level == "DEBUG":
                            logger.debug(f"\n{utils.pformat(res)}")

                        asyncio.create_task(self._distribute(res))
            except ConnectionClosedOK:
                logger.info("Connection closed, reconnection")
            except Exception as e:
                logger.error("Uncaught exception in recv_task, trace below:")
                logger.exception(e)

    @with_ws
    async def _keep_alive_task(self):
        msg = Message(topic="phoenix", event=EventType.keep_alive, ref=0).json()

        while True:
            await asyncio.sleep(self._keep_alive_interval)
            if self.ws is None:
                continue

            await self.ws.send(msg)

    @with_ws
    async def _send(self, obj):
        while self.ws is None:
            logger.error("Waiting for ws to reconnect...")
            await asyncio.sleep(1)

        logger.debug(f"Sending: {obj}")
        await self.ws.send(obj)
