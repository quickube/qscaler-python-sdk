import os
from dataclasses import field, dataclass

from pydantic import BaseModel

from qscaler_sdk.k8s.k8s_client import K8sClient
from qscaler_sdk.k8s.qworker import QWorker
from qscaler_sdk.k8s.scaler_config import ScalerConfig, ValueOrSecret


def _load_namespace_from_file():
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError("Namespace file not found. Are you running in a Kubernetes cluster?")


@dataclass
class Config:
    qworker_name: str = field(default=os.getenv("QWORKER_NAME"))
    pod_name: str = field(default=os.getenv("HOSTNAME"))
    namespace: str = field(default_factory=lambda: _load_namespace_from_file())
    k8s_api_group: str = field(default=os.getenv("K8S_API_GROUP", "quickube.com"))
    k8s_api_version: str = field(default=os.getenv("K8S_API_VERSION", "v1alpha1"))

    @property
    def qworker(self) -> QWorker:
        return k8s_client.get_qworker(config.qworker_name)

    @property
    def scaler_config(self) -> ScalerConfig:
        scaler_config = k8s_client.get_scaler_config(self.qworker.config.scalerConfigRef)
        scaler_config.load_secrets()
        return scaler_config


config = Config()
k8s_client = K8sClient(api_group=config.k8s_api_group, api_version=config.k8s_api_version, namespace=config.namespace)
