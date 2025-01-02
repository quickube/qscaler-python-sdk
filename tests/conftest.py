import os

import pytest

from qscaler_sdk.k8s.k8s_client import K8sClient
from qscaler_sdk.models.qworker import QWorker
from qscaler_sdk.models.scaler_config import ScalerConfig


@pytest.fixture(autouse=True)
def mock_incluster_environment(request, mocker):
    if "incluster" in request.keywords:
        os.environ.setdefault("QWORKER_NAME", "fake-qworker")
        os.environ.setdefault("HOSTNAME", "localhost")
        mocker.patch("qscaler_sdk.k8s.k8s_client.K8sClient._load_namespace_from_file", return_value="fake")
        mocker.patch("qscaler_sdk.k8s.k8s_client.cluster_config.load_incluster_config", return_value=None)



@pytest.fixture(autouse=True)
def setup_method():
    # Reset shared state
    ScalerConfig._instances = {}
    QWorker._instances = {}
    K8sClient._instances = {}
