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

EventType = Literal[
    "cancel",
    "order",
    "sale",
    "transfer",
    "redemption",
]


class Client:
    async def get(self, url, params=None, headers=None, exclude_none: bool = False):
        async with httpx.AsyncClient(headers=headers) as client:
            if exclude_none:
                params = {k: v for k, v in params.items() if v is not None}

            return await client.get(url, params=params)

    async def post(
        self, url, params=None, data=None, headers=None, exclude_none: bool = False
    ):
        async with httpx.AsyncClient(headers=headers) as client:
            if exclude_none:
                params = {k: v for k, v in params.items() if v is not None}
                data = {k: v for k, v in data.items() if v is not None}

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
        coro = self.client.get(url, headers=self._headers)

        return await self._rate_limiter.limit(coro)

    async def collection_stats(self, slug: str):
        url = str(self.v2_url / "collections" / slug / "stats")
        coro = self.client.get(url, headers=self._headers)

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

    async def nft_events(
        self,
        *,
        contract_address: str,
        chain: Chain,
        token_id: str,
        after: int | None = None,
        before: int | None = None,
        event_type: list[EventType] | None = None,
        limit: int = 50,
        next: str | None = None,
    ):
        assert 1 <= limit <= 50, "limit exceeded"

        url = str(
            self.v2_url
            / "events"
            / "chain"
            / chain
            / "contract"
            / contract_address
            / "nfts"
            / token_id
        )

        params = {
            "after": after,
            "before": before,
            "event_type": event_type,
            "limit": limit,
            "next": next,
        }

        coro = self.client.get(
            url, params=params, headers=self._headers, exclude_none=True
        )
        return await self._rate_limiter.limit(coro)

    ################################################################################
    # V1
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

    ################################################################################
    # UTILS
    @property
    def _headers(self):
        headers = None
        if self.api_key:
            headers = {"X-API-KEY": self.api_key}

        return headers
