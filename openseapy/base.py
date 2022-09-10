from loguru import logger

from . import utils


class OpenSeaBase:
    def __init__(self, api_key: str, test: bool, log_level: str):
        if test:
            self.api_key = ""
        else:
            assert api_key
            self.api_key = api_key

        self.log_level = log_level
        if log_level is not None:
            utils.init_logger(logger, log_level)
