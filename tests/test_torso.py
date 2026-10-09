"""Physical-side mapping and linked 3D GUI/window behavior with synthetic BDFs."""
from dataclasses import asdict
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from config import COLORS
from models import ElectrodeResult, MetricResult
from services.analysis_service import AnalysisService
from utils.project_io import save_project
from views.torso_geometry import TorsoLayout, project, visible
from test_analysis import fixture_folder
from test_record_scope import app_for
from test_windows import sine_record, settings


def torso_record(folder):
    record = sine_record(folder)
    # Relabel only this generated fixture, never a laboratory source.
    with Path(record.path).open('r+b') as stream:
        stream.seek(256)
        stream.write(b'A1'.ljust(16) + b'D32'.ljust(16))
    return record


class TorsoTests(unittest.TestCase):
    def test_person_sides_back_pairs_and_serpentine_numbering(self):
        positions = TorsoLayout().positions()
        self.assertEqual(set(positions), {f'{b}{n}' for b in 'ABCD' for n in range(1,33)})
        self.assertEqual(len({p['point'] for p in positions.values()}), 128)
        for bank in 'AC':
            self.assertTrue(all(positions[f'{bank}{n}']['point'][0] > 0 for n in range(1,33)))
        for bank in 'BD':
            self.assertTrue(all(positions[f'{bank}{n}']['point'][0] < 0 for n in range(1,33)))
        for front,back in (('A','C'),('B','D')):
            for n in range(1,33):
                a,b = (positions[f'{name}{n}']['point'] for name in (front,back))
                self.assertEqual(a, (b[0],-b[1],b[2]))
        for bank in 'ABCD':
            for lo,hi in ((1,10),(11,21),(22,32)):
                zs = [positions[f'{bank}{n}']['point'][2] for n in range(lo,hi+1)]
                self.assertEqual(zs, sorted(zs,reverse=lo==11))
        front_names = ('B32','B11','B10','A10','A11','A32')
        front_x = [project(positions[n]['point'],0)[0] for n in front_names]
        self.assertEqual(front_x, sorted(front_x))
        back_names = ('C32','C11','C10','D10','D11','D32')
        back_x = [project(positions[n]['point'],180)[0] for n in back_names]
        self.assertEqual(back_x, sorted(back_x))
        for yaw,face in ((0,'Front'),(180,'Back')):
            seen = [p for p in positions.values() if visible(p['normal'],yaw,6)]
            self.assertEqual(len(seen),64)
            self.assertTrue(all(p['face']==face for p in seen))

    def test_3d_scrubbing_clicks_camera_playback_and_invalidation(self):
        with fixture_folder() as folder:
            record = torso_record(folder)
            result = AnalysisService(settings()).analyze([record], ['A1','D32'], 'A1')
            with app_for([record]) as app:
                app.mode.set('Gain error'); app.accept_result(result); app.open_torso()
                popup = app.torso_window
                popup.timeline._scrub('1')
                self.assertEqual(app.result_scopes[app.scope.get()], ('frame',1))
                self.assertEqual(popup.view.electrodes['D32'].gain.color,'red')
                self.assertIn('D32',popup.alerts.get_children())
                popup.alerts.selection_set('D32'); popup.pick_alert()
                self.assertEqual(popup.view.yaw,180)
                self.assertEqual(app.focused_electrode,'D32')
                self.assertIn('10-20 s',popup.detail.get('1.0','end'))
                markers = popup.view.scene(800,1000)[1]
                active = [m for m in markers if m['active']]
                self.assertEqual([m['name'] for m in active],['D32'])
                self.assertEqual(active[0]['color'],COLORS['red'])
                self.assertEqual(sum(not m['active'] for m in markers),63)
                # A second window changes data while preserving camera and focus.
                app.select_window(0)
                self.assertEqual(popup.view.yaw,180)
                self.assertEqual(popup.view.selected,'D32')
                self.assertEqual(popup.view.electrodes['D32'].gain.color,'green')
                self.assertIn('0-10 s',popup.detail.get('1.0','end'))
                self.assertNotIn('D32',popup.alerts.get_children())
                popup.timeline.toggle()
                self.assertTrue(popup.timeline.playing)
                self.assertFalse(app.timeline.playing)
                app.timeline.toggle()
                self.assertTrue(app.timeline.playing)
                self.assertFalse(popup.timeline.playing)
                self.assertIsNone(popup.timeline.timer)
                popup.timeline.toggle()
                self.assertFalse(app.timeline.playing)
                self.assertIsNone(app.timeline.timer)
                app.limit_vars['bench_window_s'].set('8')
                self.assertIsNone(app.result)
                self.assertFalse(popup.timeline.playing)
                self.assertIsNone(popup.timeline.timer)
                self.assertEqual(popup.view.electrodes,{})
                self.assertEqual(popup.alerts.get_children(),())
                popup.close(); self.assertIsNone(app.torso_window)

    def test_unmapped_channels_stay_unmapped_and_pick_matches_label(self):
        with fixture_folder() as folder:
            with app_for([torso_record(folder)]) as app:
                app.open_torso(); popup=app.torso_window
                green=MetricResult('green','Synthetic pass')
                red=MetricResult('red','Synthetic fault')
                a=ElectrodeResult('A17',red,green,green,green)
                exg=ElectrodeResult('EXG1',red,green,green,green)
                popup.show([a,exg],'gain','SYNTHETIC TEST',['Gain error'],None,[],None,'')
                self.assertIn('Unmapped: EXG1',popup.mapping_notice.get())
                self.assertEqual(popup.alerts.item('EXG1')['values'][1],'Unmapped')
                popup.update_idletasks()
                marker=next(m for m in popup.view.hits if m['name']=='A17')
                event=SimpleNamespace(x=marker['x'],y=marker['y'])
                with patch.object(popup.view,'on_select') as picked:
                    popup.view.press(event); popup.view.release(event)
                    picked.assert_called_once_with(a)
                # A drag rotates the model instead of opening the wrong channel.
                with patch.object(popup.view,'on_select') as picked:
                    popup.view.press(event)
                    moved=SimpleNamespace(x=event.x+100,y=event.y+5)
                    popup.view.motion(moved); popup.view.release(moved)
                    picked.assert_not_called()
                self.assertEqual(popup.view.yaw,50)
                popup.close()

    def test_layout_project_roundtrip_and_export_keep_exact_window(self):
        with fixture_folder() as folder:
            record=torso_record(folder)
            result=AnalysisService(settings()).analyze([record],['A1','D32'],'A1')
            with app_for([record]) as app:
                app.mode.set('Gain error');app.accept_result(result);app.open_torso()
                popup=app.torso_window
                popup.timeline._scrub('1');popup.view.face('Back')
                # Changing the display layout never changes measured values.
                popup.order.set('Outer low at top');popup.change_layout()
                self.assertIs(app.result,result)
                self.assertTrue(app.torso_layout.top_to_bottom)
                export=folder/'export';export.mkdir()
                with patch('gui.filedialog.askdirectory',return_value=str(export)):
                    app.export()
                self.assertTrue((export/'torso_view.png').is_file())
                layout=json.loads((export/'torso_layout.json').read_text())
                self.assertTrue(layout['schematic'])
                self.assertEqual(layout['camera']['yaw'],180)
                self.assertIn('10-20 s',layout['scope'])
                self.assertEqual(layout['metric'],'gain')
                self.assertEqual(len(layout['positions']),128)
                data=json.loads((export/'results.json').read_text())
                self.assertEqual(data['export_view']['scope'],layout['scope'])
                project=json.loads((export/'project.json').read_text())
                self.assertEqual(project['display']['torso'],asdict(app.torso_layout))
                popup.order.set('Outer low at bottom');popup.change_layout()
                app.load_path(export/'project.json')
                self.assertTrue(app.torso_layout.top_to_bottom)
                self.assertTrue(popup.layout.top_to_bottom)
                self.assertIsNone(app.result)
                # Older projects without a display block load the user's defaults.
                old=folder/'old-project.json'
                save_project(old,[record],settings(),['A1','D32'],'A1')
                app.load_path(old)
                self.assertEqual(app.torso_layout,TorsoLayout())
                popup.close()


if __name__ == '__main__':
    unittest.main()
