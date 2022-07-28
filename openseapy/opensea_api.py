# -*- coding: utf-8 -*-
import asyncio
from functools import wraps

from .models.models import Message
from .models.types import EventType


def send(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        obj = f(self, *args, **kwargs)
        return asyncio.run(self._send(obj.json()))

    return wrapper


class OpenSeaEventAPI:
    def __init__(self):
        pass

    @send
    def collection(self, name, sub=True):
        req = Message(
            topic=f"collection:{name}",
            event=EventType.subscribe if sub else EventType.unsubscribe,
            ref=0,
        )
        return req
