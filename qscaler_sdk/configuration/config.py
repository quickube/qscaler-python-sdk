import os
from dataclasses import field, dataclass


def _load_namespace_from_file():
    print("not mocked")
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError("Namespace file not found. Are you running in a Kubernetes cluster?")


@dataclass
class Config:
    qworker_name: str = field(default=os.getenv("QWORKER_NAME"))
    msg_timeout: int = field(default=os.getenv("MESSAGE_TIMEOUT", 10))
    pod_name: str = field(default=os.getenv("HOSTNAME"))
    namespace: str = field(default_factory=lambda: _load_namespace_from_file())
    k8s_api_version: str = field(default=os.getenv("K8S_API_VERSION", "v1alpha1"))


config = Config()
