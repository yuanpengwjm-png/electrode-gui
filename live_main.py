"""Packaged application entry. --live opens the live screen directly."""
if __name__ == '__main__':
    from runtime_bootstrap import ensure_project_runtime
    ensure_project_runtime()

import json
from pathlib import Path
import sys
import time
import tkinter as tk
from views.workspace import WorkspaceApp


def main():
    root=tk.Tk();app=WorkspaceApp(root)
    if '--live' in sys.argv or '--smoke-test' in sys.argv:
        app.open_live()
    if '--smoke-test' in sys.argv:
        win=app.live_window;win.withdraw();win.start_demo()
        history=[];errors=[];started=time.monotonic()
        root.report_callback_exception=lambda c,e,t:errors.append(str(e))
        def record():
            history.append(dict(elapsed=time.monotonic()-started,states={e.name:e.metric('live').color for e in win.current}))
            if time.monotonic()-started<25:root.after(250,record)
        root.after(250,record)
        def finish():
            phases=[h['states'] for h in history]
            good=[i for i,s in enumerate(phases) if s=={'C11':'green','C12':'green'}]
            bad=[i for i,s in enumerate(phases) if s=={'C11':'green','C12':'red'}]
            success=bool(not errors and good and bad and min(good)<min(bad)<max(good))
            out=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent/'output/live_validation'
            out.mkdir(parents=True,exist_ok=True)
            (out/'live_smoke.json').write_text(json.dumps(dict(ok=success,synthetic=True,real_hardware_verified=False,history=history,errors=errors),indent=2),encoding='utf-8')
            win.close();root.destroy()
        root.after(26000,finish)
    root.mainloop()


if __name__=='__main__':main()
