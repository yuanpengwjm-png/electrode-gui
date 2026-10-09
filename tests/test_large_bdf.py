"""Disk-backed reads and channel-wise fits retain native-rate measurements."""
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
import unittest
import zipfile
import numpy as np
from scipy.optimize import minimize_scalar
from config import AnalysisSettings
from services.analysis_service import AnalysisService
from services.demo_data import create_demo, create_mode_demo
from modules.sine_fitter import SineFitter
from utils.array_store import ArrayStore
from utils.bdf_reader import BdfReader
from utils.numerics import sine_design
from test_analysis import fixture_folder


class LargeBdfTests(unittest.TestCase):
    def test_disk_and_ram_reads_identical_for_bdf_and_zip_and_cleanup(self):
        with fixture_folder() as folder:
            record = create_demo(folder/'inputs', 3)[0]
            names = ['EXG3', 'EXG1']
            expected, fs, metadata = BdfReader().read(record, names)
            archive = folder/'input.zip'
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
                z.write(record.path, 'test.bdf')
            for zipped in (False, True):
                if zipped:
                    record.path, record.member = str(archive), 'test.bdf'
                reader = BdfReader(folder/'cache', max_memory_bytes=1)
                with reader.open_data(record, names) as (actual, rate, header):
                    self.assertIsInstance(actual, np.memmap)
                    self.assertTrue(actual.flags.f_contiguous)
                    np.testing.assert_array_equal(actual, expected)
                    self.assertEqual((rate, header), (fs, metadata))
                self.assertEqual(list((folder/'cache').iterdir()), [])
            with self.assertRaisesRegex(RuntimeError, 'intentional'):
                with reader.open_data(record, names):
                    raise RuntimeError('intentional analysis failure')
            self.assertEqual(list((folder/'cache').iterdir()), [])

    def test_native_channel_fit_matches_original_vectorized_formula(self):
        s = AnalysisSettings()
        fs = 2048
        t = np.arange(fs*4)/fs
        rng = np.random.default_rng(23)
        x = 50000*np.sin(2*np.pi*5.013*(t[:, None]-np.array([0., .002, -.001])))
        x += np.array([250., -800., 310.]) + t[:, None]*np.array([140., -25., 13.])
        x += rng.normal(0, 3, x.shape)
        # Independent reproduction of the pre-refactor vectorized computation.
        trace = np.median(x-np.median(x, axis=0), axis=1)
        step = max(1, len(t)//4000)
        ts, ys = t[::step], trace[::step]
        def objective(f):
            b = sine_design(ts, f)
            return float(np.mean((ys-b @ np.linalg.lstsq(b, ys, rcond=None)[0])**2))
        grid = np.linspace(4.75, 5.25, 31)
        best = int(np.argmin([objective(f) for f in grid]))
        frequency = minimize_scalar(objective, bounds=(grid[max(0,best-1)], grid[min(30,best+1)]),
                                    method='bounded', options={'xatol':1e-10}).x
        basis = sine_design(t, frequency)
        beta = np.linalg.lstsq(basis, x, rcond=None)[0]
        expected = x-(beta[2]+(t-t.mean())[:, None]*beta[3])
        fits, lazy = SineFitter(s).fit(x, fs, 5., lazy=True)
        for i, fit in enumerate(fits):
            self.assertAlmostEqual(fit['fitted_frequency_hz'], frequency, places=10)
            self.assertAlmostEqual(fit['amplitude_pp_mV'], 2*np.hypot(beta[0,i],beta[1,i])/1000, places=9)
            self.assertAlmostEqual(fit['residual_rms_uV'], np.sqrt(np.mean((x[:,i]-basis@beta[:,i])**2)), places=7)
            np.testing.assert_allclose(lazy.column(i), expected[:,i], atol=1e-7, rtol=0)

    def test_all_modes_use_disk_context_and_match_ram_results(self):
        with fixture_folder() as folder:
            for mode in ('bench_sine', 'bench_pulse', 'ecg'):
                records = create_mode_demo(folder/mode, 3, mode)[:1]
                settings = AnalysisSettings(analysis_mode=mode, bench_windows=True,
                                            bench_window_s=1, bench_hop_s=1)
                names = ['EXG1', 'EXG2', 'EXG3']
                ram = AnalysisService(settings)
                expected = ram.analyze(records, names, 'EXG1')
                disk = AnalysisService(settings)
                disk.reader = BdfReader(folder/'cache', max_memory_bytes=1)
                with patch.object(disk.reader, 'read', side_effect=AssertionError('Full in-memory read must not be used')):
                    actual = disk.analyze(records, names, 'EXG1')
                a, b = asdict(actual), asdict(expected)
                a.pop('elapsed_s'); b.pop('elapsed_s')
                self.assertEqual(a, b)
                self.assertEqual(list((folder/'cache').iterdir()), [])

    def test_low_disk_space_fails_clearly_without_leaking_cache(self):
        with fixture_folder() as folder:
            with patch('utils.array_store.shutil.disk_usage') as usage:
                usage.return_value.free = 0
                with self.assertRaisesRegex(ValueError, 'Insufficient disk space'):
                    with ArrayStore(folder/'cache', max_memory_bytes=1) as store:
                        store.empty((100, 3))
            self.assertEqual(list((folder/'cache').iterdir()), [])

    def test_directory_cleanup_lock_does_not_discard_completed_work(self):
        with fixture_folder() as folder:
            with self.assertWarnsRegex(RuntimeWarning, 'cleanup incomplete'):
                with patch.object(Path, 'rmdir', side_effect=PermissionError('simulated sync lock')):
                    with ArrayStore(folder/'cache', max_memory_bytes=1) as store:
                        array = store.empty((100, 3))
                        array[:] = 2
                        measured = float(array[:, 1].mean())
            self.assertEqual(measured, 2)
            self.assertEqual(list((folder/'cache').rglob('*.float64')), [])


if __name__ == '__main__':
    unittest.main()
