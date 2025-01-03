import os
import signal
import threading
import time

import pytest

from qscaler_sdk.event_loop.event_loop import EventLoop, ForceShutdown


class TestEventLoop:

    @pytest.mark.parametrize("actuall_signal", [signal.SIGTERM, signal.SIGINT])
    def test_force_shutdown_on_sigterm_sigint_signal_should_run_force_exit(self, mocker, actuall_signal):
        # Arrange
        mock_force_shutdown = mocker.Mock()
        event_loop = EventLoop(check_for_death= lambda: None,
                               work=lambda: None,
                               graceful_shutdown=lambda: None,
                               force_shutdown=mock_force_shutdown)

        def send_sigterm_later():
            # wait 2 seconds then send signal
            time.sleep(2)
            signal.raise_signal(actuall_signal)


        # Start the thread that will send SIGTERM after 10 seconds
        thread = threading.Thread(target=send_sigterm_later)
        thread.start()

        # Act
        event_loop()

        mock_force_shutdown.assert_called_once()
        assert not thread.is_alive()
