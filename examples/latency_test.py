"""
Simple end-to-end latency measurement
"""

import time
from src.inlet import create_inlet
import json
import pylsl as lsl

inlet = create_inlet()
samples = []
timestamps = []
latencies = []

for sample in range(100):
    sample, timestamp = inlet.pull_sample()

    # latency = time.time() - timestamp
    latency = lsl.local_clock() - timestamp
    samples.append(sample)
    timestamps.append(timestamp)
    latencies.append(latency)

print(f"Mean latency: {sum(latencies)/len(latencies):.4f} s")

with open("data.json", "w") as f:
    json.dump({
        "samples": samples,
        "timestamps": timestamps,
        "latencies": latencies
    }, f)
