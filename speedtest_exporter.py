#!/usr/bin/env python3
# Imports
import prometheus_client
import traceback
import speedtest
import threading
import argparse
import time

# Arguments
parser = argparse.ArgumentParser(description='Prometheus exporter where it reports speedtest statistics based on user\'s preference.')
parser.add_argument('--web.listen-address', action='store', dest='listen_addr', help='Specify host and port for Prometheus to use to display metrics for scraping.')
parser.add_argument('--servers', action='store', dest='servers', help='Specific a or list of server ID(s) by comma to perform speedtests with.')
parser.add_argument('--source', action='store', dest='source', help='Specify source IP for speedtest to use to perform test.')
parser.add_argument('--interval', action='store', dest='interval', help='How often in seconds the tests should be performed.')

# Attributes
metrics = {
    'speedtest_ping': prometheus_client.Gauge('speedtest_ping', 'Ping time in milliseconds.', ['server_name', 'server_loc', 'server_id']),
    'speedtest_download': prometheus_client.Gauge('speedtest_download', 'Network download speed in Mbps.', ['server_name', 'server_loc', 'server_id']),
    'speedtest_upload': prometheus_client.Gauge('speedtest_upload', 'Network upload speed in Mbps.', ['server_name', 'server_loc', 'server_id'])
}

# Classes
class UpdateMetrics(threading.Thread):
    def __init__(self, _servers, _source, _interval):
        threading.Thread.__init__(self)
        self.servers = _servers
        self.interval = _interval
    
    def run(self):
        while True:
            try:
                print('INFO: Updating metrics...', flush=True)
                # Perform test
                tester = speedtest.Speedtest()
                tester.get_servers(self.servers)
                tester.get_best_server()
                tester.download()
                tester.upload()
                result = tester.results.dict()
                
                # Convert bytes to Mbps
                download_speed = result['download'] / 1000000.0
                upload_speed = result['upload'] / 1000000.0

                # Update metrics
                metrics['speedtest_ping'].labels(server_name=result['server']['name'], server_loc=result['server']['country'], server_id=result['server']['id']).set(result['ping'])
                metrics['speedtest_download'].labels(server_name=result['server']['name'], server_loc=result['server']['country'], server_id=result['server']['id']).set(download_speed)
                metrics['speedtest_upload'].labels(server_name=result['server']['name'], server_loc=result['server']['country'], server_id=result['server']['id']).set(upload_speed)
                print('INFO: Metrics updated!', flush=True)
            except Exception:
                # Set metrics to -1
                metrics['speedtest_ping'].labels(server_name='', server_loc='', server_id=0).set(-1)
                metrics['speedtest_download'].labels(server_name='', server_loc='', server_id=0).set(-1)
                metrics['speedtest_upload'].labels(server_name='', server_loc='', server_id=0).set(-1)
                print('ERROR: Unable to update metrics! Reason:\n{}'.format(traceback.print_exc()))

            # Wait
            time.sleep(self.interval)

# Main
if __name__ == '__main__':
    print('INFO: Loading exporter...')
    options = parser.parse_args()
    host = '0.0.0.0'
    port = 9100
    servers = []
    source = None
    interval = 900
    try:
        if options.listen_addr:
            host = options.listen_addr.split(':')[0]
            port = int(options.listen_addr.split(':')[-1])
        if options.servers:
            if ',' in options.servers:
                for server in options.servers.split(','):
                    servers.append(int(server))
        if options.source:
            source = options.source
        if options.interval:
            interval = int(options.interval)
    except Exception:
        print('ERROR: Invalid argument input! Reason:\n{}'.format(traceback.print_exc()))
    print('INFO: Exporter ready!')
    UpdateMetrics(_servers=servers, _source=source, _interval=interval).start()
    prometheus_client.start_http_server(port, host)
