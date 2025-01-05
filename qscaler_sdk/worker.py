import logging
from typing import Callable

from qscaler_sdk.brokers.brokers_factory import BrokersFactory
from qscaler_sdk.configuration.config import config
from qscaler_sdk.event_loop.event_loop import EventLoop
from qscaler_sdk.k8s.k8s_client import K8sClient
from qscaler_sdk.models.qworker import QWorker
from qscaler_sdk.models.scaler_config import ScalerConfig

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class Worker:

    def __init__(self):
        self.act = None
        self.extra_termination = lambda: None
        self.qworker = QWorker()
        self.scaler_config = ScalerConfig()
        self.broker = BrokersFactory.get_broker(self.scaler_config.spec.type)
        self.k8s_client = K8sClient()

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
        self.k8s_client.remove_owner_ref(config.pod_name)
        self.extra_termination()
        self.broker.close()
        self.k8s_client.remove_pod(config.pod_name)

    def should_i_die(self):
        self.qworker.update()

        pod_hash_changed = config.pod_spec_hash != self.qworker.status.currentPodSpecHash
        desired_pod_count = self.qworker.status.desiredReplicas - self.qworker.status.currentReplicas
        if desired_pod_count < 0 or pod_hash_changed:
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
