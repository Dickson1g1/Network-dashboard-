#!/bin/bash
cd "$(network-dashboard.sh "$0")"

python3 ping_sweep.py
python3 port_scan.py
python3 device_discovery.py
python3 packet_capture.py
python3 collect_metrics.py
python3 collect_inventory.py
python3 generate_dashboard.py

