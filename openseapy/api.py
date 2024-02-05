from typing import List, Literal

import httpx
from urlpath import URL

from .base import OpenSeaBase
from .utils.rate_limiter import FakeRateLimiter, RateLimiter

Chain = Literal[
    "arbitrum",
    "arbitrum_goerli",
    "arbitrum_nova",
    "avalanche",
    "avalanche_fuji",
    "baobab",
    "base",
    "base_goerli",
    "bsc",
    "bsctestnet",
    "ethereum",
    "goerli",
    "klaytn",
    "matic",
    "mumbai",
    "optimism",
    "optimism_goerli",
    "sepolia",
    "solana",
    "soldev",
    "zora",
    "zora_testnet",
]


class Client:
    async def get(self, url, params=None, headers=None):
        async with httpx.AsyncClient(headers=headers) as client:
            return await client.get(url, params=params)

    async def post(self, url, params=None, data=None, headers=None):
        async with httpx.AsyncClient(headers=headers) as client:
            return await client.get(url, params=params, data=data)


class OpenSeaAPI(OpenSeaBase):
    def __init__(
        self,
        api_key: str,
        test: bool,
        log_level: str,
        rate_limiter: RateLimiter = FakeRateLimiter(),
    ):
        super().__init__(api_key, test, log_level)

        testnet = "testnets-" if test else ""
        self.base_url = URL(f"https://{testnet}api.opensea.io")
        self.v1_url = self.base_url / "api/v1"
        self.v2_url = self.base_url / "api/v2"

        self.client = Client()
        self._rate_limiter = rate_limiter

    ################################################################################
    # API
    async def collection(self, slug: str):
        url = str(self.v2_url / "collections" / slug)
        coro = self.client.get(
            url,
            headers=self._headers,
        )

        return await self._rate_limiter.limit(coro)

    async def assets(
        self,
        *,
        owner: str | None = None,
        token_ids: List[str] | None = None,
        collection: str | None = None,
        collection_editor: str | None = None,
        order_direction: str = "desc",
        asset_contract_address: str | None = None,
        asset_contract_addresses: List[str] | None = None,
        limit: int = 30,
        cursor: str | None = None,
        include_orders: bool = True,
    ):
        """https://docs.opensea.io/reference/getting-assets"""
        url = str(self.v1_url / "assets")
        params = {
            "owner": owner,
            "token_ids": token_ids,
            "collection": collection,
            "collection_editor": collection_editor,
            "order_direction": order_direction,
            "asset_contract_address": asset_contract_address,
            "asset_contract_addresses": asset_contract_addresses,
            "limit": limit,
            "cursor": cursor,
            "include_orders": include_orders,
        }
        params = {k: v for k, v in params.items() if v is not None}
        coro = self.client.get(
            url,
            params=params,
            headers=self._headers,
        )

        return await self._rate_limiter.limit(coro)

    async def nft(self, *, contract_address: str, chain: Chain, token_id: str):
        url = str(
            self.v2_url
            / "chain"
            / chain
            / "contract"
            / contract_address
            / "nfts"
            / token_id
        )
        coro = self.client.get(url, headers=self._headers)
        return await self._rate_limiter.limit(coro)

    ################################################################################
    # UTILS
    @property
    def _headers(self):
        headers = None
        if self.api_key:
            headers = {"X-API-KEY": self.api_key}

        return headers
