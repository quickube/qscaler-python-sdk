import uuid
from typing import Any

from pkg.brokers.brokers_factory import BrokersFactory
from pkg.results_storage.results_storage_factory import ResultsStoragesFactory


class Client:
    def __init__(self):
        self.broker = BrokersFactory.get_broker()
        self.results_storage = ResultsStoragesFactory.get_storage()

    async def execute(self,queue: str, data: Any):
        task_id = uuid.uuid4().hex
        payload = {"task_id": task_id, "data": data}
        self.broker.publish(queue, payload)

        results = await self.results_storage.get_results(task_id)
        return results

    def is_alive(self) -> bool:
        broker_alive = self.broker.is_connected()
        storage_alive = self.results_storage.is_connected()
        return broker_alive and storage_alive
