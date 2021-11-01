import os, time
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')

import google.cloud.monitoring_v3
import google.cloud.monitoring_v3.query as query
from google.cloud.monitoring_v3 import Aggregation

_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
_METRIC_TYPE = 'pubsub.googleapis.com/subscription/ack_message_count'
_API_ENDPOINT = 'monitoring.googleapis.com'

_client = None
def _get_client():
    global _client
    if _client is None:
        _client = google.cloud.monitoring_v3.MetricServiceClient(client_options={'api_endpoint': _API_ENDPOINT})
    return _client

def get_metric(subscription_id, minutes=5, delivery_type = 'pull'):
    client = _get_client()

    q = query.Query(
        client,
        _PROJECT_ID,
        metric_type=_METRIC_TYPE,
        end_time=None,
        days=0,
        hours=0,
        minutes=minutes)

    df = q. \
        align(Aggregation.Aligner.ALIGN_SUM, minutes=5). \
        as_dataframe()
    if len(df) == 0:
        return 0
    df_ = df.unstack().reset_index()
    df__ = df_[df_.subscription_id == subscription_id][df_.delivery_type == delivery_type][['level_4', 0]].set_index('level_4')

    if len(df__) == 0:
        return 0
    r = df__.iloc[-1]
    if len(r.values) == 0:
        return 0
    v = r.values[0]
    return int(v)

def get_timeseries_value(subscription_id, minutes=5, delivery_type = 'pull'):
    project_name = "projects/{p}".format(p=_PROJECT_ID)
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = google.cloud.monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": (seconds - 60 * minutes), "nanos": nanos},
        }
    )
    aggregation = google.cloud.monitoring_v3.Aggregation(
        {
            "alignment_period": {"seconds": 60 * 1},
            "per_series_aligner": google.cloud.monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
        }
    )
    results = _get_client().list_time_series(
        request={
            "name": project_name,
            "filter": 'metric.type = "{t}" AND resource.label.subscription_id = "{subscription_id}" AND metric.label.delivery_type = "{delivery_type}"'.format(
                t=_METRIC_TYPE, subscription_id=subscription_id, delivery_type=delivery_type),
            "interval": interval,
            "view": google.cloud.monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            "aggregation": aggregation,
        }
    )
    point_value = None
    for result in results:
        for point in result.points:
            if point.value.double_value:
                point_value = point.value.double_value
    return point_value
