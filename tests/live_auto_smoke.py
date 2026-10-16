"""Synthetic ECG through real LSL: automatic discovery, stale clearing, reconnection."""
import json
from pathlib import Path
import sys
import threading
import time
import uuid
import tkinter as tk
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pylsl
from services.live_discovery import stream_key
from views.live_window import LiveWindow


def main():
    fs=256;source_id='QA_AUTO_TEST_'+uuid.uuid4().hex
    info=pylsl.StreamInfo('SYNTHETIC ECG QA TEST','ECG',2,fs,'float32',source_id)
    channels=info.desc().append_child('channels')
    for name in ('C11','C12'):
        ch=channels.append_child('channel');ch.append_child_value('label',name);ch.append_child_value('unit','uV')
    outlet=pylsl.StreamOutlet(info,chunk_size=16)
    stream=pylsl.resolve_byprop('source_id',source_id,timeout=5)[0]
    stop=threading.Event();started=time.monotonic();base=pylsl.local_clock()
    def send():
        index=0
        while not stop.is_set():
            elapsed=time.monotonic()-started
            if 19<=elapsed<27:
                index=round(elapsed*fs);stop.wait(.02);continue
            t=np.arange(index,index+16)/fs
            phase=(t+.425)%.85-.425
            y=1000*np.exp(-(phase/.015)**2)+100*np.exp(-((phase-.23)/.055)**2)
            other=y if elapsed<12 else np.zeros(len(y))
            outlet.push_chunk(np.column_stack((y,other)).tolist(),base+(index+15)/fs)
            index+=16
            stop.wait(max(0,base+index/fs-pylsl.local_clock()))
    worker=threading.Thread(target=send,daemon=True);worker.start()
    root=tk.Tk();root.withdraw();win=LiveWindow(root);win.withdraw()
    win.remembered_source=stream_key(stream);win.scan_interval.set('2')
    seen=set();errors=[];initial_receiver=None;configured=False
    root.report_callback_exception=lambda c,e,t:errors.append(str(e))
    def poll():
        nonlocal configured,initial_receiver
        elapsed=time.monotonic()-started
        if win.meta and not configured:
            initial_receiver=win.receiver;seen.add('automatic_connection')
            for channel in win.channels:channel['use']=True
            win.update_rows()
            win.mapping.set(True);win.start_monitoring();configured=True
        if win.last_result and win.last_result['valid']:
            if 'bsqi' in win.current[0].extra:seen.add('ecg_metrics')
            c12=next((e for e in win.current if e.name=='C12'),None)
            if c12 and c12.extra.get('integrity') and c12.extra['integrity'].color=='red':
                seen.add('flatline_alert')
                if win.rotation_paused:seen.add('rotation_paused')
            if elapsed>27 and win.receiver is not initial_receiver and win.monitoring:seen.add('resumed_monitoring')
        if 21<elapsed<27 and win.current and all(e.metric('live').color=='gray' for e in win.current):seen.add('stale_cleared')
        if elapsed<44:root.after(100,poll)
        else:
            expected={'automatic_connection','ecg_metrics','flatline_alert','rotation_paused','resumed_monitoring','stale_cleared'}
            result=dict(ok=seen==expected and not errors,seen=sorted(seen),errors=errors,synthetic=True,real_hardware_verified=False)
            out=Path(__file__).resolve().parents[1]/'output/live_validation/auto_ecg_smoke.json'
            out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding='utf-8')
            print(json.dumps(result));stop.set();win.close();root.destroy()
    root.after(100,poll);root.mainloop();worker.join(2)


if __name__=='__main__':main()
