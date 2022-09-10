# -*- coding: utf-8 -*-
from .exceptions import RateLimitError


def get(response_model, key=None):
    def deco(f):
        async def wrapper(self, *args, **kwargs):
            url = f(self, *args, **kwargs)

            async with self._lock:
                await self._check_rate_limit()
                res = await self.client.get(url, headers=self._headers)

            res = res.json()
            if "success" in res and not res["success"]:
                return None

            if "Request was throttled" in res:
                raise RateLimitError()

            res = key(res)
            return response_model(**res)

        return wrapper

    return deco
