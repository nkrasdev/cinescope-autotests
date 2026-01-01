from enum import Enum


class Timeout(Enum):
    ONE_SECOND = 1000
    FIVE_SECONDS = 5000
    TEN_SECONDS = 10000
    DEFAULT_TIMEOUT = 10000
