"""Known synthetic faults, clearly separated from real laboratory data."""
from pathlib import Path
import numpy as np
from models import InputRecord
from utils.demo_bdf import write_demo_bdf


def create_demo(folder, count=8):
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    fs = 2048
    t = np.arange(fs*4)/fs
    rng = np.random.default_rng(31123921)
    records = []
    for index, level in enumerate((50, 100, 150, 100, 100)):
        amplitude = np.full(count, float(level))
        delay = np.zeros(count)
        if count > 1: amplitude[1] *= .85
        if count > 2: amplitude[2] *= .955
        if count > 3: delay[3] = .003
        if count > 4: delay[4] = .00085
        if count > 5 and level == 150: amplitude[5] = 115
        if count > 7 and index == 3: amplitude[7] *= .96
        if count > 7 and index == 4: amplitude[7] *= 1.04
        x = 500*amplitude*np.sin(2*np.pi*5*(t[:, None]-delay))
        x += 2200+150*t[:, None]+rng.normal(0, .2, x.shape)
        if count > 6: x[(t > 1.5) & (t < 1.6), 6] += 20000
        path = folder/f"DEMO_{count}ch_run{index+1}_{level}mVpp.bdf"
        write_demo_bdf(path, x, fs)
        records.append(InputRecord(path.stem, str(path), 5., level, True, index < 3,
                                   "100mV-repeat" if level == 100 else "", nominal_mV=level))
    return records


def create_mode_demo(folder, count, mode):
    if mode == "bench_sine":
        return create_demo(folder, count)
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    fs = 1024
    t = np.arange(fs*30)/fs
    rng = np.random.default_rng(3921)
    x = np.zeros((len(t), count))
    for ch in range(count):
        if mode == "bench_pulse":
            delay = .004 if ch == 2 else 0.
            level = 85000 if ch == 1 else 100000
            x[:, ch] = level * (((t-delay)*2 % 1) < .15) + rng.normal(0, 2, len(t))
        else:
            for centre in np.arange(.6, 30, 1.):
                z = t-centre
                x[:, ch] += (1000*np.exp(-.5*(z/.010)**2) - 220*np.exp(-.5*((z-.03)/.008)**2)
                             + 180*np.exp(-.5*((z-.26)/.06)**2))
            x[:, ch] += rng.normal(0, 2, len(t))
            if ch == 1: x[:, ch] += 1500*np.sin(2*np.pi*.3*t)
            if ch == 2: x[(t >= 12) & (t < 18), ch] = 0
            if ch == 3: x[:, ch] += rng.normal(0, 650, len(t))
    path = folder/f"DEMO_{mode}_{count}ch.bdf"
    write_demo_bdf(path, x, fs)
    return [InputRecord(path.stem, str(path), 2., 100. if mode == "bench_pulse" else None,
                        mode == "bench_pulse", False, waveform="pulse" if mode == "bench_pulse" else "ecg")]


def create_timeline_demo(folder, count):
    """31 s sine (30 s after default crop); channel 2 loses amplitude at 10-20 s."""
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    fs = 8192
    t = np.arange(31*fs)/fs
    x = np.repeat((50000*np.sin(2*np.pi*5*t)+2200)[:, None], count, axis=1)
    if count > 1:
        fault = (t >= 10) & (t < 20)
        x[fault, 1] = 25000*np.sin(2*np.pi*5*t[fault])+2200
    x += np.random.default_rng(3921).normal(0, 2, x.shape)
    path = folder/f'DEMO_timeline_sine_{count}ch.bdf'
    write_demo_bdf(path, x, fs)
    return [InputRecord(path.stem, str(path), 5., 100., True, False, waveform='sine')]
