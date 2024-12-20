import logging
import uuid
from typing import Callable

from attr import dataclass

from pkg.brokers.brokers_factory import BrokersFactory
from pkg.configuration.config import config
from pkg.results_storage.results_storage_factory import ResultsStoragesFactory

from pkg.event_loop.event_loop import EventLoop, GracefulShutdown

logger = logging.getLogger(__name__)

class Worker:

    def __init__(self, queue: str):
        self.broker = BrokersFactory.get_broker(config.broker.type)
        self.results_storage = ResultsStoragesFactory.get_storage(config.storage.type)
        self.queue = queue
        self.act = None
        self.extra_termination = None

    @property
    def kill_queue(self):
        return f"kill_{self.queue}"

    def task(self, func: Callable):
        def wrapper():
            if self.act is not None:
                raise NotImplementedError("worker can support a single task")
            self.act = func
        return wrapper

    def shutdown(self, func=None):
        def wrapper(*args, **kwargs):
            logger.info("starting graceful shutdown")
            if func is not None:
                self.extra_termination = func(*args, **kwargs)

        return wrapper

    def graceful_shutdown(self):
        self.extra_termination()
        self.broker.close()

    def run(self):
        logger.info("starting worker")
        event_loop = EventLoop(self._work, self.graceful_shutdown)
        event_loop()

    def _work(self):
        queue, data = self.broker.get_message([self.kill_queue, self.queue])
        if queue == self.kill_queue:
            raise GracefulShutdown
        task_id = data['task_id']
        results = self.act(data['data'])
        self.results_storage.set(task_id, results)


