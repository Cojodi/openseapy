# -*- coding: utf-8 -*-
import asyncio
from functools import wraps

import aiohttp
import httpx
from loguru import logger

from .exceptions import RateLimitError


async def linear_retry(self, make_coro):
    for i in range(1, 10000):
        coro = make_coro()
        await self._check_rate_limit()
        try:
            res = await coro
            break
        except (
            httpx.ConnectError,
            httpx.ReadError,
            aiohttp.client_exceptions.ClientOSError,
        ):
            retry_in = i * 0.25
            logger.debug(f"Failed request, retry in: {retry_in}")
            await asyncio.sleep(retry_in)

    return res


def get(response_model, key=None):
    ResponseModel = response_model

    def deco(f):
        @wraps(f)
        async def wrapper(self, *args, **kwargs):
            url_and_maybe_params = f(self, *args, **kwargs)
            # with params
            if len(url_and_maybe_params) == 2:
                url, params = url_and_maybe_params
                params.pop("self")
                params.pop("url")
                params = {k: v for k, v in params.items() if v is not None}
            # without params
            else:
                url, params = url_and_maybe_params, {}

            async with self._sema:
                async with httpx.AsyncClient():
                    res = await linear_retry(
                        self,
                        lambda: self.client.get(
                            url, params=params, headers=self._headers
                        ),
                    )

            res = res.json()
            if "success" in res and not res["success"]:
                return None

            if "Request was throttled" in res:
                raise RateLimitError()

            res = key(res)
            if isinstance(res, list):
                return [ResponseModel(**r) for r in res]

            return ResponseModel(**res)

        return wrapper

    return deco


# FIXME: broke atm
def post(response_model, key=None):
    def deco(f):
        @wraps(f)
        async def wrapper(self, *args, **kwargs):
            url, body = f(self, *args, **kwargs)

            async with self._sema:
                await self._check_rate_limit()
                res = await self.client.post(url, headers=self._headers)

            res = res.json()
            if "success" in res and not res["success"]:
                return None

            if "Request was throttled" in res:
                raise RateLimitError()

            # res = key(res)
            # return response_model(**res)

            return res

        return wrapper

    return deco
