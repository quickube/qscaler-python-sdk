from unittest.mock import patch

from qscaler_sdk.models.qworker import QWorker


def test_qworker_init():
    """Test initialization of QWorker with mocked config and K8sClient."""
    with patch("qscaler_sdk.configuration.config") as MockConfig, patch("qscaler_sdk.k8s.k8s_client.K8sClient") as MockK8sClient:
        # Mock config and K8sClient
        mock_config = MockConfig.return_value
        mock_config.qworker_name = "test-qworker"

        mock_k8s_client = MockK8sClient.return_value
        mock_k8s_client.get_qworker.return_value = {
            "status": {
                "currentReplicas": 2,
                "desiredReplicas": 3,
                "currentPodSpecHash": "test-hash"
            },
            "spec": {
                "scaleConfig": {
                    "queue": "test-queue",
                    "minReplicas": 1,
                    "maxReplicas": 5,
                    "scalerConfigRef": "test-scaler-config",
                    "scalingFactor": 2
                }
            }
        }

        qworker = QWorker()

        # Verify initialization
        assert qworker.name == "test-qworker"
        mock_k8s_client.get_qworker.assert_called_once_with("test-qworker")


def test_qworker_status_property():
    """Test the status property of QWorker."""
    with patch("qscaler_sdk.configuration.config"), patch("qscaler_sdk.k8s.k8s_client.K8sClient") as MockK8sClient:
        mock_k8s_client = MockK8sClient.return_value
        mock_k8s_client.get_qworker.return_value = {
            "status": {
                "currentReplicas": 2,
                "desiredReplicas": 3,
                "currentPodSpecHash": "test-hash"
            }
        }

        qworker = QWorker()

        # Validate the status property
        status = qworker.status
        assert status.currentReplicas == 2
        assert status.desiredReplicas == 3
        assert status.currentPodSpecHash == "test-hash"


def test_qworker_config_property():
    """Test the config property of QWorker."""
    with patch("qscaler_sdk.configuration.config"), patch("qscaler_sdk.k8s.k8s_client.K8sClient") as MockK8sClient:
        mock_k8s_client = MockK8sClient.return_value
        mock_k8s_client.get_qworker.return_value = {
            "spec": {
                "scaleConfig": {
                    "queue": "test-queue",
                    "minReplicas": 1,
                    "maxReplicas": 5,
                    "scalerConfigRef": "test-scaler-config",
                    "scalingFactor": 2
                }
            }
        }

        qworker = QWorker()

        # Validate the config property
        config = qworker.config
        assert config.queue == "test-queue"
        assert config.minReplicas == 1
        assert config.maxReplicas == 5
        assert config.scalerConfigRef == "test-scaler-config"
        assert config.scalingFactor == 2


def test_qworker_update():
    """Test the update method of QWorker."""
    with patch("qscaler_sdk.configuration.config"), patch("qscaler_sdk.k8s.k8s_client.K8sClient") as MockK8sClient:
        mock_k8s_client = MockK8sClient.return_value
        mock_k8s_client.get_qworker.side_effect = [
            {
                "status": {"currentReplicas": 2},
                "spec": {"scaleConfig": {"queue": "test-queue"}}
            },
            {
                "status": {"currentReplicas": 3},
                "spec": {"scaleConfig": {"queue": "updated-queue"}}
            }
        ]

        qworker = QWorker()
        assert qworker.status.currentReplicas == 2
        assert qworker.config.queue == "test-queue"

        qworker.update()
        assert qworker.status.currentReplicas == 3
        assert qworker.config.queue == "updated-queue"