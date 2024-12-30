import logging

from kubernetes import client, config as cluster_config
from kubernetes.client.rest import ApiException
from pydantic import BaseModel

from qscaler_sdk.k8s.qworker import QWorker, ScaleConfig, QWorkerStatus
from qscaler_sdk.k8s.scaler_config import ScalerConfig, ScalerConfigConfig
from qscaler_sdk.utils.singleton import SingletonMeta

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

class K8sClient(metaclass=SingletonMeta):

    def __init__(self, api_group, api_version, namespace:str):
        cluster_config.load_incluster_config()
        self.api_group = api_group
        self.api_version = api_version
        self.namespace = namespace

    def get_qworker(self, name: str) -> QWorker:
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

    def get_scaler_config(self, name: str) -> ScalerConfig:
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
                                config=ScalerConfigConfig(**crd['spec']['config']))
        except ApiException as e:
            print(f"Error retrieving qworker CR: {e.status} - {e.reason}")

    def remove_owner_ref(self, name:str):
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=name, namespace=self.namespace)

        if not pod.metadata.owner_references:
            logger.info(f"Pod {name} has no owner references.")
            return

        body = {"metadata": {"ownerReferences": []}}
        response = v1.patch_namespaced_pod(name=name, namespace=self.namespace, body=body)
        logger.info(f"Removed owner references for pod {name}. Response: {response}")
