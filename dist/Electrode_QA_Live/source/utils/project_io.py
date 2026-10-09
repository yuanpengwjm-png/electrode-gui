"""JSON projects and migration of the earlier electrode experiment config."""
from dataclasses import asdict, fields
from pathlib import Path
import json
import math
from config import AnalysisSettings
from models import InputRecord

UNIT_FACTORS = {"mVpp":1., "mVpeak":2., "mVrms":2*math.sqrt(2), "uVpp":.001, "Vpp":1000.}


def load_project(path):
    path = Path(path).resolve()
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if len({entry.get("group", "default") for entry in data["records"]}) > 1:
        raise ValueError("Load different wiring/experiment groups separately; do not pool them for linearity or repetition")
    records = []
    valid = {f.name for f in fields(InputRecord)}
    for entry in data["records"]:
        if "input_amplitude" in entry:  # previous tool's config, without importing it
            if entry.get("montage", "monopolar") != "monopolar" or "signals" in entry:
                raise ValueError("This project contains differential paths; load individual monopolar electrode channels")
            unit = entry.get("input_unit", "mVpp")
            if unit not in UNIT_FACTORS:
                raise ValueError(f"Convert {unit} to mVpp before loading this project")
            value = entry.get("input_amplitude")
            entry = dict(id=entry["id"], path=entry["path"], member=entry.get("member"), frequency_hz=entry["frequency_hz"],
                input_mVpp=None if value is None else value*UNIT_FACTORS[unit], input_confirmed=entry.get("input_confirmed", False),
                sweep=entry.get("linearity_included", True), repeat_group=entry.get("repeat_group", ""), nominal_mV=entry.get("repeat_nominal_mV"))
        record = InputRecord(**{k:v for k,v in entry.items() if k in valid})
        record.path = str((path.parent/record.path).resolve())
        records.append(record)
    setting_keys = {f.name for f in fields(AnalysisSettings)}
    values = {k:v for k,v in data.get("settings", {}).items() if k in setting_keys}
    if data.get('version', 1) < 3:
        # Old projects stored the former blank defaults as null. Adopt the
        # user's new defaults while preserving any explicit numeric limits.
        defaults = AnalysisSettings()
        for key in ('thd_limit_pct', 'frequency_limit_pct'):
            if values.get(key) is None:
                values[key] = getattr(defaults, key)
    settings = AnalysisSettings(**values)
    settings.validate()
    return records, settings, data.get("channels", []), data.get("reference", "")


def save_project(path, records, settings, channels, reference, display=None):
    payload = dict(version=3, records=[asdict(r) for r in records], settings=asdict(settings), channels=channels, reference=reference)
    if display is not None:
        payload['display'] = display
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
