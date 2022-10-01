# -*- coding: utf-8 -*-
import pytest
from openseapy import OpenSea

# @pytest.mark.asyncio
# async def test_ratelimit():
#     os_ = OpenSea("<API_TOKEN>", test=False, log_level=None)

#     futs = [os_.api.collection("blockpass") for _ in range(100)]
#     res = await asyncio.gather(*futs)

#     assert len(res) == 100


@pytest.mark.asyncio
async def test_asset():
    os = OpenSea(test=True, log_level=None)

    res = await os.api.assets(
        owner="0x2066ab6Aa45120E5dB70aB618b58ae126B0cBe04", limit=1
    )
    print(res)
