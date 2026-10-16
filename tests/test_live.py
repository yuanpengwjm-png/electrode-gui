"""Live sine checks and stale-source behavior; all signals are synthetic."""
import copy
import json
from pathlib import Path
import queue
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from services.live_analysis import LiveConfig, Confirmation, analyze_sine_window, frame_problem
from services.lsl_stream import SampleBuffer
from test_analysis import fixture_folder


class LiveTests(unittest.TestCase):
    def setUp(self):
        self.fs=1024;self.t=np.arange(5120)/self.fs
        self.x=np.column_stack((5000*np.sin(2*np.pi*5*self.t)+900,5000*np.sin(2*np.pi*5*self.t+.2)-300))
        self.cfg=LiveConfig(input_confirmed=True,mapping_confirmed=True)

    def analyze(self,x=None,t=None,scales=None,cfg=None):
        return analyze_sine_window(self.x if x is None else x,self.t if t is None else t,['C11','C12'],[1,1] if scales is None else scales,self.fs,cfg or self.cfg)

    def test_normal_and_channel_specific_amplitude_fault(self):
        good=self.analyze();self.assertEqual([e.metric('live').color for e in good['electrodes']],['green','green'])
        self.x[:,1]*=.5
        bad=self.analyze();self.assertEqual([e.metric('live').color for e in bad['electrodes']],['green','red'])
        self.assertAlmostEqual(bad['electrodes'][1].gain.values['gain_error_pct'],-50,places=3)

    def test_noise_flat_nonfinite_and_wrong_tone(self):
        rng=np.random.default_rng(42)
        for y in (np.zeros(len(self.t)),rng.normal(0,5000,len(self.t)),5000*np.sin(2*np.pi*12*self.t)):
            self.x[:,1]=y
            r=self.analyze();self.assertEqual(r['electrodes'][0].metric('live').color,'green');self.assertEqual(r['electrodes'][1].metric('live').color,'red')
        self.x[0,1]=np.nan
        r=self.analyze();self.assertEqual(r['electrodes'][0].metric('live').color,'green');self.assertEqual(r['electrodes'][1].metric('live').color,'red')

    def test_confirmation_and_units_gate_green(self):
        for key in ('mapping_confirmed','input_confirmed'):
            cfg=copy.deepcopy(self.cfg);setattr(cfg,key,False)
            self.assertTrue(all(e.metric('live').color!='green' for e in self.analyze(cfg=cfg)['electrodes']))
        r=self.analyze(scales=[1,None]);self.assertEqual(r['electrodes'][1].metric('live').color,'yellow')
        self.assertTrue(all(e.metric('live').color=='green' for e in self.analyze(x=self.x/1e6,scales=[1e6,1e6])['electrodes']))

    def test_complete_windows_and_timestamp_gaps(self):
        r=self.analyze(x=self.x[:2000],t=self.t[:2000]);self.assertFalse(r['valid']);self.assertEqual(r['electrodes'][0].metric('live').color,'gray')
        t=self.t.copy();t[2000:]+=.05
        self.assertFalse(self.analyze(t=t)['valid'])
        t=self.t.copy();t[2000]=t[1999]
        self.assertFalse(self.analyze(t=t)['valid'])

    def test_persistence_distinct_windows_and_reset(self):
        self.x[:,1]*=.5;counter=Confirmation()
        first=counter.apply(self.analyze());self.assertFalse(first['electrodes'][1].metric('live').values['persistent_alert'])
        counter.apply(first);self.assertEqual(counter.counts['C12'][1],1)
        second=counter.apply(self.analyze(t=self.t+1));self.assertTrue(second['electrodes'][1].metric('live').values['persistent_alert'])
        counter.reset();third=counter.apply(self.analyze(t=self.t+2));self.assertFalse(third['electrodes'][1].metric('live').values['persistent_alert'])

    def test_gui_stale_data_setting_revision_export_and_cleanup(self):
        import tkinter as tk
        from views.live_window import LiveWindow
        root=tk.Tk();root.withdraw();win=LiveWindow(root);win.withdraw()
        error_patch=patch('views.live_window.messagebox.showerror',side_effect=lambda *a,**k: (_ for _ in ()).throw(AssertionError(str(a))))
        error_patch.start()
        try:
            b=SampleBuffer(2,1024);b.append(self.x,self.t)
            stopped=[]
            receiver=SimpleNamespace(buffer=b,failure=None,clock_offset=None,is_alive=lambda:True,stop=lambda:stopped.append(True))
            win.receiver=receiver;win.meta=dict(demo=True,name='TEST',labels=['C11','C12'],units=['uV','uV'],nominal_srate=1024)
            win.channels=[dict(index=i,name=n,original_label=n,unit='uV',use=True) for i,n in enumerate(['C11','C12'])]
            win.config=self.cfg;win.mapping.set(True);win.monitoring=True
            win.last_result=self.analyze();win.publish(win.last_result['electrodes'])
            self.assertTrue(all(e.metric('live').color=='green' for e in win.current))
            # A settings edit must invalidate both visible results and a queued old worker.
            token=(receiver,win.revision);old=win.last_result;win.vars['amplitude'].set('20')
            win.events.put(('analysis',(token,old)));win.handle_events()
            self.assertTrue(all(e.metric('live').color=='gray' for e in win.current))
            # A fresh UI must not preserve green when samples stop arriving.
            win.monitoring=True;win.last_result=self.analyze();win.publish(win.last_result['electrodes'])
            b.last_received=time.monotonic()-3;win.update_live()
            self.assertIsNone(win.last_result);self.assertTrue(all(e.metric('live').color=='gray' for e in win.current))
            self.assertFalse(win.torso.electrodes)
            with fixture_folder() as folder:
                saved=win.save(folder)
                with np.load(saved,allow_pickle=False) as data:
                    meta=json.loads(str(data['metadata_json']));self.assertFalse(meta['assessment_current'])
                    self.assertTrue(all(e['extra']['live']['color']=='gray' for e in meta['electrodes']))
                    np.testing.assert_array_equal(data['samples_native'],self.x)
            win.close();self.assertTrue(stopped)
        finally:error_patch.stop();root.destroy()


if __name__=='__main__':unittest.main(verbosity=2)
