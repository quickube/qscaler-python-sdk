import pytest
from kubernetes.client import CustomObjectsApi, CoreV1Api
from kubernetes.client.rest import ApiException
from kubernetes.client.models.v1_secret import V1Secret
from qscaler_sdk.k8s.k8s_client import K8sClient


@pytest.mark.incluster
class TestK8sClient:

    @pytest.fixture
    def fake_client(self):
        return K8sClient()

    def test_get_qworker_on_non_existing_qworker_should_raise_api_exception(self, mocker, fake_client: K8sClient):
        # Arrange
        def fake_get_namespaced(*args, **kwargs):
            raise ApiException()

        mocker.patch.object(CustomObjectsApi, "get_namespaced_custom_object", side_effect=fake_get_namespaced,
                            autospec=True)
        # Act
        with pytest.raises(ApiException):
            # Assert
            fake_client.get_qworker("fake-qworker")

    def test_get_scaler_config_on_non_existing_scaler_config_should_raise_api_exception(self, mocker,
                                                                                        fake_client: K8sClient):
        # Arrange
        def fake_get_namespaced(*args, **kwargs):
            raise ApiException()

        mocker.patch.object(CustomObjectsApi, "get_namespaced_custom_object", side_effect=fake_get_namespaced,
                            autospec=True)
        # Act
        with pytest.raises(ApiException):
            # Assert
            fake_client.get_scaler_config("fake-scaler-config")

    def test_extract_secret_value_on_b64_decoding_should_decode_secret_value(self, mocker, fake_client: K8sClient):
        # Arrange
        decoded_secret = "Aa123456"
        encoded_secret = "QWExMjM0NTY="
        secret_key = "key"
        fake_secret = V1Secret(data={secret_key: encoded_secret})
        mocker.patch.object(CoreV1Api, "read_namespaced_secret", return_value=fake_secret, autospec=True)

        # Act
        secret_value = fake_client.extract_secret_value(name="secret", key=secret_key)
        # Assert
        assert secret_value == decoded_secret
