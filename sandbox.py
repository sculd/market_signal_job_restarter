

import util.metric

print(util.metric.get_metric('market_bwt_stream'))
print(util.metric.get_timeseries_value('market_bwt_stream'))

import util.k8s
util.k8s.delete_pod('market-realtime-move-report')
