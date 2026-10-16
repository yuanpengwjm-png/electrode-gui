"""Wrong-interpreter recovery must validate the target and avoid restart loops."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import runtime_bootstrap as boot


class RuntimeTests(unittest.TestCase):
    def test_healthy_runtime_is_unchanged(self):
        with patch.object(boot.importlib.util,'find_spec',return_value=object()), patch.object(boot.subprocess,'Popen') as launch:
            boot.ensure_project_runtime();launch.assert_not_called()

    def test_missing_module_redirects_to_verified_project_python(self):
        target=boot.project_python()
        with patch.object(boot.importlib.util,'find_spec',return_value=None), \
             patch.object(boot.sys,'executable',str(target.parent/'other-python.exe')), \
             patch.object(boot.sys,'argv',['live_main.py','--live']), \
             patch.dict(boot.os.environ,{},clear=True), \
             patch.object(boot.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as probe, \
             patch.object(boot.subprocess,'Popen') as launch:
            with self.assertRaises(SystemExit):boot.ensure_project_runtime()
            self.assertEqual(probe.call_args.args[0][0],str(target))
            self.assertEqual(launch.call_args.args[0],[str(target),str(Path('live_main.py').resolve()),'--live'])
            self.assertEqual(launch.call_args.kwargs['env']['ELECTRODE_QA_RUNTIME_HANDOFF'],str(target))

    def test_handoff_guard_prevents_loop(self):
        target=boot.project_python()
        with patch.object(boot.importlib.util,'find_spec',return_value=None), \
             patch.dict(boot.os.environ,{'ELECTRODE_QA_RUNTIME_HANDOFF':str(target)}), \
             patch.object(boot.subprocess,'Popen') as launch:
            boot.ensure_project_runtime();launch.assert_not_called()

    def test_broken_target_is_not_launched(self):
        with patch.object(boot.importlib.util,'find_spec',return_value=None), \
             patch.object(boot.sys,'executable','wrong-python.exe'), \
             patch.dict(boot.os.environ,{},clear=True), \
             patch.object(boot.subprocess,'run',return_value=SimpleNamespace(returncode=1)), \
             patch.object(boot.subprocess,'Popen') as launch:
            boot.ensure_project_runtime();launch.assert_not_called()


if __name__=='__main__':unittest.main()
