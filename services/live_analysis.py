"""Known-sine live checks. Source health and signal findings are separate."""
from dataclasses import dataclass, field
import math
import time
import numpy as np
from config import AnalysisSettings
from models import ElectrodeResult, MetricResult, InputRecord, combine
from modules.bench_spectrum import BenchSpectrumAnalyzer
from modules.gain_error import AmplitudePeakGainError


@dataclass
class LiveConfig:
    frequency_hz: float = 5.
    input_mVpp: float = 10.
    window_s: float = 5.
    hop_s: float = 1.
    input_confirmed: bool = False
    mapping_confirmed: bool = False
    limits: AnalysisSettings = field(default_factory=lambda: AnalysisSettings(exclude_last_s=0))
    profile: str = 'sine'

    def validate(self, rate):
        self.limits.validate()
        if self.profile not in ('sine', 'ecg'):
            raise ValueError('Choose ECG quality or known-sine input.')
        values = (self.window_s, self.hop_s, rate)
        if self.profile == 'sine':
            values += (self.frequency_hz, self.input_mVpp)
        for value in values:
            if not math.isfinite(value) or value <= 0:
                raise ValueError('Frequency, amplitude, window, step and sample rate must be positive finite numbers.')
        if not 2 <= self.window_s <= 10 or self.hop_s > self.window_s:
            raise ValueError('Use a 2–10 s window, with step no longer than the window.')
        if self.profile == 'ecg':
            if rate < 100 or self.window_s < 4:
                raise ValueError('ECG quality needs at least 100 Hz and a 4–10 s window (10 s recommended).')
        elif self.frequency_hz >= rate/4 or self.frequency_hz*self.window_s < self.limits.min_cycles:
            raise ValueError('Need at least four samples/cycle and the configured minimum cycles/window.')


def electrode(name, metrics):
    na = MetricResult('yellow', 'Not assessed in this live screen')
    return ElectrodeResult(name, metrics.get('gain', na), na, na, na, extra=metrics)


def unavailable(names, reason, color='gray'):
    return [electrode(n, {'live': MetricResult(color, reason)}) for n in names]


def frame_problem(t, rate, window_s):
    t = np.asarray(t)
    required = round(rate*window_s)
    if len(t) < required:
        return f'Warming up: {len(t)/rate:.1f} / {window_s:g} s'
    if not np.isfinite(t).all():
        return 'Invalid source timestamps'
    dt = np.diff(t)
    if np.any(dt <= 0) or np.any(dt > 1.5/rate):
        return 'Timestamp gap / restart: waiting for a complete continuous window'
    actual = (len(t)-1)/(t[-1]-t[0])
    if abs(actual/rate-1) > .05 or np.std(dt)/np.mean(dt) > .2:
        return 'Source timestamps do not match the nominal sample interval'
    return None


def analyze_sine_window(samples, timestamps, names, scales, rate, config):
    """Independent channel fits; no file tail crop, no cross-channel contamination."""
    started = time.monotonic()
    config.validate(rate)
    samples = np.asarray(samples, float)
    if samples.shape != (len(timestamps), len(names)) or len(scales) != len(names):
        raise ValueError('Channel dimensions do not match the received data')
    if len(set(names)) != len(names) or any(not n.strip() for n in names):
        raise ValueError('Monitored channels need unique, explicit labels')
    problem = frame_problem(timestamps, rate, config.window_s)
    if problem:
        return dict(electrodes=unavailable(names, problem), elapsed_s=0., valid=False,
                    reason=problem, start_s=None, end_s=None)
    spectrum = BenchSpectrumAnalyzer(config.limits)
    gain = AmplitudePeakGainError(config.limits)
    record = InputRecord('LIVE', '', frequency_hz=config.frequency_hz,
                         input_mVpp=config.input_mVpp, input_confirmed=config.input_confirmed, waveform='sine')
    results = []
    for i, name in enumerate(names):
        scale = scales[i]
        if scale is None or not np.isfinite(scale) or scale <= 0:
            results.extend(unavailable([name], 'Voltage unit unknown: confirm the LSL unit/conversion', 'yellow'))
            continue
        if not config.mapping_confirmed:
            results.extend(unavailable([name], 'Confirm the selected stream and physical channel mapping', 'yellow'))
            continue
        y = samples[:, i]*scale
        integrity = MetricResult('green', 'Finite, varying samples; hardware rail limits not available')
        if not np.isfinite(y).all():
            results.append(electrode(name, {'live': MetricResult('red', 'Nonfinite signal samples; inspect this channel')}))
            continue
        pp = float(np.ptp(y))
        if pp < config.limits.min_response_uVpp:
            results.append(electrode(name, {'live': MetricResult('red', 'Near-flat / no measurable sine response', {'raw_uVpp': pp})}))
            continue
        extra = spectrum.analyze(y, rate, config.frequency_hz)
        values = extra['frequency'].values
        fitted_frequency = float(values.get('measured_hz', config.frequency_hz))
        t = np.arange(len(y))/rate
        mat = np.column_stack((np.sin(2*np.pi*fitted_frequency*t), np.cos(2*np.pi*fitted_frequency*t), np.ones(len(t)), t-t.mean()))
        beta = np.linalg.lstsq(mat, y, rcond=None)[0]
        amplitude = float(2*np.hypot(beta[0], beta[1]))
        residual = y-mat@beta
        residual_pct = float(100*np.sqrt(np.mean(residual**2))/max(amplitude/(2*np.sqrt(2)),1e-12))
        step_pct = float(100*np.max(np.abs(np.diff(residual)))/max(amplitude,1e-12))
        reasons = []
        if amplitude < config.limits.min_response_uVpp:
            reasons.append('no_reliable_sine_response')
        if residual_pct > config.limits.max_residual_pct:
            reasons.append('large_sine_fit_residual')
        if step_pct > config.limits.max_residual_step_pct:
            reasons.append('abrupt_residual_step')
        fit = dict(amplitude_pp_mV=amplitude/1000, quality_reasons=reasons)
        gain_metric = gain.evaluate(fit, record)
        quality = MetricResult('red' if reasons else 'green',
            'Signal shape: '+', '.join(reasons) if reasons else 'Sine shape within the configured residual limits',
            dict(residual_pct=residual_pct, residual_step_pct=step_pct, raw_uVpp=pp))
        # A narrow nominal search alone must not hide an entirely different tone.
        fft = np.abs(np.fft.rfft((y-y.mean())*np.hanning(len(y))))
        fft[0] = 0
        dominant = float(np.argmax(fft)*rate/len(y))
        if abs(dominant-config.frequency_hz) > max(2*rate/len(y), config.frequency_hz*config.limits.frequency_search_pct/100):
            quality = MetricResult('red', f'Dominant tone {dominant:.3f} Hz is inconsistent with the declared sine input', {'dominant_hz':dominant})
        components = dict(gain=gain_metric, shape=quality, integrity=integrity, **extra)
        # Timing, independent repeats, and linearity are not live health components.
        summary = combine([components[k] for k in ('gain','shape','snr','thd','frequency')])
        summary.values = dict(output_mVpp=amplitude/1000, frequency_hz=fitted_frequency,
                              gain_error_pct=gain_metric.values.get('gain_error_pct'),
                              thd_pct=extra['thd'].values.get('thd_pct'), snr_db=extra['snr'].values.get('snr_db'))
        components['live'] = summary
        results.append(electrode(name, components))
    return dict(electrodes=results, elapsed_s=time.monotonic()-started, valid=True,
                reason='', start_s=float(timestamps[0]), end_s=float(timestamps[-1]))


def analyze_live_window(samples, timestamps, names, scales, rate, config):
    if config.profile == 'sine':
        return analyze_sine_window(samples, timestamps, names, scales, rate, config)
    from modules.ecg_quality import ECGQualityAnalyzer
    import copy
    started = time.monotonic()
    config.validate(rate)
    samples = np.asarray(samples, float)
    if samples.shape != (len(timestamps), len(names)) or len(scales) != len(names):
        raise ValueError('Channel dimensions do not match the received data')
    if len(set(names)) != len(names) or any(not n.strip() for n in names):
        raise ValueError('Monitored channels need unique labels')
    problem = frame_problem(timestamps, rate, config.window_s)
    if problem:
        return dict(electrodes=unavailable(names, problem), elapsed_s=0., valid=False,
                    reason=problem, start_s=None, end_s=None)
    settings = copy.deepcopy(config.limits)
    settings.ecg_window_s = config.window_s
    settings.ecg_hop_s = config.hop_s
    analyzer = ECGQualityAnalyzer(settings)
    results = []
    for i, name in enumerate(names):
        scale = scales[i]
        if not config.mapping_confirmed:
            results.extend(unavailable([name], 'Verify physical channel mapping first', 'yellow'))
        elif scale is None or not np.isfinite(scale) or scale <= 0:
            results.extend(unavailable([name], 'Voltage unit unknown: confirm conversion', 'yellow'))
        elif not np.isfinite(samples[:,i]).all():
            results.extend(unavailable([name], 'Missing / non-finite signal samples', 'red'))
        else:
            metrics = analyzer.analyze_window(samples[:,i]*scale, rate)
            metrics['integrity'].message += '; ADC rail limits unavailable: clipping not assessed'
            metrics['live'] = copy.deepcopy(metrics['ecg_quality'])
            metrics['live'].message += '; prototype quality criteria, not an electrode-damage diagnosis'
            results.append(electrode(name, metrics))
    return dict(electrodes=results, elapsed_s=time.monotonic()-started, valid=True,
                reason='', start_s=float(timestamps[0]), end_s=float(timestamps[-1]))


class Confirmation:
    """Show first abnormal finding immediately; label persistence after distinct windows."""
    def __init__(self):
        self.counts = {}
        self.last_end = None

    def reset(self):
        self.counts.clear(); self.last_end = None

    def apply(self, result):
        if not result['valid']:
            self.reset(); return result
        if result['end_s'] == self.last_end:
            return result
        self.last_end = result['end_s']
        for item in result['electrodes']:
            metric = item.metric('live')
            old = self.counts.get(item.name, ('gray', 0))
            count = old[1]+1 if old[0] == metric.color else 1
            self.counts[item.name] = (metric.color,count)
            metric.values['consecutive_windows'] = count
            metric.values['persistent_alert'] = metric.color == 'red' and count >= 2
        return result
