import datetime as dt
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from .base import Token


################################################################################
# BASE
class AssetContract(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    address: str
    asset_contract_type: str
    chain_identifier: str
    created_date: dt.datetime
    name: str
    nft_version: Optional[str]
    opensea_version: Optional[str]
    owner: Optional[int]
    schema_name: str
    symbol: str
    total_supply: Optional[str]
    description: Optional[str]
    external_link: Optional[str]
    image_url: Optional[str]
    default_to_fiat: bool
    dev_buyer_fee_basis_points: int
    dev_seller_fee_basis_points: int
    only_proxied_transfers: bool
    opensea_buyer_fee_basis_points: int
    opensea_seller_fee_basis_points: int
    buyer_fee_basis_points: int
    seller_fee_basis_points: int
    payout_address: Optional[str]


class AssetStats(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    one_day_volume: float
    one_day_change: float
    one_day_sales: int
    one_day_average_price: float
    one_day_difference: float
    seven_day_volume: float
    seven_day_change: float
    seven_day_sales: int
    seven_day_average_price: float
    seven_day_difference: float
    thirty_day_volume: float
    thirty_day_change: float
    thirty_day_sales: int
    thirty_day_average_price: float
    thirty_day_difference: float
    total_volume: float
    total_sales: int
    total_supply: int
    count: int
    num_owners: int
    average_price: float
    num_reports: int
    market_cap: float
    floor_price: Optional[float]


class AssetFees(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    seller_fees: Dict[str, int]
    opensea_fees: Dict[str, int]


class PaymentToken(Token):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    image_url: Optional[str]
    eth_price: Optional[str]
    usd_price: Optional[str]


class CollectionBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # traits: Optional[List[dict]]
    banner_image_url: Optional[str]
    chat_url: Optional[str]
    created_date: dt.datetime
    default_to_fiat: bool
    description: Optional[str]
    dev_buyer_fee_basis_points: str
    dev_seller_fee_basis_points: str
    discord_url: Optional[str]
    display_data: dict
    external_url: Optional[str]
    featured: bool
    featured_image_url: Optional[str]
    hidden: bool
    safelist_request_status: str
    image_url: Optional[str]
    is_subject_to_whitelist: bool
    large_image_url: Optional[str]
    medium_username: Optional[str]
    name: Optional[str]
    only_proxied_transfers: bool
    opensea_buyer_fee_basis_points: Optional[str | float | int]
    opensea_seller_fee_basis_points: Optional[str | float | int]
    payout_address: Optional[str]
    require_email: bool
    short_description: Optional[str]
    slug: str
    telegram_url: Optional[str]
    twitter_username: Optional[str]
    instagram_username: Optional[str]
    wiki_url: Optional[str]
    is_nsfw: bool
    fees: AssetFees


class Collection_(CollectionBase):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    stats: AssetStats
    editors: List[str]
    payment_tokens: List[PaymentToken]
    primary_asset_contracts: List[AssetContract]


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    username: Optional[str]


class Owner(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user: Optional[User]
    profile_img_url: Optional[str]
    address: str
    config: Optional[str]


class SaleStats(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # TODO
    asset: dict


class Asset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    num_sales: int
    background_color: Optional[str]
    image_url: Optional[str]
    image_preview_url: Optional[str]
    image_thumbnail_url: Optional[str]
    image_original_url: Optional[str]
    animation_url: Optional[str]
    animation_original_url: Optional[str]
    name: Optional[str]
    description: Optional[str]
    external_link: Optional[str]
    asset_contract: AssetContract
    permalink: Optional[str]
    collection: CollectionBase
    decimals: Optional[int]
    token_metadata: Optional[str]
    seaport_sell_orders: Optional[Any]
    is_nsfw: bool
    owner: Optional[Owner]
    creator: Optional[Owner]
    traits: List[dict]
    last_sale: Optional[SaleStats]
    top_bid: Optional[float]
    listing_date: Optional[dt.datetime]
    transfer_fee: Optional[float]
    transfer_fee_payment_token: Optional[str]
    supports_wyvern: bool
    rarity_data: Optional[Any]
    token_id: str


################################################################################
# RESPONSES
class PaginatedResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    next: Optional[str]
    previous: Optional[str]


class Collections(PaginatedResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    collections: List[Collection_]


class Collection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    collection: Collection_


class Assets(PaginatedResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    assets: List[Asset]
