"""Reusable LSL transport from the validated lsl-check tool; no GUI imports or byte decoding."""
from __future__ import annotations

from collections import deque
import math
import threading
import time
import xml.etree.ElementTree as ET

import numpy as np


def unit_to_uv(unit):
    key = unit.strip().lower().replace('μ', 'u').replace('µ', 'u').replace(' ', '')
    return {'uv': 1., 'microvolt': 1., 'microvolts': 1., 'mv': 1000.,
            'millivolt': 1000., 'millivolts': 1000., 'v': 1e6,
            'volt': 1e6, 'volts': 1e6, 'nv': .001}.get(key)


def metadata(info):
    xml = info.as_xml()
    root = ET.fromstring(xml)
    channels = root.findall('./desc/channels/channel')
    names, units = [], []
    for i in range(info.channel_count()):
        node = channels[i] if i < len(channels) else None
        names.append((node.findtext('label') or node.findtext('name') or '').strip()
                     if node is not None else '')
        units.append((node.findtext('unit') or '').strip() if node is not None else '')
    return dict(name=info.name(), type=info.type(), source_id=info.source_id(),
                uid=info.uid(), hostname=info.hostname(), channel_count=info.channel_count(),
                nominal_srate=info.nominal_srate(), channel_format=info.channel_format(),
                labels=names, units=units, xml=xml,
                demo=info.source_id().startswith('DEMO_BioSemiLSL_'))


class SampleBuffer:
    """Bounded raw-unit buffer; one row = one timestamp, one column = one channel."""
    def __init__(self, channels, rate):
        self.capacity = max(1, min(int(math.ceil(rate * 10)), 64 * 1024**2 // (8 * (channels + 1))))
        self.channels = channels
        self.rate = rate
        self.parts = deque()
        self.count = self.total = self.gaps = self.nonmonotonic = self.nonfinite = 0
        self.last_timestamp = None
        self.last_received = None
        self.first_received = None
        self.started = time.monotonic()
        self.lock = threading.Lock()

    def append(self, samples, timestamps):
        x = np.asarray(samples, dtype=np.float64)
        t = np.asarray(timestamps, dtype=np.float64)
        if x.shape != (len(t), self.channels) or not np.isfinite(t).all():
            raise ValueError('数据维度或时间戳无效')
        if not len(t):
            return
        with self.lock:
            dt = np.diff(t if self.last_timestamp is None else np.r_[self.last_timestamp, t])
            self.gaps += int(np.count_nonzero(dt > 1.5 / self.rate))
            self.nonmonotonic += int(np.count_nonzero(dt <= 0))
            self.nonfinite += int(np.count_nonzero(~np.isfinite(x)))
            self.last_timestamp = float(t[-1])
            self.last_received = time.monotonic()
            if self.first_received is None:
                self.first_received = self.last_received
            self.total += len(t)
            self.parts.append((x.copy(), t.copy()))
            self.count += len(t)
            while self.count > self.capacity:
                a, b = self.parts.popleft()
                excess = self.count - self.capacity
                if len(b) <= excess:
                    self.count -= len(b)
                else:
                    self.parts.appendleft((a[excess:].copy(), b[excess:].copy()))
                    self.count -= excess

    def snapshot(self, columns=None, seconds=10):
        with self.lock:
            n = min(self.count, int(seconds * self.rate))
            rows, stamps = [], []
            for x, t in reversed(self.parts):
                take = min(n, len(t))
                if take:
                    rows.append(x[-take:] if columns is None else x[-take:, columns])
                    stamps.append(t[-take:])
                n -= take
                if not n:
                    break
            stats = dict(total=self.total, buffered=self.count, gaps=self.gaps,
                         nonmonotonic=self.nonmonotonic, nonfinite=self.nonfinite,
                         silence_s=None if self.last_received is None else time.monotonic()-self.last_received,
                         elapsed_s=time.monotonic()-self.started)
            if not stamps:
                return np.empty((0, self.channels if columns is None else len(columns))), np.empty(0), stats
            return np.concatenate(rows[::-1]), np.concatenate(stamps[::-1]), stats


class Receiver(threading.Thread):
    def __init__(self, info, events):
        super().__init__(daemon=True)
        self.info, self.events = info, events
        self.stop_event = threading.Event()
        self.buffer = None
        self.meta = None
        self.failure = None
        self.clock_offset = None

    def stop(self):
        self.stop_event.set()

    def run(self):
        import pylsl
        from pylsl.util import TimeoutError as LSLTimeoutError
        inlet = None
        try:
            # Keep original source timestamps. Store clock correction separately.
            inlet = pylsl.StreamInlet(self.info, max_buflen=3, recover=False)
            inlet.open_stream(timeout=5)
            self.meta = metadata(inlet.info(timeout=5))
            fs, nc = self.meta['nominal_srate'], self.meta['channel_count']
            if not math.isfinite(fs) or fs <= 0 or nc < 1 or nc > 4096:
                raise ValueError('请选择具有正采样率的数值型连续数据流；不支持事件/文本流或超过4096路的流。')
            if self.meta['channel_format'] == pylsl.cf_string:
                raise ValueError('这是文本/事件流，请选择 EEG 数值数据流。')
            self.buffer = SampleBuffer(nc, fs)
            self.events.put(('connected', self))
            last_correction = 0.
            # Limit each pull to ~50 ms and at most 1 million values.
            chunk_size = max(1, min(4096, int(fs*.05), 1000000 // nc))
            while not self.stop_event.is_set():
                x, t = inlet.pull_chunk(timeout=.1, max_samples=chunk_size)
                if len(t):
                    self.buffer.append(x, t)
                if time.monotonic()-last_correction > 2:
                    try:
                        self.clock_offset = float(inlet.time_correction(timeout=0.))
                        last_correction = time.monotonic()
                    except LSLTimeoutError:
                        pass
        except Exception as exc:
            self.failure = str(exc)
            self.events.put(('error', (self, str(exc))))
        finally:
            if inlet is not None:
                try:
                    inlet.close_stream()
                except Exception:
                    pass
            self.events.put(('ended', self))


class DemoOutlet(threading.Thread):
    """An actual LSL outlet, unmistakably labeled as synthetic."""
    def __init__(self):
        import uuid
        super().__init__(daemon=True)
        self.source_id = 'DEMO_BioSemiLSL_'+uuid.uuid4().hex
        self.stop_event = threading.Event()
        self.ready = threading.Event()
        self.error = None

    def stop(self):
        self.stop_event.set()

    def run(self):
        try:
            import pylsl
            fs = 1024
            info = pylsl.StreamInfo('DEMO_ONLY_5Hz_10mVpp', 'EEG', 2, fs, 'float32', self.source_id)
            channels = info.desc().append_child('channels')
            for name in ('C11', 'C12'):
                ch = channels.append_child('channel')
                ch.append_child_value('label', name)
                ch.append_child_value('unit', 'uV')
            outlet = pylsl.StreamOutlet(info, chunk_size=32)
            self.ready.set()
            start, n = pylsl.local_clock(), 0
            while not self.stop_event.is_set():
                due = start+(n+32)/fs
                if self.stop_event.wait(max(0, due-pylsl.local_clock())):
                    break
                t = np.arange(n, n+32)/fs
                x = np.column_stack((5000*np.sin(2*np.pi*5*t)+1300,
                                     5000*np.sin(2*np.pi*5*t+.3)-900))
                outlet.push_chunk(x.tolist(), timestamp=start+(n+31)/fs)
                n += 32
        except Exception as exc:
            self.error = str(exc)
            self.ready.set()
