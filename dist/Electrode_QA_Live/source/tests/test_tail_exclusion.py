"""Tail faults never enter retained metrics, windows, exports or 3D states."""
from dataclasses import asdict
import json
from pathlib import Path
import unittest
import numpy as np

from config import AnalysisSettings
from models import InputRecord
from services.analysis_service import AnalysisService
from utils.bdf_reader import BdfReader
from utils.demo_bdf import write_demo_bdf
from utils.project_io import load_project, save_project
from utils.report_exporter import ReportExporter
from test_analysis import fixture_folder
from test_record_scope import app_for


def record_with_tail(folder, waveform='sine', duration=21, name='tail-fault'):
    fs=256
    t=np.arange(fs*duration)/fs
    clean=np.sin(2*np.pi*5*t)
    if waveform=='pulse':
        clean=np.where(clean>=0,1.,-1.)
    data=np.repeat((25000*clean+1000)[:,None],2,axis=1)
    if duration>1:
        data[-fs:]+=18000
        data[-fs//2,0]=262143  # One digital rail in the discarded final second.
    path=folder/(name+'.bdf')
    write_demo_bdf(path,data,fs)
    return InputRecord(name,str(path),5,50,True,False,waveform=waveform),data,fs


class TailExclusionTests(unittest.TestCase):
    def test_defaults_legacy_migration_and_explicit_settings_roundtrip(self):
        with fixture_folder() as folder:
            record,_,_=record_with_tail(folder)
            with app_for([record]) as app:
                self.assertEqual(float(app.limit_vars['exclude_last_s'].get()),1)
                self.assertEqual(float(app.limit_vars['frequency_limit_pct'].get()),.1)
                self.assertEqual(float(app.limit_vars['thd_limit_pct'].get()),1)
                self.assertEqual(app.prepare()[1].exclude_last_s,1)
                path=folder/'old.json'
                old=dict(version=2,records=[asdict(record)],settings=dict(thd_limit_pct=None,frequency_limit_pct=None),
                         channels=['EXG1','EXG2'],reference='EXG1')
                path.write_text(json.dumps(old))
                app.load_path(path)
                self.assertEqual(float(app.limit_vars['frequency_limit_pct'].get()),.1)
                self.assertEqual(float(app.limit_vars['thd_limit_pct'].get()),1)
                self.assertEqual(app.settings.exclude_last_s,1)
            # Existing numeric tolerances are deliberate and must survive.
            old['settings']['frequency_limit_pct']=.25
            old['settings']['thd_limit_pct']=2
            path.write_text(json.dumps(old))
            self.assertEqual(load_project(path)[1].frequency_limit_pct,.25)
            self.assertEqual(load_project(path)[1].thd_limit_pct,2)
            # In new projects, explicitly blank acceptance and disabled crop persist.
            s=AnalysisSettings(exclude_last_s=0,frequency_limit_pct=None,thd_limit_pct=None)
            save_project(path,[record],s,['EXG1','EXG2'],'EXG1')
            self.assertEqual(asdict(load_project(path)[1]),asdict(s))

    def test_sine_and_pulse_match_independent_clean_prefix_including_clipping(self):
        with fixture_folder() as folder:
            for waveform,mode in (('sine','bench_sine'),('pulse','bench_pulse')):
                record,data,fs=record_with_tail(folder,waveform,name=waveform)
                original=Path(record.path).read_bytes()
                prefix=folder/(waveform+'-prefix.bdf')
                write_demo_bdf(prefix,data[:-fs],fs)
                clean_record=InputRecord(record.id,str(prefix),5,50,True,False,waveform=waveform)
                s=AnalysisSettings(analysis_mode=mode,bench_windows=True,bench_hop_s=10)
                service=AnalysisService(s)
                service.reader=BdfReader(folder/'cache',max_memory_bytes=1)
                trimmed=service.analyze([record],['EXG1','EXG2'],'EXG1')
                self.assertEqual(list((folder/'cache').iterdir()),[])
                s.exclude_last_s=0
                clean=AnalysisService(s).analyze([clean_record],['EXG1','EXG2'],'EXG1')
                untrimmed=AnalysisService(s).analyze([record],['EXG1','EXG2'],'EXG1')
                self.assertEqual(trimmed.runs[0].channels,clean.runs[0].channels)
                self.assertEqual(trimmed.frames,clean.frames)
                self.assertEqual([(f['start_s'],f['end_s']) for f in trimmed.frames],[(0,10),(10,20)])
                self.assertEqual(trimmed.runs[0].duration_s,20)
                self.assertEqual(trimmed.runs[0].source_duration_s,21)
                self.assertEqual(trimmed.runs[0].excluded_tail_s,1)
                self.assertEqual(Path(record.path).read_bytes(),original)
                self.assertIn('digital_rail_clipping',untrimmed.runs[0].channels['EXG1']['fit']['quality_reasons'])
                self.assertNotIn('digital_rail_clipping',trimmed.runs[0].channels['EXG1']['fit']['quality_reasons'])
                # Every retained crossing uses the original, unshifted time axis.
                for name in ('EXG1','EXG2'):
                    events=trimmed.runs[0].channels[name]['sync'].values
                    self.assertTrue(all(0<=t<20 for t in events['rising_events_s']+events['falling_events_s']))

    def test_ecg_and_each_batch_file_are_cropped_separately(self):
        with fixture_folder() as folder:
            a,data,fs=record_with_tail(folder,duration=12,name='a')
            b,_,_=record_with_tail(folder,duration=10,name='b')
            for r in (a,b):r.waveform='ecg'
            s=AnalysisSettings(analysis_mode='ecg')
            result=AnalysisService(s).analyze([a,b],['EXG1','EXG2'],'')
            self.assertEqual([r.duration_s for r in result.runs],[11,9])
            self.assertEqual([(f['record_id'],f['start_s'],f['end_s']) for f in result.frames],[('a',0,10),('a',1,11)])
            self.assertEqual(result.runs[1].channels['EXG1']['complete_windows'],0)
            self.assertIn('9.00 s retained',result.runs[1].channels['EXG1']['extra']['integrity'].message)
            prefix=folder/'ecg-prefix.bdf';write_demo_bdf(prefix,data[:-fs],fs)
            clean=InputRecord(a.id,str(prefix),waveform='ecg')
            s.exclude_last_s=0
            reference=AnalysisService(s).analyze([clean],['EXG1','EXG2'],'')
            self.assertEqual(result.frames,reference.frames)

    def test_short_and_fractional_exclusions_are_explicit(self):
        with fixture_folder() as folder:
            record,_,_=record_with_tail(folder,duration=1)
            service=AnalysisService(AnalysisSettings())
            with self.assertRaisesRegex(ValueError,'leaves no samples'):
                service.analyze([record],['EXG1'],'EXG1')
            for value in (-1,float('nan'),float('inf')):
                with self.assertRaises(ValueError):AnalysisSettings(exclude_last_s=value).validate()
            record,_,_=record_with_tail(folder,duration=3,name='short')
            s=AnalysisSettings(bench_windows=True)
            result=AnalysisService(s).analyze([record],['EXG1'],'EXG1')
            self.assertEqual(result.runs[0].duration_s,2)
            self.assertEqual(result.frames,[])
            s.exclude_last_s=.101
            result=AnalysisService(s).analyze([record],['EXG1'],'EXG1')
            self.assertEqual(result.runs[0].excluded_tail_s,26/256)
            self.assertEqual(result.runs[0].duration_s,3-26/256)

    def test_gui_3d_and_exports_report_the_retained_interval(self):
        with fixture_folder() as folder:
            record,_,_=record_with_tail(folder)
            with Path(record.path).open('r+b') as stream:
                stream.seek(256);stream.write(b'A1'.ljust(16)+b'D32'.ljust(16))
            s=AnalysisSettings(bench_windows=True,bench_hop_s=10)
            result=AnalysisService(s).analyze([record],['A1','D32'],'A1')
            with app_for([record]) as app:
                app.mode.set('Gain error');app.accept_result(result);app.open_torso()
                app.select_window(1)
                self.assertEqual(app.torso_window.timeline.items[-1][2],20)
                self.assertIn('analyzed 0-20 s of 21 s',app.detail.get('1.0','end'))
                self.assertIn('excluded 20-21 s',app.torso_window.detail.get('1.0','end'))
                ReportExporter().save(result,folder/'export','gain',electrodes=app.displayed_electrodes(),scope=app.scope.get())
                payload=json.loads((folder/'export/results.json').read_text())
                self.assertEqual(payload['runs'][0]['excluded_tail_s'],1)
                self.assertEqual(payload['runs'][0]['source_duration_s'],21)
                self.assertEqual(payload['runs'][0]['duration_s'],20)
                self.assertEqual(payload['settings']['frequency_limit_pct'],.1)
                page=(folder/'export/report.html').read_text()
                self.assertIn('Excluded tail',page);self.assertIn('0-20 s',page)
                self.assertEqual(load_project(folder/'export/project.json')[1].exclude_last_s,1)
                app.limit_vars['exclude_last_s'].set('0')
                self.assertIsNone(app.result);self.assertEqual(app.torso_window.view.electrodes,{})


if __name__=='__main__':unittest.main()
