import logging
import pickle
from typing import Any, List, Optional

import redis

from qscaler_sdk.brokers.broker import Broker
from qscaler_sdk.configuration.config import config


logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

class RedisBroker(Broker):
    redis_client = None

    def __init__(self):
        """Initialize the Redis connection, but only once."""
        if self.redis_client is None:
            self.redis_client = redis.Redis(
                host=config.scaler_config.config.host,
                port=config.scaler_config.config.port,
                password=config.scaler_config.config.password.value,
                db=config.scaler_config.config.db,
            )

    def is_connected(self) -> bool:
        """Check if Redis is reachable."""
        return self.redis_client.ping()

    def _publish(self, queue: str, data: bytes):
        """Publish task to the given task queue."""
        self.redis_client.lpush(queue, data)

    def _get_message(self, queues: List[str]) -> Optional[bytes]:
        """get single message from the kill queue or the task queue"""
        val = self.redis_client.brpop(queues, timeout=10)
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
