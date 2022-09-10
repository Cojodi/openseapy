# -*- coding: utf-8 -*-
import datetime as dt
from typing import Dict, List, Optional

from pydantic import BaseModel

from .base import Token
from .types import Address


################################################################################
# BASE
class AssetContract(BaseModel):
    address: Address
    asset_contract_type: str
    created_date: dt.datetime
    name: str
    nft_version: str
    opensea_version: Optional[str]
    owner: int
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
    payout_address: Optional[Address]



class AssetStats(BaseModel):
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
    seller_fees: Dict[Address, int]
    opensea_fees: Dict[Address, int]


class PaymentToken(Token):
    id: int
    image_url: Optional[str]
    eth_price: Optional[float]
    usd_price: Optional[float]


class Collection(BaseModel):
    editors: List[Address]
    payment_tokens: List[PaymentToken]
    primary_asset_contracts: List[AssetContract]
    traits: dict
    stats: AssetStats
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
    opensea_buyer_fee_basis_points: str
    opensea_seller_fee_basis_points: str
    payout_address: Optional[Address]
    require_email: bool
    short_description: Optional[str]
    slug: str
    telegram_url: Optional[str]
    twitter_username: Optional[str]
    instagram_username: Optional[str]
    wiki_url: Optional[str]
    is_nsfw: bool
    fees: AssetFees
