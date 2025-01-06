import logging
import pickle
from typing import Any, List, Optional

import redis

from qscaler.brokers.broker import Broker
from qscaler.configuration.config import config
from qscaler.models.scaler_config import ScalerConfig

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class RedisBroker(Broker):
    redis_client = None

    def __init__(self):
        """Initialize the Redis connection, but only once."""
        self.scaler_config = ScalerConfig()
        if self.redis_client is None:
            self.redis_client = redis.Redis(
                host=self.scaler_config.spec.config.host,
                port=self.scaler_config.spec.config.port,
                password=self.scaler_config.spec.config.password.value,
                # db=self.scaler_config.spec.config.db,  # missing in the go struct
            )

    def is_connected(self) -> bool:
        """Check if Redis is reachable."""
        return self.redis_client.ping()

    def _publish(self, queue: str, data: bytes):
        """Publish task to the given task queue."""
        self.redis_client.lpush(queue, data)

    def _get_message(self, queues: List[str]) -> Optional[bytes]:
        """get single message from the kill queue or the task queue"""
        val = self.redis_client.brpop(queues, timeout=config.pulling_interval)
        if val is None:
            logger.info("didn't find msg for {timeout} seconds, will try again")
            return None
        return val[1]

    def close(self):
        """Close the Redis connection."""
        self.redis_client.close()
        print("Closed Redis connection")

    def _serialize(self, data: Any) -> bytes:
        return pickle.dumps(data)

    def _deserialize(self, data: bytes) -> Any:
        return pickle.loads(data)
