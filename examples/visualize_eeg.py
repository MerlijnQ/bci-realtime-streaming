"""
Live visualization of EEG stream
"""

import time

import matplotlib.pyplot as plt
from src.inlet import create_inlet
from src.buffer import CircularBuffer
import pylsl as lsl
import numpy as np

FS = 250
BUFFER_SEC = 60
N_CHANNELS = 8

#maxsamples = FS * BUFFER_SEC
#number of samples in 60 seconds = 250 x 60 = 15000 samples
counter = 0

def get_stats(data):

    num_samples = data.shape[0]
    #[max_samples, 2] = data.shape

    #calculate throughput

    timestamps = data[:, 0]
    latency = data[:, 1]
  
    duration = np.max(timestamps) - np.min(timestamps)
    print(f"Duration: {duration:.4f} s")
    print(f"Number of samples: {num_samples}")
    throughput = (num_samples-1) / duration #offset by one as  the first sample does not have a previous sample to calculate the inter-sample interval

    #Works for now due to large buffer size, but may need to be adjusted for smaller buffer sizes as you will accidentilly 
    #include the difference between firsy and last as it is ciruclar.
    #calculate jitter (in milliseconds)
    inter_sample_intervals = np.diff(timestamps)
    jitter = np.std(inter_sample_intervals)

    #calculate mean latency
    average_latency = np.mean(latency)

    return throughput, jitter, average_latency

def plot(inlet, buffer):
    plt.ion()
    _, ax = plt.subplots()

    start = time.time()
    end = start + 10

    while time.time() < end:
        sample, timestamp = inlet.pull_sample()
        latency = lsl.local_clock() - timestamp

        if sample == 0.0:
            raise ValueError("Received sample is 0.0, which may indicate an issue with the data stream.")   
        
        buffer.append(sample)
        buffer.append_time_latency(timestamp, latency)
        data = buffer.get()

        plot_data = data + np.arange(N_CHANNELS) * -10.0  # Offset each channel for better visibility

        ax.clear()
        ax.plot(plot_data)
        ax.set_title("Live EEG (Simulated)")
        plt.pause(0.01)

    plt.close()
    timestamps_and_latencies = buffer.get_time_latency()
    return data, timestamps_and_latencies

def main():
        
    inlet = create_inlet()
    buffer = CircularBuffer(FS * BUFFER_SEC, N_CHANNELS)

    _, timestamps_and_latencies = plot(inlet, buffer)
    throughput, jitter, average_latency = get_stats(timestamps_and_latencies)
    print(f"Throughput: {throughput:.2f} samples/sec")
    print(f"Jitter: {jitter:.6f} Seconds")
    print(f"Average Latency: {average_latency:.6f} milliseconds ")

if __name__ == "__main__":
    main()

