"""Signal-level checks for the stage split, new algorithms and English UI."""
from dataclasses import replace
from pathlib import Path
import json
import re
import unittest
from unittest.mock import patch
import numpy as np
from config import AnalysisSettings
from models import InputRecord
from modules.bench_spectrum import BenchSpectrumAnalyzer
from modules.ecg_quality import ECGQualityAnalyzer, BeatAgreement
from services.analysis_service import AnalysisService
from services.demo_data import create_mode_demo
from utils.demo_bdf import write_demo_bdf
from utils.project_io import save_project, load_project
from utils.report_exporter import ReportExporter
from test_analysis import fixture_folder


class StageTests(unittest.TestCase):
    def test_harmonics_are_separated_from_noise_and_frequency_is_individual(self):
        fs = 2048
        t = np.arange(fs*10)/fs
        rng = np.random.default_rng(3)
        y = 2000*np.sin(2*np.pi*5.1*t) + 200*np.sin(2*np.pi*10.2*t) + rng.normal(0, 1, len(t))
        analyzer = BenchSpectrumAnalyzer(AnalysisSettings(thd_limit_pct=2, frequency_limit_pct=.5))
        result = analyzer.analyze(y, fs, 5)
        self.assertAlmostEqual(result['thd'].values['thd_pct'], 10, delta=.15)
        self.assertAlmostEqual(result['frequency'].values['error_pct'], 2, delta=.05)
        self.assertEqual(result['frequency'].color, 'red')
        self.assertEqual(result['thd'].color, 'red')
        self.assertGreater(result['snr'].values['snr_db'], result['sinad'].values['sinad_db']+20)

    def test_unset_acceptance_is_not_green(self):
        t = np.arange(4096)/1024
        result = BenchSpectrumAnalyzer(AnalysisSettings(thd_limit_pct=None, frequency_limit_pct=None)).analyze(1000*np.sin(2*np.pi*5*t), 1024, 5)
        self.assertEqual(result['thd'].color, 'yellow')
        self.assertEqual(result['frequency'].color, 'yellow')

    def test_pulse_bypasses_sine_fit_and_measures_both_edges(self):
        with fixture_folder() as folder:
            records = create_mode_demo(folder, 3, 'bench_pulse')
            service = AnalysisService(AnalysisSettings(analysis_mode='bench_pulse', frequency_limit_pct=1))
            with patch.object(service.fitter, 'fit', side_effect=AssertionError('Sine fit must not run')):
                result = service.analyze(records, ['EXG1','EXG2','EXG3'], 'EXG1')
            a = result.runs[0].channels
            self.assertAlmostEqual(a['EXG1']['gain'].values['output_mVpp'], 100, delta=.01)
            self.assertEqual(a['EXG2']['gain'].color, 'red')
            self.assertNotIn('thd', a['EXG1']['extra'])
            for direction in ('rising','falling'):
                self.assertAlmostEqual(a['EXG3']['sync'].values['directions'][direction]['median_ms'], 4, delta=1)
            self.assertEqual(a['EXG3']['sync'].color, 'red')

    def test_mode_mismatch_and_mixed_setups_are_rejected(self):
        r = InputRecord('r','no-file.bdf',waveform='ecg')
        with self.assertRaisesRegex(ValueError, 'does not match'):
            AnalysisService(AnalysisSettings()).analyze([r],['A1'],'A1')
        with self.assertRaisesRegex(ValueError, 'setups'):
            AnalysisService(AnalysisSettings()).analyze([replace(r,waveform='sine'),InputRecord('r2','other.bdf',setup_group='other')],['A1'],'A1')

    def test_short_ecg_is_never_padded_into_valid_windows(self):
        with fixture_folder() as folder:
            path = folder/'short.bdf'
            write_demo_bdf(path, np.zeros((512,2)), 256)
            r = InputRecord('short',str(path),waveform='ecg')
            service = AnalysisService(AnalysisSettings(analysis_mode='ecg'))
            with patch.object(service.fitter, 'fit', side_effect=AssertionError('No sine fitting on ECG')):
                result = service.analyze([r],['EXG1','EXG2'],'')
            self.assertEqual(result.frames, [])
            self.assertTrue(all(e.metric('ecg_quality').color == 'yellow' for e in result.electrodes))
            self.assertIn('2.00 s', result.electrodes[0].metric('ecg_quality').message)

    def test_two_detectors_and_flatline_baseline_faults(self):
        with fixture_folder() as folder:
            records = create_mode_demo(folder, 4, 'ecg')
            result = AnalysisService(AnalysisSettings(analysis_mode='ecg')).analyze(records,['EXG1','EXG2','EXG3','EXG4'],'')
            self.assertEqual(len(result.frames), 5)
            first = result.frames[0]['metrics']
            self.assertEqual(first['EXG1']['ecg_quality'].color, 'green')
            self.assertGreater(first['EXG1']['bsqi'].values['value'], .9)
            self.assertEqual(first['EXG2']['bassqi'].color,'red')
            self.assertEqual(result.frames[1]['metrics']['EXG3']['integrity'].color, 'red')
            self.assertEqual(first['EXG3']['integrity'].color, 'green')
            self.assertEqual(first['EXG4']['ksqi'].color,'red')

    def test_matching_is_one_to_one_and_no_beats_is_undefined(self):
        score, matched = BeatAgreement.score([1.,1.02,2.], [1.01,2.], .05)
        self.assertEqual(matched, 2)
        self.assertAlmostEqual(score, 2/3)
        self.assertEqual(BeatAgreement.score([], [], .05), (None, 0))

    def test_constant_ecg_flatline_and_clipping_are_explicit(self):
        analyzer = ECGQualityAnalyzer(AnalysisSettings(analysis_mode='ecg'))
        result = analyzer.analyze_window(np.zeros(2500), 250)
        self.assertEqual(result['integrity'].color, 'red')
        self.assertEqual(result['bsqi'].color, 'yellow')
        self.assertEqual(result['ecg_quality'].color, 'red')
        clipped = analyzer.analyze_window(np.full(2500, 100.), 250, [-100,100])
        self.assertEqual(clipped['integrity'].values['clipped_samples'],2500)

    def test_ecg_export_keeps_window_scope_and_project_mode(self):
        with fixture_folder() as folder:
            records = create_mode_demo(folder/'data',3,'ecg')
            result = AnalysisService(AnalysisSettings(analysis_mode='ecg')).analyze(records,['EXG1','EXG2','EXG3'],'')
            frame = result.frames[1]
            displayed = [replace(e, extra=frame['metrics'][e.name]) for e in result.electrodes]
            ReportExporter().save(result,folder/'report','integrity',electrodes=displayed,scope='5-15 s')
            payload = json.loads((folder/'report/results.json').read_text(encoding='utf-8'))
            self.assertEqual(payload['export_view']['scope'],'5-15 s')
            self.assertEqual(payload['export_view']['electrode_results'][2]['extra']['integrity']['color'],'red')
            _,settings,_,reference=load_project(folder/'report/project.json')
            self.assertEqual(settings.analysis_mode,'ecg'); self.assertEqual(reference,'')
            self.assertIn('start_s,end_s', (folder/'report/ecg_windows.csv').read_text(encoding='utf-8-sig'))
            self.assertNotRegex((folder/'report/report.html').read_text(encoding='utf-8'),r'[\u4e00-\u9fff]')

    def test_gui_switch_clears_result_and_english_controls(self):
        import tkinter as tk
        from gui import ElectrodeQAApp
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No Tk display')
        root.withdraw()
        try:
            app = ElectrodeQAApp(root)
            app.result = object()
            app.profile.set('Stage 2 - ECG quality'); app.change_profile()
            self.assertIsNone(app.result)
            self.assertEqual(app.mode.get(),'ECG quality')
            self.assertEqual(str(app.ref_combo.cget('state')),'disabled')
            def check_widgets(widget):
                if 'text' in widget.keys():
                    self.assertNotRegex(str(widget.cget('text')),r'[\u4e00-\u9fff]')
                for child in widget.winfo_children(): check_widgets(child)
            check_widgets(root)
        finally:
            root.destroy()


if __name__ == '__main__':
    unittest.main()
