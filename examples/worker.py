import logging
import time
from typing import Dict, Any

from qscaler.worker import Worker

worker = Worker()

@worker.shutdown
def shutdown():
    print("Shutting down worker...")


@worker.task
def example(task: Dict[str, Any]) -> Any:
    print("hello this s an example")
    time.sleep(5)


if __name__ == "__main__":
    logging.basicConfig()
    worker.run()
