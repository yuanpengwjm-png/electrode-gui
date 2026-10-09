"""Known-input tests: real BDF bytes, fault classes, matching and UI wiring."""
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
import copy
import json
import shutil
import time
import unittest
import uuid
import numpy as np

from config import AnalysisSettings
from models import InputRecord
from modules.gain_error import AmplitudePeakGainError
from modules.sine_fitter import SineFitter
from modules.time_synchronization import TimeSynchronizationAnalyzer, ZeroCrossingDetector
from services.analysis_service import AnalysisService
from services.demo_data import create_demo
from utils.bdf_reader import BdfReader
from utils.project_io import save_project, load_project
from utils.report_exporter import ReportExporter


@contextmanager
def fixture_folder():
    # Inherit the workspace ACL; Windows Python 3.13's tempfile 0700 ACL can
    # exclude a restricted process token from its own temporary directory.
    root = (Path(__file__).resolve().parents[1]/"output/test-fixtures").resolve()
    root.mkdir(parents=True, exist_ok=True)
    folder = root/uuid.uuid4().hex
    folder.mkdir()
    try:
        yield folder
    finally:
        if folder.resolve().parent != root:
            raise RuntimeError("Refusing cleanup outside fixture root")
        shutil.rmtree(folder)


class AnalysisTests(unittest.TestCase):
    def test_bdf_metadata_scaling_and_dynamic_channel_count(self):
        with fixture_folder() as folder:
            records = create_demo(folder, 12)
            reader = BdfReader()
            info = reader.inspect(records[0])
            self.assertEqual(len(info.voltage_labels), 12)
            self.assertEqual(info.sample_rates["EXG1"], 2048)
            self.assertEqual(info.duration_s, 4)
            chosen = reader.choose_channels(info, 3)
            x, fs, _ = reader.read(records[0], chosen)
            self.assertEqual(x.shape, (8192, 3))
            fits, _ = SineFitter(AnalysisSettings()).fit(x, fs, 5)
            self.assertAlmostEqual(fits[0]["amplitude_pp_mV"], 50, places=3)
            with self.assertRaises(ValueError):
                reader.choose_channels(info, 13)

    def test_known_fault_classes_and_full_export(self):
        with fixture_folder() as folder:
            records = create_demo(folder/"inputs", 8)
            # This original four-second fixture checks its full event counts.
            result = AnalysisService(AnalysisSettings(exclude_last_s=0)).analyze(records, [f"EXG{i}" for i in range(1,9)], "EXG1")
            a = {e.name:e for e in result.electrodes}
            self.assertEqual(a["EXG1"].gain.color, "green")
            self.assertEqual(a["EXG1"].synchronization.color, "yellow")
            self.assertEqual(a["EXG2"].gain.color, "red")
            self.assertEqual(a["EXG2"].linearity.color, "green")
            self.assertEqual(a["EXG3"].gain.color, "yellow")
            self.assertEqual(a["EXG4"].synchronization.color, "red")
            self.assertEqual(a["EXG5"].synchronization.color, "yellow")
            self.assertEqual(a["EXG6"].linearity.color, "red")
            self.assertEqual(a["EXG7"].gain.color, "yellow")
            self.assertEqual(a["EXG8"].repetition.color, "red")
            ReportExporter().save(result, folder/"export", title="TEST DATA")
            for name in ("heatmap.png", "results.json", "report.html", "electrodes.csv", "zero_pairs.csv", "zero_counts_and_time.csv", "project.json"):
                self.assertTrue((folder/"export"/name).exists())
            payload = json.loads((folder/"export/results.json").read_text(encoding="utf-8"))
            self.assertEqual(len(payload["electrodes"]), 8)
            run = result.runs[0].channels["EXG4"]["sync"].values
            self.assertGreater(run["rising_count"], 15)
            self.assertGreater(run["falling_count"], 15)
            for d in ("rising", "falling"):
                self.assertAlmostEqual(run["directions"][d]["median_ms"], 3, delta=.002)

    def test_single_bdf_is_not_linearity_or_independent_repetition(self):
        with fixture_folder() as folder:
            records = create_demo(folder, 8)[:1]
            result = AnalysisService(AnalysisSettings()).analyze(records, ["EXG1", "EXG2"], "EXG1")
            self.assertEqual(len(result.electrodes), 2)
            self.assertTrue(all(e.linearity.color == "yellow" and e.repetition.color == "yellow" for e in result.electrodes))
            self.assertEqual(result.electrodes[0].metric("current").color, "green")
            self.assertEqual(result.electrodes[0].metric("overall").color, "yellow")

    def test_unknown_input_cannot_show_green_gain(self):
        record = InputRecord("unknown", "x.bdf", input_mVpp=100, input_confirmed=False)
        fit = dict(amplitude_pp_mV=100, quality_reasons=[])
        result = AmplitudePeakGainError(AnalysisSettings()).evaluate(fit, record)
        self.assertEqual(result.color, "yellow")

    def test_three_color_threshold_boundaries(self):
        settings = AnalysisSettings()
        self.assertEqual(settings.color(3.99, 5), "green")
        self.assertEqual(settings.color(4, 5), "yellow")
        self.assertEqual(settings.color(5, 5), "yellow")
        self.assertEqual(settings.color(-5.01, 5), "red")

    def test_actual_crossings_both_directions_and_signed_time(self):
        settings = AnalysisSettings()
        fs = 4096
        t = np.arange(fs*3)/fs
        x = 50000*np.sin(2*np.pi*5*(t[:, None]-np.array([0., -.002]))) + 6000+100*t[:, None]
        fits, centred = SineFitter(settings).fit(x, fs, 5)
        data = TimeSynchronizationAnalyzer(settings).evaluate_all(centred, fits, ["EXG1", "EXG2"], "EXG1", fs, 5)
        for direction in ("rising", "falling"):
            self.assertAlmostEqual(data["EXG2"].values["directions"][direction]["median_ms"], -2, delta=.001)
        detector = ZeroCrossingDetector(settings)
        np.testing.assert_allclose(detector.detect(np.array([-4., -1., 3., 5.]), 1000, 5, 5, "rising"), [.00125])
        np.testing.assert_allclose(detector.detect(np.array([4., 1., -3., -5.]), 1000, 5, 5, "falling"), [.00125])

    def test_missing_period_is_not_reindexed_onto_next_cycle(self):
        analyzer = TimeSynchronizationAnalyzer(AnalysisSettings())
        reference = np.array([.2, .4, .6, .8])
        target = np.array([.202, .402, .802])
        pairs, counts = analyzer.match_direction(reference, target, 5, 1)
        self.assertEqual(counts["missing"], 1)
        self.assertEqual([p["reference_event_index"] for p in pairs], [0, 1, 3])
        self.assertTrue(all(abs(p["delay_ms"]-2) < 1e-8 for p in pairs))
        reversed_pairs, counts = analyzer.match_direction(reference, reference+.1, 5, 1)
        self.assertEqual(reversed_pairs, [])
        self.assertEqual(counts["missing"], 4)

    def test_bad_reference_invalidates_relative_timing(self):
        settings = AnalysisSettings()
        t = np.arange(4096)/1024
        x = 50000*np.sin(2*np.pi*5*t)
        fits = [dict(amplitude_pp_mV=100., quality_reasons=["bad_reference"]), dict(amplitude_pp_mV=100., quality_reasons=[])]
        result = TimeSynchronizationAnalyzer(settings).evaluate_all(np.column_stack((x,x)), fits, ["EXG1","EXG2"], "EXG1", 1024, 5)
        self.assertEqual(result["EXG2"].color, "yellow")
        self.assertIn("Reference", result["EXG2"].message)

    def test_duplicate_records_rejected_and_project_roundtrip(self):
        with fixture_folder() as folder:
            records = create_demo(folder, 3)
            duplicate = copy.deepcopy(records[0])
            duplicate.id += "copy"
            with self.assertRaises(ValueError):
                AnalysisService(AnalysisSettings()).analyze([records[0],duplicate], ["EXG1"], "EXG1")
            save_project(folder/"project.json", records, AnalysisSettings(), ["EXG1","EXG2"], "EXG1")
            loaded, settings, channels, reference = load_project(folder/"project.json")
            self.assertEqual([asdict(r) for r in records], [asdict(r) for r in loaded])
            self.assertEqual(channels, ["EXG1","EXG2"])
            self.assertEqual(reference, "EXG1")

    def test_gui_dynamic_count_background_analysis_and_stale_result_clear(self):
        import tkinter as tk
        from gui import ElectrodeQAApp
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        root.withdraw()
        try:
            with fixture_folder() as folder:
                app = ElectrodeQAApp(root)
                app.records = create_demo(folder, 12)[:1]
                app.refresh_records()
                app.initialize_channels()
                app.count.set("3")
                app.apply_count()
                self.assertEqual(app.channels, ["EXG1", "EXG2", "EXG3"])
                app.run()
                deadline = time.monotonic()+15
                while app.busy and time.monotonic() < deadline:
                    root.update()
                    time.sleep(.01)
                self.assertFalse(app.busy)
                self.assertIsNotNone(app.result)
                root.update_idletasks()
                self.assertEqual(len(app.heatmap.canvas.find_withtag("electrode_circle")), 3)
                self.assertEqual(len(app.results_tree.get_children()), 3)
                app.limit_vars["gain_limit_pct"].set("6")
                self.assertIsNone(app.result)
                self.assertEqual(len(app.heatmap.canvas.find_withtag("electrode_circle")), 0)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
