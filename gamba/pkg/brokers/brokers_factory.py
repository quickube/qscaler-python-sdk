from typing import Optional
from pkg.brokers.redis_broker import RedisBroker
from pkg.configuration.config import Brokers, config


class BrokersFactory:

    @staticmethod
    def get_broker(broker: Optional[str] = None):
        if broker is None:
            broker = config.broker.type
        if broker == Brokers.REDIS.value:
            return RedisBroker()
        else:
            raise NotImplementedError
