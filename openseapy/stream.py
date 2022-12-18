# -*- coding: utf-8 -*-
import asyncio
import json
from asyncio.exceptions import TimeoutError
from functools import wraps

import websockets
from loguru import logger
from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedOK,
    InvalidStatusCode,
)

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
        self._keep_alive_interval = 20

        self._subscriptions = set

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

                    for name in self.subscriptions:
                        await self.collection(name, sub=True)

                    while True:
                        res = await ws.recv()
                        res = json.loads(res)
                        res["event"] = EventType(res["event"])

                        if self.log_level == "DEBUG":
                            logger.debug(f"\n{utils.pformat(res)}")

                        asyncio.create_task(self._distribute(res))
            except (
                ConnectionClosedOK,
                ConnectionClosed,
                InvalidStatusCode,
                TimeoutError,
            ):
                logger.error("Connection closed, reconnection (recv task)")
            except Exception as e:
                logger.error("Uncaught exception (receive task), trace below:")
                logger.exception(e)
                asyncio.sleep(1)

            # reset ws
            self.ws = None

    @with_ws
    async def _keep_alive_task(self):
        msg = Message(topic="phoenix", event=EventType.keep_alive, ref=0).json()

        while True:
            try:
                await asyncio.sleep(self._keep_alive_interval)
                if self.ws is None:
                    logger.error("Waiting for ws to reconnect... (keep alive)")
                    continue

                await self.ws.send(msg)
            except (
                ConnectionClosed,
                ConnectionClosedOK,
                InvalidStatusCode,
                TimeoutError,
            ):
                logger.error("Connection close, reconnection (keep alive)")
            except Exception as e:
                logger.error(f"Uncaught exception (keep alive), trace below:")
                logger.exception(e)
                asyncio.sleep(1)

    @with_ws
    async def _send(self, obj):
        while self.ws is None:
            logger.error("Waiting for ws to reconnect... (send)")
            await asyncio.sleep(1)

        logger.debug(f"Sending: {obj}")
        await self.ws.send(obj)
