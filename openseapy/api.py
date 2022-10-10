# -*- coding: utf-8 -*-
import asyncio
import time
from asyncio import Semaphore
from typing import List

from urlpath import URL

from .base import OpenSeaBase
from .helper import get
from .models.api import Assets, Collection


class OpenSeaAPI(OpenSeaBase):
    def __init__(
        self,
        api_key: str,
        max_parallel_requests: int,
        requests_timeframe_seconds: int,
        test: bool,
        log_level: str,
    ):
        super().__init__(api_key, test, log_level)

        testnet = "testnets-" if test else ""
        self.base_url = URL(f"https://{testnet}api.opensea.io")
        self.v1_url = self.base_url / "api/v1"
        self.v2_url = self.base_url / "v2"

        # rate limiting
        self._max_parallel_requests = max_parallel_requests
        self._requests_timeframe_seconds = requests_timeframe_seconds

        self._sema = Semaphore(max_parallel_requests)
        self._request_times = []

    ################################################################################
    # API
    @get(response_model=Collection)
    def collection(self, slug: str):
        url = str(self.v1_url / "collection" / slug)
        return url

    @get(response_model=Assets)
    def assets(
        self,
        *,
        owner: str = None,
        token_ids: List[str] = None,
        collection: str = None,
        collection_editor: str = None,
        order_direction: str = "desc",
        asset_contract_address: str = None,
        asset_contract_addresses: List[str] = None,
        limit: int = 30,
        cursor: str = None,
        include_orders: bool = True,
    ):
        """https://docs.opensea.io/reference/getting-assets"""
        url = str(self.v1_url / "assets")

        return url, locals()

    ################################################################################
    # UTILS
    @property
    def _headers(self):
        headers = None
        if self.api_key:
            headers = {"X-API-KEY": self.api_key}

        return headers

    async def _check_rate_limit(self):
        now = time.perf_counter()
        if len(self._request_times) == self._max_parallel_requests:
            first = self._request_times[0]
            timeframe = now - first
            if timeframe < self._requests_timeframe_seconds:
                await asyncio.sleep(self._requests_timeframe_seconds - timeframe)

            self._request_times = self._request_times[1:] + [time.perf_counter()]
        else:
            self._request_times.append(now)
