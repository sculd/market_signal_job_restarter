import argparse
import os, time
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), 'credential.json')
import util.logging as logging
import util.metric, util.k8s

_POD_NAME_PREFIX = 'market-realtime-move-report'

def run(subscription_id):
    while True:
        metric = util.metric.get_timeseries_value(subscription_id)
        if not metric:
            util.k8s.delete_pod(_POD_NAME_PREFIX)
        time.sleep(60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--subscription", action="store_true", help="forces run without waiting without observing the schedule.")
    args = parser.parse_args()

    run(args.subscription)

    logging.info('main routine is done.')
