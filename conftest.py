import os

import pytest

from qscaler.k8s.k8s_client import K8sClient
from qscaler.models.qworker import QWorker
from qscaler.models.scaler_config import ScalerConfig


@pytest.fixture(autouse=True)
def mock_incluster_environment(request, mocker):
    if "incluster" in request.keywords:
        os.environ.setdefault("QWORKER_NAME", "fake-qworker")
        os.environ.setdefault("HOSTNAME", "localhost")
        mocker.patch("qscaler.k8s.k8s_client.K8sClient._load_namespace", return_value="fake")
        mocker.patch("qscaler.k8s.k8s_client.cluster_config.load_config", return_value=None)


@pytest.fixture(autouse=True)
def setup_method():
    # Reset shared state
    ScalerConfig._instances = {}
    QWorker._instances = {}
    K8sClient._instances = {}
