# -*- coding: utf-8 -*-
import os

from loguru import logger

from openseapy import OpenSeaStream
from openseapy.utils import pformat

opensea = OpenSeaStream(
    os.environ.get("OS_API_KEY", None), test=True, log_level="DEBUG"
)


@opensea.event
async def on_reply(msg):
    logger.info(pformat(msg))


@opensea.event
async def on_item_listed(msg):
    logger.info(msg.payload.payment_token.address)
    logger.info(pformat(msg))


@opensea.event
async def on_item_cancelled(msg):
    logger.info(pformat(msg))


@opensea.event
async def on_item_transferred(msg):
    logger.info(pformat(msg))


@opensea.event
async def on_item_sold(msg):
    logger.info(pformat(msg))


@opensea.event
async def on_item_received_offer(msg):
    logger.info(pformat(msg))


@opensea.event
async def on_item_received_bid(msg):
    logger.info(pformat(msg))


def main():
    try:
        sub = True
        while True:
            # the name of the collection
            opensea.collection("genesisblockagents", sub=sub)
            sub = not sub
            input()
    except KeyboardInterrupt:
        opensea.worker.kill()


if __name__ == "__main__":
    main()
