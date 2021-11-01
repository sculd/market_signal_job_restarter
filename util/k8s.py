from kubernetes import client, config
from util.command import run_command

def get_pod_name_and_namespace(pod_name_prefix):
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        if pod_name_prefix in i.metadata.name:
            return i.metadata.name, i.metadata.namespace
    return '', ''

def _delete_pod_with_exact_name(pod_name, namespace):
    run_command(['kubectl', 'delete', 'pod', pod_name, '-n', namespace])

def delete_pod(pod_name_prefix):
    pod_name, namespace = get_pod_name_and_namespace(pod_name_prefix)
    print('pod_name: {pod_name}, namespace: {namespace}'.format(pod_name=pod_name, namespace=namespace))
    _delete_pod_with_exact_name(pod_name, namespace)
