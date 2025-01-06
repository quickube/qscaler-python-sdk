from pydantic import BaseModel

from qscaler.configuration.config import config
from qscaler.k8s.k8s_client import K8sClient
from qscaler.utils.singleton import SingletonMeta


class ScaleConfig(BaseModel):
    queue: str
    minReplicas: int
    maxReplicas: int
    scalerConfigRef: str
    scalingFactor: int
    activateVPA: bool


class QWorkerStatus(BaseModel):
    currentReplicas: int
    desiredReplicas: int
    currentPodSpecHash: str


class QWorker(metaclass=SingletonMeta):

    def __init__(self):
        self.name = config.qworker_name
        self.k8s_client = K8sClient()
        self.crd = self.k8s_client.get_qworker(self.name)

    @property
    def status(self) -> QWorkerStatus:
        return QWorkerStatus(**self.crd['status'])

    @property
    def config(self) -> ScaleConfig:
        return ScaleConfig(**self.crd['spec']['scaleConfig'])

    def update(self):
        self.crd = self.k8s_client.get_qworker(self.name)