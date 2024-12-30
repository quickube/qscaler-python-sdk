from typing import Optional

from pydantic import BaseModel



class SecretKeyRef(BaseModel):
    name: str
    key: str


class ValueFrom(BaseModel):
    secretKeyRef: SecretKeyRef


class ValueOrSecret(BaseModel):
    value: Optional[str] = None
    valueFrom: Optional[ValueFrom] = None


class ScalerConfigConfig(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    password: Optional[ValueOrSecret] = None
    db: Optional[str] = None


class ScalerConfig:

    def __init__(self, name: str, type: str, config: ScalerConfigConfig):
        self.name = name
        self.type = type
        self.config = config
