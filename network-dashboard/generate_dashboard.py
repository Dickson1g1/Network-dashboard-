import json
import glob
import os

os.makedirs("dashboard", exist_ok=True)


# -----------------------------
# Helper for alert colors
# -----------------------------
def alert_color(value, warn, crit):
    if value >= crit:
        return "red"
    elif value >= warn:
        return "orange"
    else:
        return "green"



# -----------------------------
# Load latest ping log
# -----------------------------
ping_logs = sorted(glob.glob("logs/ping_*.json"))
if not ping_logs:
    print("No ping logs found twin. Go and run ping_sweep.py first and come back.")
    exit(1)

# -----------------------------
# Load latest device discovery log (#2)
# -----------------------------
latest_ping = ping_logs[-1]
with open(latest_ping) as f:
    ping_data = json.load(f)

ping_rows = ""
for entry in ping_data["results"]:
    color = "green" if entry["status"] == "up" else "red"
    ping_rows += f"<tr><td>{entry['ip']}</td><td style='color:{color}'>{entry['status']}</td></tr>\n"

# -----------------------------
# Load latest port scan log (#1)
# -----------------------------
port_logs = sorted(glob.glob("logs/ports_*.json"))
ports_section = ""

if port_logs:
    latest_ports = port_logs[-1]
    with open(latest_ports) as f:
        port_data = json.load(f)

    port_rows = ""
    for host in port_data["results"]:
        ip = host.get("ip", "unknown")
        for p in host.get("ports", []):
            port_rows += (
                f"<tr>"
                f"<td>{ip}</td>"
                f"<td>{p['port']}/{p['protocol']}</td>"
                f"<td>{p['state']}</td>"
                f"<td>{p['service']}</td>"
                f"<td>{p['info']}</td>"
                f"</tr>\n"
            )

    ports_section = f"""
    <h2>Port Scan Results</h2>
    <p>Latest port scan: {port_data['timestamp']}</p>
    <table>
        <tr>
            <th>IP</th>
            <th>Port/Proto</th>
            <th>State</th>
            <th>Service</th>
            <th>Info</th>
        </tr>
        {port_rows}
    </table>
    """


# -----------------------------
# Load latest device discovery log (#3)
# -----------------------------
device_logs = sorted(glob.glob("logs/devices_*.json"))
device_section = ""

if device_logs:
    latest_devices = device_logs[-1]
    with open(latest_devices) as f:
        device_data = json.load(f)

    device_rows = ""
    for d in device_data["devices"]:
        device_rows += (
            f"<tr>"
            f"<td>{d['ip']}</td>"
            f"<td>{d['mac']}</td>"
            f"<td>{d['vendor']}</td>"
            f"</tr>\n"
        )

    device_section = f"""
    <h2>Device Discovery</h2>
    <p>Latest device scan: {device_data['timestamp']}</p>
    <table>
        <tr>
            <th>IP</th>
            <th>MAC Address</th>
            <th>Vendor</th>
        </tr>
        {device_rows}
    </table>
    """


# -----------------------------
# Load latest packet capture log
# -----------------------------

packet_logs = sorted(glob.glob("logs/packets_*.json"))
packet_section = ""

if packet_logs:
    latest_packets = packet_logs[-1]
    with open(latest_packets) as f:
        packet_data = json.load(f)

    # Protocol table
    proto_rows = ""
    for proto, count in packet_data["analysis"]["protocols"].items():
        proto_rows += f"<tr><td>{proto}</td><td>{count}</td></tr>\n"

    # Source table
    src_rows = ""
    for src, count in packet_data["analysis"]["sources"].items():
        src_rows += f"<tr><td>{src}</td><td>{count}</td></tr>\n"

    packet_section = f"""
    <h2>Packet Capture Summary</h2>
    <p>Latest capture: {packet_data['timestamp']}</p>

    <h3>Protocol Breakdown</h3>
    <table>
        <tr><th>Protocol</th><th>Count</th></tr>
        {proto_rows}
    </table>

    <h3>Top Source IPs</h3>
    <table>
        <tr><th>Source IP</th><th>Packets</th></tr>
        {src_rows}
    </table>
    """


# -----------------------------
# Load latest system metrics log
# -----------------------------
metrics_logs = sorted(glob.glob("logs/metrics_*.json"))
metrics_section = ""
global_alerts = ""

if metrics_logs:
    latest_metrics = metrics_logs[-1]
    with open(latest_metrics) as f:
        m = json.load(f)

    # Alerts
    if m["cpu_percent"] >= 90:
        global_alerts += "<p style='color:red;'>CRITICAL: CPU above 90%!</p>"
    elif m["cpu_percent"] >= 80:
        global_alerts += "<p style='color:orange;'>Warning: CPU above 80%.</p>"

    if m["ram_percent"] >= 90:
        global_alerts += "<p style='color:red;'>CRITICAL: RAM above 90%!</p>"
    elif m["ram_percent"] >= 80:
        global_alerts += "<p style='color:orange;'>Warning: RAM above 80%.</p>"

    if m["disk_percent"] >= 95:
        global_alerts += "<p style='color:red;'>CRITICAL: Disk above 95%!</p>"
    elif m["disk_percent"] >= 85:
        global_alerts += "<p style='color:orange;'>Warning: Disk above 85%.</p>"

    metrics_section = f"""
    <h2>System Metrics (Client VM)</h2>
    <p>Latest metrics: {m['timestamp']}</p>

    <table>
        <tr><th>Metric</th><th>Value</th></tr>

        <tr><td>CPU Usage</td>
            <td style="color:{alert_color(m['cpu_percent'], 80, 90)}">
                {m['cpu_percent']}%
            </td>
        </tr>

        <tr><td>RAM Usage</td>
            <td style="color:{alert_color(m['ram_percent'], 80, 90)}">
                {m['ram_percent']}%
            </td>
        </tr>

        <tr><td>Disk Usage</td>
            <td style="color:{alert_color(m['disk_percent'], 85, 95)}">
                {m['disk_percent']}%
            </td>
        </tr>

        <tr><td>Uptime (seconds)</td><td>{m['uptime_seconds']}</td></tr>
    </table>
    """


# -----------------------------
# Load latest inventory log
# -----------------------------
inventory_logs = sorted(glob.glob("logs/inventory_*.json"))
inventory_section = ""

if inventory_logs:
    latest_inventory = inventory_logs[-1]
    with open(latest_inventory) as f:
        inv = json.load(f)

    inventory_section = f"""
    <h2>System Inventory (Client VM)</h2>
    <p>Latest inventory: {inv['timestamp']}</p>

    <h3>Installed Packages</h3>
    <pre>{inv['installed_packages']}</pre>

    <h3>Running Processes</h3>
    <pre>{inv['running_processes']}</pre>

    <h3>Installed Services</h3>
    <pre>{inv['services']}</pre>

    <h3>Running Services</h3>
    <pre>{inv['running_services']}</pre>

    <h3>Executables in /usr/bin</h3>
    <pre>{inv['executables']}</pre>

    <h3>Recently Modified Files (24h)</h3>
    <pre>{inv['recent_files']}</pre>

    <h3>Files in /home</h3>
    <pre>{inv['home_files']}</pre>
    """



# -----------------------------
# Build final HTML
# -----------------------------
html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Network Health & Security Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        table {{ border-collapse: collapse; width: 80%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        h1, h2 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>Network Health & Security Dashboard</h1>

    <h2>Ping Status</h2>
    <p>Latest ping scan: {ping_data['timestamp']}</p>
    <table>
        <tr><th>IP Address</th><th>Status</th></tr>
        {ping_rows}
    </table>

    {ports_section}

    {device_section}

    {packet_section}

    {metrics_section}

    {inventory_section}


</body>
</html>
"""

output_file = "dashboard/index.html"
with open(output_file, "w") as f:
    f.write(html)

print(f"Bro, your dashboard is ready. Check it out: {output_file}")



