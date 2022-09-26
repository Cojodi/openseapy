# -*- coding: utf-8 -*-
from loguru import logger

from .models.stream import Message
from .models.types import EventType


class OpenSeaEvent:
    EVENT_HANDLER_MAPPING = {
        EventType.reply: "on_reply",
        EventType.close: "on_close",
        # item events
        EventType.item_listed: "on_item_listed",
        EventType.item_sold: "on_item_sold",
        EventType.item_transferred: "on_item_transferred",
        EventType.item_metadata_updated: "on_item_metadata_updated",
        EventType.item_cancelled: "on_item_cancelled",
        EventType.item_received_offer: "on_item_received_offer",
        EventType.item_received_bid: "on_item_received_bid",
    }

    def __init__(self):
        self.event_handlers = {}

    def event(self, f):
        fname = f.__name__
        allowed_function_names = self.EVENT_HANDLER_MAPPING.values()
        if fname not in allowed_function_names:
            raise ValueError(
                f"Unknown event_handler function: {fname}\n"
                f"Allowed: {', '.join(v for v in allowed_function_names)}"
            )

        self.event_handlers[f.__name__] = f

    async def _distribute(self, msg):
        event = EventType(msg["event"])
        handler_name = self.EVENT_HANDLER_MAPPING.get(event, None)
        if handler_name is None:
            logger.error(f"unknown handler: {handler_name}")
            return

        handler = self.event_handlers.get(handler_name, None)
        if handler is None:
            return

        await handler(Message(**msg))
