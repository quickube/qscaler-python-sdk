import pytest

from unittest.mock import MagicMock, patch
from kubernetes.client.rest import ApiException
from qscaler_sdk.k8s.k8s_client import K8sClient


def test_get_qworker_exception():
    """Test get_qworker method when an ApiException occurs."""
    with patch("kubernetes.client.CustomObjectsApi") as MockCustomObjectsApi:
        mock_api = MockCustomObjectsApi.return_value
        mock_api.get_namespaced_custom_object.side_effect = ApiException(status=404, reason="Not Found")

        client = K8sClient()
        client.namespace = "test-namespace"

        with pytest.raises(ApiException):
            client.get_qworker("test-name")


def test_extract_secret_value():
    """Test the extract_secret_value method."""
    with patch("kubernetes.client.CoreV1Api") as MockCoreV1Api:
        mock_api = MockCoreV1Api.return_value
        mock_api.read_namespaced_secret.return_value = MagicMock(data={"key": "dGVzdC12YWx1ZQ=="})

        client = K8sClient()
        client.namespace = "test-namespace"

        result = client.extract_secret_value("test-secret", "key")

        mock_api.read_namespaced_secret.assert_called_once_with(name="test-secret", namespace="test-namespace")
        assert result == "test-value"


def test_remove_owner_ref():
    """Test the remove_owner_ref method."""
    with patch("kubernetes.client.CoreV1Api") as MockCoreV1Api:
        mock_api = MockCoreV1Api.return_value
        mock_api.read_namespaced_pod.return_value = MagicMock(metadata=MagicMock(owner_references=[]))

        client = K8sClient()
        client.namespace = "test-namespace"

        client.remove_owner_ref("test-pod")

        mock_api.read_namespaced_pod.assert_called_once_with(name="test-pod", namespace="test-namespace")
        mock_api.patch_namespaced_pod.assert_not_called()


def test_remove_owner_ref_with_owner():
    """Test the remove_owner_ref method with existing owner references."""
    with patch("kubernetes.client.CoreV1Api") as MockCoreV1Api:
        mock_api = MockCoreV1Api.return_value
        mock_api.read_namespaced_pod.return_value = MagicMock(metadata=MagicMock(owner_references=["owner"]))

        client = K8sClient()
        client.namespace = "test-namespace"

        client.remove_owner_ref("test-pod")

        mock_api.read_namespaced_pod.assert_called_once_with(name="test-pod", namespace="test-namespace")
        mock_api.patch_namespaced_pod.assert_called_once_with(
            name="test-pod", namespace="test-namespace", body={"metadata": {"ownerReferences": []}}
        )
