"""LinearityAnalyzer: output versus three or more known input levels."""
import numpy as np
from models import MetricResult, combine


class LinearityAnalyzer:
    def __init__(self, settings):
        self.settings = settings

    def evaluate(self, runs, channel):
        frequencies = sorted({r.record.frequency_hz for r in runs if r.record.sweep})
        results = []
        for frequency in frequencies:
            group = [r for r in runs if r.record.sweep and r.record.frequency_hz == frequency]
            if any(r.channels[channel]["fit"]["quality_reasons"] for r in group):
                results.append(MetricResult("yellow", f"{frequency:g} Hz sweep contains invalid waveforms; repeat the measurement"))
                continue
            if any(r.record.input_mVpp is None or not r.record.input_confirmed for r in group):
                results.append(MetricResult("yellow", "Actual inputs for linearity are unconfirmed"))
                continue
            x = np.array([r.record.input_mVpp for r in group])
            if len(set(x)) < 3:
                results.append(MetricResult("yellow", "Linearity needs at least 3 input levels at the same frequency"))
                continue
            y = np.array([r.channels[channel]["fit"]["amplitude_pp_mV"] for r in group])
            k, b = np.linalg.lstsq(np.column_stack((x, np.ones(len(x)))), y, rcond=None)[0]
            deviation = float(100*np.max(np.abs(y-(k*x+b)))/np.ptp(x))
            color = self.settings.color(deviation, self.settings.linearity_limit_pct)
            results.append(MetricResult(color, f"Linearity deviation {deviation:.3f}% of input span" +
                                        ("; nonlinearity exceeds the limit" if color == "red" else ", near the limit" if color == "yellow" else ", within limits"),
                                        dict(frequency_hz=frequency, deviation_pct=deviation, slope=float(k), intercept_mVpp=float(b))))
        result = combine(results, "No linearity sweep; multiple input levels at one frequency are required")
        result.values = {"sweeps": [r.values for r in results]}
        return result
