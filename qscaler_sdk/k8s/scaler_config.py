from typing import Optional

from pydantic import BaseModel, Field

from qscaler_sdk.k8s.k8s_client import K8sClient
from qscaler_sdk.k8s.qworker import QWorker


class Secret(BaseModel):
    """
    Represents a secret.
    """
    name: str = Field(..., description="Name of the secret.")
    key: str = Field(..., description="Key in the secret to reference.")


class ValueOrSecret(BaseModel):
    """
    Represents a value or a secret reference.
    """
    value: Optional[str] = Field(None, description="Plaintext value.")
    secret: Optional[Secret] = Field(None, description="Reference to a Kubernetes secret.")


class RedisConfig(BaseModel):
    """
    Represents the Redis configuration.
    """
    host: str = Field(..., description="Redis host address.")
    port: str = Field(..., description="Redis port number.")
    password: Optional[ValueOrSecret] = Field(None, description="Redis password as a value or secret.")


class ScalerTypeConfigs(BaseModel):
    """
    Represents different scaler type configurations.
    """
    redis: Optional[RedisConfig] = Field(None, description="Configuration for Redis scaler.")


class ScalerConfigSpec(BaseModel):
    """
    Represents the spec section of ScalerConfig.
    """
    type: str = Field(..., description="Type of scaler (e.g., Redis).")
    config: ScalerTypeConfigs = Field(..., description="Specific configuration for the scaler type.")


class ScalerConfig:

    def __init__(self):
        qworker = QWorker()
        self.name = qworker.config.scalerConfigRef
        self.k8s_client = K8sClient()
        self.crd = self.k8s_client.get_scaler_config(self.name)
        self._replace_secrets_with_values()

    @property
    def spec(self):
        return ScalerConfigSpec(**self.crd['spec'])

    def _replace_secrets_with_values(self):
        model = self.spec
        for field_name, _ in model.model_fields.items():
            field = getattr(model, field_name)
            if isinstance(field, ValueOrSecret) and (field.secret is not None):
                field.value = self.k8s_client.extract_secret_value(name=field.secret.name, key=field.secret.key)
                setattr(model, field_name, field)
                field.secret = None
        self.crd = model
