"""Use the project's LSL environment when a source entry was opened with another Python."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys


def project_python():
    repo = Path(__file__).resolve().parent
    local = repo / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if local.is_file():
        return local
    # Compatibility for this existing lab checkout; fresh clones use .venv.
    return repo.parent / '.venv-lsl' / 'Scripts' / 'python.exe'


def ensure_project_runtime():
    # Frozen builds must bundle their own dependencies. Importing a GUI module
    # from another application must not restart that application's process.
    if getattr(sys, 'frozen', False) or importlib.util.find_spec('pylsl') is not None:
        return
    target = project_python()
    if (not target.is_file() or Path(sys.executable).resolve() == target.resolve()
            or os.environ.get('ELECTRODE_QA_RUNTIME_HANDOFF') == str(target)):
        return
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    try:
        probe = subprocess.run([str(target), '-c', 'import tkinter,numpy,scipy,matplotlib,pylsl'],
                               capture_output=True, timeout=15, creationflags=flags)
        if probe.returncode:
            return
        env = os.environ.copy()
        env['ELECTRODE_QA_RUNTIME_HANDOFF'] = str(target)
        entry = str(Path(sys.argv[0]).resolve())
        subprocess.Popen([str(target), entry, *sys.argv[1:]], env=env, creationflags=flags)
    except (OSError, subprocess.TimeoutExpired):
        return
    raise SystemExit(0)
