class BaseError(Exception):
    def __str__(self):
        return type(self).__name__


class RateLimitError(BaseError):
    pass
