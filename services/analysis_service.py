"""Route BDF data to the appropriate analysis. No Tkinter dependency."""
from dataclasses import asdict
from pathlib import Path
from time import perf_counter
import math
import numpy as np
from models import AnalysisResult, ElectrodeResult, RunResult, MetricResult, combine
from utils.bdf_reader import BdfReader
from modules.sine_fitter import SineFitter
from modules.gain_error import AmplitudePeakGainError
from modules.linearity import LinearityAnalyzer
from modules.time_synchronization import TimeSynchronizationAnalyzer
from modules.repeatability import RepeatabilityAnalyzer
from modules.bench_spectrum import BenchSpectrumAnalyzer
from modules.pulse_analyzer import PulseAnalyzer
from modules.ecg_quality import ECGQualityAnalyzer
from modules.windowing import WindowPlan


class AnalysisService:
    def __init__(self, settings):
        settings.validate()
        self.settings = settings
        self.reader = BdfReader()
        self.fitter = SineFitter(settings)
        self.gain = AmplitudePeakGainError(settings)
        self.linearity = LinearityAnalyzer(settings)
        self.synchronization = TimeSynchronizationAnalyzer(settings)
        self.repetition = RepeatabilityAnalyzer(settings)
        self.spectrum = BenchSpectrumAnalyzer(settings)
        self.pulse = PulseAnalyzer(settings)
        self.ecg = ECGQualityAnalyzer(settings)

    def _validate(self, records, channels, reference):
        if not records or not channels or len(set(channels)) != len(channels):
            raise ValueError("Add BDF records and select unique electrode channels")
        if self.settings.analysis_mode != "ecg" and reference not in channels:
            raise ValueError("Select a timing reference from the selected channels")
        sources = [(str(Path(r.path).resolve()).lower(), r.member) for r in records]
        if len(set(sources)) != len(sources) or len({r.id for r in records}) != len(records):
            raise ValueError("A BDF source or record ID cannot appear twice")
        if len({r.setup_group for r in records}) != 1:
            raise ValueError("Different physical setups must be analyzed as separate projects")
        expected = {"bench_sine":"sine", "bench_pulse":"pulse", "ecg":"ecg"}[self.settings.analysis_mode]
        for r in records:
            if r.waveform not in ("unknown", expected):
                raise ValueError(f"{r.id}: declared {r.waveform} waveform does not match {expected} analysis")
            if not isinstance(r.input_confirmed, bool) or not isinstance(r.sweep, bool):
                raise ValueError("input_confirmed and sweep must be boolean")
            if expected == "ecg":
                continue
            if not math.isfinite(r.frequency_hz) or r.frequency_hz <= 0:
                raise ValueError(f"{r.id}: frequency must be positive")
            for value in (r.input_mVpp, r.nominal_mV):
                if value is not None and (not math.isfinite(value) or value <= 0):
                    raise ValueError(f"{r.id}: input amplitude must be positive")
            if r.input_confirmed and r.input_mVpp is None:
                raise ValueError(f"{r.id}: confirmed input requires a value")

    def analyze(self, records, channels, reference, progress=lambda _: None):
        self._validate(records, channels, reference)
        start = perf_counter()
        if self.settings.analysis_mode == "ecg":
            return self._analyze_ecg(records, channels, progress, start)
        runs, frames = [], []
        for index, record in enumerate(records):
            progress(f"{index+1}/{len(records)}: reading {record.id}")
            with self.reader.open_data(record, channels, progress) as (x, fs, metadata):
                x, source_duration, excluded = self._retained_data(x, fs, record, progress)
                clipped = (self._clipped_counts(x, channels, metadata) if excluded
                           else metadata["clipped_samples_full_record"])
                data = self._measure_bench(record, channels, reference, x, fs,
                                           clipped, progress)
                if self.settings.bench_windows:
                    spans = WindowPlan(self.settings.bench_window_s, self.settings.bench_hop_s).spans(len(x), fs)
                    for number, (left, right) in enumerate(spans):
                        progress(f"{record.id}: window {number+1}/{len(spans)} | {left/fs:g}-{right/fs:g} s")
                        segment = x[left:right]
                        clipped = self._clipped_counts(segment, channels, metadata)
                        measured = self._measure_bench(record, channels, reference, segment, fs, clipped)
                        metrics = {}
                        for name, values in measured.items():
                            # Store summaries per window. Whole-record event pairs remain available.
                            timing = values["sync"]
                            timing.values = {k: v for k, v in timing.values.items()
                                             if k not in ("pairs", "rising_events_s", "falling_events_s")}
                            timing.values["window_start_s"] = left/fs
                            timing.values["window_end_s"] = right/fs
                            metrics[name] = dict(gain=values["gain"], synchronization=timing, **values["extra"])
                        frames.append(dict(record_id=record.id, start_s=left/fs, end_s=right/fs,
                                           analysis_mode=self.settings.analysis_mode, metrics=metrics))
                    for name in channels:
                        data[name]["complete_windows"] = len(spans)
                        data[name]["unassessed_tail_s"] = 0 if spans else len(x)/fs
                runs.append(RunResult(record, data, fs, len(x)/fs, source_duration, excluded))
        electrodes = []
        for name in channels:
            labels = [r.record.id for r in runs]
            gain = combine([r.channels[name]["gain"] for r in runs], labels=labels)
            gain.values = {"records": {r.record.id:r.channels[name]["gain"].values for r in runs}}
            sync = combine([r.channels[name]["sync"] for r in runs], labels=labels)
            sync.values = {"records": {r.record.id:r.channels[name]["sync"].values for r in runs}}
            extra = {}
            for key in runs[0].channels[name]["extra"]:
                extra[key] = combine([r.channels[name]["extra"][key] for r in runs], labels=labels)
                extra[key].values = {"records":{r.record.id:r.channels[name]["extra"][key].values for r in runs}}
            electrodes.append(ElectrodeResult(name, gain, self.linearity.evaluate(runs, name), sync,
                                              self.repetition.evaluate(runs, name, reference), name == reference, extra))
        return AnalysisResult(electrodes, runs, reference, perf_counter()-start, asdict(self.settings), frames)

    def _retained_data(self, x, fs, record, progress):
        """Apply one per-file crop before any fitting, event detection or windows.

        The stop boundary is exclusive and stays on the original time axis.
        Ceil excludes at least the requested duration, rounded up to one sample.
        The slice is a view, including when the source is disk-backed.
        """
        source_duration = len(x)/fs
        excluded_samples = math.ceil(self.settings.exclude_last_s*fs)
        stop = len(x)-excluded_samples
        if stop <= 0:
            raise ValueError(f"{record.id}: recorded {source_duration:g} s; excluding the final "
                             f"{self.settings.exclude_last_s:g} s leaves no samples. "
                             "Reduce Exclude final (s), or set it to 0.")
        excluded = excluded_samples/fs
        progress(f"{record.id}: analyze 0-{stop/fs:g} s of {source_duration:g} s; excluded final {excluded:g} s")
        return x[:stop], source_duration, excluded

    @staticmethod
    def _clipped_counts(x, channels, metadata):
        # Recount inside the retained interval: clipping in an excluded tail
        # must not contaminate whole-record quality or any retained window.
        counts = {}
        for i, name in enumerate(channels):
            lo, hi = metadata["physical_limits_uV"][name]
            counts[name] = int(np.count_nonzero((x[:, i] <= lo) | (x[:, i] >= hi)))
        return counts

    def _measure_bench(self, record, channels, reference, x, fs, clipped, progress=lambda _: None):
        """Identical algorithms for the whole record and an isolated window."""
        is_pulse = self.settings.analysis_mode == "bench_pulse"
        fitter = self.pulse if is_pulse else self.fitter
        fits, centred = fitter.fit(x, fs, record.frequency_hz, lazy=True, progress=progress)
        for i, name in enumerate(channels):
            if clipped[name]:
                fits[i]["quality_reasons"].append("digital_rail_clipping")
        timings = self.synchronization.evaluate_all(centred, fits, channels, reference, fs, record.frequency_hz)
        pulse_frequencies = self.pulse.frequencies(timings, record.frequency_hz) if is_pulse else {}
        data = {}
        for i, name in enumerate(channels):
            progress(f"{record.id}: {name} / {len(channels)} channels")
            extra = dict(frequency=pulse_frequencies[name]) if is_pulse else self.spectrum.analyze(x[:, i], fs, record.frequency_hz)
            if clipped[name]:
                for metric in extra.values():
                    if metric.color == "green":
                        metric.color = "yellow"
                    metric.message += "; digital clipping detected"
            timing = timings[name]
            timing.values["sample_period_ms"] = 1000/fs
            timing.values["event_definition"] = "pulse plateau midpoint" if is_pulse else "detrended sine zero"
            if name != reference and 1000/fs > min(self.settings.sync_delay_limit_ms, self.settings.sync_jitter_limit_ms):
                if timing.color == "green":
                    timing.color = "yellow"
                timing.message += f"; sample interval {1000/fs:.4f} ms exceeds a timing limit: interpolation needs calibration"
            data[name] = dict(fit=fits[i], gain=self.gain.evaluate(fits[i], record), sync=timing, extra=extra)
        return data

    def _analyze_ecg(self, records, channels, progress, start):
        runs, frames = [], []
        for index, record in enumerate(records):
            progress(f"{index+1}/{len(records)}: reading ECG {record.id}")
            with self.reader.open_data(record, channels, progress) as (x, fs, metadata):
                x, source_duration, excluded = self._retained_data(x, fs, record, progress)
                window = round(self.settings.ecg_window_s*fs)
                spans = WindowPlan(self.settings.ecg_window_s, self.settings.ecg_hop_s).spans(len(x), fs)
                starts = [left for left, _ in spans]
                channel_windows = {name:[] for name in channels}
                for number, offset in enumerate(starts):
                    progress(f"{record.id}: ECG window {number+1}/{len(starts)}")
                    measurements = {name:self.ecg.analyze_window(x[offset:offset+window, i], fs,
                                    metadata["physical_limits_uV"][name]) for i, name in enumerate(channels)}
                    frames.append(dict(record_id=record.id, start_s=offset/fs, end_s=(offset+window)/fs,
                                       metrics=measurements))
                    for name in channels:
                        channel_windows[name].append(measurements[name])
                data = {}
                for name in channels:
                    windows = channel_windows[name]
                    if windows:
                        metrics = {k:combine([w[k] for w in windows]) for k in windows[0]}
                        for key, metric in metrics.items():
                            metric.values = dict(complete_windows=len(windows),
                                green_windows=sum(w[key].color == "green" for w in windows),
                                yellow_windows=sum(w[key].color == "yellow" for w in windows),
                                red_windows=sum(w[key].color == "red" for w in windows))
                    else:
                        metrics = self.ecg.unavailable(f"Insufficient data: {source_duration:.2f} s recorded; "
                            f"{len(x)/fs:.2f} s retained after excluding {excluded:g} s; "
                            f"{self.settings.ecg_window_s:g} s required")
                    data[name] = dict(extra=metrics, complete_windows=len(starts),
                                      unassessed_tail_s=(len(x)-(starts[-1]+window))/fs if starts else len(x)/fs)
                runs.append(RunResult(record, data, fs, len(x)/fs, source_duration, excluded))
        electrodes = []
        for name in channels:
            extra = {k:combine([r.channels[name]["extra"][k] for r in runs], labels=[r.record.id for r in runs]) for k in runs[0].channels[name]["extra"]}
            for k in extra:
                extra[k].values = {"records":{r.record.id:r.channels[name]["extra"][k].values for r in runs}}
            na = MetricResult("yellow", "Not applicable to ECG quality mode")
            electrodes.append(ElectrodeResult(name, na, na, na, na, False, extra))
        return AnalysisResult(electrodes, runs, "", perf_counter()-start, asdict(self.settings), frames)
