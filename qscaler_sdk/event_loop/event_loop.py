import logging
import signal
from typing import Callable, NoReturn, Union


class GracefulShutdown(Exception):
    pass

class ForceShutdown(Exception):
    pass


logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class EventLoop:
    """
    on sigint: force shutdown
    on sigterm: force shutdown
    on death_check: graceful shutdown
    """
    def __init__(self, check_for_death: Callable, work: Callable, graceful_shutdown: Callable, force_shutdown: Callable):
        self.check_for_death = check_for_death
        self.work = work
        self.graceful_shutdown = graceful_shutdown
        self.force_shutdown = force_shutdown
        signal.signal(signal.SIGINT, self.force_exit)
        signal.signal(signal.SIGTERM, self.force_exit)

    def __call__(self):
        try:
            while not self.exit_gracefully():
                self.work()
        except GracefulShutdown:
            self.graceful_shutdown()
        except ForceShutdown:
            self.force_shutdown()


    @staticmethod
    def force_exit(*args, **kwargs) -> NoReturn:
        logger.info("got sigterm/sigint, starting force shutdown process...")
        raise ForceShutdown

    def exit_gracefully(self, *args, **kwargs) -> Union[bool, NoReturn]:
        """
        checks whether pod should die and exit gracefully
        """
        if self.check_for_death():
            logger.info("got signal to die after finishing work, starting graceful shutdown process...")
            raise GracefulShutdown
        return False
