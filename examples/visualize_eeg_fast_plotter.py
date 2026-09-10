"""
Live visualization of EEG stream
"""


import matplotlib.pyplot as plt
from src.inlet import create_inlet
from src.buffer import CircularBuffer
import pylsl as lsl
import numpy as np
from live_plotter import FastLivePlotter

import logging
import pandas as pd

import threading
import time


FS = 250
BUFFER_SEC = 2
LATENCY_BUFFER_SEC = 60
N_CHANNELS = 8
WINDOW_SEC = BUFFER_SEC       

#maxsamples = FS * BUFFER_SEC
#number of samples in 60 seconds = 250 x 60 = 15000 samples


class Logger():
    def __init__(self):
        self._records = {
            "Timestamp": [],
            "Latency": []
        }
        logging.basicConfig(
            filename="measurements.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self._logger = logging.getLogger(__name__)


    def log(self, timestamp, latency):
        self._records["Timestamp"].append(timestamp)
        self._records["Latency"].append(latency)
    
    def calculate_stats(self):
        df = pd.DataFrame(self._records)

        throughput = len(df) / (df["Timestamp"].max() - df["Timestamp"].min())
        jitter = df["Timestamp"].diff().std()
        average_latency = df["Latency"].mean()
        print(f"Throughput: {throughput:.2f} samples/sec")
        print(f"Jitter: {jitter * 1000 :.6f} milliseconds")
        print(f"Average Latency: {average_latency:.6f} milliseconds")
        print(f"Total number of samples: {len(df)}")


        self._logger.info("Stats calculated on the recorded data on:" \
        f" Throughput: {throughput:.2f} samples/sec, Jitter: {jitter:.6f} ms, Average Latency: {average_latency:.6f} ms, total number of samples: {len(df)}")


class Recorder(Logger):
    def __init__(self):
        super().__init__()
        self.inlet = create_inlet()
        self.buffer = CircularBuffer(FS * BUFFER_SEC, N_CHANNELS)
        self.stop_recording = threading.Event()

    def record(self, seconds=60):


        self.start = lsl.local_clock()
        print(f"start time is: {self.start} s, recording for {seconds} seconds")

        end = self.start + seconds

        while (lsl.local_clock() < end and not self.stop_recording.is_set()):
                sample, timestamp = self.inlet.pull_sample()
                latency = lsl.local_clock() - timestamp
            
                if sample == 0.0:
                    raise ValueError("Received sample is 0.0, which may indicate an issue with the data stream.")   
                
                self.buffer.append(sample, timestamp)

                self.log(timestamp, latency)
                
                

        print(f"end time is: {lsl.local_clock()} s")
        # print(f"the final size of the data in the buffer is: {data.shape[0]}")
        # print(f"the actual duration of the code is:{lsl.local_clock() - self.start} s")
        # print(f"there were {counter} samples that were 0.0")
        # only here we retrieve the timestamps and latencies that are then used to calculate the 
        
        #signal to stop this thread
        self.stop_recording.set()


    def plot(self, live_plotter, window_sec=WINDOW_SEC):

        #     plot_data = [data[:, i] for i in range(data.shape[1])]
        #     live_plotter.plot(y_data_list=plot_data)

        data, timestamps = self.buffer.get()

        window_samples = window_sec * FS
        window_data = data[-window_samples:]

        window_time = timestamps[-window_samples:] - self.start  # relative seconds, e.g. 0..10, then 1..11, ..

        plot_data = [window_data[:, i] for i in range(window_data.shape[1])]
        x_data_list = [window_time for _ in plot_data]   # same time axis for every channel subplot

        live_plotter.plot(y_data_list=plot_data, x_data_list=x_data_list)

        # print("the number of rows is", data.shape[0])
        # print("the first channel is", data[:, 0])

   

def main():
        
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

    recorder = Recorder()

    recording_thread = threading.Thread(target=recorder.record, kwargs={"seconds": 60}, daemon=True)
    recording_thread.start()

    start_plotting = False

    while not recorder.stop_recording.is_set():
        if (recorder.buffer.index >= recorder.buffer.max_samples -1) or start_plotting:
            start_plotting = True
            recorder.plot(live_plotter, window_sec=WINDOW_SEC)
        time.sleep(0.1)

    recording_thread.join()

    recorder.calculate_stats()

if __name__ == "__main__":
    main()

