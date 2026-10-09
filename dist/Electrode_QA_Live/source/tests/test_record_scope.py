"""Regressions for per-file Vpp confirmation, analysis and displayed scope."""
from contextlib import contextmanager
from dataclasses import replace
import json
import tkinter as tk
import unittest

from config import AnalysisSettings
from gui import ElectrodeQAApp
from models import MetricResult
from services.analysis_service import AnalysisService
from services.demo_data import create_demo, create_mode_demo
from utils.report_exporter import ReportExporter
from test_analysis import fixture_folder


@contextmanager
def app_for(records):
    root = tk.Tk()
    root.withdraw()
    try:
        app = ElectrodeQAApp(root)
        app.records = records
        app.refresh_records()
        app.initialize_channels()
        yield app
    finally:
        root.destroy()


class RecordScopeTests(unittest.TestCase):
    def test_checkbox_applies_to_selected_file_and_run_applies_pending_edit(self):
        with fixture_folder() as folder:
            records = [replace(r, input_confirmed=False) for r in create_demo(folder, 2)[:2]]
            with app_for(records) as app:
                app.confirmed.set(True)
                # A duplicate Tk selection event must not reset the user's edit.
                app.select_record()
                self.assertTrue(app.confirmed.get())
                request = app.prepare()
                chosen, settings, channels, reference = request
                self.assertEqual(len(chosen), 1)
                self.assertTrue(chosen[0].input_confirmed)
                self.assertFalse(app.records[1].input_confirmed)
                self.assertEqual(app.record_tree.item('0')['values'][-1], 'Yes')
                self.assertEqual(app.record_tree.item('1')['values'][-1], 'No')
                self.assertEqual(len(app.prepare(all_records=True)[0]), 2)  # Save project retains all files.
                result = AnalysisService(settings).analyze(chosen, channels, reference)
                app.mode.set('Gain error')
                app.accept_result(result)
                self.assertEqual(app.displayed_electrodes()[0].gain.color, 'green')
                self.assertNotIn('unconfirmed', app.detail.get('1.0', 'end'))
                # The second, unprocessed file must not inherit file 1's result or checkbox.
                app.record_tree.selection_set('1')
                app.select_record()
                self.assertFalse(app.confirmed.get())
                self.assertIsNone(app.result)
                chosen, settings, channels, reference = app.prepare()
                result = AnalysisService(settings).analyze(chosen, channels, reference)
                app.accept_result(result)
                self.assertIn('unconfirmed', app.detail.get('1.0', 'end'))

    def test_batch_confirmation_reasons_are_attributed_and_single_view_is_isolated(self):
        with fixture_folder() as folder:
            records = create_demo(folder, 2)[:2]
            records[1].input_confirmed = False
            with app_for(records) as app:
                app.analysis_target.set('All loaded records')
                selected, settings, channels, reference = app.prepare()
                result = AnalysisService(settings).analyze(selected, channels, reference)
                aggregate = result.electrodes[0].gain
                self.assertEqual(aggregate.color, 'yellow')
                self.assertIn(records[1].id + ': Actual input Vpp is unconfirmed', aggregate.message)
                self.assertNotIn(records[0].id + ':', aggregate.message)
                app.accept_result(result)
                self.assertEqual(app.scope.get(), 'Record: ' + records[0].id)
                self.assertEqual(app.displayed_electrodes()[0].gain.color, 'green')
                # Result selection also selects the corresponding editable record.
                app.scope.set('Record: ' + records[1].id)
                app.change_scope()
                self.assertEqual(app.selected, 1)
                self.assertFalse(app.confirmed.get())
                self.assertEqual(app.displayed_electrodes()[0].gain.color, 'yellow')
                app.scope.set('All analyzed records / worst case')
                app.change_scope()
                self.assertIs(app.displayed_electrodes(), result.electrodes)
                # Returning to file 1 excludes file 2's warning in details and export.
                app.record_tree.selection_set('0')
                app.select_record()
                app.mode.set('Gain error')
                app.redraw()
                self.assertNotIn(records[1].id, app.detail.get('1.0', 'end'))
                ReportExporter().save(result, folder/'export', 'gain',
                                      electrodes=app.displayed_electrodes(), scope=app.scope.get())
                data = json.loads((folder/'export/results.json').read_text(encoding='utf-8'))
                self.assertEqual(data['export_view']['scope'], 'Record: ' + records[0].id)
                self.assertEqual(data['export_view']['electrode_results'][0]['gain']['color'], 'green')
                self.assertEqual(len(data['runs']), 2)

    def test_single_record_never_borrows_batch_failure_or_protocol_metrics(self):
        with fixture_folder() as folder:
            records = create_demo(folder, 1)
            result = AnalysisService(AnalysisSettings()).analyze(records, ['EXG1'], 'EXG1')
            result.electrodes[0].extra['snr'] = MetricResult('red', 'Failure in another record')
            single = result.record_electrodes(records[0].id)[0]
            self.assertEqual(single.extra['snr'].color, 'green')
            self.assertEqual(single.linearity.color, 'yellow')
            self.assertIn('Multi-record', single.linearity.message)
            self.assertEqual(result.electrodes[0].linearity.color, 'green')
            self.assertEqual(result.electrodes[0].repetition.color, 'green')

    def test_ecg_window_selection_is_preserved(self):
        with fixture_folder() as folder:
            records = create_mode_demo(folder, 3, 'ecg')
            with app_for(records) as app:
                app.profile.set('Stage 2 - ECG quality')
                app.change_profile()
                selected, settings, channels, reference = app.prepare()
                result = AnalysisService(settings).analyze(selected, channels, reference)
                app.accept_result(result)
                app.scope.set('Record: ' + records[0].id)
                self.assertEqual(app.displayed_electrodes()[2].extra['integrity'].color, 'red')
                label = next(k for k, v in app.result_scopes.items() if v == ('frame', 0))
                app.scope.set(label)
                app.change_scope()
                self.assertEqual(app.displayed_electrodes()[2].extra['integrity'].color, 'green')


if __name__ == '__main__':
    unittest.main()
