import os
from dataclasses import field, dataclass
from enum import Enum


class Brokers(Enum):
    REDIS = "redis"


@dataclass
class BrokerConfig:
    type: str = field(default=os.getenv("BROKER"))
    host: str = field(default=os.getenv("BROKER_HOST"))
    port: int = field(default_factory=lambda: int(os.getenv("BROKER_PORT", -1)))
    password: str = field(default=os.getenv("BROKER_PASSWORD"))
    db: str = field(default=os.getenv("BROKER_DB"))

    def __post_init__(self):
        if self.type == Brokers.REDIS.value:
            self._redis_validations()
        else:
            raise NotImplementedError(f"Invalid broker type entered: {self.type}")

    def _redis_validations(self):
        assert self.db is not None, "redis db must be entered"


@dataclass
class Config:
    broker: BrokerConfig = field(default_factory=lambda: BrokerConfig())


config = Config()
