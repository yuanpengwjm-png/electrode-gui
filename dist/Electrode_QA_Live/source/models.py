"""Data shared by the GUI, metrics and report exporter; no GUI imports here."""
from dataclasses import dataclass, field, replace
from typing import Any


@dataclass
class MetricResult:
    color: str  # green / yellow / red
    message: str
    values: dict[str, Any] = field(default_factory=dict)


@dataclass
class InputRecord:
    id: str
    path: str
    frequency_hz: float = 5.0
    input_mVpp: float | None = None
    input_confirmed: bool = False
    sweep: bool = True
    repeat_group: str = ""
    member: str | None = None  # optional BDF member in a ZIP
    nominal_mV: float | None = None
    waveform: str = "unknown"
    setup_group: str = "default"


@dataclass
class RunResult:
    record: InputRecord
    channels: dict[str, dict]
    sample_rate_hz: float
    duration_s: float
    source_duration_s: float | None = None
    excluded_tail_s: float = 0.0

    @property
    def recorded_duration_s(self):
        return self.duration_s if self.source_duration_s is None else self.source_duration_s


@dataclass
class ElectrodeResult:
    name: str
    gain: MetricResult
    linearity: MetricResult
    synchronization: MetricResult
    repetition: MetricResult
    is_reference: bool = False
    extra: dict[str, MetricResult] = field(default_factory=dict)

    def metric(self, mode: str) -> MetricResult:
        if mode in self.extra:
            return self.extra[mode]
        if mode == "bench_summary":
            items = [self.gain] + [self.extra[k] for k in ("snr", "thd", "frequency") if k in self.extra]
            if not self.is_reference:
                items.append(self.synchronization)
        elif mode == "current":
            # Self-comparison is not an independent synchronization measurement.
            items = [self.gain] if self.is_reference else [self.gain, self.synchronization]
        elif mode == "overall":
            items = [self.metric("bench_summary"), self.linearity, self.repetition]
            if not self.is_reference:
                items.append(self.synchronization)
        else:
            return getattr(self, mode, MetricResult("yellow", "Not applicable to this analysis mode"))
        rank = {"green": 0, "yellow": 1, "red": 2}
        color = max(items, key=lambda m: rank[m.color]).color
        details = [m.message for m in items if m.color != "green"]
        message = "; ".join(dict.fromkeys(details)) if details else "Completed checks are within the current limits"
        if self.is_reference:
            message += "; REF timing has not been independently verified"
        return MetricResult(color, message)


@dataclass
class AnalysisResult:
    electrodes: list[ElectrodeResult]
    runs: list[RunResult]
    reference: str
    elapsed_s: float
    settings: dict
    frames: list[dict] = field(default_factory=list)

    def record_electrodes(self, record_id: str) -> list[ElectrodeResult]:
        """Project one analyzed record without borrowing another record's flags."""
        run = next(r for r in self.runs if r.record.id == record_id)
        unavailable = MetricResult("yellow", "Multi-record check: analyze All loaded records and select All analyzed records / worst case")
        result = []
        for electrode in self.electrodes:
            data = run.channels[electrode.name]
            if "gain" in data:
                result.append(replace(electrode, gain=data["gain"], synchronization=data["sync"],
                                      linearity=unavailable, repetition=unavailable, extra=data["extra"]))
            else:
                result.append(replace(electrode, extra=data["extra"]))
        return result

    def window_electrodes(self, index: int) -> list[ElectrodeResult]:
        """Return only this window's checks, never whole-record or batch metrics."""
        frame = self.frames[index]
        unavailable = MetricResult("yellow", "Linearity and independent repetition cannot be assessed from one time window")
        electrodes = []
        for electrode in self.electrodes:
            metrics = frame["metrics"][electrode.name]
            if "gain" in metrics:
                extra = {k: v for k, v in metrics.items() if k not in ("gain", "synchronization")}
                electrodes.append(replace(electrode, gain=metrics["gain"], synchronization=metrics["synchronization"],
                                          linearity=unavailable, repetition=unavailable, extra=extra))
            else:
                electrodes.append(replace(electrode, extra=metrics))
        return electrodes


def combine(results: list[MetricResult], empty="No evaluable data", labels=None) -> MetricResult:
    if not results:
        return MetricResult("yellow", empty)
    rank = {"green": 0, "yellow": 1, "red": 2}
    color = max(results, key=lambda r: rank[r.color]).color
    messages = [(f"{labels[i]}: " if labels and len(results) > 1 else "") + r.message
                for i, r in enumerate(results) if r.color == color]
    return MetricResult(color, "; ".join(dict.fromkeys(messages)))
