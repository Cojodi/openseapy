import datetime as dt
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, model_validator

from .types import Address, EventType, FloatingPrice, ListingType, Wei


################################################################################
# BASE
class Collection(BaseModel):
    slug: str


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    address: Address


class Token(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    address: Address
    decimals: int
    # TODO probably FloatingPrice
    eth_price: str
    name: Optional[str]
    symbol: str
    usd_price: FloatingPrice


class Chain(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str


class Transaction(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    hash: str
    timestamp: dt.datetime


class ItemMetadata(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    animation_url: Optional[str]
    image_url: Optional[str]
    metadata_url: Optional[str]
    name: Optional[str]


class Item(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    chain: Optional[Chain]
    metadata: Optional[ItemMetadata]
    nft_id: Optional[str]
    permalink: Optional[str]

    @property
    def token_id(self):
        return self.nft_id.rsplit("/", 1)[-1]

    @property
    def token_address(self):
        return self.nft_id.rsplit("/", 2)[-2]


class BaseEvent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    collection: Collection
    event_timestamp: dt.datetime


################################################################################
# ITEM
class ItemListedEvent(BaseEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    item: Item
    base_price: Wei
    payment_token: Optional[Token]
    quantity: int

    expiration_date: dt.datetime
    listing_type: Optional[ListingType]
    listing_date: dt.datetime
    is_private: bool

    maker: User
    taker: Optional[User]

    @model_validator(mode="before")
    def f(cls, values):
        if "listing_type" in values and values["listing_type"] not in (
            None,
            "dutch",
            "english",
        ):
            print(values["listing_type"])
        return values


class ItemSoldEvent(BaseEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    item: Item
    sale_price: Wei
    payment_token: Optional[Token]
    quantity: int

    closing_date: dt.datetime
    listing_type: Optional[ListingType]
    transaction: Optional[Transaction]
    is_private: bool

    maker: User
    taker: User


class ItemTransferredEvent(BaseEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    item: Item
    quantity: int
    from_account: User
    to_account: User
    transaction: Optional[Transaction]


class ItemMetadataUpdatedEvent(BaseEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    image_preview_url: str
    animation_url: Optional[str]
    background_color: str
    metadata_url: str
    # TODO traittype
    traits: List[dict]


class ItemCancelledEvent(BaseEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    item: Item
    payment_token: Optional[Token]
    quantity: int

    listing_type: Optional[ListingType]


class ItemReceivedOfferEvent(BaseEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    item: Item
    base_price: Wei
    payment_token: Optional[Token]
    quantity: int

    created_date: dt.datetime
    expiration_date: dt.datetime

    maker: User
    taker: Optional[User]


class ItemReceivedBidEvent(BaseEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    item: Item
    base_price: Wei
    payment_token: Optional[Token]
    quantity: int

    created_date: dt.datetime
    expiration_date: dt.datetime

    maker: User
    taker: Optional[User]


# TODO collection_offer
# TODO trait_offer


################################################################################
# MESSAGE
ItemEvent = Union[
    ItemListedEvent,
    ItemSoldEvent,
    ItemTransferredEvent,
    ItemMetadataUpdatedEvent,
    ItemCancelledEvent,
    ItemReceivedOfferEvent,
    ItemReceivedBidEvent,
]

MESSAGE_MAPPING = {
    EventType.item_listed: ItemListedEvent,
    EventType.item_sold: ItemSoldEvent,
    EventType.item_transferred: ItemTransferredEvent,
    EventType.item_metadata_updated: ItemMetadataUpdatedEvent,
    EventType.item_cancelled: ItemCancelledEvent,
    EventType.item_received_offer: ItemReceivedOfferEvent,
    EventType.item_received_bid: ItemReceivedBidEvent,
}


class Message(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    topic: str
    event: EventType
    payload: Union[dict, ItemEvent] = {}
    ref: Optional[int]

    @model_validator(mode="after")
    def parse_payload(cls, values):
        Cls = MESSAGE_MAPPING.get(values["event"], None)
        if Cls is not None:
            Message._parse_payload(values, Cls)

        return values

    @staticmethod
    def _parse_payload(values, Cls):
        values["payload"] = Cls(**values["payload"]["payload"])
