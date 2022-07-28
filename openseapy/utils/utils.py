# -*- coding: utf-8 -*-
import asyncio
import sys
import threading as th
from pprint import pformat as pformat_
from types import CoroutineType


class Worker(th.Thread):
    def __init__(self):
        self.event_loop = asyncio.new_event_loop()

        super().__init__(target=self.run_loop, args=(self.event_loop,))
        self.start()

    def run_loop(self, loop):
        try:
            asyncio.set_event_loop(loop)
            loop.run_forever()
        except KeyboardInterrupt:
            asyncio.gather(*asyncio.Task.all_tasks()).cancel()
            loop.stop()
            loop.close()

    def push(self, func, *args):
        if isinstance(func, CoroutineType):
            asyncio.run_coroutine_threadsafe(func, self.event_loop)
        else:
            self.event_loop.call_soon_threadsafe(func, *args)


def pformat(msg):
    if hasattr(msg, "dict"):
        return pformat_(msg.dict())

    return pformat_(msg)


def init_logger(logger, level):
    logger.remove()

    levels = ("DEBUG", "INFO", "WARNING", "ERROR")
    if level not in levels:
        raise ValueError(f"Unknown log level: {level}\nAllowed Values: {levels}")

    levels = levels[levels.index(level) :]
    for level in levels:
        logger.add(sys.stderr, level=level)
