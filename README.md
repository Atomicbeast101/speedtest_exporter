# Prometheus Speedtest Exporter
Prometheus exporter where it reports speedtest statistics based on user's preference.

## Requirements
* Python v3
* Python Packages: `prometheus_client speedtest-cli`

## Setup
1. Install required Python packages
2. Run program:
```bash
python3 speedtest_exporter.py
```

## Usage
* `--web.listen-address="0.0.0.0:9100"` = Specify host and port for Prometheus to use to display metrics for scraping.
* `--servers` = Specific a or list of server ID(s) by comma to perform speedtests with. You can find the ID through [here](https://www.speedtestserver.com/).
* `--source` = Specify source IP for speedtest to use to perform test.
* `--interval` = How often in seconds the tests should be performed.

## Metrics Example
```
# HELP speedtest_ping Ping time in milliseconds.
# TYPE speedtest_ping gauge
speedtest_ping{server_id="1062",server_loc="United States",server_name="Mount Pleasant, MI"} 29.629
# HELP speedtest_download Network download speed in bytes/sec.
# TYPE speedtest_download gauge
speedtest_download{server_id="1062",server_loc="United States",server_name="Mount Pleasant, MI"} 1.7703202804595023e+08
# HELP speedtest_upload Network upload speed in bytes/sec.
# TYPE speedtest_upload gauge
speedtest_upload{server_id="1062",server_loc="United States",server_name="Mount Pleasant, MI"} 4.086002063756785e+06
```