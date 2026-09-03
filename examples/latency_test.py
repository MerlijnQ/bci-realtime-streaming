"""
Simple end-to-end latency measurement
"""

import time
from src.inlet import create_inlet
import json
import pylsl as lsl

inlet = create_inlet()
latencies = []

for _ in range(100):
    _, timestamp = inlet.pull_sample()

    # latency = time.time() - timestamp
    latency = lsl.local_clock() - timestamp
    latencies.append(latency)

print(f"Mean latency: {sum(latencies)/len(latencies):.4f} s")

with open("latencies.json", "w") as f:
    json.dump(latencies, f)
