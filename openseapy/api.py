# -*- coding: utf-8 -*-
import asyncio
import time
from asyncio import Semaphore

from httpx import AsyncClient
from urlpath import URL

from .base import OpenSeaBase
from .helper import get
from .models.api import Collection


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

        self.client = AsyncClient()

        # rate limiting
        self._max_parallel_requests = max_parallel_requests
        self._requests_timeframe_seconds = requests_timeframe_seconds

        self._lock = Semaphore(max_parallel_requests)
        self._request_times = []

    ################################################################################
    # API
    @get(response_model=Collection, key=lambda res: res["collection"])
    def collection(self, slug: str):
        url = str(self.v1_url / "collection" / slug)
        return url

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
