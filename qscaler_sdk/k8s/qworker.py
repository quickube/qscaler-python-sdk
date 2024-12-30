from pydantic import BaseModel


class ScaleConfig(BaseModel):
    queue: str
    minReplicas: int
    maxReplicas: int
    scalerConfigRef: str
    scalingFactor: int


class QWorkerStatus(BaseModel):
    currentReplicas: int
    desiredReplicas: int

    @property
    def diff(self) -> int:
        return self.desiredReplicas - self.currentReplicas


class QWorker:

    def __init__(self, name: str, config: ScaleConfig, status: QWorkerStatus):
        self.name = name
        self.config = config
        self.status = status
