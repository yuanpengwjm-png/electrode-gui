"""Count and compare BOTH actual zero-crossing directions without re-indexing gaps."""
import numpy as np
from models import MetricResult


class ZeroCrossingDetector:
    def __init__(self, settings):
        self.settings = settings

    def detect(self, samples, fs, peak_uV, frequency, direction):
        if direction not in ("rising", "falling"):
            raise ValueError("Detect rising and falling separately")
        z = np.asarray(samples) * (1 if direction == "rising" else -1)
        if peak_uV <= 0 or len(z) < 2:
            return np.array([])
        h = peak_uV*self.settings.zero_hysteresis_peak_fraction
        crossings = np.flatnonzero((z[:-1] < 0) & (z[1:] >= 0))
        negative = np.flatnonzero(z <= -h)
        positive = np.flatnonzero(z >= h)
        result, last_confirmation = [], -1
        # Iterate crossing candidates, not every 16,384-Hz sample.
        for k, i in enumerate(crossings):
            left = np.searchsorted(negative, i, side="right")-1
            right = np.searchsorted(positive, i+1)
            if left < 0 or right == len(positive) or negative[left] <= last_confirmation:
                continue
            confirmation = positive[right]
            if k+1 < len(crossings) and crossings[k+1] < confirmation:
                continue  # zero chatter: keep the last crossing before +h
            time = float((i-z[i]/(z[i+1]-z[i]))/fs)
            if not result or time-result[-1] >= .5/frequency:
                result.append(time)
                last_confirmation = confirmation
        return np.asarray(result)


class TimeSynchronizationAnalyzer:
    def __init__(self, settings):
        self.settings = settings
        self.detector = ZeroCrossingDetector(settings)

    def match_direction(self, reference, target, frequency, duration):
        """Each interior reference event owns a disjoint +/-T/4 window.

        Missing windows stay missing; target events are never shifted/re-numbered
        to hide a skipped period. A whole-cycle absolute offset is unidentifiable.
        """
        gap = self.settings.zero_match_period_fraction/frequency
        pairs, missing, ambiguous = [], 0, 0
        eligible = [(i, t) for i, t in enumerate(reference) if gap <= t <= duration-gap]
        for index, t in eligible:
            lo, hi = np.searchsorted(target, [t-gap, t+gap], side="left")
            # Include a point exactly on the upper boundary.
            hi = int(np.searchsorted(target, t+gap, side="right"))
            if hi-lo == 0:
                missing += 1
            elif hi-lo != 1:
                ambiguous += 1
            else:
                pairs.append(dict(reference_event_index=index, reference_zero_s=float(t),
                                  electrode_zero_s=float(target[lo]), delay_ms=float((target[lo]-t)*1000)))
        # Extra target events in the interior must also be reported.
        extra = 0
        if eligible:
            interior = target[(target >= eligible[0][1]-gap) & (target <= eligible[-1][1]+gap)]
            extra = max(0, len(interior)-len(pairs))
        return pairs, dict(reference_windows=len(eligible), missing=missing, ambiguous=ambiguous, extra=extra)

    def evaluate_all(self, centred, fits, names, reference, fs, frequency):
        ref_index = names.index(reference)
        duration = (len(centred)-1)/fs
        events = {}
        for i, name in enumerate(names):
            column = centred.column(i) if hasattr(centred, 'column') else centred[:, i]
            events[name] = {d: self.detector.detect(column, fs, fits[i]["amplitude_pp_mV"]*500,
                                                  frequency, d) for d in ("rising", "falling")}
        result = {}
        for i, name in enumerate(names):
            values = dict(reference=reference, rising_count=len(events[name]["rising"]),
                          rising_events_s=events[name]["rising"].tolist(),
                          falling_events_s=events[name]["falling"].tolist(),
                          falling_count=len(events[name]["falling"]),
                          reference_rising_count=len(events[reference]["rising"]),
                          reference_falling_count=len(events[reference]["falling"]), directions={}, pairs=[])
            all_delays, p95s, count_problems, too_short = [], [], [], False
            for direction in ("rising", "falling"):
                pairs, counts = self.match_direction(events[reference][direction], events[name][direction], frequency, duration)
                delays = np.array([p["delay_ms"] for p in pairs])
                values["directions"][direction] = dict(**counts, paired_count=len(pairs),
                    median_ms=float(np.median(delays)) if len(delays) and i != ref_index else None,
                    abs_p95_ms=float(np.percentile(np.abs(delays), 95)) if len(delays) and i != ref_index else None)
                values["pairs"].extend([dict(**p, direction=direction) for p in pairs])
                all_delays.extend(delays)
                if len(delays):
                    p95s.append(float(np.percentile(np.abs(delays), 95)))
                if any(counts[key] for key in ("missing", "ambiguous", "extra")):
                    label = "Rising" if direction == "rising" else "Falling"
                    count_problems.append(f"{label} missing {counts['missing']} / ambiguous {counts['ambiguous']} / extra {counts['extra']}")
                too_short |= len(pairs) < self.settings.min_zero_pairs
            values["max_direction_p95_ms"] = max(p95s) if p95s and i != ref_index else None
            values["jitter_ms"] = float(np.std(all_delays, ddof=1)) if len(all_delays) >= 2 and i != ref_index else None
            if i == ref_index:
                values["pairs"] = []
                result[name] = MetricResult("yellow", "REF: self-comparison at 0 ms is not independent verification", values)
            elif fits[i]["quality_reasons"] or fits[ref_index]["quality_reasons"]:
                reason = "Reference waveform" if fits[ref_index]["quality_reasons"] else "Electrode waveform"
                result[name] = MetricResult("yellow", reason+" quality is insufficient; repeat the timing test", values)
            elif count_problems:
                result[name] = MetricResult("red", "Event count mismatch; check missing cycles, polarity or noise: "+"; ".join(count_problems), values)
            elif too_short:
                result[name] = MetricResult("yellow", "Insufficient complete event pairs; at least 3 per direction are required", values)
            else:
                p95, jitter = values["max_direction_p95_ms"], values["jitter_ms"]
                colors = [self.settings.color(p95, self.settings.sync_delay_limit_ms),
                          self.settings.color(jitter, self.settings.sync_jitter_limit_ms)]
                color = "red" if "red" in colors else "yellow" if "yellow" in colors else "green"
                up = values["directions"]["rising"]["median_ms"]
                down = values["directions"]["falling"]["median_ms"]
                message = f"Rising {up:+.3f} ms; Falling {down:+.3f} ms; P95 {p95:.3f} ms; jitter {jitter:.3f} ms"
                result[name] = MetricResult(color, message+("; limit exceeded, check required" if color == "red" else ", near the limit" if color == "yellow" else ""), values)
        return result
