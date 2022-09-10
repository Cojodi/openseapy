import datetime as dt
from typing import Optional

from pydantic import BaseModel

from .types import Address, FloatingPrice


################################################################################
# BASE
class Collection(BaseModel):
    slug: str


class User(BaseModel):
    address: Address


class Token(BaseModel):
    address: Address
    decimals: int
    name: Optional[str]
    symbol: str
    eth_price: FloatingPrice
    usd_price: FloatingPrice


class Chain(BaseModel):
    name: str


class Transaction(BaseModel):
    hash: str
    timestamp: dt.datetime


class ItemMetadata(BaseModel):
    animation_url: Optional[str]
    image_url: Optional[str]
    metadata_url: Optional[str]
    name: Optional[str]


class Item(BaseModel):
    chain: Chain
    metadata: ItemMetadata
    nft_id: str
    permalink: str

    @property
    def token_id(self):
        return self.nft_id.rsplit("/", 1)[-1]

    @property
    def token_address(self):
        return self.nft_id.rsplit("/", 2)[-2]
