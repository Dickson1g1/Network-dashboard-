import subprocess
import json
from datetime import datetime
import os

TARGETS_FILE = "targets.txt"
OUTPUT_DIR = "logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_targets():
    if not os.path.exists(TARGETS_FILE):
        print(f"{TARGETS_FILE} not found. Create it and add IPs gang.")
        return []
    with open(TARGETS_FILE) as f:
        return [line.strip() for line in f if line.strip()]

def run_nmap_scan(ip):
    # -sV: service/version detection
    # -O: OS detection (needs root, may not always succeed)
    # -T4: faster timing
    # -Pn: skip host discovery (assume up if we target it)

    cmd = [
        "sudo", "nmap",
        "-sV",
        "-O",
        "-T4",
        "-Pn",
        ip
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    return result.stdout

def parse_nmap_output(raw_output):
    lines = raw_output.splitlines()
    host_info = {
        "ip": None,
        "ports": [],
        "os_guess": None
    }


    for line in lines:
        line = line.strip()
        if line.startswith("Nmap scan report for"):
            parts = line.split()
            host_info["ip"] = parts[-1]
        elif "/tcp" in line or "/udp" in line:
            # Example: "22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5"
            parts = line.split()
            if len(parts) >= 3:
                port_proto = parts[0]
                state = parts[1]
                service = parts[2]
                extra = " ".join(parts[3:]) if len(parts) > 3 else ""
                port, proto = port_proto.split("/")
                host_info["ports"].append({
                    "port": port,
                    "protocol": proto,
                    "state": state,
                    "service": service,
                    "info": extra
                })

        elif line.startswith("OS details:") or line.startswith("Aggressive OS guesses:"):
            host_info["os_guess"] = line

    return host_info

def main():
    targets = load_targets()
    if not targets:
        print("No targets to scan.")
        return


    all_results = []
    for ip in targets:
        print(f"[+] Scanning {ip} with Nmap...")
        raw = run_nmap_scan(ip)
        parsed = parse_nmap_output(raw)
        all_results.append(parsed)

    timestamp = datetime.now().isoformat()
    log_file = os.path.join(
        OUTPUT_DIR,
        f"ports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with open(log_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "results": all_results
        }, f, indent=2)

    print(f"[+] Port scan complete. Results saved to {log_file}")

if __name__ == "__main__":
    main()

