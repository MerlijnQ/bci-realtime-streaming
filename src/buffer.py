"""
Circular buffer for real-time EEG samples
"""

import numpy as np

class CircularBuffer:
    def __init__(self, max_samples, n_channels):
        self.max_samples = max_samples
        self.n_channels = n_channels
        self.buffer = np.zeros((max_samples, n_channels))
        self.timestampedbuffer = np.zeros((max_samples, 2)) #timestamps and latency
        self.index = 0
        self.index_time = 0
        self.is_full = False

    def append(self, sample):
        self.buffer[self.index] = sample
        self.index = (self.index + 1) % self.max_samples
        if self.index == 0:
            self.is_full = True

    def append_time_latency(self, timestamp, latency):
        self.timestampedbuffer[self.index_time] = np.array([timestamp, latency])
        self.index_time = (self.index_time + 1) % self.max_samples
        if self.index_time == 0:
            self.is_full = True

    def get(self):
        if not self.is_full:
            return self.buffer[:self.index]
        return np.vstack((
            self.buffer[self.index:],
            self.buffer[:self.index]
        ))

    def get_time_latency(self):
        if not self.is_full:
            return self.timestampedbuffer[:self.index_time]
        return np.vstack((
            self.timestampedbuffer[self.index_time:],
            self.timestampedbuffer[:self.index_time]
        ))

