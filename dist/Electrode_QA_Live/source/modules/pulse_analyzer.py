"""Two-level pulse measurements; no sine fit is used for pulse recordings."""
import numpy as np
from modules.bench_spectrum import BenchSpectrumAnalyzer
from utils.centered_channels import CenteredChannels


class PulseAnalyzer:
    def __init__(self, settings):
        self.settings = settings

    def fit(self, x, fs, frequency, lazy=False, progress=lambda _: None):
        if not 0 < frequency < fs/4:
            raise ValueError("At least four samples per nominal pulse period are required")
        fits, offsets = [], []
        for i in range(x.shape[1]):
            progress(f"Fitting pulse plateaus: channel {i+1}/{x.shape[1]}")
            y = x[:, i]
            low, high = np.percentile(y, [.5, 99.5])
            # Two robust plateau centres. Requires both levels to be represented;
            # extremely narrow pulses (<~0.5% duty cycle) are outside this model.
            for _ in range(5):
                split = (low+high)/2
                a, b = y[y <= split], y[y > split]
                if not len(a) or not len(b):
                    break
                low, high = float(np.median(a)), float(np.median(b))
            amplitude = float(high-low)
            reasons = []
            if amplitude < self.settings.min_response_uVpp:
                reasons.append("no_reliable_pulse_response")
            if len(y)/fs*frequency < self.settings.min_cycles:
                reasons.append("too_few_cycles")
            offsets.append((high+low)/2)
            residual = np.minimum(np.abs(y-low), np.abs(y-high))
            if amplitude and float(np.median(residual))/amplitude > .10:
                reasons.append("unstable_pulse_plateaus")
            fits.append(dict(amplitude_pp_mV=amplitude/1000, low_uV=float(low), high_uV=float(high),
                             quality_reasons=reasons, measurement="two plateau medians; midpoint edge timing"))
        centred = CenteredChannels(x, offsets)
        return fits, centred if lazy else centred.as_array()

    def frequencies(self, timings, nominal):
        output = {}
        helper = BenchSpectrumAnalyzer(self.settings)
        for channel, metric in timings.items():
            # Reference event series and target series remain on original time axes.
            events = metric.values.get("rising_events_s", [])
            if len(events) < 4:
                from models import MetricResult
                output[channel] = MetricResult("yellow", "At least 4 rising edges are needed for pulse frequency")
                continue
            periods = np.diff(events)
            measured = float(1/np.median(periods))
            output[channel] = helper.frequency_result(measured, nominal, bool(np.all(periods > 0)))
        return output
