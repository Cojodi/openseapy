from typing import List

import httpx
from urlpath import URL

from .base import OpenSeaBase
from .utils.rate_limiter import FakeRateLimiter, RateLimiter


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
        self.v2_url = self.base_url / "v2"

        self.client = Client()
        self._rate_limiter = rate_limiter

    ################################################################################
    # API
    async def collection(self, slug: str):
        url = str(self.v1_url / "collection" / slug)
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
        coro = self.client.get(
            url,
            params=dict(
                owner=owner,
                token_ids=token_ids,
                collection=collection,
                collection_editor=collection_editor,
                order_direction=order_direction,
                asset_contract_address=asset_contract_address,
                asset_contract_addresses=asset_contract_addresses,
                limit=limit,
                cursor=cursor,
                include_orders=include_orders,
            ),
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
