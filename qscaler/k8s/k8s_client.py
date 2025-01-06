import logging
from base64 import b64decode
from typing import Any

from kubernetes import client, config as cluster_config
from kubernetes.client.rest import ApiException

from qscaler.utils.singleton import SingletonMeta

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class K8sClient(metaclass=SingletonMeta):

    def __init__(self):
        cluster_config.load_incluster_config()
        self.api_group = "quickube.com"
        self.api_version = "v1alpha1"
        self.namespace = self._load_namespace_from_file()

    @staticmethod
    def _load_namespace_from_file():
        try:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise RuntimeError("Namespace file not found. Are you running in a Kubernetes cluster?")

    def get_qworker(self, name: str) -> dict:
        api_instance = client.CustomObjectsApi()
        try:
            crd = api_instance.get_namespaced_custom_object(
                group=self.api_group,
                version=self.api_version,
                namespace=self.namespace,
                plural="qworkers",
                name=name
            )
            return crd
        except ApiException as e:
            logger.error(f"Error retrieving qworker CR: {e.status} - {e.reason}")
            raise e

    def get_scaler_config(self, name: str) -> dict:
        api_instance = client.CustomObjectsApi()
        try:
            crd = api_instance.get_namespaced_custom_object(
                group=self.api_group,
                version=self.api_version,
                namespace=self.namespace,
                plural="scalerconfigs",
                name=name
            )
            return crd
        except ApiException as e:
            logger.error(f"Error retrieving qworker CR: {e.status} - {e.reason}")
            raise e

    def remove_owner_ref(self, name: str):
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=name, namespace=self.namespace)

        if not pod.metadata.owner_references:
            logger.info(f"Pod {name} has no owner references.")
            return

        patch_body = {
            "metadata": {
                "ownerReferences": None
            }
        }
        v1.patch_namespaced_pod(name=name, namespace=self.namespace, body=patch_body)
        logger.info(f"Removed owner references for pod {name}")

    def extract_secret_value(self, name: str, key: str) -> Any:
        v1 = client.CoreV1Api()
        secret = v1.read_namespaced_secret(name=name, namespace=self.namespace)
        value = self._decode_secret(secret.data[key])
        return value

    def remove_pod(self, name: str):
        v1 = client.CoreV1Api()
        v1.delete_namespaced_pod(name=name, namespace=self.namespace)

    @staticmethod
    def _decode_secret(value: str):
        return b64decode(value).decode()