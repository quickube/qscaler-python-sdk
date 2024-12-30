from typing import Optional

from pydantic import BaseModel

from qscaler_sdk.configuration.config import k8s_client


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

    def load_secrets(self):
        model = self.config
        for field_name, _ in model.__fields__.items():
            field = getattr(model, field_name)
            if isinstance(field, ValueOrSecret) and (field.value is None):
                secret_ref = field.valueFrom.secretKeyRef
                field.value = k8s_client.extract_secret_value(name=secret_ref.name, key=secret_ref.key)
                setattr(model, field_name, field)
        self.config = model
