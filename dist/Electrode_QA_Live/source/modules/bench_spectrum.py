"""Sine-only frequency, noise and harmonic measurements, independent of the GUI.

Noise is the band-limited residual AFTER the specified harmonics are removed.
SINAD adds those harmonics back to the denominator. No clinical limits are implied.
"""
import math
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.signal import resample_poly, welch
from models import MetricResult


class BenchSpectrumAnalyzer:
    def __init__(self, settings):
        self.settings = settings

    def frequency_result(self, measured, nominal, reliable=True):
        error = 100 * (measured / nominal - 1)
        values = dict(measured_hz=float(measured), nominal_hz=nominal, error_pct=float(error))
        if not reliable:
            return MetricResult("yellow", "Frequency estimate is unreliable or at the search boundary", values)
        limit = self.settings.frequency_limit_pct
        if limit is None:
            return MetricResult("yellow", f"Frequency {measured:.6f} Hz ({error:+.4f}%); set a calibrated tolerance", values)
        return MetricResult(self.settings.color(error, limit), f"Frequency error {error:+.4f}%", values)

    def analyze(self, samples_uV, fs, nominal):
        s = self.settings
        if nominal * 2 >= min(s.bench_bandwidth_hz, fs / 2):
            m = MetricResult("yellow", "Analysis bandwidth must include the fundamental and at least its second harmonic")
            return {key: m for key in ("snr", "sinad", "thd", "frequency")}
        # Anti-aliased reduction for fast tone fitting. The measurement band is
        # explicitly limited below both the original and reduced Nyquist limits.
        factor = max(1, int(fs // max(512., s.bench_bandwidth_hz * 4)))
        y = resample_poly(np.asarray(samples_uV, float), 1, factor) if factor > 1 else np.asarray(samples_uV, float)
        rate = fs / factor
        t = np.arange(len(y)) / rate
        t = t - t.mean()
        band = min(s.bench_bandwidth_hz, fs * .45, rate * .45)
        margin = s.frequency_search_pct / 100
        low, high = nominal * (1 - margin), nominal * (1 + margin)
        stride = max(1, len(y) // 4000)
        ts, ys = t[::stride], y[::stride]

        def objective(f):
            b = np.column_stack((np.sin(2*np.pi*f*ts), np.cos(2*np.pi*f*ts), np.ones(len(ts)), ts))
            return float(np.mean((ys - b @ np.linalg.lstsq(b, ys, rcond=None)[0]) ** 2))

        grid = np.linspace(low, high, 25)
        index = int(np.argmin([objective(f) for f in grid]))
        f = float(minimize_scalar(objective, bounds=(grid[max(0,index-1)], grid[min(len(grid)-1,index+1)]),
                                  method="bounded", options={"xatol": 1e-9}).x)
        order = min(int(s.harmonic_count), int(band // f))
        columns = [np.ones(len(t)), t]
        for h in range(1, order + 1):
            columns.extend((np.sin(2*np.pi*h*f*t), np.cos(2*np.pi*h*f*t)))
        design = np.column_stack(columns)
        beta = np.linalg.lstsq(design, y, rcond=None)[0]
        tone_power = np.array([(beta[2*h]**2 + beta[2*h+1]**2) / 2 for h in range(1, order+1)])
        fundamental = float(tone_power[0])
        residual = y - design @ beta
        frequencies, psd = welch(residual, rate, nperseg=min(len(y), max(32, int(rate*2))), detrend="constant")
        df = frequencies[1] - frequencies[0]
        noise_power = float(np.sum(psd[(frequencies > 0) & (frequencies <= band)]) * df)
        harmonic_power = float(tone_power[1:].sum())
        valid = len(y)/rate*nominal >= s.min_cycles and fundamental > (s.min_response_uVpp/(2*np.sqrt(2)))**2
        valid &= min(f-low, high-f) > nominal*margin*.01
        floor = max(fundamental, 1e-24) * 1e-16  # finite 160 dB numerical reporting ceiling
        snr = float(10*np.log10(max(fundamental, 1e-24)/max(noise_power, floor)))
        sinad = float(10*np.log10(max(fundamental, 1e-24)/max(noise_power+harmonic_power, floor)))
        thd = float(100*np.sqrt(harmonic_power/max(fundamental, 1e-24)))
        values = dict(frequency_hz=f, bandwidth_hz=band, highest_harmonic=order,
                      noise_rms_uV=math.sqrt(noise_power), fundamental_rms_uV=math.sqrt(fundamental),
                      snr_db=snr, sinad_db=sinad, thd_pct=thd,
                      definition="SNR excludes fitted harmonics 2..N; SINAD includes them; DC/drift excluded")
        if not valid:
            unavailable = MetricResult("yellow", "Insufficient cycles/response or frequency outside search range", values)
            return dict(snr=unavailable, sinad=unavailable, thd=unavailable,
                        frequency=self.frequency_result(f, nominal, False))
        color = "green" if snr >= s.snr_good_db else "yellow" if snr >= s.snr_bad_db else "red"
        thd_color = "yellow" if s.thd_limit_pct is None else s.color(thd, s.thd_limit_pct)
        return dict(
            snr=MetricResult(color, f"SNR {snr:.2f} dB, 0–{band:g} Hz (specified harmonics excluded)", values),
            sinad=MetricResult("yellow", f"SINAD {sinad:.2f} dB; descriptive measurement, no acceptance limit", values),
            thd=MetricResult(thd_color, f"THD {thd:.4f}% through harmonic {order}" +
                             ("; set a calibrated tolerance" if s.thd_limit_pct is None else ""), values),
            frequency=self.frequency_result(f, nominal))
