import subprocess
import json
from datetime import datetime
import os
from collections import Counter

OUTPUT_DIR = "logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_tcpdump():
    cmd = ["sudo", "tcpdump", "-nn", "-c", "200"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def analyze_packets(raw):
    protocols = Counter()
    sources = Counter()

    for line in raw.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue

        # Source IP
        if parts[0].count(".") >= 3:
            src = parts[0]
            sources[src] += 1

        # Protocol detection
        if "ARP" in line:
            protocols["ARP"] += 1
        elif "ICMP" in line:
            protocols["ICMP"] += 1
        elif "TCP" in line:
            protocols["TCP"] += 1
        elif "UDP" in line:
            protocols["UDP"] += 1
        else:
            protocols["OTHER"] += 1

    return {
        "protocols": dict(protocols),
        "sources": dict(sources)
    }

def main():
    print("[+] Capturing packets for 200 packets...")
    raw = run_tcpdump()

    analysis = analyze_packets(raw)
    timestamp = datetime.now().isoformat()

    log_file = os.path.join(
        OUTPUT_DIR,
        f"packets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with open(log_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "analysis": analysis
        }, f, indent=2)

    print(f"[+] All done sir, Packet capture saved to {log_file}")
    print("[+] Protocol counts:", analysis["protocols"])
    print("[+] Top sources:", analysis["sources"])

if __name__ == "__main__":
    main()


