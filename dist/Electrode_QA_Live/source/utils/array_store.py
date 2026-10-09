"""Per-analysis scratch arrays: small arrays in RAM, large arrays on disk."""
from pathlib import Path
import shutil
import tempfile
import uuid
import warnings
import numpy as np


class ArrayStore:
    def __init__(self, root=None, max_memory_bytes=64 * 1024**2):
        self.root = Path(root) if root else Path(tempfile.gettempdir())/'electrode-qa-cache'
        self.max_memory_bytes = max_memory_bytes
        self.folder = None
        self.arrays = []

    def __enter__(self):
        return self

    def empty(self, shape):
        size = int(np.prod(shape)) * np.dtype('float64').itemsize
        if size <= self.max_memory_bytes:
            return np.empty(shape, dtype='float64', order='F')
        self.root.mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(self.root).free < size + 256 * 1024**2:
            raise ValueError(f'Insufficient disk space for temporary BDF cache: need about {size/1024**3:.2f} GiB plus 256 MiB free')
        if self.folder is None:
            self.folder = self.root/uuid.uuid4().hex
            self.folder.mkdir()
        path = self.folder/f'{len(self.arrays)}.float64'
        # Columns are contiguous: each electrode can be fitted without reading
        # every other channel's disk pages again.
        try:
            array = np.memmap(path, mode='w+', dtype='float64', shape=shape, order='F')
        except Exception:
            path.unlink(missing_ok=True)
            raise
        self.arrays.append((array, path))
        return array

    def __exit__(self, exc_type, exc, traceback):
        notices = []
        for array, path in self.arrays:
            array._mmap.close()
            try:
                path.unlink()
            except OSError as error:
                notices.append(f'{path}: {error}')
        self.arrays.clear()
        if self.folder is not None:
            try:
                self.folder.rmdir()  # Only our own now-empty UUID directory.
            except OSError as error:
                notices.append(f'{self.folder}: {error}')
        # A sync service / antivirus lock must not discard completed metrics or
        # replace the original analysis exception with a cleanup exception.
        if notices:
            warnings.warn('Temporary BDF cache cleanup incomplete: ' + '; '.join(notices), RuntimeWarning)
        return False
