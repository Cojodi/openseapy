# -*- coding: utf-8 -*-
from functools import wraps

from .models.stream import Message
from .models.types import EventType


def send(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        obj = f(self, *args, **kwargs)
        return await self._send(obj.json())

    return wrapper


class OpenSeaEventAPI:
    subscriptions = set()

    @send
    def collection(self, name, sub=True, ref=0):
        if sub:
            self.subscriptions.add(name)
        else:
            self.subscriptions.remove(name)

        req = Message(
            topic=f"collection:{name}",
            event=EventType.subscribe if sub else EventType.unsubscribe,
            ref=ref,
        )
        return req
