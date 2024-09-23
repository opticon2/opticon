import os

import yaml


def template_deployment(namespace, dns_name, repo, branch, code_dir, base_image, git_sync_image, replicas=1, cpu_limit="500m", memory_limit="1000Mi", suffix="opticon", base_dns="mini.kube"):
    deployment_dict = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": f"{dns_name}",
            "namespace": f"{namespace}",
            "labels": {
                "app": f"{dns_name}"
            }
        },
        "spec": {
            "replicas": int(replicas),
            "selector": {
                "matchLabels": {
                    "app": f"{dns_name}"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": f"{dns_name}"
                    }
                },
                "spec": {
                    "serviceAccountName": "opticon-serviceaccount",
                    "containers": [
                        {
                            "name": "git-sync",
                            "image": f"{git_sync_image}",
                            "volumeMounts": [
                                {
                                    "name": "code",
                                    "mountPath": "/tmp/code"
                                }
                            ],
                            "env": [
                                {"name": "GIT_SYNC_REPO", "value": f"{repo}"},
                                {"name": "GIT_SYNC_BRANCH", "value": f"{branch}"},
                                {"name": "GIT_SYNC_ROOT", "value": "/tmp/code"},
                                {"name": "GIT_SYNC_DEST", "value": "repo"},
                                {"name": "GIT_KNOWN_HOSTS", "value": "false"},
                                {"name": "GIT_SYNC_WAIT", "value": "60"}
                            ]
                        },
                        {
                            "name": "streamlit",
                            "image": f"{base_image}",
                            "env": [
                                {"name": "IN_HUB", "value": "True"},
                                {"name": "CODE_DIR", "value": f"repo/{code_dir}"},
                                {"name": "ENTRYPOINT", "value": "main.py"},
                                {"name": "KEYCLOAK_CLIENT_ID", "valueFrom":
                                    {"configMapKeyRef":{"name": "auth-config", "key": "KEYCLOAK_CLIENT_ID"}}},
                                {"name": "KEYCLOAK_CLIENT_SECRET", "valueFrom":
                                    {"configMapKeyRef": {"name": "auth-config", "key": "KEYCLOAK_CLIENT_SECRET"}}},
                                {"name": "KEYCLOAK_AUTHORITY", "valueFrom":
                                    {"configMapKeyRef": {"name": "auth-config", "key": "KEYCLOAK_AUTHORITY"}}},
                                {"name": "KEYCLOAK_REDIRECT_URI", "value": f"http://{suffix}-{dns_name}.{base_dns}"},
                                {"name": "KEYCLOAK_REDIRECT_URI_TLS", "value": f"https://{suffix}-{dns_name}.{base_dns}"},
                            ],
                            "command": ["/app/launch/launch.sh"],
                            "ports": [{"containerPort": 80}],
                            "volumeMounts": [
                                {"name": "code", "mountPath": "/app"},
                                {"name": "launch", "mountPath": "/app/launch"}
                            ],
                            "resources": {
                                "limits": {
                                    "cpu": cpu_limit,
                                    "memory": memory_limit
                                }
                            }
                        }
                    ],
                    "volumes": [
                        {"name": "code", "emptyDir": {}},
                        {
                            "name": "launch",
                            "configMap": {
                                "name": "streamlit-launch-script",
                                "defaultMode": 0o500
                            }
                        }
                    ]
                }
            }
        }
    }
    return deployment_dict


def template_service(namespace, dns_name):
    service_dict = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": f"{dns_name}",
            "namespace": f"{namespace}"
        },
        "spec": {
            "ports": [
                {
                    "port": 80,
                    "targetPort": 80,
                    "protocol": "TCP"
                }
            ],
            "type": "ClusterIP",
            "selector": {
                "app": f"{dns_name}"
            }
        }
    }
    return service_dict


def template_ingress(namespace, dns_name, base_dns_path, ingress_annotations, suffix):
    dns_url = f"{suffix}-{dns_name}.{base_dns_path}"
    ingress_annotations = ingress_annotations or {}
    ingress_dict = {

        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": f"{dns_name}",
            "namespace": f"{namespace}"
        },
        "spec": {
            "rules": [
                {
                    "host": dns_url,
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": f"{dns_name}",
                                        "port": {
                                            "number": 80
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
    return ingress_dict
