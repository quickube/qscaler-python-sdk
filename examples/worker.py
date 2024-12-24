from typing import Dict, Any

from qscaler_sdk.worker.worker import Worker

worker = Worker(queue="queue1")


@worker.shutdown
def shutdown():
    print("Shutting down worker...")


@worker.task
def example(task: Dict[str, Any]) -> Any:
    # IMPLEMENT ME
    # ---------------------------------
    param1 = task['param1']
    param2 = task['param2']
    result = param1 + param2
    # ---------------------------------
    return result


if __name__ == "__main__":
    worker.run()
