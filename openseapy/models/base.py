import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .types import Address, FloatingPrice


################################################################################
# BASE
class Collection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    slug: str


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    address: Address


class Token(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    address: Address
    decimals: int
    name: Optional[str]
    symbol: str
    eth_price: FloatingPrice
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
