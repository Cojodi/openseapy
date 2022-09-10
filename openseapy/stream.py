# -*- coding: utf-8 -*-
import asyncio
import json
from functools import wraps

import websockets
from loguru import logger

from . import utils
from .base import OpenSeaBase
from .event import OpenSeaEvent
from .event_api import OpenSeaEventAPI
from .models.stream import Message
from .models.types import EventType


def with_ws(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        while not hasattr(self, "ws"):
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

    def init(self, loop=None):
        if loop is None:
            loop = asyncio

        loop.create_task(self._recv_task())
        loop.create_task(self._keep_alive_task())

    async def _recv_task(self):
        async with websockets.connect(self.url) as ws:
            self.ws = ws

            while True:
                res = await ws.recv()
                res = json.loads(res)
                res["event"] = EventType(res["event"])

                if self.log_level == "DEBUG":
                    logger.debug(f"\n{utils.pformat(res)}")

                await self._distribute(res)


    @with_ws
    async def _keep_alive_task(self):
        msg = Message(topic="phoenix", event=EventType.keep_alive, ref=0).json()

        while True:
            await asyncio.sleep(self._keep_alive_interval)
            await self.ws.send(msg)

    @with_ws
    async def _send(self, obj):
        logger.debug(f"Sending: {obj}")
        await self.ws.send(obj)
