"""Synthetic real-LSL source: C12 loses half its amplitude during 8–18 s / 30 s."""
import numpy as np
from services.lsl_stream import DemoOutlet


class FaultDemo(DemoOutlet):
    def run(self):
        try:
            import pylsl
            fs=1024
            info=pylsl.StreamInfo('DEMO_ONLY_ElectrodeFault_5Hz','EEG',2,fs,'float32',self.source_id)
            chs=info.desc().append_child('channels')
            for name in ('C11','C12'):
                c=chs.append_child('channel');c.append_child_value('label',name);c.append_child_value('unit','uV')
            outlet=pylsl.StreamOutlet(info,chunk_size=32);self.ready.set()
            start,n=pylsl.local_clock(),0
            while not self.stop_event.is_set():
                if self.stop_event.wait(max(0,start+(n+32)/fs-pylsl.local_clock())):break
                t=np.arange(n,n+32)/fs
                fault=((t%30)>=8)&((t%30)<18)
                x=np.column_stack((5000*np.sin(2*np.pi*5*t)+1000,
                    np.where(fault,2500.,5000.)*np.sin(2*np.pi*5*t+.2)-500))
                outlet.push_chunk(x.tolist(),timestamp=start+(n+31)/fs);n+=32
        except Exception as exc:self.error=str(exc);self.ready.set()
