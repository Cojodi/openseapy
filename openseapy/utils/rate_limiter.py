import asyncio as aio
from abc import ABC, abstractmethod

from aioredis_semaphore import Semaphore


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
        self.redis_namespace = redis_namespace
        self.redis = redis
        self.sleep_time = sleep_time

        self.sema = Semaphore(redis, semaphore_value, redis_namespace)

    async def release(self):
        _, keys = await self.redis.scan()
        for key in keys:
            key = key.decode()
            if self.redis_namespace in key:
                await self.redis.delete(key)

    async def limit(self, coro):
        async with self.sema:
            res = await coro
            await aio.sleep(self.sleep_time)

        return res
