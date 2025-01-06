
import pytest

from qscaler.k8s.k8s_client import K8sClient
from qscaler.models.qworker import QWorker


@pytest.mark.incluster
class TestQworker:

    def test_init_on_fetching_crd_should_fetch_once(self, mocker):
        # Arrange
        client = K8sClient()
        crd_fetch_method = mocker.patch.object(client, "get_qworker", return_value={})
        # Act
        QWorker()
        # Assert
        crd_fetch_method.assert_called_once()

    def test_update_on_refreshing_crd_should_fetch_again(self, mocker):
        # Arrange
        client = K8sClient()
        first_crd = {}
        second_crd = {"second": True}
        mocker.patch.object(client, "get_qworker", return_value=first_crd)
        qworker = QWorker()
        # Act
        crd_fetch_method = mocker.patch.object(client, "get_qworker", return_value=second_crd)
        qworker.update()
        # Assert
        crd_fetch_method.assert_called_once()
        assert qworker.crd == second_crd