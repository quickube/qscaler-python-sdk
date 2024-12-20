import signal


class GracefulShutdown(Exception):
    pass


class EventLoop:
    def __init__(self, func, exit_function):
        self.exit_function = exit_function
        self.func = func
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def __call__(self, *args, **kwargs):
        try:
            while True:
                self.func(*args, **kwargs)
        except GracefulShutdown:
            self.exit_function()

    def exit_gracefully(self, signum, frame):
        raise GracefulShutdown
