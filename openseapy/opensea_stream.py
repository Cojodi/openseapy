# -*- coding: utf-8 -*-
import asyncio
import json
from functools import wraps

import websockets
from loguru import logger

from . import utils
from .models.models import Message
from .models.types import EventType
from .opensea_api import OpenSeaEventAPI
from .opensea_event import OpenSeaEvent


def with_ws(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        while not hasattr(self, "ws"):
            await asyncio.sleep(0.2)

        return await f(self, *args, **kwargs)

    return wrapper


class OpenSeaStream(OpenSeaEventAPI, OpenSeaEvent):
    def __init__(self, api_key="", test=False, log_level="ERROR"):
        if not test:
            assert api_key

        super(OpenSeaEventAPI, self).__init__()
        super(OpenSeaEvent, self).__init__()
        self._log_level = log_level
        utils.init_logger(logger, log_level)

        testnet = "testnets-" if test else ""
        self.url = (
            f"wss://{testnet}stream.openseabeta.com/socket/websocket?token={api_key}"
        )
        self._keep_alive_interval = 25

        self.worker = utils.Worker()
        self.worker.push(self._recv_task())
        self.worker.push(self._keep_alive_task())

    async def _recv_task(self):
        async with websockets.connect(self.url) as ws:
            self.ws = ws

            while True:
                res = await ws.recv()
                res = json.loads(res)
                res["event"] = EventType(res["event"])

                if self._log_level == "DEBUG":
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
        await self.ws.send(obj)
