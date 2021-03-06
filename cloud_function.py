import os
from kubernetes import client

_PODS_NAME_PREFIX = os.getenv("POD_NAME_PREFIX")
_K8_CLUSTER_IP = os.getenv("K8_CLUSTER_IP")

import google.auth
from google.auth.transport import requests


def get_token():
    # getting the credentials and project details for gcp project
    credentials, your_project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    print('[get_token] your_project_id:', your_project_id)

    # getting request object
    auth_req = google.auth.transport.requests.Request()

    credentials.refresh(auth_req)  # refresh token
    # cehck for valid credentials
    return credentials.token


def delete_pods():
    print('[delete_pods]')
    print('[delete_pods] get_token:', get_token())

    configuration = client.Configuration()
    configuration.host = "https://{ip}:443".format(ip=_K8_CLUSTER_IP)
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + get_token()}
    client.Configuration.set_default(configuration)

    v1 = client.CoreV1Api()
    print("[delete_pods] Listing pods:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s" % (i.metadata.namespace, i.metadata.name))
        if _PODS_NAME_PREFIX in i.metadata.name:
            print('delete {n}'.format(n=i.metadata.name))
            v1.delete_namespaced_pod(i.metadata.name, i.metadata.namespace)


def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    print(event)
    delete_pods()

def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    print('request_json:', request_json)
    delete_pods()
    return 'delete_pods'
