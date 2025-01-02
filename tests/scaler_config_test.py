import pytest

from qscaler_sdk.k8s.k8s_client import K8sClient
from qscaler_sdk.models.scaler_config import ScalerConfig


@pytest.mark.incluster
class TestScalerConfig:

    @pytest.fixture
    def fake_qworker_crd(self):
        return {
            'spec': {
                'scaleConfig': {
                    'scalerConfigRef': 'scaler-name',
                    'queue': 'fake-q',
                    'minReplicas': 1,
                    'maxReplicas': 2,
                    'scalingFactor': 1
                }
            }
        }

    def test_init_on_fetching_crd_should_fetch_once(self, mocker, fake_qworker_crd):
        client = K8sClient()
        # Arrange
        crd_fetch_method = mocker.patch.object(client, "get_scaler_config", return_value={}, autospec=True)
        mocker.patch.object(client, "get_qworker", return_value=fake_qworker_crd, autospec=True)
        mocker.patch("qscaler_sdk.models.scaler_config.ScalerConfig._replace_secrets_with_values", return_value=None,
                     autospec=True)
        # Act
        ScalerConfig()
        # Assert
        crd_fetch_method.assert_called_once()

    def test_init_on_filling_secret_values_should_fill_them_into_value_spot(self, mocker, fake_qworker_crd):
        client = K8sClient()
        # Arrange
        fake_crd = {
            "spec": {
                "type": "redis",
                "config": {
                    "host": "fake_host",
                    "port": 111,
                    "password": {
                        "secret": {
                            "name": "secret-name",
                            "key": "data"
                        }
                    }
                }
            }
        }

        def fake_secret_fetch(name: str, key: str):
            return {"secret-name": {"data": "actual-secret"}}[name][key]

        mocker.patch.object(client, "get_scaler_config", return_value=fake_crd, autospec=True)
        mocker.patch.object(client, "get_qworker", return_value=fake_qworker_crd, autospec=True)
        fetch_secret_method = mocker.patch.object(client, "extract_secret_value", side_effect=fake_secret_fetch,
                                                  autospec=True)
        # Act
        scaler_config = ScalerConfig()
        # Assert
        fetch_secret_method.assert_called_once()
        assert scaler_config.spec.config.password.value == "actual-secret"
