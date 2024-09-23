import kopf
import kubernetes

from src.templating import template_deployment, template_service, template_ingress
import yaml
import logging


global config


logging.basicConfig(level=logging.INFO)
logging.info("Init Operator")

@kopf.on.create('streamlit-apps')
def create_fn(spec, name, namespace, logger, **kwargs):
    logging.info("Creating App")
    # Get params from spec
    repo = spec.get('repo', None)
    branch = spec.get('branch', None)
    code_dir = spec.get('code_dir', None)
    base_image = spec.get('base_image', None)
    git_sync_image = spec.get("git_sync_image", None)
    replicas = spec.get('replicas', None)
    memory_limit = spec.get('memory_limit', None)
    cpu_limit = spec.get('cpu_limit', None)
    base_dns = spec.get('base_dns', None)
    suffix = spec.get('suffix', None)
    dns_name = spec.get("dns_name", None)

    if not repo:
        raise kopf.PermanentError(f"Repo must be set. Got {repo!r}.")
    if not branch:
        raise kopf.PermanentError(f"Branch must be set. Got {branch!r}.")
    if not code_dir:
        raise kopf.PermanentError(f"Code directory must be set. Got {code_dir!r}.")

    # Template the deployment
    deployment_data = template_deployment(namespace=namespace,
                                          dns_name=dns_name,
                                          repo=repo,
                                          branch=branch,
                                          code_dir=code_dir,
                                          base_image=base_image,
                                          git_sync_image=git_sync_image,
                                          replicas=replicas,
                                          cpu_limit=cpu_limit,
                                          memory_limit=memory_limit,
                                          suffix=suffix,
                                          base_dns=base_dns)
    kopf.adopt(deployment_data)

    # Template the service
    service_data = template_service(namespace, dns_name)
    kopf.adopt(service_data)

    # Template the ingress
    ingress_data = template_ingress(namespace, dns_name, base_dns, {}, suffix)
    kopf.adopt(ingress_data)

    api = kubernetes.client.CoreV1Api()
    apps_api = kubernetes.client.AppsV1Api()
    networking_api = kubernetes.client.NetworkingV1Api()
    # Create the deployment
    deployment_obj = apps_api.create_namespaced_deployment(
        namespace=namespace,
        body=deployment_data,
    )


    # Create the service
    service_obj = api.create_namespaced_service(
        namespace=namespace,
        body=service_data,
    )

    # Create the ingress
    ingress_obj = networking_api.create_namespaced_ingress(
        namespace=namespace,
        body=ingress_data,
    )

    return {
        'ingress-name': ingress_obj.metadata.name,
        'service-name': service_obj.metadata.name,
        'deployment-name': deployment_obj.metadata.name
    }
