"""Fit the common test frequency and each electrode's sine amplitude/baseline."""
from dataclasses import asdict
import numpy as np
from utils.numerics import fit_record
from utils.centered_channels import CenteredChannels


class SineFitter:
    def __init__(self, settings):
        self.settings = settings

    def fit(self, x_uV, fs, frequency, lazy=False, progress=lambda _: None):
        coefficients = []
        fits = fit_record(x_uV, fs, frequency, asdict(self.settings), coefficients, progress)
        beta = np.asarray(coefficients)
        centred = CenteredChannels(x_uV, beta[:, 2], beta[:, 3], fs)
        return fits, centred if lazy else centred.as_array()
