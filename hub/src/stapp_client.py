from kubernetes import client, config
import os
import logging

logging.basicConfig(level=logging.INFO)

NAMESPACE_DEPLOYMENTS = os.getenv("NAMESPACE_DEPLOYMENTS")
STREAMLIT_SUFFIX = os.getenv("STREAMLIT_SUFFIX")
STREAMLIT_BASE_DNS = os.getenv("STREAMLIT_BASE_DNS")
GIT_SYNC_IMAGE = f"{os.getenv('GIT_SYNC_IMAGE_NAME')}:{os.getenv('GIT_SYNC_IMAGE_TAG')}"

class StappClient:
    def __init__(self):
        if os.getenv('ENVIRONMENT') == 'local':
            self.config = config.load_kube_config(config_file="~/.kube/config", context="proxy")
        else:
            self.config = config.load_incluster_config()
        self.api = client.CustomObjectsApi()
        self.v1 = client.CoreV1Api()

    def list_streamlit_apps(self):
        # List instances of the custom resource
        custom_resource_list = self.api.list_namespaced_custom_object(
            group="opticon.dev",
            version="v1",
            namespace=NAMESPACE_DEPLOYMENTS,
            plural="streamlit-apps"
        )

        outputs = []
        for item in custom_resource_list['items']:
            # Extrahiere relevante Felder aus der Spezifikation des Custom Resources
            spec = item.get('spec', {})
            name = spec.get('name', 'N/A')
            dns_name = spec.get('dns_name', 'N/A')
            repo = spec.get('repo', 'N/A')
            branch = spec.get('branch', 'N/A')
            code_dir = spec.get('code_dir', 'N/A')
            base_image = spec.get('base_image', 'N/A')
            git_sync_image = spec.get('git_sync_image', 'N/A')
            replicas = spec.get('replicas', 'N/A')
            cpu_limit = spec.get('cpu_limit', 'N/A')
            memory_limit = spec.get('memory_limit', 'N/A')

            # Füge die Felder zur Ausgabe hinzu
            outputs.append({
                "name": name,
                "dns_name": dns_name,
                "repo": repo,
                "branch": branch,
                "code_dir": code_dir,
                "base_image": base_image,
                "git_sync_image": git_sync_image,
                "replicas": replicas,
                "cpu_limit": cpu_limit,
                "memory_limit": memory_limit
            })

        return outputs

    def create_streamlit_app(self, name, dns_name, repo, branch, code_dir, base_image, replicas, cpu_limit, memory_limit):
        # Create the custom resource
        resp = self.api.create_namespaced_custom_object(
            group="opticon.dev",
            version="v1",
            namespace=NAMESPACE_DEPLOYMENTS,
            plural="streamlit-apps",
            body={
                "apiVersion": "opticon.dev/v1",
                "kind": "StreamlitApp",
                "metadata": {
                    "name": dns_name
                },
                "spec": {
                    "repo": repo,
                    "branch": branch,
                    "code_dir": code_dir,
                    "base_image": base_image,
                    "replicas": replicas,
                    "git_sync_image": GIT_SYNC_IMAGE,
                    "cpu_limit": cpu_limit,
                    "memory_limit": memory_limit,
                    "suffix": STREAMLIT_SUFFIX,
                    "base_dns": STREAMLIT_BASE_DNS,
                    "name": name,
                    "dns_name": dns_name
                }
            }
        )
        logging.info(f"Sent task creating app with data: {[dns_name, repo, branch, code_dir]} with response: {resp}")

    def delete_streamlit_app(self, dns_name):
        # Delete the custom resource
        self.api.delete_namespaced_custom_object(
            group="opticon.dev",
            version="v1",
            namespace=NAMESPACE_DEPLOYMENTS,
            plural="streamlit-apps",
            name=dns_name,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
            )
        )

    def delete_pod_for_streamlit_app(self, dns_name):
        # Find the pod for the custom resource
        pod_list = self.v1.list_namespaced_pod(
            namespace=NAMESPACE_DEPLOYMENTS,
            label_selector=f"app={dns_name}"
        )
        print(pod_list)
        # Delete the pod
        for item in pod_list.items:
            pod_name = item.metadata.name
            self.v1.delete_namespaced_pod(
                name=pod_name,
                namespace=NAMESPACE_DEPLOYMENTS,
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                )
            )
