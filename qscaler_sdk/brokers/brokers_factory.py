from typing import Optional

from qscaler_sdk.brokers.redis_broker import RedisBroker
from qscaler_sdk.configuration.config import config, Brokers


class BrokersFactory:

    @staticmethod
    def get_broker(broker: Optional[str] = None):
        if broker is None:
            broker = config.broker.type
        if broker == Brokers.REDIS.value:
            return RedisBroker()
        else:
            raise NotImplementedError
