# -*- coding: utf-8 -*-
import asyncio

import pytest
from openseapy import OpenSea


# @pytest.mark.asyncio
# async def test_ratelimit():
#     os_ = OpenSea("<API_TOKEN>", test=False, log_level=None)

#     futs = [os_.api.collection("blockpass") for _ in range(100)]
#     res = await asyncio.gather(*futs)

#     assert len(res) == 100
