#!/usr/bin/env python3

from prometheus_client import start_http_server, Gauge
from threading import Thread
import subprocess
import argparse
import json


# Arguments
parser = argparse.ArgumentParser(description='Prometheus exporter for network speedtests.')
parser.add_argument('--web.listen-address', action='store', dest='listen_addr', help='Specify host and port to display metrics for scraping.')
parser.add_argument('--server_id', action='store', dest='server_id', help='Specify server by ID to perform speedtests on.')
parser.add_argument('--bind_ip', action='store', dest='bind_ip', help='Bind to specific source IP address to run speedtests from.')


# Attributes
speedtest_cmd = 'speedtest-cli --json'
metrics = {
    'speedtest_ping': Gauge('speedtest_ping', 'Current ping time in milliseconds.', ['sponsor', 'host']),
    'speedtest_download': Gauge('speedtest_download', 'Current network download speed in bytes per second.', ['sponsor', 'host']),
    'speedtest_upload': Gauge('speedtest_upload', 'Current network upload speed in bytes per second.', ['sponsor', 'host'])
}


def mbit_to_bytes(_value):
    # Convert Mbit to bit
    _value *= 1000000

    # Bit to bytes
    _value *= 0.125

    return _value


def update_metrics():
    output = subprocess.Popen(speedtest_cmd.split(' '), shell=True, stdout=subprocess.PIPE)
    # stdout, stderr
    raw_json, _ = output.communicate()
    data = json.loads(raw_json)

    sponsor = data['sponsor']
    host = data['host']
    metrics['speedtest_ping'].labels(sponsor=sponsor, host=host).set(data['latency'])
    metrics['speedtest_download'].labels(sponsor=sponsor, host=host).set(mbit_to_bytes(data['download']))
    metrics['speedtest_upload'].labels(sponsor=sponsor, host=host).set(mbit_to_bytes(data['upload']))


def metrics_updater(_interval):
    while True:
        update_metrics()
        time.sleep(_interval)


# Main
if __name__ == '__main__':
    # Handle arguments
    if parser.server_id:
        speedtest_cmd += ' --server {}'.format(parser.server_id)
    if parser.bind_ip:
        speedtest_cmd += ' --source {}'.format(parser.bind_ip)

    # Run tests
    print('Performing test speedtest before running metrics updater...')
    try:
        subprocess.Popen(speedtest_cmd.split(' '), shell=True, stdout=subprocess.PIPE)
    except:
        print('ERROR: Invalid server id or IP to bind to!')
        exit()
    
    # Start metrics updater
    Thread(target=update_metrics).start()

    # Start HTTP server
    try:
        if parser.listen_addr:
            if len(parser.listen_addr.split(':')) == 2:
                ip = parser.listen_addr.split(':')[0]
                port = int(parser.listen_addr.split(':')[-1])
                print('INFO: Listening on {}:{}...'.format(ip, port))
                start_http_server(ip, addr=port)
            else:
                print('ERROR: Invalid web.listen_address value! Must have IP and port separated by : !')
                exit()
        else:
            print('INFO: Listening on {}:{}...'.format('0.0.0.0', 9100))
            start_http_server('0.0.0.0', addr=9100)
    except:
        print('ERROR: Invalid IP for web.listen_address flag!')
        exit()
