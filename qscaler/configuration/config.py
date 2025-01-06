import os
from dataclasses import field, dataclass


@dataclass
class Config:
    qworker_name: str = field(default=os.getenv("QWORKER_NAME"))
    pulling_interval: int = field(default=os.getenv("PULLING_INTERVAL", 2))
    pod_name: str = field(default=os.getenv("HOSTNAME"))  # in K8s it is the name of the pod
    pod_spec_hash: str = field(default=os.getenv("POD_SPEC_HASH"))


config = Config()
