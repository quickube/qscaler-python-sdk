import logging
from base64 import b64decode
from typing import Any

from kubernetes import client, config as cluster_config
from kubernetes.client.rest import ApiException

from qscaler_sdk.configuration.config import config
from qscaler_sdk.k8s.qworker import QWorker, ScaleConfig, QWorkerStatus
from qscaler_sdk.k8s.scaler_config import ScalerConfig, ScalerConfigConfig
from qscaler_sdk.utils.singleton import SingletonMeta

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class K8sClient(metaclass=SingletonMeta):

    def __init__(self, namespace: str, api_version: str, api_group: str = "quikcube.com"):
        cluster_config.load_incluster_config()
        self.api_group = api_group
        self.api_version = api_version
        self.namespace = namespace

    @property
    def qworker(self):
        return self._get_qworker(config.qworker.name)

    @property
    def scaler_config(self) -> ScalerConfig:
        scaler_config = self._get_scaler_config(self.qworker.config.scalerConfigRef)
        scaler_config.load_secrets()
        return scaler_config

    def _get_qworker(self, name: str) -> QWorker:
        api_instance = client.CustomObjectsApi()
        try:
            crd = api_instance.get_namespaced_custom_object(
                group=self.api_group,
                version=self.api_version,
                namespace=self.namespace,
                plural="qworkers",
                name=name
            )
            return QWorker(name=name, config=ScaleConfig(**crd['spec']['scaleConfig']),
                           status=QWorkerStatus(**crd['status']))
        except ApiException as e:
            print(f"Error retrieving qworker CR: {e.status} - {e.reason}")

    def _get_scaler_config(self, name: str) -> ScalerConfig:
        api_instance = client.CustomObjectsApi()
        try:
            crd = api_instance.get_namespaced_custom_object(
                group=self.api_group,
                version=self.api_version,
                namespace=self.namespace,
                plural="scalerconfigs",
                name=name
            )
            return ScalerConfig(name=name,
                                type=crd['spec']['type'],
                                config=ScalerConfigConfig(**crd['spec']['config']),
                                k8s_client=self)
        except ApiException as e:
            print(f"Error retrieving qworker CR: {e.status} - {e.reason}")

    def remove_owner_ref(self, name: str):
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=name, namespace=self.namespace)

        if not pod.metadata.owner_references:
            logger.info(f"Pod {name} has no owner references.")
            return

        body = {"metadata": {"ownerReferences": []}}
        response = v1.patch_namespaced_pod(name=name, namespace=self.namespace, body=body)
        logger.info(f"Removed owner references for pod {name}. Response: {response}")

    def extract_secret_value(self, name: str, key: str) -> Any:
        v1 = client.CoreV1Api()
        secret = v1.read_namespaced_secret(name=name, namespace=self.namespace)
        value = self._decode_secret(secret.data[key])
        return value

    @staticmethod
    def _decode_secret(value: str):
        return b64decode(value).decode()


k8s_client = K8sClient(api_version=config.k8s_api_version, namespace=config.namespace)
