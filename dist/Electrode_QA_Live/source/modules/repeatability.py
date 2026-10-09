"""Independent repetitions at the same frequency, nominal input and wiring."""
import numpy as np
from models import MetricResult, combine


class RepeatabilityAnalyzer:
    def __init__(self, settings):
        self.settings = settings

    def evaluate(self, runs, channel, reference):
        groups = sorted({(r.record.repeat_group, r.record.frequency_hz) for r in runs if r.record.repeat_group})
        results = []
        for label, frequency in groups:
            group = [r for r in runs if r.record.repeat_group == label and r.record.frequency_hz == frequency]
            if len(group) < self.settings.min_repeat_runs:
                results.append(MetricResult("yellow", f"{label} has {len(group)} runs; at least {self.settings.min_repeat_runs} independent runs are required"))
                continue
            known = all(r.record.input_confirmed and r.record.input_mVpp is not None for r in group)
            levels = {r.record.nominal_mV if r.record.nominal_mV is not None else r.record.input_mVpp for r in group}
            if len(levels) != 1 or None in levels:
                results.append(MetricResult("yellow", "Repeat group input settings are inconsistent or missing"))
                continue
            if any(r.channels[channel]["fit"]["quality_reasons"] for r in group):
                results.append(MetricResult("yellow", "Repeat group contains invalid waveforms; repeat the measurements"))
                continue
            amplitudes = [r.channels[channel]["fit"]["amplitude_pp_mV"] /
                          (r.record.input_mVpp if known else 1) for r in group]
            cv = float(100*np.std(amplitudes, ddof=1)/np.mean(amplitudes))
            values = dict(group=label, independent_runs=len(group), amplitude_cv_pct=cv,
                          basis="gain" if known else "recorded_amplitude", direction_sd_ms={})
            color = self.settings.color(cv, self.settings.repeat_cv_limit_pct)
            message = f"Repeat {'gain' if known else 'output amplitude'} CV {cv:.3f}%"
            if channel != reference:
                timing_valid = all(not r.channels[channel]["fit"]["quality_reasons"] and
                    all(not d["missing"] and not d["ambiguous"] and not d["extra"] and d["paired_count"] >= self.settings.min_zero_pairs
                        for d in r.channels[channel]["sync"].values["directions"].values()) and
                    not r.channels[reference]["fit"]["quality_reasons"] for r in group)
                if not timing_valid:
                    results.append(MetricResult("red" if color == "red" else "yellow", message+"; repeat timing data are insufficient", values))
                    continue
                for direction in ("rising", "falling"):
                    medians = [r.channels[channel]["sync"].values["directions"][direction]["median_ms"] for r in group]
                    values["direction_sd_ms"][direction] = float(np.std(medians, ddof=1))
                sd = max(values["direction_sd_ms"].values())
                timing_color = self.settings.color(sd, self.settings.repeat_delay_sd_limit_ms)
                color = "red" if "red" in (color, timing_color) else "yellow" if "yellow" in (color, timing_color) else "green"
                message += f"; repeat delay SD {sd:.3f} ms"
            else:
                message += "; REF: amplitude repeatability only"
            if not known:
                message += " (includes generator and fixture variation)"
            results.append(MetricResult(color, message, values))
        result = combine(results, "No independent repeat group; cycles within one BDF are not separate experiments")
        result.values = {"groups": [r.values for r in results]}
        return result
