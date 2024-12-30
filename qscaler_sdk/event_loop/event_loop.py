import signal
from typing import Callable


class GracefulShutdown(Exception):
    pass


class EventLoop:
    def __init__(self, death_check: Callable, work: Callable, graceful_shutdown: Callable):
        self.death_check = death_check
        self.work = work
        self.graceful_shutdown = graceful_shutdown
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def __call__(self):
        try:
            while True:
                if self.death_check():
                    self.exit_gracefully()
                self.work()
        except GracefulShutdown:
            self.graceful_shutdown()

    def exit_gracefully(self, *args, **kwargs):
        raise GracefulShutdown
