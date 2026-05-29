import subprocess
import json
from datetime import datetime
import os

OUTPUT_DIR = "logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CLIENT_IP = "192.168.11.143"
CLIENT_USER = "bdickson"
REMOTE_FILE = "/home/bdickson/inventory-agent/system_inventory.json"

def fetch_inventory():
    local_file = os.path.join(
        OUTPUT_DIR,
        f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    cmd = [
        "scp",
        f"{CLIENT_USER}@{CLIENT_IP}:{REMOTE_FILE}",
        local_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("[!] Failed to fetch inventory:", result.stderr)
        return None

    print(f"[+] Inventory saved to {local_file}")
    return local_file

if __name__ == "__main__":
    fetch_inventory()

