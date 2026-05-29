import os
import subprocess
import json
from datetime import datetime

# this will be my network range

NETWORK_PREFIX = "192.168.11."

results = []
timestamp = datetime.now().isoformat()

for host in range(1, 255): 
    ip = f"{NETWORK_PREFIX}{host}"
    # -c 1 = send 1 ping, -W 1 = 1 second timeout

    response = subprocess.run( 
	["ping", "-c", "1", "-W", "1", ip],
	stdout=subprocess.DEVNULL,
	stderr=subprocess.DEVNULL
    )
    status = "up" if response.returncode == 0 else "down"
    results.append({"ip": ip, "status": status})

os.makedirs("logs", exist_ok=True) 
log_file = f"logs/ping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with open(log_file, "w") as f:
    json.dump({"timestamp": timestamp, "results": results}, f, indent=2) 

print(f"I am done bruh. Results saved to {log_file}")




