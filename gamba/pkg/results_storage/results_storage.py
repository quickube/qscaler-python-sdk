import asyncio
from abc import ABC, abstractmethod
from typing import Any

from pkg.utils.singleton import SingletonMeta


class ResultsStorage(ABC, metaclass=SingletonMeta):

    def set(self, key: str, value: Any):
        serialized_data = self._serialize(value)
        self._set(key, serialized_data)

    def get(self, key: str) -> Any:
        data = self._get(key)
        if data:
            return self._deserialize(data)
        return None

    async def get_results(self, task_id: str):
        results = None
        while results is None:
            await asyncio.sleep(2)
            results = self.get(task_id)
        self.delete(task_id)
        return results

    @abstractmethod
    def _set(self, key: str, value: Any):
        pass

    @abstractmethod
    def _get(self, key: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, key: str):
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def _serialize(self, data: Any) -> bytes:
        pass

    @abstractmethod
    def _deserialize(self, data: bytes) -> Any:
        pass
