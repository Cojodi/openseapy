from .api import OpenSeaAPI
from .stream import OpenSeaStream
from .utils.rate_limiter import FakeRateLimiter, RateLimiter


class OpenSea:
    def __init__(
        self,
        api_key: str = "",
        test: bool = False,
        stream: bool = False,
        log_level="ERROR",
        rate_limiter: RateLimiter = FakeRateLimiter(),
    ):
        self.api = OpenSeaAPI(api_key, test, log_level, rate_limiter)
        if stream:
            self.stream = OpenSeaStream(api_key, test, log_level)
