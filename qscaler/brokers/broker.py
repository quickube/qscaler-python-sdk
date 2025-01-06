from abc import ABC
from abc import abstractmethod
from typing import Any, List, Optional

from qscaler.utils.singleton import SingletonMeta


class Broker(ABC, metaclass=SingletonMeta):

    def publish(self, queue: str, data: Any):
        serialized_data = self._serialize(data)
        self._publish(queue, serialized_data)

    def get_message(self, queues: List[str]) -> Optional[Any]:
        serialized_data = self._get_message(queues)
        if serialized_data is None:
            return None
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
