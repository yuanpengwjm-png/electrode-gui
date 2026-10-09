"""Synthetic BDF writer used only by demo generation and tests."""
import numpy as np

def write_demo_bdf(path, x, fs):
    """Minimal continuous BDF fixture writer; x is in microvolts."""
    def fixed(value, width):
        b = str(value).encode("ascii")
        if len(b) > width:
            raise ValueError("Demo header field too long")
        return b.ljust(width)
    n, nc = x.shape
    if n % fs:
        raise ValueError("Demo length must contain whole one-second records")
    header = (b"\xffBIOSEMI" + fixed("Synthetic QA", 80) + fixed("Sine sweep", 80)
              + b"01.01.2600.00.00" + fixed(256*(nc+1), 8) + fixed("24BIT", 44)
              + fixed(n//fs, 8) + fixed(1, 8) + fixed(nc, 4))
    fields = [([f"EXG{i+1}" for i in range(nc)], 16), ([""]*nc, 80), (["uV"]*nc, 8),
              ([-262144]*nc, 8), ([262143]*nc, 8), ([-8388608]*nc, 8), ([8388607]*nc, 8),
              (["Synthetic no filter"]*nc, 80), ([fs]*nc, 8), ([""]*nc, 32)]
    for values, width in fields:
        header += b"".join(fixed(v, width) for v in values)
    d = np.rint((x+262144)*16777215/524287-8388608).astype(np.int64)
    if np.any((d < -8388608) | (d > 8388607)):
        raise ValueError("Synthetic fixture exceeds the BDF range")
    with path.open("wb") as f:
        f.write(header)
        for rec in range(n//fs):
            values = (d[rec*fs:(rec+1)*fs].T.reshape(-1) & 0xffffff).astype(np.uint32)
            packed = np.column_stack((values & 255, (values >> 8) & 255, (values >> 16) & 255)).astype(np.uint8)
            f.write(packed.tobytes())
