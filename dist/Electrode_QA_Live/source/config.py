"""Editable project criteria. These are engineering starting points, not standards."""
from dataclasses import dataclass, asdict
import math

COLORS = {"green": "#21866A", "yellow": "#E7B647", "red": "#C84E58"}
COLOR_LABELS = {"green": "Within limits", "yellow": "Review / insufficient data", "red": "Check required"}
BENCH_VIEWS = {"Bench summary": "bench_summary", "Gain + timing": "current", "Gain error": "gain",
               "Linearity": "linearity", "Time synchronization": "synchronization",
               "Repetition": "repetition", "SNR": "snr", "SINAD": "sinad", "THD": "thd",
               "Frequency error": "frequency", "Full protocol (incl. repeats)": "overall"}
ECG_VIEWS = {"ECG quality": "ecg_quality", "Beat agreement (bSQI)": "bsqi", "QRS power (pSQI)": "psqi",
             "Kurtosis (kSQI)": "ksqi", "Baseline (basSQI)": "bassqi", "Flatline / clipping": "integrity"}
VIEW_LABELS = BENCH_VIEWS


@dataclass
class AnalysisSettings:
    analysis_mode: str = "bench_sine"  # bench_sine / bench_pulse / ecg
    gain_limit_pct: float = 5.0
    linearity_limit_pct: float = 2.0
    sync_delay_limit_ms: float = 1.0
    sync_jitter_limit_ms: float = 0.2
    repeat_cv_limit_pct: float = 2.0
    repeat_delay_sd_limit_ms: float = 0.2
    warning_fraction: float = 0.8
    min_cycles: float = 3.0
    max_residual_pct: float = 2.0
    max_residual_step_pct: float = 2.0
    frequency_search_pct: float = 5.0
    min_response_uVpp: float = 1.0
    zero_hysteresis_peak_fraction: float = 0.02
    min_zero_pairs: int = 3
    zero_match_period_fraction: float = 0.25
    min_repeat_runs: int = 3
    snr_good_db: float = 20.0
    snr_bad_db: float = 10.0
    bench_bandwidth_hz: float = 100.0
    harmonic_count: int = 5  # highest harmonic order, including the fundamental
    thd_limit_pct: float | None = 1.0  # User-selected default; blank still means uncalibrated.
    frequency_limit_pct: float | None = 0.1
    exclude_last_s: float = 1.0  # Analysis-only tail exclusion; original BDF is unchanged.
    bench_windows: bool = False  # GUI enables this; legacy CLI keeps whole-record work.
    bench_window_s: float = 10.0
    bench_hop_s: float = 1.0
    ecg_window_s: float = 10.0
    ecg_hop_s: float = 5.0
    ecg_match_ms: float = 50.0
    ecg_min_beats: int = 3
    bsqi_good: float = 0.90
    bsqi_bad: float = 0.60
    psqi_low: float = 0.50
    psqi_high: float = 0.80
    psqi_bad: float = 0.40
    ksqi_min: float = 5.0
    bassqi_good: float = 0.95
    bassqi_bad: float = 0.90
    flatline_s: float = 0.75
    flat_epsilon_uV: float = 0.10

    def validate(self):
        if not isinstance(self.bench_windows, bool):
            raise ValueError("bench_windows must be boolean")
        for key, value in asdict(self).items():
            if key in ("analysis_mode", "bench_windows") or (key in ("thd_limit_pct", "frequency_limit_pct") and value is None):
                continue
            if key == "exclude_last_s":
                if not math.isfinite(float(value)) or value < 0:
                    raise ValueError("exclude_last_s must be a non-negative finite number (0 disables exclusion)")
                continue
            if not math.isfinite(float(value)) or value <= 0:
                raise ValueError(f"{key} must be a positive finite number")
        if self.analysis_mode not in ("bench_sine", "bench_pulse", "ecg"):
            raise ValueError("Select Bench / Sine, Bench / Pulse, or ECG quality")
        for key in ("min_zero_pairs", "min_repeat_runs", "ecg_min_beats"):
            if getattr(self, key) < 3 or int(getattr(self, key)) != getattr(self, key):
                raise ValueError(f"{key} must be an integer of at least 3")
        if not 2 <= self.harmonic_count <= 20 or int(self.harmonic_count) != self.harmonic_count:
            raise ValueError("Harmonic order must be an integer from 2 to 20")
        if self.snr_bad_db >= self.snr_good_db:
            raise ValueError("SNR bad boundary must be below the good boundary")
        if self.bench_hop_s > self.bench_window_s:
            raise ValueError("Bench window step must not exceed window duration")
        if self.ecg_window_s < 4 or self.ecg_hop_s > self.ecg_window_s:
            raise ValueError("ECG window must be >= 4 s; hop must not exceed the window")
        if self.ecg_match_ms >= 125 or self.flatline_s > self.ecg_window_s:
            raise ValueError("Beat match tolerance must be < 125 ms; flatline duration must fit the ECG window")
        for low, high in ((self.bsqi_bad, self.bsqi_good), (self.bassqi_bad, self.bassqi_good)):
            if not 0 < low < high <= 1:
                raise ValueError("SQI boundaries must satisfy 0 < bad < good <= 1")
        if not 0 < self.psqi_bad < self.psqi_low < self.psqi_high <= 1:
            raise ValueError("pSQI boundaries must satisfy 0 < bad < low < high <= 1")
        if not 0 < self.warning_fraction < 1:
            raise ValueError("Warning fraction must be between 0 and 1")
        if not 0 < self.zero_match_period_fraction < .5:
            raise ValueError("Event matching window must be smaller than half a period")
        if not 0 < self.zero_hysteresis_peak_fraction < .5 or self.frequency_search_pct >= 50:
            raise ValueError("Invalid crossing hysteresis or frequency search range")

    def color(self, value, limit):
        if abs(value) > limit:
            return "red"
        if abs(value) >= limit * self.warning_fraction:
            return "yellow"
        return "green"
