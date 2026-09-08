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

def get_stats(data):


    num_samples = data.shape[0]
    #[max_samples, 2] = data.shape

    #calculate throughput

    timestamps = data[:, 0]
    latency = data[:, 1]

    # print(f"the timestamps are: {timestamps}")
  
    duration = np.max(timestamps) - np.min(timestamps)
    print(f"Duration: {duration:.4f} s")
    print(f"Number of samples: {num_samples}")
    throughput = (num_samples-1) / duration # offset by one as the first sample does not have a previous sample to calculate the inter-sample interval

    #Works for now due to large buffer size, but may need to be adjusted for smaller buffer sizes as you will accidentilly 
    #include the difference between first and last as it is ciruclar.
    #calculate jitter (in milliseconds)
    inter_sample_intervals = np.diff(timestamps)
    jitter = np.std(inter_sample_intervals)

    #calculate mean latency
    average_latency = np.mean(latency)

    return throughput, jitter, average_latency

def plot(inlet, buffer):
    plt.ion()
    _, ax = plt.subplots()

    start = lsl.local_clock()
    print(f"start time is: {start} s")
    end = start + 20

    # plot_every_n = 50 # plots every 50 samples
    # sample_counter = 0

    while lsl.local_clock() < end:
        sample, timestamp = inlet.pull_sample()
        latency = lsl.local_clock() - timestamp


        if sample == 0.0:
            raise ValueError("Received sample is 0.0, which may indicate an issue with the data stream.")   
        
        buffer.append(sample)
        # note: append_time_latency appends to a SEPARATE buffer. This buffer only stores
        # the timestamps and the latency, NOT the samples. 
        buffer.append_time_latency(timestamp, latency)
        
        data = buffer.get()
        plot_data = data + np.arange(N_CHANNELS) * -10.0  # Offset each channel for better visibility            

        window_size = 50 # samples

        n = data.shape[0]
        window_start = (n // window_size) * window_size
        window_end = n

        x = np.arange(window_start, window_end)
        y = plot_data[window_start:window_end, :]

        ax.clear()
        ax.plot(x, y)
        ax.set_xlim(window_start, window_start + window_size)
        ax.set_title("Live EEG (Simulated)")    
        plt.pause(0.001)

        # note: buffer.get is only retrieving the samples, not the timestamps or latency.
        data = buffer.get()
        plt.pause(0.01)

    plt.close()

    print(f"end time is: {lsl.local_clock()} s")
    print(f"the final size of the data in the buffer is: {data.shape[0]}")
    print(f"the actual duration of the code is:{lsl.local_clock() - start} s")
    # print(f"there were {counter} samples that were 0.0")
    # only here we retrive the timestamps and latencies that are then used to calculate the stats
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

