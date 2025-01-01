import logging
from typing import Callable

from qscaler_sdk.brokers.brokers_factory import BrokersFactory
from qscaler_sdk.configuration.config import config
from qscaler_sdk.event_loop.event_loop import EventLoop
from qscaler_sdk.k8s.k8s_client import k8s_client
from qscaler_sdk.k8s.qworker import QWorker

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class Worker:

    def __init__(self):
        self.broker = BrokersFactory.get_broker(k8s_client.scaler_config.type)
        self.act = None
        self.extra_termination = None
        self.qworker = QWorker()

    @property
    def queue(self):
        self.qworker.update()
        return self.qworker.config.queue

    def run(self):
        logger.info("starting worker...")
        event_loop = EventLoop(check_for_death=self.should_i_die,
                               work=self.work,
                               graceful_shutdown=self.graceful_shutdown)
        event_loop()

    def work(self):
        logger.info("fetching work...")
        data = self.broker.get_message(self.queue)
        if data is None:
            return
        logger.info("doing work...")
        self.act(data)

    def graceful_shutdown(self):
        logger.info("starting graceful shutdown...")
        k8s_client.remove_owner_ref(config.pod_name)
        self.extra_termination()
        self.broker.close()

    def should_i_die(self):
        self.qworker.update()
        if self.qworker.status.desiredReplicas - self.qworker.status.currentReplicas < 0:
            logger.info("got diff in qworker config, starting graceful shutdown...")
            return True
        return False

    def task(self, func: Callable):
        def wrapper():
            if self.act is not None:
                raise NotImplementedError("worker supports a single task")
            self.act = func

        return wrapper

    def shutdown(self, func=None):
        def wrapper(*args, **kwargs):
            logger.info("starting graceful shutdown")
            if func is not None:
                self.extra_termination = func(*args, **kwargs)

        return wrapper
