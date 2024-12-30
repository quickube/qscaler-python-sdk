from abc import ABC
from abc import abstractmethod
from typing import Any, List

from qscaler_sdk.utils.singleton import SingletonMeta)


class Broker(ABC, metaclass=SingletonMeta):

    def publish(self, queue: str, data: Any):
        serialized_data = self._serialize(data)
        self._publish(queue, serialized_data)

    def get_message(self, queues: List[str]) -> Any:
        serialized_data = self._get_message(queues)
        return self._deserialize(serialized_data)

    @abstractmethod
    def _publish(self, queue: str, data: bytes):
        pass

    @abstractmethod
    def _get_message(self, queues: List[str]) -> bytes:
        pass

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def _serialize(self, data: Any) -> bytes:
        pass

    @abstractmethod
    def _deserialize(self, data: bytes) -> Any:
        pass
