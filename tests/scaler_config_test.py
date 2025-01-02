
from unittest.mock import patch
from qscaler_sdk.models.scaler_config import ScalerConfig, ScalerConfigSpec


def test_scaler_config_init():
    """Test initialization of ScalerConfig with mocked QWorker and K8sClient."""
    with patch("qscaler_sdk.models.qworker.QWorker") as MockQWorker, patch("qscaler_sdk.k8s.k8s_client.K8sClient") as MockK8sClient:
        # Mock QWorker
        mock_qworker = MockQWorker.return_value
        mock_qworker.config.scalerConfigRef = "test-scaler-config"

        # Mock K8sClient
        mock_k8s_client = MockK8sClient.return_value
        mock_k8s_client.get_scaler_config.return_value = {
            "spec": {
                "type": "Redis",
                "config": {
                    "redis": {
                        "host": "localhost",
                        "port": 6379,
                        "password": {"value": "test-password"}
                    }
                }
            }
        }

        mock_k8s_client.get_qworker.return_value = {
            ""
        }

        scaler_config = ScalerConfig()

        # Verify initialization
        assert scaler_config.name == "test-scaler-config"
        mock_k8s_client.get_scaler_config.assert_called_once_with("test-scaler-config")

def test_scaler_config_spec_property():
    """Test the spec property of ScalerConfig."""
    with patch("qscaler_sdk.models.QWorker"), patch("qscaler_sdk.k8s.k8s_client.K8sClient") as MockK8sClient:
        mock_k8s_client = MockK8sClient.return_value
        mock_k8s_client.get_scaler_config.return_value = {
            "spec": {
                "type": "Redis",
                "config": {
                    "redis": {
                        "host": "localhost",
                        "port": 6379,
                        "password": {"value": "test-password"}
                    }
                }
            }
        }

        scaler_config = ScalerConfig()

        # Validate the spec property
        spec = scaler_config.spec
        assert isinstance(spec, ScalerConfigSpec)
        assert spec.type == "Redis"
        assert spec.config.redis.host == "localhost"
        assert spec.config.redis.port == 6379
        assert spec.config.redis.password.value == "test-password"