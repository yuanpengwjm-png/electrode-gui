"""Window isolation, localized fault detection, playback and export integration."""
import csv
import json
import unittest
import numpy as np
from config import AnalysisSettings
from models import InputRecord
from modules.windowing import WindowPlan
from services.analysis_service import AnalysisService
from services.demo_data import create_mode_demo
from utils.demo_bdf import write_demo_bdf
from utils.report_exporter import ReportExporter
from test_analysis import fixture_folder
from test_record_scope import app_for


def sine_record(folder, duration=30, name='window-sine', clip=False):
    fs = 512
    t = np.arange(duration*fs)/fs
    y = np.repeat((50000*np.sin(2*np.pi*2*t)+2200)[:, None], 2, axis=1)
    if duration >= 20:
        mask = (t >= 10) & (t < 20)
        y[mask, 1] = 25000*np.sin(2*np.pi*2*t[mask])+2200
    if clip:
        y[12*fs, 1] = 262143  # Exact BDF digital rail, confined to the second window.
    path = folder/(name+'.bdf')
    write_demo_bdf(path, y, fs)
    return InputRecord(name, str(path), 2., 100., True, False, waveform='sine')


def settings():
    # These fixtures test exact 0-10 / 10-20 / 20-30 boundaries. Cropping has
    # separate end-to-end tests and is explicitly disabled for this control.
    return AnalysisSettings(exclude_last_s=0, bench_windows=True, bench_window_s=10, bench_hop_s=10,
                            thd_limit_pct=1, frequency_limit_pct=.1,
                            sync_delay_limit_ms=3, sync_jitter_limit_ms=3)


class WindowTests(unittest.TestCase):
    def test_full_windows_cover_end_without_padding_or_crossing_files(self):
        plan = WindowPlan(10, 5)
        self.assertEqual(plan.spans(30, 10), [])
        self.assertEqual(plan.spans(100, 10), [(0, 100)])
        spans = plan.spans(213, 10)
        self.assertEqual(spans, [(0, 100), (50, 150), (100, 200), (113, 213)])
        with self.assertRaises(ValueError):
            WindowPlan(10, 11).spans(300, 10)

    def test_local_amplitude_fault_is_absent_from_other_windows(self):
        with fixture_folder() as folder:
            record = sine_record(folder)
            result = AnalysisService(settings()).analyze([record], ['EXG1', 'EXG2'], 'EXG1')
            self.assertEqual([(f['start_s'],f['end_s']) for f in result.frames], [(0,10),(10,20),(20,30)])
            electrodes = [result.window_electrodes(i)[1] for i in range(3)]
            self.assertEqual([e.gain.color for e in electrodes], ['green','red','green'])
            self.assertAlmostEqual(electrodes[1].gain.values['gain_error_pct'], -50, delta=.01)
            # A rising crossing exactly at the left boundary lacks preceding
            # negative samples to confirm the detector's hysteresis condition.
            self.assertIn(electrodes[0].synchronization.values['rising_count'], (19, 20))
            self.assertEqual(electrodes[0].synchronization.values['falling_count'], 20)
            self.assertNotIn('pairs', electrodes[0].synchronization.values)
            self.assertEqual(electrodes[0].linearity.color, 'yellow')
            self.assertEqual(electrodes[0].repetition.color, 'yellow')

    def test_clipping_is_checked_inside_each_window(self):
        with fixture_folder() as folder:
            record = sine_record(folder, clip=True)
            result = AnalysisService(settings()).analyze([record], ['EXG1', 'EXG2'], 'EXG1')
            first = result.window_electrodes(0)[1].gain.values['quality_reasons']
            middle = result.window_electrodes(1)[1].gain.values['quality_reasons']
            self.assertNotIn('digital_rail_clipping', first)
            self.assertIn('digital_rail_clipping', middle)

    def test_two_short_files_never_become_one_complete_window(self):
        with fixture_folder() as folder:
            records = [sine_record(folder, 3, 'short3'), sine_record(folder, 7, 'short7')]
            result = AnalysisService(settings()).analyze(records, ['EXG1','EXG2'], 'EXG1')
            self.assertEqual(result.frames, [])
            self.assertEqual([r.channels['EXG1']['unassessed_tail_s'] for r in result.runs], [3,7])
            with app_for(records) as app:
                app.accept_result(result)
                self.assertIn('No complete windows', app.timeline.caption.get())
                self.assertEqual(str(app.timeline.play.cget('state')), 'disabled')

    def test_pulse_windows_use_pulse_measurements(self):
        with fixture_folder() as folder:
            records = create_mode_demo(folder, 2, 'bench_pulse')
            s = settings(); s.analysis_mode = 'bench_pulse'
            result = AnalysisService(s).analyze(records, ['EXG1','EXG2'], 'EXG1')
            self.assertEqual(len(result.frames), 3)
            for frame in result.frames:
                self.assertNotIn('snr', frame['metrics']['EXG2'])
                self.assertEqual(frame['metrics']['EXG2']['gain'].color, 'red')
                self.assertEqual(frame['metrics']['EXG2']['synchronization'].values['event_definition'], 'pulse plateau midpoint')

    def test_gui_drag_play_focus_invalidation_and_export_scope(self):
        with fixture_folder() as folder:
            record = sine_record(folder)
            result = AnalysisService(settings()).analyze([record], ['EXG1','EXG2'], 'EXG1')
            with app_for([record]) as app:
                app.mode.set('Gain error')
                app.accept_result(result)
                self.assertEqual(app.result_scopes[app.scope.get()], ('frame',0))
                app.show_detail(app.displayed_electrodes()[1])
                app.timeline.next_alert()
                self.assertEqual(app.result_scopes[app.scope.get()], ('frame',1))
                self.assertEqual(app.focused_electrode, 'EXG2')
                self.assertIn('Window only: 10-20 s', app.detail.get('1.0','end'))
                self.assertEqual(app.displayed_electrodes()[1].gain.color, 'red')
                ReportExporter().save(result, folder/'export', 'gain',
                                      electrodes=app.displayed_electrodes(), scope=app.scope.get())
                payload = json.loads((folder/'export/results.json').read_text(encoding='utf-8'))
                self.assertIn('10-20 s', payload['export_view']['scope'])
                with (folder/'export/window_summary.csv').open(encoding='utf-8-sig') as handle:
                    rows = list(csv.DictReader(handle))
                self.assertEqual(len(rows),6)
                self.assertEqual([(float(r['start_s']), r['electrode']) for r in rows if r['color']=='red'], [(10.,'EXG2')])
                with (folder/'export/ecg_windows.csv').open(encoding='utf-8-sig') as handle:
                    self.assertEqual(len(list(csv.DictReader(handle))), 0)
                app.timeline._scrub('0')
                self.assertEqual(app.result_scopes[app.scope.get()], ('frame',0))
                app.timeline.toggle()
                self.assertTrue(app.timeline.playing)
                # Execute the scheduled callback without waiting ten seconds.
                app.timeline.after_cancel(app.timeline.timer); app.timeline.timer = None
                app.timeline._tick()
                self.assertEqual(app.result_scopes[app.scope.get()], ('frame',1))
                app.timeline.after_cancel(app.timeline.timer); app.timeline.timer = None
                app.timeline._tick()
                self.assertFalse(app.timeline.playing)
                self.assertEqual(app.result_scopes[app.scope.get()], ('frame',2))
                app.timeline.toggle()
                self.assertTrue(app.timeline.playing)
                app.limit_vars['bench_window_s'].set('8')
                self.assertIsNone(app.result)
                self.assertFalse(app.timeline.playing)
                self.assertIsNone(app.timeline.timer)
                self.assertEqual(app.timeline.items, [])

    def test_switching_files_stops_playback_and_keeps_windows_separate(self):
        with fixture_folder() as folder:
            records = [sine_record(folder, name='record-a'), sine_record(folder, name='record-b')]
            result = AnalysisService(settings()).analyze(records, ['EXG1', 'EXG2'], 'EXG1')
            with app_for(records) as app:
                app.mode.set('Gain error')
                app.accept_result(result)
                app.timeline.toggle()
                self.assertTrue(app.timeline.playing)
                app.record_tree.selection_set('1')
                app.select_record()
                self.assertFalse(app.timeline.playing)
                self.assertIsNone(app.timeline.timer)
                self.assertEqual(app.result_scopes[app.scope.get()], ('record', 'record-b'))
                self.assertEqual([item[0] for item in app.timeline.items], [3, 4, 5])
                app.timeline.next_alert()
                self.assertEqual(app.result_scopes[app.scope.get()], ('frame', 4))
                self.assertEqual(app.selected, 1)
                self.assertIn('record-b', app.detail.get('1.0', 'end'))
                self.assertNotIn('record-a', app.detail.get('1.0', 'end'))


if __name__ == '__main__':
    unittest.main()
