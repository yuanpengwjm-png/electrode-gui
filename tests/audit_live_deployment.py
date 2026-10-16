"""Reproduce deployment limitations; these probes record behavior, not acceptance criteria."""
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.live_analysis import LiveConfig, analyze_live_window, frame_problem
from services.live_discovery import choose_stream
from services.lsl_stream import SampleBuffer


def main():
    fs=512;t=np.arange(fs*10)/fs;cfg=LiveConfig(profile='ecg',window_s=10,mapping_confirmed=True)
    rows=[]
    for width in (.012,.018,.025,.035):
        clean=np.zeros(len(t))
        for beat in np.arange(.5,10,.85):
            clean+=1000*np.exp(-((t-beat)/width)**2)+180*np.exp(-((t-beat-.24)/.065)**2)
        for label,y in [('clean',clean),('gain_x10',10*clean),('50Hz_100uV',clean+100*np.sin(2*np.pi*50*t))]:
            item=analyze_live_window(y[:,None],t,['A1'],[1],fs,cfg)['electrodes'][0]
            rows.append(dict(qrs_width_s=width,input=label,color=item.metric('live').color,
                             reasons=item.metric('live').message,metrics={k:v.values.get('value') for k,v in item.extra.items()}))
    other=SimpleNamespace(channel_count=lambda:3,nominal_srate=lambda:100,channel_format=lambda:1,
                          source_id=lambda:'accelerometer',hostname=lambda:'lab',uid=lambda:'motion1',name=lambda:'Motion sensor')
    capacities=[dict(channels=n,rate_hz=rate,buffer_s=SampleBuffer(n,rate).capacity/rate)
                for n,rate in ((128,2048),(128,8192),(256,8192))]
    gap=t.copy();gap[len(gap)//2:]+=.02
    benchmark=np.tile(clean[:,None],(1,128));started=time.perf_counter()
    result=analyze_live_window(benchmark,t,[f'ch{i}' for i in range(128)],[1]*128,fs,cfg)
    report=dict(synthetic=True,real_hardware_verified=False,
                unrelated_numeric_stream_auto_selected=choose_stream([other]) is other,
                timestamp_gap_rejection=frame_problem(gap,fs,10),buffer_capacities=capacities,
                algorithm_only_128ch_512hz_s=time.perf_counter()-started,
                algorithm_only_results=len(result['electrodes']),morphology_probes=rows)
    out=Path(__file__).resolve().parents[1]/'output/live_validation/deployment_audit.json'
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='morphology_probes'},indent=2))
    for row in rows:print(row['qrs_width_s'],row['input'],row['color'],'pSQI',row['metrics']['psqi'])


if __name__=='__main__':main()
