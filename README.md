# Prometheus Network Speedtest Exporter
Prometheus exporter for network speedtests using `speedtest-cli` command in Linux distros. Developed in Python3 language and has been tested on Ubuntu v18.04.

## Requirements
* Python v3+
* Python Packages: `prometheus_client`
* Speedtest-cli

## Setup
1. Install `speedtest-cli`.
    * Ubuntu/Debian: `apt install speedtest-cli`
    * CentOS/RHEL: `wget -O speedtest-cli https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py; chmod +x speedtest-cli;`
2. Run program:
```py
python3 speedtest_exporter.py
```

## Command Arguments
* `--web.listen-address="0.0.0.0:9100"` = Specify host and port to display metrics for scraping. (DEFAULT: 0.0.0.0:9100)
* `--server_id` = Specify server by ID to perform speedtests on.
* `--bind_ip` = Bind to specific source IP address to run speedtests from. (DEFAULT: Closest server to source will automatically be used.)
* `--interval` = Set interval in seconds on how often data should be updated. (DEFAULT: 10 seconds)

## Metrics Example
```
# HELP speedtest_upload Current network upload speed in bytes/sec.
# TYPE speedtest_upload gauge
speedtest_upload 102188975.87000838
# HELP speedtest_download Current network download speed in bytes/sec.
# TYPE speedtest_download gauge
speedtest_download 305429320.9009878
# HELP speedtest_ping Current ping time in milliseconds.
# TYPE speedtest_ping gauge
speedtest_ping 53.816
```