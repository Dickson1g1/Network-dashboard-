import subprocess
import json
from datetime import datetime
import os

OUTPUT_DIR = "logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_arp_scan():
    cmd = ["sudo", "arp-scan", "--localnet"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def parse_arp_output(raw):
    devices = []
    for line in raw.splitlines():
        if ":" in line and "." in line:
            parts = line.split()
            if len(parts) >= 3:
                ip = parts[0]
                mac = parts[1]
                vendor = " ".join(parts[2:])
                devices.append({
                    "ip": ip,
                    "mac": mac,
                    "vendor": vendor
                })
    return devices

def main():
    print("[+] Running ARP scan...")
    raw = run_arp_scan()
    discovered = parse_arp_output(raw)

    timestamp = datetime.now().isoformat()
    log_file = os.path.join(
        OUTPUT_DIR,
        f"devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with open(log_file, "w") as f:
        json.dump({"timestamp": timestamp, "devices": discovered}, f, indent=2)

    print(f"[+] Device discovery saved to {log_file}")
    print("[+] Devices found:")

    for d in discovered:
        print(f"    {d['ip']} - {d['mac']} - {d['vendor']}")

if __name__ == "__main__":
    main()


