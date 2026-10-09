"""Read BDF/ZIP catalogs without extracting or modifying the original files."""
from pathlib import Path
import re
import zipfile
from models import InputRecord
from utils.bdf_reader import BdfReader


def records_from_paths(paths):
    records = []
    for path in map(Path, paths):
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                members = sorted(n for n in archive.namelist() if n.lower().endswith(".bdf"))
            if not members:
                raise ValueError(f"No BDF files in {path.name}")
        else:
            members = [None]
        for member in members:
            name = Path(member or path.name)
            context = (str(path) + " " + str(member or "")).lower()
            waveform = "ecg" if "ecg" in context else "pulse" if "pulse" in context else "sine" if "sine" in context else "unknown"
            frequency = re.search(r"([\d.]+)hz", name.stem, re.I)
            amplitude = re.search(r"([\d.]+)mv", name.stem, re.I)
            group = name.parent.name if member else path.parent.name
            r = InputRecord(id=f"{name.stem}-{len(records)+1}", path=str(path.resolve()), member=member,
                frequency_hz=float(frequency[1]) if frequency else 5.,
                input_mVpp=float(amplitude[1]) if amplitude else None,
                input_confirmed=False, waveform=waveform, setup_group=group or "default")
            BdfReader().inspect(r)
            records.append(r)
    return records
