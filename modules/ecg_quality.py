"""Transparent ECG SQI prototype. Two different beat detectors, complete windows.

The fusion rule is conservative: worst component wins. It is an engineering
screen, not a validated diagnosis of electrode damage or ECG interpretability.
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt, find_peaks, resample_poly, welch
from scipy.stats import kurtosis
from models import MetricResult, combine


def longest_true(mask):
    edges = np.diff(np.r_[False, np.asarray(mask, bool), False].astype(int))
    starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
    return int(np.max(ends-starts)) if len(starts) else 0


def bandpass(x, fs, low, high):
    return sosfiltfilt(butter(3, (low, high), btype="bandpass", fs=fs, output="sos"), x)


class EnergyQRSDetector:
    """Derivative energy + 100 ms integration, then local peak refinement."""
    def detect(self, x, fs):
        filtered = bandpass(x, fs, 5, 18)
        energy = np.diff(filtered, prepend=filtered[0])**2
        width = max(1, round(.10*fs))
        integrated = np.convolve(energy, np.ones(width)/width, mode="same")
        span = float(np.percentile(integrated, 99)-np.median(integrated))
        if span <= 1e-20:
            return np.array([])
        peaks, _ = find_peaks(integrated, distance=max(1, round(.25*fs)),
                             height=np.median(integrated)+.20*span, prominence=.12*span)
        refined = []
        half = max(1, round(.09*fs))
        for peak in peaks:
            lo, hi = max(0, peak-half), min(len(x), peak+half+1)
            k = lo + int(np.argmax(np.abs(filtered[lo:hi])))
            if not refined or k-refined[-1] >= .25*fs:
                refined.append(k)
        return np.asarray(refined, float)/fs


class ProminenceQRSDetector:
    """Independent amplitude/prominence path; no derivative-energy candidates."""
    def detect(self, x, fs):
        filtered = np.abs(bandpass(x, fs, 5, 25))
        baseline = float(np.median(filtered))
        span = float(np.percentile(filtered, 99)-baseline)
        if span <= 1e-12:
            return np.array([])
        peaks, _ = find_peaks(filtered, distance=max(1, round(.25*fs)),
                             height=baseline+.35*span, prominence=.30*span)
        return peaks.astype(float)/fs


class BeatAgreement:
    """One-to-one matching; one detected beat cannot satisfy two matches."""
    @staticmethod
    def score(a, b, tolerance):
        a, b = np.sort(a), np.sort(b)
        i = j = matched = 0
        while i < len(a) and j < len(b):
            if abs(a[i]-b[j]) <= tolerance:
                matched += 1; i += 1; j += 1
            elif a[i] < b[j]:
                i += 1
            else:
                j += 1
        union = len(a)+len(b)-matched
        return (float(matched/union) if union else None), matched


class ECGQualityAnalyzer:
    metric_keys = ("bsqi", "psqi", "ksqi", "bassqi", "integrity")

    def __init__(self, settings):
        self.settings = settings
        self.detector_a = EnergyQRSDetector()
        self.detector_b = ProminenceQRSDetector()

    def unavailable(self, message):
        return {key: MetricResult("yellow", message) for key in (*self.metric_keys, "ecg_quality")}

    def analyze_window(self, raw_uV, fs, limits=None):
        s = self.settings
        raw = np.asarray(raw_uV, float)
        if not np.isfinite(raw).all():
            return self.unavailable("Missing or non-finite samples; window unavailable")
        if fs < 100:
            return self.unavailable("ECG SQI requires a sample rate of at least 100 Hz")
        if len(raw) < round(s.ecg_window_s*fs):
            return self.unavailable(f"Insufficient data: need a complete {s.ecg_window_s:g} s ECG window")
        flat_samples = longest_true(np.abs(np.diff(raw)) <= s.flat_epsilon_uV)
        flat_s = (flat_samples+1)/fs if flat_samples else 0.
        clipped = 0 if limits is None else int(np.count_nonzero((raw <= limits[0]) | (raw >= limits[1])))
        integrity_bad = flat_s >= s.flatline_s or clipped > 0
        integrity = MetricResult("red" if integrity_bad else "green",
            f"Longest near-flat segment {flat_s:.3f} s; digital rail samples {clipped}",
            dict(flatline_s=flat_s, clipped_samples=clipped, epsilon_uV=s.flat_epsilon_uV))
        if np.ptp(raw) <= s.flat_epsilon_uV:
            metrics = self.unavailable("No measurable ECG variation; spectral ratios and beat agreement are undefined")
            metrics["integrity"] = integrity
            metrics["ecg_quality"] = combine([integrity])
            return metrics
        factor = max(1, int(fs // 250))
        x = resample_poly(raw-raw.mean(), 1, factor) if factor > 1 else raw-raw.mean()
        rate = fs/factor
        a, b = self.detector_a.detect(x, rate), self.detector_b.detect(x, rate)
        # Both detectors see identical input; avoid edge effects in both equally.
        duration = len(x)/rate
        a = a[(a >= .2) & (a < duration-.2)]
        b = b[(b >= .2) & (b < duration-.2)]
        agreement, matched = BeatAgreement.score(a, b, s.ecg_match_ms/1000)
        counts = dict(value=agreement, detector_a_count=len(a), detector_b_count=len(b), matched=matched,
                      detector_a_s=a.tolist(), detector_b_s=b.tolist(), tolerance_ms=s.ecg_match_ms)
        if agreement is None or min(len(a), len(b)) < s.ecg_min_beats:
            bsqi = MetricResult("yellow", "Insufficient detected beats for reliable bSQI", counts)
        else:
            color = "green" if agreement > s.bsqi_good else "yellow" if agreement >= s.bsqi_bad else "red"
            bsqi = MetricResult(color, f"bSQI {agreement:.3f}; A={len(a)}, B={len(b)}, matched={matched}", counts)
        f, p = welch(x, rate, nperseg=min(len(x), round(rate*4)), detrend="constant")
        df = float(f[1]-f[0])
        def power(low, high):
            return float(np.sum(p[(f >= low) & (f < high)])*df)
        denominator = power(5, 40)
        total = power(0, 40)
        psqi = None if denominator <= 1e-20 else power(5, 15)/denominator
        bas = None if total <= 1e-20 else float(np.clip(1-power(0, 1)/total, 0, 1))
        k = float(kurtosis(x, fisher=False, bias=False))
        if psqi is None:
            pmetric = MetricResult("yellow", "pSQI denominator is too small")
        else:
            color = "green" if s.psqi_low <= psqi <= s.psqi_high else "yellow" if s.psqi_bad <= psqi < s.psqi_low else "red"
            pmetric = MetricResult(color, f"pSQI {psqi:.3f} = P[5,15) / P[5,40)", dict(value=float(psqi)))
        bmetric = MetricResult("yellow", "basSQI denominator is too small") if bas is None else MetricResult(
            "green" if bas >= s.bassqi_good else "yellow" if bas >= s.bassqi_bad else "red",
            f"basSQI {bas:.3f} = 1 - P[0,1) / P[0,40)", dict(value=bas))
        kmetric = MetricResult("green" if k > s.ksqi_min else "red", f"Pearson kurtosis {k:.3f}", dict(value=k)) if np.isfinite(k) else MetricResult("yellow", "Kurtosis is undefined")
        result = dict(bsqi=bsqi, psqi=pmetric, ksqi=kmetric, bassqi=bmetric, integrity=integrity)
        result["ecg_quality"] = combine(list(result.values()))
        result["ecg_quality"].message = "Prototype ECG screen: " + result["ecg_quality"].message
        return result
