"""Header discovery and calibrated 24-bit BDF reading, including ZIP members."""
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import re
import zipfile

from models import InputRecord
from utils.numerics import read_bdf_stream
from utils.array_store import ArrayStore


@dataclass
class BdfInfo:
    labels: list[str]
    voltage_labels: list[str]
    sample_rates: dict[str, float]
    duration_s: float


class BdfReader:
    def __init__(self, cache_root=None, max_memory_bytes=64 * 1024**2):
        self.cache_root = cache_root
        self.max_memory_bytes = max_memory_bytes

    @contextmanager
    def _open(self, record):
        path = Path(record.path)
        if record.member:
            with zipfile.ZipFile(path) as z:
                info = z.getinfo(record.member)
                with z.open(info) as stream:
                    yield stream, info.file_size
        else:
            with path.open("rb") as stream:
                yield stream, path.stat().st_size

    def inspect(self, record: InputRecord) -> BdfInfo:
        with self._open(record) as (stream, size):
            h = stream.read(256)
            if len(h) != 256 or h[0] != 255 or b"BDF+D" in h[192:236]:
                raise ValueError("A continuous 24-bit BDF file is required; BDF+D is unsupported")
            nc, hb = int(h[252:256]), int(h[184:192])
            nr, duration = int(h[236:244]), float(h[244:252])
            if nc < 1 or nc > 4096 or hb != 256*(nc+1) or duration <= 0:
                raise ValueError("Invalid BDF header")
            fields = []
            for width in (16, 80, 8, 8, 8, 8, 8, 80, 8, 32):
                b = stream.read(width*nc)
                if len(b) != width*nc:
                    raise ValueError("Incomplete BDF header")
                fields.append([b[i*width:(i+1)*width].decode("latin1").strip() for i in range(nc)])
            samples = [int(s) for s in fields[8]]
            if any(s <= 0 for s in samples):
                raise ValueError("Invalid BDF samples per record")
            actual, remainder = divmod(size-hb, 3*sum(samples))
            if actual <= 0 or remainder or nr not in (-1, actual):
                raise ValueError("Incomplete BDF or record count mismatch")
            labels = fields[0]
            voltage = [label for label, unit in zip(labels, fields[2])
                       if unit in ("uV", "µV", "mV", "V") and not re.search(r"status|annotation", label, re.I)]
            return BdfInfo(labels, voltage, dict(zip(labels, [s/duration for s in samples])), actual*duration)

    def read(self, record: InputRecord, channels: list[str]):
        if not channels or len(set(channels)) != len(channels):
            raise ValueError("Select unique electrode channels")
        with self._open(record) as (stream, size):
            return read_bdf_stream(stream, size, channels)

    @contextmanager
    def open_data(self, record: InputRecord, channels: list[str], progress=lambda _: None):
        """Decode record by record; release scratch data even if analysis fails."""
        if not channels or len(set(channels)) != len(channels):
            raise ValueError('Select unique electrode channels')
        with ArrayStore(self.cache_root, self.max_memory_bytes) as store:
            with self._open(record) as (stream, size):
                data = read_bdf_stream(stream, size, channels, allocator=store.empty, progress=progress)
            yield data

    @staticmethod
    def choose_channels(info: BdfInfo, count: int, pool="EXG"):
        if pool == "EXG":
            names = [s for s in info.voltage_labels if re.fullmatch(r"EXG\d+", s, re.I)]
        elif pool == "scalp":
            names = [s for s in info.voltage_labels if not re.fullmatch(r"EXG\d+", s, re.I)]
        else:
            names = info.voltage_labels
        if count < 1 or count > len(names):
            raise ValueError(f"This channel group has {len(names)} voltage channels; cannot select {count} electrodes")
        return names[:count]
