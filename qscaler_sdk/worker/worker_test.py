import os


class TestWorker:

    def test_init_on_no_queue_name_should_try_fetching_from_env(self):
        # Arrange
        env_queue = "env_q"
        os.environ.setdefault("QUEUE_NAME", env_queue)
        # Act
        from qscaler_sdk.worker.worker import Worker

        worker = Worker()
        # Assert
        assert worker.queue == env_queue
