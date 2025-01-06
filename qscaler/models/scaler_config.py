from typing import Optional, Union

from pydantic import BaseModel, Field, model_validator

from qscaler.k8s.k8s_client import K8sClient
from qscaler.models.qworker import QWorker
from qscaler.utils.singleton import SingletonMeta


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
    port: int = Field(..., description="Redis port number.")
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
    config: Union[RedisConfig, dict] = Field(..., description="Specific configuration for the scaler type.")

    @model_validator(mode="after")
    def parse_config(self):
        if self.type == "redis":
            if not isinstance(self.config, RedisConfig):
                self.config = RedisConfig(host=self.config['host'],
                                          port=self.config['port'],
                                          password=self.config['password'])
        else:
            raise NotImplementedError(f"Scaler type '{self.type}' is not implemented.")
        return self


class ScalerConfig(metaclass=SingletonMeta):

    def __init__(self):
        qworker = QWorker()
        self.name = qworker.config.scalerConfigRef
        self.k8s_client = K8sClient()
        self.crd = self.k8s_client.get_scaler_config(self.name)
        self._replace_secrets_with_values()

    @property
    def spec(self):
        return ScalerConfigSpec(type=self.crd['spec']['type'], config=self.crd['spec']['config'])

    def _replace_secrets_with_values(self):
        model = self.spec.config
        for field_name, _ in model.model_fields.items():
            field = getattr(model, field_name)
            if isinstance(field, ValueOrSecret) and (field.secret is not None):
                field.value = self.k8s_client.extract_secret_value(name=field.secret.name, key=field.secret.key)
                setattr(model, field_name, field)
                field.secret = None
        self.crd['spec']['config'] = model
