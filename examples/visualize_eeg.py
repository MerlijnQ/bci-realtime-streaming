"""
Live visualization of EEG stream
"""

import matplotlib.pyplot as plt
from src.inlet import create_inlet
from src.buffer import CircularBuffer
import pylsl as lsl
import numpy as np

FS = 250
BUFFER_SEC = 2
N_CHANNELS = 8

inlet = create_inlet()
buffer = CircularBuffer(FS * BUFFER_SEC, N_CHANNELS)

plt.ion()
fig, ax = plt.subplots()

# start_time = lsl.local_clock()

while True:
    sample, _ = inlet.pull_sample()
    if sample == 0.0:
        plt.close()
        # end_time = lsl.local_clock()

        # throughput = counter / (end_time - start_time)
        # print(f"Throughput: {throughput:.2f} samples/sec")

        data = buffer.get()
        #timestamp, channels = data.
        
        #calculate throughput
        num_samples, num_channels = data.shape
        first_timestamp = data[0, 0]
        last_timestamp = data[-1, 0]
        duration = last_timestamp - first_timestamp
        throughput = num_samples / duration
        print(f"Throughput: {throughput:.2f} samples/sec")

        #calculate jitter
        timestamps = data[:, 0]
        inter_sample_intervals = np.diff(timestamps)
        jitter = np.std(inter_sample_intervals)
        print(f"Jitter: {jitter:.6f} seconds")

        #mean latency between samples
        mean_latency = np.mean(inter_sample_intervals)
        print(f"Mean Latency: {mean_latency:.6f} seconds")

    

    buffer.append(sample)
    data = buffer.get()

    #print(data.shape)
    #Shape is timestamp, channels.
    index = data.shape[0] -1
    for i in range(N_CHANNELS):
        data[index:, i] = data[index:, i] + i * -10.0  # Offset each channel for better visibility

    ax.clear()
    ax.plot(data)
    ax.set_title("Live EEG (Simulated)")
    plt.pause(0.01)
