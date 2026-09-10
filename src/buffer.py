"""
Circular buffer for real-time EEG samples
"""

import numpy as np

class CircularBuffer:
    def __init__(self, max_samples, n_channels):
        self.max_samples = max_samples
        self.n_channels = n_channels
        self.buffer = np.zeros((max_samples, n_channels))
        self.timestamps = np.zeros(max_samples)
        self.index = 0
        self.is_full = False

    def append(self, sample, timestamp):
        self.buffer[self.index] = sample
        self.timestamps[self.index] = timestamp
        self.index = (self.index + 1) % self.max_samples
        if self.index == 0:
            self.is_full = True

    def get(self):
        if not self.is_full:
            return self.buffer[:self.index], self.timestamps[:self.index]
        else:
            return np.vstack((
                self.buffer[self.index:],
                self.buffer[:self.index]
            )), np.hstack((
                self.timestamps[self.index:],
                self.timestamps[:self.index]
            ))    