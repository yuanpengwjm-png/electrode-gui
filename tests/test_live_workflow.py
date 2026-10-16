"""Source safety, peer navigation, ECG routing, and alert-driven camera behavior."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.live_discovery import choose_stream, stream_key
from services.live_analysis import LiveConfig, analyze_live_window, unavailable
from modules.ecg_quality import ECGQualityAnalyzer
from config import AnalysisSettings


def source(name='BioSemi', source_id='device1', uid='uid1', rate=512, fmt=1):
    return SimpleNamespace(name=lambda:name, source_id=lambda:source_id, uid=lambda:uid,
        hostname=lambda:'lab-pc', nominal_srate=lambda:rate, channel_format=lambda:fmt,
        channel_count=lambda:2)


class SourceTests(unittest.TestCase):
    def test_unique_multiple_and_restarted_sources(self):
        a=source();b=source(source_id='device2')
        self.assertIs(choose_stream([a]),a)
        self.assertIsNone(choose_stream([a,b]))
        self.assertIsNone(choose_stream([b],stream_key(a)))
        restarted=source(uid='new-uid')
        self.assertIs(choose_stream([b,restarted],stream_key(a)),restarted)
        self.assertIsNone(choose_stream([a,source(uid='duplicate')],stream_key(a)))

    def test_markers_text_and_demo_are_not_auto_connected(self):
        for s in (source(rate=0),source(rate=float('nan')),source(fmt=6),source(source_id='DEMO_other')):
            self.assertIsNone(choose_stream([s]))
        old=source(source_id='');new=source(source_id='',uid='new')
        self.assertIsNone(choose_stream([new],stream_key(old)))


class ECGTests(unittest.TestCase):
    def test_ecg_reuses_post_metrics_without_sine_gain(self):
        fs=512;t=np.arange(fs*10)/fs
        y=np.zeros(len(t))
        for beat in np.arange(.5,10,.85):
            y+=1000*np.exp(-((t-beat)/.025)**2)+180*np.exp(-((t-beat-.24)/.065)**2)
        cfg=LiveConfig(window_s=10,profile='ecg',mapping_confirmed=True,input_confirmed=False)
        result=analyze_live_window(y[:,None],t,['C11'],[1],fs,cfg)
        expected=ECGQualityAnalyzer(AnalysisSettings(ecg_window_s=10)).analyze_window(y,fs)
        item=result['electrodes'][0]
        self.assertTrue(result['valid']);self.assertNotIn('gain',item.extra)
        for key in ('bsqi','psqi','bassqi','ksqi','integrity'):
            self.assertEqual(item.extra[key].color,expected[key].color)
        self.assertIn('clipping not assessed',item.extra['integrity'].message)

    def test_ecg_flatline_units_and_timestamp_guards(self):
        fs=512;t=np.arange(fs*10)/fs;x=np.zeros((len(t),1))
        cfg=LiveConfig(window_s=10,profile='ecg',mapping_confirmed=True)
        check=lambda x,t,scale:analyze_live_window(x,t,['C11'],[scale],fs,cfg)
        self.assertEqual(check(x,t,1)['electrodes'][0].metric('live').color,'red')
        self.assertEqual(check(x,t,None)['electrodes'][0].metric('live').color,'yellow')
        self.assertFalse(check(x[:100],t[:100],1)['valid'])
        t[100:]+=.1
        self.assertFalse(check(x,t,1)['valid'])


class GUIWorkflowTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        from views.live_window import LiveWindow
        self.root=tk.Tk();self.root.withdraw()
        self.win=LiveWindow(self.root);self.win.withdraw()

    def tearDown(self):
        self.win.close();self.root.destroy()

    def test_auto_discovery_connects_once_and_manual_disconnect_stays_off(self):
        win=self.win;s=source()
        with patch.object(win,'search') as search:
            win.discover_if_needed();win.discover_if_needed()
            self.assertEqual(search.call_count,1)
        with patch.object(win,'connect_info') as connect:
            win.events.put(('streams',[s]));win.handle_events();connect.assert_called_once_with(s)
            win.disconnect();win.events.put(('streams',[s]));win.handle_events()
            self.assertEqual(connect.call_count,1)

    def test_ambiguous_sources_and_missing_dependency(self):
        win=self.win
        with patch.object(win,'connect_info') as connect:
            win.events.put(('streams',[source(),source(source_id='other')]))
            win.handle_events();connect.assert_not_called()
        win.events.put(('search_error',"No module named 'pylsl'"));win.handle_events()
        self.assertFalse(win.auto_connect.get());self.assertIn('Python environment',win.status.get())

    def test_hardware_channels_are_never_preselected_by_test_names(self):
        win=self.win
        meta=dict(name='BioSemi',hostname='lab-pc',source_id='device1',channel_count=3,
                  nominal_srate=512,channel_format=1,labels=['C11','C12','A1'],units=['uV']*3,demo=False)
        receiver=SimpleNamespace(meta=meta);win.receiver=receiver
        win.events.put(('connected',receiver));win.handle_events()
        self.assertFalse(any(c['use'] for c in win.channels))
        self.assertFalse(hasattr(win,'select_pair'))
        win.receiver=None

    def test_alert_pauses_focuses_and_requires_manual_resume(self):
        win=self.win
        win.publish(unavailable(['C11'],'within limits','green'))
        self.assertFalse(win.rotation_paused)
        win.publish(unavailable(['C12'],'test warning','yellow'))
        self.assertTrue(win.rotation_paused);self.assertEqual(win.focused,'C12')
        win.toggle_rotation();self.assertTrue(win.rotation_paused)
        win.publish(unavailable(['C11'],'test fault','red'))
        self.assertEqual(win.focused,'C11')
        win.publish(unavailable(['C11'],'recovered','green'))
        self.assertTrue(win.rotation_paused)
        win.toggle_rotation();self.assertFalse(win.rotation_paused)

    def test_rotation_uses_elapsed_seconds_and_profile_clears_old_result(self):
        win=self.win
        win.after_cancel(win.rotation_timer)
        win.rotation_last=100;win.torso.yaw=0
        with patch('views.live_window.time.monotonic',return_value=102),patch.object(win,'winfo_viewable',return_value=True):
            win.rotate()
        self.assertAlmostEqual(win.torso.yaw,36)
        self.assertEqual(win.profile.get(),'ECG quality');self.assertEqual(win.vars['window'].get(),'10')
        win.monitoring=True;win.profile.set('Known sine');win.change_profile()
        self.assertFalse(win.monitoring);self.assertEqual(win.vars['window'].get(),'5')

    def test_changed_metadata_requires_new_confirmation(self):
        from services.live_discovery import metadata_signature
        win=self.win
        meta=dict(name='BioSemi',hostname='lab-pc',source_id='device1',channel_count=2,
                  nominal_srate=512,channel_format=1,labels=['C11','C12'],units=['uV','uV'],demo=False)
        saved=dict(signature=metadata_signature(meta),channels=[],unit='Confirmed: uV',mapping=True,confirmed=True)
        win.resume_setup=saved
        changed=dict(meta,labels=['C12','C11'])
        receiver=SimpleNamespace(meta=changed);win.receiver=receiver
        with patch.object(win,'start_monitoring') as start:
            win.events.put(('connected',receiver));win.handle_events();start.assert_not_called()
        self.assertFalse(win.mapping.get());self.assertIn('metadata changed',win.status.get())
        win.receiver=None

    def test_matching_metadata_restores_verified_setup(self):
        from services.live_discovery import metadata_signature
        win=self.win
        meta=dict(name='BioSemi',hostname='lab-pc',source_id='device1',channel_count=2,
                  nominal_srate=512,channel_format=1,labels=['C11','C12'],units=['uV','uV'],demo=False)
        channels=[dict(index=i,name=n,original_label=n,unit='uV',use=True) for i,n in enumerate(meta['labels'])]
        win.resume_setup=dict(signature=metadata_signature(meta),channels=channels,unit='Confirmed: uV',mapping=True,confirmed=False)
        receiver=SimpleNamespace(meta=meta);win.receiver=receiver
        with patch.object(win,'start_monitoring') as start:
            win.events.put(('connected',receiver));win.handle_events();start.assert_called_once()
        self.assertTrue(win.mapping.get());self.assertEqual(win.channels,channels)
        win.receiver=None

    def test_workspace_exposes_two_peer_modes(self):
        from views.workspace import WorkspaceApp
        app=WorkspaceApp(self.root)
        app.open_post();app.open_live()
        self.assertIs(app.post_app.workspace,app)
        self.assertEqual(app.live_window.profile.get(),'ECG quality')
        self.assertEqual(app.live_window.on_post,app.open_post)
        app.live_window.close();app.post_window.destroy()


if __name__=='__main__':unittest.main()
