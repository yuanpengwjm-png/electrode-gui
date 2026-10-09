"""Tested BDF and sine kernels extracted from the existing bench-qa tool.
No GUI imports and no runtime dependency on bench-qa.
"""
import math
import numpy as np
from scipy.optimize import minimize_scalar


def read_bdf_stream(stream, size, selected, allocator=None, progress=lambda _: None):
    """Read only selected channels from continuous 24-bit BDF, in microvolts."""
    h = stream.read(256)
    if len(h) != 256 or h[0] != 255:
        raise ValueError("Expected a 24-bit BDF file")
    if b"BDF+D" in h[192:236]:
        raise ValueError("Discontinuous BDF+D is unsupported; do not concatenate its segments")
    nc, hb = int(h[252:256]), int(h[184:192])
    nr, duration = int(h[236:244]), float(h[244:252])
    if nc < 1 or hb != 256 * (nc + 1) or duration <= 0:
        raise ValueError("Invalid BDF header")
    fields = []
    for width in (16, 80, 8, 8, 8, 8, 8, 80, 8, 32):
        b = stream.read(width * nc)
        if len(b) != width * nc:
            raise ValueError("Truncated BDF channel header")
        fields.append([b[j*width:(j+1)*width].decode("latin1").strip() for j in range(nc)])
    ns = np.array(fields[8], dtype=int)
    if np.any(ns <= 0):
        raise ValueError("Invalid samples per record")
    indices = []
    for label in selected:
        if fields[0].count(label) != 1:
            raise ValueError(f"Missing or ambiguous channel: {label}")
        indices.append(fields[0].index(label))
    if len(set(ns[indices])) != 1:
        raise ValueError("Selected channels have different sampling rates")
    actual, remainder = divmod(size - hb, int(3 * ns.sum()))
    if actual <= 0 or remainder or nr not in (-1, actual):
        raise ValueError("Truncated file or BDF record count mismatch")
    n = int(actual * ns[indices[0]])
    if allocator is None and n * len(indices) > 80_000_000:
        raise ValueError("Selected data exceed in-memory read limit; use BdfReader.open_data for disk-backed analysis")
    x = allocator((n, len(indices))) if allocator else np.empty((n, len(indices)), dtype=float, order='F')
    offsets = np.r_[0, np.cumsum(ns)] * 3
    calibrations = []
    for i in indices:
        unit = fields[2][i]
        factor = {"uV": 1., "µV": 1., "mV": 1000., "V": 1e6}.get(unit)
        if factor is None:
            raise ValueError(f"Unsupported BDF physical unit: {unit!r}")
        p0, p1, d0, d1 = (float(fields[k][i]) for k in (3, 4, 5, 6))
        if not all(math.isfinite(v) for v in (p0, p1, d0, d1)) or p1 <= p0 or d1 <= d0:
            raise ValueError("Invalid BDF calibration")
        calibrations.append((p0, p1, d0, d1, factor))
    clipped = np.zeros(len(indices), dtype=int)
    for rec in range(actual):
        if rec % max(1, actual//20) == 0:
            progress(f"Decoding BDF record {rec+1}/{actual}" + (" using disk cache" if isinstance(x, np.memmap) else ""))
        buf = stream.read(int(offsets[-1]))
        if len(buf) != offsets[-1]:
            raise ValueError("Incomplete BDF data record")
        for j, i in enumerate(indices):
            b = np.frombuffer(buf[int(offsets[i]):int(offsets[i+1])], dtype=np.uint8).reshape(-1, 3).astype(np.int32)
            d = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
            d = np.where(d >= 2**23, d - 2**24, d)
            p0, p1, d0, d1, factor = calibrations[j]
            x[rec*ns[i]:(rec+1)*ns[i], j] = ((d-d0)*(p1-p0)/(d1-d0)+p0)*factor
            clipped[j] += np.count_nonzero((d <= d0) | (d >= d1))
    return x, float(ns[indices[0]] / duration), {
        "duration_s": actual * duration,
        "clipped_samples_full_record": dict(zip(selected, clipped.tolist())),
        "physical_limits_uV": {label: [cal[0]*cal[4], cal[1]*cal[4]] for label, cal in zip(selected, calibrations)},
    }


def sine_design(t, f):
    return np.column_stack((np.sin(2*np.pi*f*t), np.cos(2*np.pi*f*t),
                            np.ones(len(t)), t-t.mean()))


def fit_record(x, fs, frequency, settings, coefficients_out=None, progress=lambda _: None):
    """Common frequency, then native-rate fits one electrode at a time.

    Frequency search uses the same median-channel trace and time samples as
    before, without materializing an N-sample by C-channel temporary matrix.
    """
    if x.ndim != 2 or len(x) < 16:
        raise ValueError("Too few samples or nonfinite data")
    if not 0 < frequency < fs / 4:
        raise ValueError("Need at least four samples per nominal sine cycle")
    t = np.arange(len(x)) / fs
    step = max(1, len(t) // 4000)
    ts = t[::step]
    probe = np.empty((len(ts), x.shape[1]))
    for i in range(x.shape[1]):
        y = np.asarray(x[:, i])
        if not np.isfinite(y).all():
            raise ValueError("Too few samples or nonfinite data")
        probe[:, i] = y[::step] - np.median(y)
    ys = np.median(probe, axis=1)
    del probe

    def objective(f):
        b = sine_design(ts, f)
        return float(np.mean((ys-b @ np.linalg.lstsq(b, ys, rcond=None)[0])**2))

    margin = settings["frequency_search_pct"] / 100
    grid = np.linspace(frequency*(1-margin), frequency*(1+margin), 31)
    best = int(np.argmin([objective(f) for f in grid]))
    lo, hi = grid[max(0, best-1)], grid[min(len(grid)-1, best+1)]
    f = float(minimize_scalar(objective, bounds=(lo, hi), method="bounded",
                              options={"xatol": 1e-10}).x)
    b = sine_design(t, f)
    inverse = np.linalg.pinv(b)  # One shared SVD, not one factorization per channel.
    result = []
    for i in range(x.shape[1]):
        progress(f"Fitting native samples: channel {i+1}/{x.shape[1]}")
        y = np.asarray(x[:, i])
        beta = inverse @ y
        if coefficients_out is not None:
            coefficients_out.append(beta)
        residual = y - b @ beta
        amp = float(2*np.hypot(beta[0], beta[1]))
        rms = float(np.sqrt(np.mean(residual**2)))
        reasons = []
        if len(x)/fs*frequency < settings["min_cycles"]:
            reasons.append("too_few_cycles")
        if min(f-grid[0], grid[-1]-f) < frequency*margin*.01:
            reasons.append("frequency_at_search_boundary")
        ratio, jump = None, None
        if amp < settings["min_response_uVpp"]:
            reasons.append("no_reliable_sine_response")
        else:
            ratio = float(100*rms/(amp/(2*np.sqrt(2))))
            jump = float(100*np.max(np.abs(np.diff(residual)))/amp)
            if ratio > settings["max_residual_pct"]:
                reasons.append("large_sine_fit_residual")
            if jump > settings["max_residual_step_pct"]:
                reasons.append("abrupt_residual_step")
        result.append(dict(amplitude_pp_mV=amp/1000, fitted_frequency_hz=f,
                           residual_rms_uV=rms, residual_pct=ratio,
                           residual_step_pct=jump, quality_reasons=reasons))
    return result
