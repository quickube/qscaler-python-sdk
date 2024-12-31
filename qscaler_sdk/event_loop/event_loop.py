import logging
import signal
from typing import Callable


class GracefulShutdown(Exception):
    pass

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

class EventLoop:
    def __init__(self, check_for_death: Callable, work: Callable, graceful_shutdown: Callable):
        self.check_for_death = check_for_death
        self.work = work
        self.graceful_shutdown = graceful_shutdown
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def __call__(self):
        try:
            while not self.check_for_death():
                self.work()
            self.exit_gracefully()
        except GracefulShutdown:
            self.graceful_shutdown()

    def exit_gracefully(self, *args, **kwargs):
        logger.info("got sigterm/sigint, starting shutdown process...")
        raise GracefulShutdown
