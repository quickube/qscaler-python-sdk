import logging
from typing import Callable

from qscaler.brokers.brokers_factory import BrokersFactory
from qscaler.configuration.config import config
from qscaler.event_loop.event_loop import EventLoop
from qscaler.k8s.k8s_client import K8sClient
from qscaler.models.qworker import QWorker
from qscaler.models.scaler_config import ScalerConfig

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
        self.current_task = None

    @property
    def queue(self):
        self.qworker.update()
        return self.qworker.config.queue

    def run(self):
        """
        graceful shutdown: removing owner ref and starting graceful shutdown
        force shutdown: publishing task back to queue and closing broker
        """
        logger.info("starting worker...")
        event_loop = EventLoop(check_for_death=self.should_i_die,
                               work=self.work,
                               graceful_shutdown=self.graceful_shutdown,
                               force_shutdown=self.force_shutdown)
        event_loop()

    def work(self):
        logger.info("fetching work...")
        self.current_task = self.broker.get_message(self.queue)
        if self.current_task:
            logger.info("doing work...")
            self.act(self.current_task)
            self.current_task = None

    def force_shutdown(self):
        logger.info("starting force shutdown...")
        self.broker.publish(queue=self.queue, data=self.current_task)
        self.broker.close()

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
