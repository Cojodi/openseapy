# -*- coding: utf-8 -*-
from .api import OpenSeaAPI
from .stream import OpenSeaStream


class OpenSea:
    def __init__(
        self,
        api_key: str = "",
        max_parallel_requests: int = 3,
        requests_timeframe_seconds: int = 1,
        test: bool = False,
        stream: bool = False,
        log_level="ERROR",
    ):
        self.api = OpenSeaAPI(
            api_key, max_parallel_requests, requests_timeframe_seconds, test, log_level
        )

        if stream:
            print("stream")
            self.stream = OpenSeaStream(api_key, test, log_level)
