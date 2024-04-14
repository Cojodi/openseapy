import asyncio
from functools import wraps

import httpx
from loguru import logger

from .exceptions import RateLimitError


async def paginate(f, *args, cursor_key="next", **kwargs):
    cursor = ""
    while cursor is not None:
        kwargs["cursor"] = cursor
        res = await f(*args, **kwargs)
        j = res.json()

        cursor = j.get(cursor_key, None)
        yield res

        if cursor is None:
            return


async def linear_retry(self, make_coro):
    for i in range(1, 10000):
        coro = make_coro()
        await self._check_rate_limit()
        try:
            res = await coro
            # TODO check for status_codes instead of items

            res = res.json()
            # DEBUG
            # logger.error(res)

            is_throttled = "detail" in res and "Request was throttled" in res["detail"]
            has_failed = "success" in res and not res["success"]
            if is_throttled:
                await asyncio.sleep(i * 0.25)
                continue

            return None if has_failed else res
        except (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadError,
            httpx.ReadTimeout,
        ):
            retry_in = i * 0.25
            logger.debug(f"Failed request, retry in: {retry_in}")
            await asyncio.sleep(retry_in)


def get(response_model):
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
                async with httpx.AsyncClient() as client:
                    res = await linear_retry(
                        self,
                        lambda: client.get(url, params=params, headers=self._headers),
                    )

            if res is None:
                return res

            try:
                return ResponseModel(**res)
            except Exception as e:
                logger.error(e)
                logger.exception(e)
                logger.error(res)
                raise e

        return wrapper

    return deco


# FIXME: broke atm
def post(response_model):
    def deco(f):
        @wraps(f)
        async def wrapper(self, *args, **kwargs):
            url, body = f(self, *args, **kwargs)

            async with self._sema:
                await self._check_rate_limit()
                res = await self.client.post(url, headers=self._headers)

            if "success" in res and not res["success"]:
                return None

            if "Request was throttled" in res:
                raise RateLimitError()

            # res = key(res)
            # return response_model(**res)

            return res

        return wrapper

    return deco
