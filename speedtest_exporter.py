#!/usr/bin/env python3

from prometheus_client import start_http_server, Gauge
from threading import Thread
import subprocess
import argparse
import json
import time


# Arguments
parser = argparse.ArgumentParser(description='Prometheus exporter for network speedtests.')
parser.add_argument('--web.listen-address', action='store', dest='listen_addr', help='Specify host and port to display metrics for scraping.')
parser.add_argument('--server_id', action='store', dest='server_id', help='Specify server by ID to perform speedtests on.')
parser.add_argument('--bind_ip', action='store', dest='bind_ip', help='Bind to specific source IP address to run speedtests from.')
parser.add_argument('--interval', action='store', dest='interval', help='Set interval in seconds on how often data should be updated.')


# Attributes
speedtest_cmd = 'speedtest-cli --json --bytes'
metrics_set = False
metrics = {
    'speedtest_ping': Gauge('speedtest_ping', 'Current ping time in milliseconds.'),
    'speedtest_download': Gauge('speedtest_download', 'Current network download speed in bytes/sec.'),
    'speedtest_upload': Gauge('speedtest_upload', 'Current network upload speed in bytes/sec.')
}


def update_metrics():
    global metrics, metrics_set
    output = subprocess.Popen(speedtest_cmd.split(' '), stdout=subprocess.PIPE)
    # stdout, stderr
    raw_json, _ = output.communicate()
    data = json.loads(raw_json)

    sponsor = data['server']['sponsor']
    host = data['server']['host']
    metrics['speedtest_ping'].set(data['ping'])
    metrics['speedtest_download'].set(data['download'])
    metrics['speedtest_upload'].set(data['upload'])
    metrics_set = True


def metrics_updater(_interval):
    while True:
        update_metrics()
        time.sleep(_interval)


# Main
if __name__ == '__main__':
    # Handle arguments
    interval = 10
    options = parser.parse_args()
    if options.server_id:
        speedtest_cmd += ' --server {}'.format(options.server_id)
    if options.bind_ip:
        speedtest_cmd += ' --source {}'.format(options.bind_ip)
    if options.interval:
        interval = int(options.interval)

    # Run tests
    print('INFO: Performing test speedtest before running metrics updater...')
    try:
        subprocess.Popen(speedtest_cmd.split(' '), shell=True, stdout=subprocess.PIPE)
    except:
        print('ERROR: Invalid server id or IP to bind to!')
        exit()
    print('INFO: Tests complete!')
    
    # Start metrics updater
    Thread(target=metrics_updater, args=(interval, )).start()

    # Wait till initial metrics are set
    print('INFO: Waiting for initial metrics to be set...')
    while not metrics_set:
        time.sleep(1)
    print('INFO: Initial metrics are set! Proceeding to start HTTP service...')

    # Start HTTP server
    try:
        if options.listen_addr:
            if len(options.listen_addr.split(':')) == 2:
                ip = options.listen_addr.split(':')[0]
                port = int(options.listen_addr.split(':')[-1])
                print('INFO: Listening on {}:{}...'.format(ip, port))
                start_http_server(port, addr=ip)
            else:
                print('ERROR: Invalid web.listen_address value! Must have IP and port separated by : !')
                exit()
        else:
            print('INFO: Listening on {}:{}...'.format('0.0.0.0', 9100))
            start_http_server(9100, addr='0.0.0.0')
    except:
        print('ERROR: Invalid IP for web.listen_address flag!')
        exit()
