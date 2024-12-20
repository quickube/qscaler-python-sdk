import pickle
from typing import Any

import redis

from pkg.configuration.config import config
from pkg.results_storage.results_storage import ResultsStorage


class RedisResultsStorage(ResultsStorage):
    redis_client = None

    def __init__(self):
        """Initialize the Redis client, but only once."""
        if self.redis_client is None:
            # Only initialize if it's the first time
            self.redis_client = redis.Redis(
                host=config.storage.host,
                port=config.storage.port,
                password=config.storage.password,
                db=config.storage.db
            )

        self.is_connected()
    def is_connected(self) -> bool:
        """Check if Redis is reachable."""
        return self.redis_client.ping()

    def _get(self, key: str) -> bytes:
        """Get the value from Redis."""
        response = self.redis_client.get(key)
        return response

    def _set(self, key: str, value: bytes):
        """Set a value in Redis."""
        self.redis_client.set(name=key, value=value)

    def delete(self, key: str):
        """Delete a key in Redis."""
        self.redis_client.delete(key)

    def _serialize(self, data: Any) -> bytes:
        return pickle.dumps(data)

    def _deserialize(self, data: bytes) -> Any:
        return pickle.loads(data)
