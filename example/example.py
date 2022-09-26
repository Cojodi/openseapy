# -*- coding: utf-8 -*-
import asyncio

import aioconsole
from loguru import logger
from openseapy import OpenSea
from openseapy.utils import pformat

opensea = OpenSea(
    api_key="<API_KEY>",
    max_parallel_requests=3,  # 3 requests / requests_timeframe_seconds
    requests_timeframe_seconds=1,
    test=True,
    stream=True,
    log_level=None,  # use logging settings from app
)


@opensea.stream.event
async def on_reply(msg):
    logger.info(pformat(msg))


@opensea.stream.event
async def on_item_listed(msg):
    logger.info(msg.payload.payment_token.address)
    logger.info(pformat(msg))


@opensea.stream.event
async def on_item_cancelled(msg):
    logger.info(pformat(msg))


@opensea.stream.event
async def on_item_transferred(msg):
    logger.info(pformat(msg))


@opensea.stream.event
async def on_item_sold(msg):
    logger.info(pformat(msg))


@opensea.stream.event
async def on_item_received_offer(msg):
    logger.info(pformat(msg))


@opensea.stream.event
async def on_item_received_bid(msg):
    logger.info(pformat(msg))


async def amain():
    # initialize the stream tasks
    asyncio.create_task(opensea.stream.start())

    try:
        sub = True
        while True:
            # the name of the collection
            await opensea.stream.collection("*", sub=sub)
            # or
            # await opensea.stream.collection("<slug>", sub=sub)
            sub = not sub
            await aioconsole.ainput()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(amain())
    loop.run_forever()
