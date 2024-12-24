import time
from typing import Dict, Any

from qscaler_sdk.worker.worker import Worker

worker = Worker(queue_name="queue1")

@worker.shutdown
def shutdown():
    print("Shutting down worker...")


@worker.task
def example(task: Dict[str, Any]) -> Any:
    time.sleep(5)


if __name__ == "__main__":
    worker.run()
