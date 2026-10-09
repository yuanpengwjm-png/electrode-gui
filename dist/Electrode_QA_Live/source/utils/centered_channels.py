"""Materialize a single detrended electrode only when its crossings are needed."""
import numpy as np


class CenteredChannels:
    def __init__(self, samples, offsets, slopes=None, fs=1.):
        self.samples = samples
        self.offsets = offsets
        self.slopes = slopes
        self.fs = fs

    def __len__(self):
        return len(self.samples)

    def column(self, index):
        result = np.asarray(self.samples[:, index]) - self.offsets[index]
        if self.slopes is not None:
            time = (np.arange(len(self.samples)) - (len(self.samples)-1)/2) / self.fs
            result -= time * self.slopes[index]
        return result

    def as_array(self):
        return np.column_stack([self.column(i) for i in range(self.samples.shape[1])])
