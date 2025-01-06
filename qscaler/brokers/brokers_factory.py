from enum import Enum
from typing import Optional

from qscaler.brokers.redis_broker import RedisBroker
from qscaler.configuration.config import config


class Brokers(Enum):
    REDIS = "redis"

class BrokersFactory:

    @staticmethod
    def get_broker(broker: Optional[str] = None):
        if broker is None:
            broker = config.broker.type
        if broker == Brokers.REDIS.value:
            return RedisBroker()
        else:
            raise NotImplementedError
