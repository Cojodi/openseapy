import asyncio as aio
from abc import ABC, abstractmethod


class RateLimiter(ABC):
    @abstractmethod
    async def limit(self, coro):
        ...


class FakeRateLimiter(RateLimiter):
    async def limit(self, coro):
        return await coro


class AsyncioRateLimiter(RateLimiter):
    def __init__(self, semaphore_value, sleep_time=0):
        self.sema = aio.Semaphore(semaphore_value)
        self.sleep_time = sleep_time

    async def limit(self, coro):
        async with self.sema:
            res = await coro
            await aio.sleep(self.sleep_time)

        return res


class AsyncRedisRateLimiter(RateLimiter):
    def __init__(self, redis, semaphore_value, redis_namespace, sleep_time=0):
        from aioredis_semaphore import Semaphore

        self.sema = Semaphore(redis, semaphore_value, redis_namespace)
        self.sleep_time = sleep_time

    async def limit(self, coro):
        async with self.sema:
            res = await coro
            await aio.sleep(self.sleep_time)

        return res
