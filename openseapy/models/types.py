# -*- coding: utf-8 -*-
from enum import Enum


class EventType(Enum):
    subscribe = "phx_join"
    unsubscribe = "phx_leave"
    keep_alive = "heartbeat"
    reply = "phx_reply"
    close = "phx_close"

    # items
    item_listed = "item_listed"
    item_sold = "item_sold"
    item_transferred = "item_transferred"
    item_metadata_update = "item_metadata_update"
    item_cancelled = "item_cancelled"
    item_received_offer = "item_received_offer"
    item_received_bid = "item_received_bid"


class Wei(str):
    pass


class Address(str):
    pass


class FloatingPrice(str):
    pass


# TODO types for auction style
class ListingType(Enum):
    dutch = "dutch"
