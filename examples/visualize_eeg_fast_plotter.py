"""
Live visualization of EEG stream
"""

import time

import matplotlib.pyplot as plt
from src.inlet import create_inlet
from src.buffer import CircularBuffer
import pylsl as lsl
import numpy as np
from live_plotter import FastLivePlotter


FS = 250
BUFFER_SEC = 60
N_CHANNELS = 8
WINDOW_SEC = 10       
PLOT_EVERY_N = 20 

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


def record(inlet, buffer, live_plotter):
    start = lsl.local_clock()
    print(f"start time is: {start} s")
    end = start + 60
    
    sample_counter = 0

    while lsl.local_clock() < end:
            sample, timestamp = inlet.pull_sample()
            latency = lsl.local_clock() - timestamp
        
            if sample == 0.0:
                raise ValueError("Received sample is 0.0, which may indicate an issue with the data stream.")   
            
            buffer.append(sample)
    
            # note: append_time_latency appends to a SEPARATE buffer. This buffer only stores
            # the timestamps and the latency, NOT the samples. 
            buffer.append_time_latency(timestamp, latency)
    
            sample_counter += 1
            data = buffer.get()

            if sample_counter % PLOT_EVERY_N == 0:
                plot(buffer=buffer, live_plotter=live_plotter, start_time = start)
    
            # note: buffer.get is only retrieving the samples, not the timestamps or latency.

            
    print(f"end time is: {lsl.local_clock()} s")
    print(f"the final size of the data in the buffer is: {data.shape[0]}")
    print(f"the actual duration of the code is:{lsl.local_clock() - start} s")
    # print(f"there were {counter} samples that were 0.0")
    # only here we retrieve the timestamps and latencies that are then used to calculate the stats
    timestamps_and_latencies = buffer.get_time_latency()
    return data, timestamps_and_latencies



def plot(buffer, live_plotter, start_time, window_sec=WINDOW_SEC):

    #     plot_data = [data[:, i] for i in range(data.shape[1])]
    #     live_plotter.plot(y_data_list=plot_data)

    data = buffer.get()
    timestamps = buffer.get_time_latency()[:, 0]

    window_samples = window_sec * FS
    window_data = data[-window_samples:]
    window_time = timestamps[-window_samples:] - start_time  # relative seconds, e.g. 0..10, then 1..11, ..

    plot_data = [window_data[:, i] for i in range(window_data.shape[1])]
    x_data_list = [window_time for _ in plot_data]   # same time axis for every channel subplot

    live_plotter.plot(y_data_list=plot_data, x_data_list=x_data_list)

    # print("the number of rows is", data.shape[0])
    # print("the first channel is", data[:, 0])

   

def main():
        
    inlet = create_inlet()
    buffer = CircularBuffer(FS * BUFFER_SEC, N_CHANNELS)

    # put this into main
    plt.rcParams["figure.figsize"] = (10, 16)

    xlabels = [None] * (N_CHANNELS - 1) + ["Time (samples)"]
    ylabels = [f"Ch {i+1}" for i in range(N_CHANNELS)]

    live_plotter = FastLivePlotter(
                n_plots=N_CHANNELS,
                n_rows=N_CHANNELS,
                n_cols=1,
                xlabels=xlabels,
                ylabels=ylabels,
                ylims=[(-3, 3)] * N_CHANNELS,
            )

    _, timestamps_and_latencies = record(inlet, buffer, live_plotter)
    throughput, jitter, average_latency = get_stats(timestamps_and_latencies)
    print(f"Throughput: {throughput:.2f} samples/sec")
    print(f"Jitter: {jitter:.6f} milliseconds")
    print(f"Average Latency: {average_latency:.6f} milliseconds ")

if __name__ == "__main__":
    main()

