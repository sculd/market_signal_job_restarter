import os
from kubernetes import client

_PODS_NAME_PREFIX = "market-realtime-move-report"

import google.auth
from google.auth.transport import requests


def get_token():
    # getting the credentials and project details for gcp project
    credentials, your_project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])

    # getting request object
    auth_req = google.auth.transport.requests.Request()

    credentials.refresh(auth_req)  # refresh token
    # cehck for valid credentials
    return credentials.token


def delete_pods():
    print('delete_pods')
    print(get_token())

    configuration = client.Configuration()
    configuration.host = "https://{ip}:443".format(ip=os.getenv('k8_cluster_ip'))
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + get_token()}
    client.Configuration.set_default(configuration)

    v1 = client.CoreV1Api()
    print("Listing pods:")
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