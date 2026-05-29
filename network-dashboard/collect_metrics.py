import subprocess
import json
from datetime import datetime
import os

OUTPUT_DIR = "logs"
HISTORY_DIR = "history"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)


CLIENT_IP = "192.168.11.143"
CLIENT_USER = "bdickson"
REMOTE_FILE = "/home/bdickson/metrics-agent/system_metrics.json"

def fetch_metrics():
    local_file = os.path.join(
        OUTPUT_DIR,
        f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    cmd = [
        "scp",
        f"{CLIENT_USER}@{CLIENT_IP}:{REMOTE_FILE}",
        local_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("[!] Failed to fetch metrics:", result.stderr)
        return None

    print(f"[+] Metrics saved to {local_file}")
    return local_file

def append_history(metric_name, value):
    path = os.path.join(HISTORY_DIR, f"{metric_name}.json")

    # Load existing history
    if os.path.exists(path):
        with open(path) as f:
            history = json.load(f)
    else:
        history = []

    # Append new entry
    history.append({
        "timestamp": datetime.now().isoformat(),
        "value": value
    })

    # Save back
    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def main():
    file = fetch_metrics()
    if not file:
        return

    with open(file) as f:
        data = json.load(f)

    append_history("cpu", data["cpu_percent"])
    append_history("ram", data["ram_percent"])
    append_history("disk", data["disk_percent"])

    print("[+] History updated.")

if __name__ == "__main__":
    main()


