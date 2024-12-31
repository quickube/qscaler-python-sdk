from typing import Optional

from pydantic import BaseModel


class Secret(BaseModel):
    name: str
    key: str


class ValueOrSecret(BaseModel):
    value: Optional[str] = None
    secret: Optional[Secret] = None


class ScalerConfigConfig(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    password: Optional[ValueOrSecret] = None
    db: Optional[str] = None


class ScalerConfig:

    def __init__(self, name: str, type: str, config: ScalerConfigConfig, k8s_client):
        self.name = name
        self.type = type
        self.config = config
        self.client = k8s_client

    def load_secrets(self):
        model = self.config
        for field_name, _ in model.model_fields.items():
            field = getattr(model, field_name)
            if isinstance(field, ValueOrSecret) and (field.value is None):
                field.value = self.client.extract_secret_value(name=field.secret.name, key=field.secret.key)
                setattr(model, field_name, field)
        self.config = model
