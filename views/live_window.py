"""Live LSL sine screen sharing the existing application's grid, torso and metrics."""
from dataclasses import asdict
from pathlib import Path
import copy
import json
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import numpy as np
from config import AnalysisSettings
from services.lsl_stream import Receiver, unit_to_uv
from services.live_analysis import LiveConfig, analyze_live_window, unavailable, Confirmation, frame_problem
from services.live_discovery import choose_stream, stream_key, metadata_signature
from views.heatmap_view import HeatmapView
from views.torso_view import TorsoView
from views.torso_geometry import TorsoLayout


class LiveWindow(tk.Toplevel):
    def __init__(self,parent,settings=None,layout=None,on_post=None):
        super().__init__(parent)
        self.title('Electrode QA | Real-time')
        self.geometry(f'1360x{min(930,self.winfo_screenheight()-70)}');self.minsize(1000,620)
        self.settings=copy.deepcopy(settings or AnalysisSettings())
        self.settings.analysis_mode='bench_sine';self.settings.exclude_last_s=0
        self.events=queue.Queue();self.receiver=self.demo=self.meta=self.config=None
        self.streams=[];self.channels=[];self.current=[];self.changes=[];self.last_colors={}
        self.monitoring=self.closed=self.scanning=False
        self.revision=0;self.job=None;self.next_analysis=0;self.last_result=None;self.focused=None
        self.last_display_state=None;self.confirmation=Confirmation()
        self.on_post=on_post
        self.remembered_source=None;self.resume_setup=None;self.next_scan=0
        self.connected_at=None;self.rotation_paused=False;self.alert_target=None
        self.rotation_last=time.monotonic()
        self.build(layout or TorsoLayout())
        self.protocol('WM_DELETE_WINDOW',self.close);self.bind('<Destroy>',self.on_destroy,add='+')
        self.timer=self.after(100,self.tick)
        self.rotation_timer=self.after(40,self.rotate)

    @staticmethod
    def button(parent,text,command,side='left'):
        b=ttk.Button(parent,text=text,command=command);b.pack(side=side,padx=3,pady=2);return b

    def build(self,layout):
        shell=ttk.Frame(self,padding=12);shell.pack(fill='both',expand=True)
        heading=ttk.Frame(shell);heading.pack(fill='x')
        ttk.Label(heading,text='Real-time · LSL',font=('Segoe UI',19,'bold')).pack(side='left')
        self.button(heading,'Post analysis',self.open_post,side='right')
        ttk.Button(heading,text='Real-time (current)',state='disabled').pack(side='right',padx=6)
        ttk.Label(shell,text='Signal-path screening. A red channel means check required; it does not identify physical electrode damage.').pack(anchor='w')
        bar=ttk.Frame(shell);bar.pack(fill='x',pady=6)
        self.scan_button=self.button(bar,'1. Search LSL',self.search)
        self.stream_box=ttk.Combobox(bar,state='readonly',width=62);self.stream_box.pack(side='left',fill='x',expand=True,padx=6)
        self.button(bar,'2. Connect',self.connect_selected);self.button(bar,'Disconnect',self.disconnect)
        auto=ttk.Frame(shell);auto.pack(fill='x',pady=(0,5))
        self.auto_connect=tk.BooleanVar(value=True);self.scan_interval=tk.StringVar(value='5')
        ttk.Checkbutton(auto,text='Auto-discover / reconnect',variable=self.auto_connect,command=self.auto_changed).pack(side='left')
        ttk.Label(auto,text='Retry every (s)').pack(side='left',padx=(15,4))
        ttk.Spinbox(auto,from_=2,to=60,textvariable=self.scan_interval,width=5).pack(side='left')
        self.button(auto,'Choose another source',self.forget_source)
        self.banner=tk.Label(shell,text='Not connected',anchor='w',bg='#E0E8F0',padx=10,pady=7,font=('Segoe UI',11,'bold'));self.banner.pack(fill='x')
        self.source=tk.StringVar(value='Select the correct ActiView stream. No IP / port required.')
        ttk.Label(shell,textvariable=self.source,wraplength=1250).pack(anchor='w',pady=4)
        self.status=tk.StringVar(value='Search ActiView, or try the explicitly synthetic fault demo.')
        footer=ttk.Frame(shell);footer.pack(side='bottom',fill='x',pady=5)
        self.button(footer,'Save window + log',self.save);self.button(footer,'Metadata',self.show_metadata)
        ttk.Label(footer,textvariable=self.status,wraplength=880).pack(side='left',padx=8)
        body=ttk.Frame(shell);body.pack(fill='both',expand=True)
        left_wrap=ttk.Frame(body,width=380);left_wrap.pack(side='left',fill='y',padx=(0,12));left_wrap.pack_propagate(False)
        settings_canvas=tk.Canvas(left_wrap,highlightthickness=0,width=355,bg='#F4F7FA')
        settings_scroll=ttk.Scrollbar(left_wrap,command=settings_canvas.yview)
        settings_scroll.pack(side='right',fill='y');settings_canvas.pack(fill='both',expand=True)
        settings_canvas.configure(yscrollcommand=settings_scroll.set)
        left=ttk.Frame(settings_canvas);left_id=settings_canvas.create_window(0,0,anchor='nw',window=left)
        left.bind('<Configure>',lambda _:settings_canvas.configure(scrollregion=settings_canvas.bbox('all')))
        settings_canvas.bind('<Configure>',lambda e:settings_canvas.itemconfigure(left_id,width=e.width))
        self.settings_canvas=settings_canvas
        right=ttk.Frame(body);right.pack(side='left',fill='both',expand=True)
        self.profile=tk.StringVar(value='ECG quality')
        profile=ttk.Combobox(left,textvariable=self.profile,state='readonly',values=('ECG quality','Known sine'))
        profile.pack(fill='x',pady=(0,5));profile.bind('<<ComboboxSelected>>',self.change_profile)
        self.profile_hint=tk.StringVar(value='ECG: SQI / baseline / flatline; prototype thresholds.')
        ttk.Label(left,textvariable=self.profile_hint,wraplength=350).pack(anchor='w',pady=(0,5))
        ttk.Label(left,text='Only select physically connected test channels',font=('Segoe UI',10,'bold')).pack(anchor='w')
        box=ttk.Frame(left);box.pack(fill='x',pady=4)
        self.tree=ttk.Treeview(box,columns=('use','index','label','unit'),show='headings',height=5,selectmode='browse')
        for key,title,width in (('use','Use',35),('index','#',35),('label','Channel',145),('unit','Unit',75)):
            self.tree.heading(key,text=title);self.tree.column(key,width=width,stretch=key=='label')
        scroll=ttk.Scrollbar(box,command=self.tree.yview);self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y');self.tree.pack(fill='x');self.tree.bind('<Button-1>',self.toggle_channel)
        row=ttk.Frame(left);row.pack(fill='x')
        self.button(row,'Map label',self.map_label);self.button(row,'Clear selection',self.clear_channels)
        ttk.Label(left,text='Click Use to toggle; Map label edits the selected row.',foreground='#657588').pack(anchor='w')
        self.mapping=tk.BooleanVar(value=False)
        ttk.Checkbutton(left,text='I verified stream / physical channel mapping',variable=self.mapping,command=self.invalidate).pack(anchor='w',pady=3)
        self.unit=tk.StringVar(value='Auto: stream metadata')
        units=ttk.Combobox(left,textvariable=self.unit,state='readonly',values=('Auto: stream metadata','Confirmed: uV','Confirmed: mV','Confirmed: V','Confirmed: custom uV/count'))
        units.pack(fill='x',pady=3);units.bind('<<ComboboxSelected>>',self.invalidate)
        self.vars={};self.sine_rows=[]
        for key,label,value in [('frequency','Input frequency (Hz)',5),('amplitude','Actual input (mVpp)',10),('window','Window (s), 2–10',5),('step','Recheck every (s)',1),('scale','Custom uV/count',1),('gain','Gain limit (%)',self.settings.gain_limit_pct),('frequency_limit','Frequency error (%)',self.settings.frequency_limit_pct or .1),('thd','THD limit (%)',self.settings.thd_limit_pct or 1)]:
            row=ttk.Frame(left);row.pack(fill='x',pady=1)
            ttk.Label(row,text=label).pack(side='left')
            var=tk.StringVar(value=str(value));self.vars[key]=var
            entry=ttk.Entry(row,textvariable=var,width=9);entry.pack(side='right');var.trace_add('write',self.invalidate)
            if key in ('frequency','amplitude','gain','frequency_limit','thd'):self.sine_rows.append(entry)
        for text,fn in [('3. Start monitoring',self.start_monitoring),('Stop monitoring (keep receiving)',self.stop_monitoring)]:
            ttk.Button(left,text=text,command=fn).pack(fill='x',pady=3)
        ttk.Label(left,text='Green: evaluated limits met\nYellow: review / confirmation needed\nRed: signal check required\nGray: no current assessment\n\nECG default: last 10 s, recheck every 1 s.\nTwo red windows: persistent alert (overlapping).\nNo final-second file crop in live mode.',foreground='#657588').pack(anchor='w',pady=5)
        self.counts=tk.StringVar(value='No current assessment')
        ttk.Label(right,textvariable=self.counts,font=('Segoe UI',11,'bold'),wraplength=860).pack(anchor='w',pady=3)
        # Reserve detail and waveform space before the expanding grid.
        bottom=ttk.Frame(right);bottom.pack(side='bottom',fill='x')
        self.wave=tk.Canvas(bottom,height=110,bg='white',highlightthickness=0);self.wave.pack(fill='x',pady=4)
        self.detail=tk.Text(bottom,height=4,wrap='word',font=('Segoe UI',10),relief='flat');self.detail.pack(fill='x')
        self.set_detail('Click an electrode for its current waveform and reasons.')
        self.notebook=ttk.Notebook(right);self.notebook.pack(fill='both',expand=True)
        grid_tab=ttk.Frame(self.notebook);torso_tab=ttk.Frame(self.notebook)
        self.notebook.add(grid_tab,text='Live electrode grid');self.notebook.add(torso_tab,text='Live 3D torso')
        self.grid=HeatmapView(grid_tab,self.show_detail);self.grid.pack(fill='both',expand=True)
        self.grid.empty_text='Waiting for an LSL source\nVerify channels, then start monitoring'
        row=ttk.Frame(torso_tab);row.pack(fill='x')
        self.torso=TorsoView(torso_tab,self.show_detail,layout)
        for face in ('Front','Back'):self.button(row,face,lambda f=face:self.face_torso(f))
        self.button(row,'Pause / resume',self.toggle_rotation)
        self.button(row,'Next alert',self.next_alert)
        self.rotation_status=tk.StringVar(value='Rotating · 18 degrees/s')
        ttk.Label(torso_tab,textvariable=self.rotation_status).pack(fill='x')
        self.torso.canvas.bind('<ButtonPress-1>',lambda _:self.pause_rotation('Paused for inspection'),add='+')
        self.torso.pack(fill='both',expand=True)
        self.notebook.select(torso_tab)
        self.change_profile()

    def open_post(self):
        if self.on_post:self.on_post();return
        from gui import ElectrodeQAApp
        if not hasattr(self,'post_window') or not self.post_window.winfo_exists():
            self.post_window=tk.Toplevel(self);self.post_app=ElectrodeQAApp(self.post_window)
        self.post_window.deiconify();self.post_window.lift()

    def change_profile(self,*_):
        ecg=self.profile.get()=='ECG quality'
        for entry in self.sine_rows:entry.configure(state='disabled' if ecg else 'normal')
        self.profile_hint.set('ECG: SQI / baseline / flatline; prototype thresholds.' if ecg else 'Known sine only: gain / frequency / THD / residuals.')
        self.vars['window'].set('10' if ecg else '5')
        self.invalidate()

    def pause_rotation(self,reason):
        self.rotation_paused=True;self.rotation_status.set(reason)

    def face_torso(self,face):
        self.pause_rotation('Paused for inspection');self.torso.face(face)

    def alerts(self):
        return sorted([e for e in self.current if e.metric('live').color in ('red','yellow')],
                      key=lambda e:(e.metric('live').color!='red',e.name))

    def toggle_rotation(self):
        if not self.rotation_paused:self.pause_rotation('Paused for inspection');return
        if self.alerts():
            self.rotation_status.set('Paused: review current red / yellow alerts first');return
        self.rotation_paused=False;self.alert_target=None;self.rotation_last=time.monotonic()
        self.rotation_status.set('Rotating · 18 degrees/s')

    def next_alert(self):
        alerts=self.alerts()
        if not alerts:return
        names=[e.name for e in alerts]
        index=(names.index(self.focused)+1)%len(names) if self.focused in names else 0
        self.show_detail(alerts[index]);self.pause_rotation('Paused on alert: '+alerts[index].name)

    def rotate(self):
        if self.closed:return
        now=time.monotonic();elapsed=now-self.rotation_last;self.rotation_last=now
        if not self.rotation_paused and self.torso.drag is None and self.winfo_viewable():
            self.torso.yaw=(self.torso.yaw+18*elapsed)%360
            if self.notebook.index('current')==1:self.torso.draw()
        self.rotation_timer=self.after(40,self.rotate)

    def selected_channels(self):return [c for c in self.channels if c['use']]

    def invalidate(self,*_):
        self.resume_setup=None
        self.stop_monitoring();self.status.set('Settings changed. Click Start monitoring to use the new configuration.')

    def update_rows(self):
        self.tree.delete(*self.tree.get_children())
        for c in self.channels:self.tree.insert('','end',iid=str(c['index']),values=('Yes' if c['use'] else '—',c['index']+1,c['name'],c['unit'] or '?'))

    def toggle_channel(self,event):
        row=self.tree.identify_row(event.y)
        if row and self.tree.identify_column(event.x)=='#1':
            self.channels[int(row)]['use']=not self.channels[int(row)]['use'];self.mapping.set(False);self.update_rows();self.invalidate()

    def map_label(self):
        if not self.tree.selection():return
        c=self.channels[int(self.tree.selection()[0])]
        name=simpledialog.askstring('Physical channel label','Verified physical label for this LSL column:',initialvalue=c['name'],parent=self)
        if name and name.strip():c['name']=name.strip();self.mapping.set(False);self.update_rows();self.invalidate()

    def clear_channels(self):
        for c in self.channels:c['use']=False
        self.mapping.set(False);self.update_rows();self.invalidate()

    def scales(self,channels):
        if self.unit.get().startswith('Auto'):return [unit_to_uv(c['unit']) for c in channels]
        factor={'Confirmed: uV':1.,'Confirmed: mV':1000.,'Confirmed: V':1e6}.get(self.unit.get())
        if factor is None:factor=float(self.vars['scale'].get())
        if not np.isfinite(factor) or factor<=0:raise ValueError('Conversion factor must be positive and finite.')
        return [factor]*len(channels)

    def search(self):
        if self.scanning:return
        self.scanning=True;self.scan_button.configure(state='disabled');self.status.set('Searching LSL for 3 seconds…')
        def worker():
            try:
                import pylsl
                self.events.put(('streams',pylsl.resolve_streams(wait_time=3)))
            except Exception as exc:self.events.put(('search_error',str(exc)))
        threading.Thread(target=worker,daemon=True).start()

    def auto_changed(self):
        self.next_scan=0
        self.status.set('Automatic discovery enabled.' if self.auto_connect.get() else 'Automatic discovery paused.')

    def forget_source(self):
        self.disconnect();self.remembered_source=None;self.resume_setup=None
        self.auto_connect.set(True);self.next_scan=0;self.search()

    def prepare_reconnect(self):
        if self.monitoring and self.meta:
            self.resume_setup=dict(signature=metadata_signature(self.meta),channels=copy.deepcopy(self.channels),
                                   unit=self.unit.get(),mapping=self.mapping.get())
        self.stop_monitoring()
        if self.receiver:self.receiver.stop()
        self.receiver=None;self.connected_at=None

    def discover_if_needed(self):
        if not self.auto_connect.get() or self.demo:return
        now=time.monotonic()
        if self.receiver:
            r=self.receiver
            last=r.buffer.last_received if r.buffer else None
            if r.failure or not r.is_alive() or (self.connected_at is not None and now-(last or self.connected_at)>6):
                self.prepare_reconnect()
                self.banner.configure(text='Source interrupted · waiting for the same source',bg='#E0E8F0')
            else:return
        if self.scanning or now<self.next_scan:return
        try:
            interval=float(self.scan_interval.get())
            if not np.isfinite(interval) or not 2<=interval<=60:raise ValueError()
        except ValueError:
            self.status.set('Discovery interval must be 2–60 seconds.');return
        self.next_scan=now+interval;self.search()

    def connect_selected(self):
        index=self.stream_box.current()
        if index<0 or index>=len(self.streams):
            messagebox.showinfo('Choose stream','Search and select ActiView first.',parent=self);return
        auto=self.auto_connect.get()
        self.disconnect();self.resume_setup=None;self.auto_connect.set(auto);self.connect_info(self.streams[index])

    def connect_info(self,info):
        self.remembered_source=stream_key(info);self.connected_at=time.monotonic()
        self.stop_monitoring();self.meta=None;self.channels=[];self.update_rows();self.unit.set('Auto: stream metadata')
        self.mapping.set(False)
        self.receiver=Receiver(info,self.events);self.receiver.start();self.banner.configure(text='Connecting…',bg='#E0E8F0')

    def disconnect(self):
        self.auto_connect.set(False);self.resume_setup=None
        self.stop_monitoring()
        if self.receiver:self.receiver.stop();self.receiver=None
        if self.demo:self.demo.stop();self.demo=None
        self.banner.configure(text='Disconnected · no current assessment',bg='#E0E8F0')

    def stop_monitoring(self):
        self.revision+=1;self.monitoring=False;self.last_result=None;self.confirmation.reset()
        self.publish(unavailable([c['name'] for c in self.selected_channels()],'Not assessed / monitoring stopped'))
        self.banner.configure(text=('SYNTHETIC DEMO · ' if self.meta and self.meta['demo'] else '')+'Monitoring stopped · no current assessment',bg='#E0E8F0')

    def start_monitoring(self):
        try:
            if not self.meta or not self.receiver or self.receiver.failure or not self.receiver.is_alive():raise ValueError('Connect to a running LSL data stream first.')
            channels=self.selected_channels();names=[c['name'] for c in channels]
            if not names or len(names)!=len(set(names)):raise ValueError('Select uniquely labeled test channels.')
            limits=copy.deepcopy(self.settings)
            ecg=self.profile.get()=='ECG quality'
            if not ecg:
                for key,attr in [('gain','gain_limit_pct'),('frequency_limit','frequency_limit_pct'),('thd','thd_limit_pct')]:setattr(limits,attr,float(self.vars[key].get()))
            cfg=LiveConfig(frequency_hz=5 if ecg else float(self.vars['frequency'].get()),
                           input_mVpp=10 if ecg else float(self.vars['amplitude'].get()),
                           window_s=float(self.vars['window'].get()),hop_s=float(self.vars['step'].get()),
                           input_confirmed=True,mapping_confirmed=self.mapping.get(),limits=limits,
                           profile='ecg' if ecg else 'sine')
            cfg.validate(self.meta['nominal_srate'])
            if self.receiver.buffer.capacity<round(cfg.window_s*self.meta['nominal_srate']):raise ValueError('Window exceeds the 64 MiB buffer; shorten window or lower the stream rate.')
            self.scales(channels);self.revision+=1;self.config=cfg;self.monitoring=True;self.next_analysis=0
            self.last_result=None;self.confirmation.reset();self.changes=[];self.last_colors={}
            self.publish(unavailable(names,'Waiting for a complete continuous window'));self.status.set('Monitoring started.')
        except (ValueError,TypeError) as exc:messagebox.showerror('Cannot start',str(exc),parent=self)

    def start_demo(self):
        self.disconnect()
        self.profile.set('Known sine');self.change_profile()
        from services.live_demo import FaultDemo
        demo=self.demo=FaultDemo();demo.start()
        self.status.set('Synthetic demo: C12 drops from 10 to 5 mVpp at 8–18 s in each 30 s cycle.')
        def worker():
            try:
                import pylsl
                if not demo.ready.wait(6) or demo.error:raise RuntimeError(demo.error or 'Demo timeout')
                streams=pylsl.resolve_byprop('source_id',demo.source_id,timeout=5)
                if not streams:raise RuntimeError('Demo LSL stream not found')
                self.events.put(('demo_ready',(demo,streams[0])))
            except Exception as exc:self.events.put(('demo_error',(demo,str(exc))))
        threading.Thread(target=worker,daemon=True).start()

    def handle_events(self):
        while True:
            try:kind,payload=self.events.get_nowait()
            except queue.Empty:return
            if kind in ('streams','search_error'):
                self.scanning=False;self.scan_button.configure(state='normal')
                if kind=='search_error':
                    if "No module named 'pylsl'" in payload:
                        self.auto_connect.set(False)
                        self.status.set('pylsl is missing in this Python environment. Close and use Start_Electrode_QA.cmd. This is not a missing ActiView stream.')
                    else:self.status.set('Search failed: '+payload)
                    continue
                selected=self.stream_box.current()
                previous=stream_key(self.streams[selected]) if 0<=selected<len(self.streams) else None
                self.streams=payload;self.stream_box.configure(values=[f'{s.name()} | {s.channel_count()} ch | {s.nominal_srate():g} Hz | {s.hostname()}' for s in payload]);self.stream_box.set('')
                if len(payload)==1:self.stream_box.current(0)
                elif previous:
                    for i,s in enumerate(payload):
                        if stream_key(s)==previous:self.stream_box.current(i);break
                self.status.set(f'{len(payload)} streams found.' if payload else 'No stream. Check ActiView acquisition / LSL setup, or try demo.')
                if self.auto_connect.get() and self.receiver is None and not self.demo:
                    chosen=choose_stream(payload,self.remembered_source)
                    if chosen is not None:
                        self.stream_box.current(payload.index(chosen));self.connect_info(chosen)
                    elif payload:
                        self.status.set('Waiting for the remembered source, or multiple candidates: select a source and Connect. Use Choose another source to reset.')
            elif kind=='connected' and payload is self.receiver:
                self.meta=payload.meta;m=self.meta
                self.channels=[dict(index=i,name=n or f'LSL_COLUMN_{i+1}',original_label=n,unit=m['units'][i],use=False) for i,n in enumerate(m['labels'])]
                self.update_rows();self.source.set(f"{m['name']} | {m['hostname']} | {m['channel_count']} channels | {m['nominal_srate']:g} Hz | {m['source_id']}")
                self.banner.configure(text='SYNTHETIC DEMO · NOT HARDWARE' if m['demo'] else 'Connected · verify mapping, units and input',bg='#FFF0D8' if m['demo'] else '#E0E8F0')
                saved=self.resume_setup;self.resume_setup=None
                if saved and saved['signature']==metadata_signature(m):
                    self.channels=saved['channels'];self.unit.set(saved['unit'])
                    self.mapping.set(saved['mapping']);self.update_rows();self.start_monitoring()
                elif saved:
                    self.status.set('Source metadata changed. Verify channel mapping and units again before monitoring.')
                if m['demo'] and self.demo:
                    for c in self.channels:c['use']=True
                    self.update_rows()
                    for key,value in [('frequency','5'),('amplitude','10'),('window','5'),('step','1')]:self.vars[key].set(value)
                    self.mapping.set(True);self.start_monitoring()
            elif kind=='error' and payload[0] is self.receiver:
                self.prepare_reconnect();self.status.set('Stream error: '+payload[1]);self.banner.configure(text='Stream error · no current assessment',bg='#FBE4DF')
            elif kind=='ended' and payload is self.receiver:self.prepare_reconnect()
            elif kind=='demo_ready' and payload[0] is self.demo:self.connect_info(payload[1])
            elif kind=='demo_error' and payload[0] is self.demo:self.status.set('Demo failed: '+payload[1])
            elif kind in ('analysis','analysis_error'):
                token,data=payload
                if self.job==token:self.job=None
                if token!=(self.receiver,self.revision) or not self.monitoring:continue
                names=[c['name'] for c in self.selected_channels()]
                if kind=='analysis_error':self.publish(unavailable(names,'Analysis failed: '+data));self.status.set('Analysis failed: '+data);continue
                latest=self.receiver.buffer.last_timestamp
                if data['end_s'] is not None and latest is not None and latest-data['end_s']>max(2.,2*self.config.hop_s):
                    self.publish(unavailable(names,'Analysis behind stream: reduce selected channels / rate'));self.status.set(f"Old result discarded; calculation took {data['elapsed_s']:.2f} s.");continue
                self.last_result=self.confirmation.apply(data);self.publish(data['electrodes'])
                self.status.set(f"Analysis {data['elapsed_s']:.2f} s | Window {self.config.window_s:g} s | Latest window only; no file tail crop")

    def tick(self):
        if self.closed:return
        try:self.handle_events();self.discover_if_needed();self.update_live()
        except Exception as exc:self.stop_monitoring();self.status.set('Live error: '+str(exc))
        finally:
            if not self.closed:self.timer=self.after(100,self.tick)

    def update_live(self):
        r=self.receiver
        if not r or not r.buffer or not self.meta:return
        channels=self.selected_channels();names=[c['name'] for c in channels]
        window=self.config.window_s if self.config else 5.
        x,t,stats=r.buffer.snapshot([c['index'] for c in channels],seconds=window)
        problem=None
        if stats['silence_s'] is None or stats['silence_s']>2 or r.failure:problem='No fresh samples; current assessments cleared'
        if len(t) and r.clock_offset is not None:
            import pylsl
            age=pylsl.local_clock()-(t[-1]+r.clock_offset)
            if age>2:problem=f'Source timestamps are {age:.1f} s old; waiting for current samples'
        prefix='SYNTHETIC DEMO · ' if self.meta['demo'] else 'LIVE LSL · '
        if problem:
            self.banner.configure(text=prefix+problem,bg='#FBE4DF');self.last_result=None;self.confirmation.reset()
            self.publish(unavailable(names,problem));self.draw_wave(x,t,channels);return
        if self.monitoring:
            problem=frame_problem(t,self.meta['nominal_srate'],window)
            if problem:self.last_result=None;self.confirmation.reset();self.publish(unavailable(names,problem))
            self.banner.configure(text=prefix+(problem or f'Monitoring {len(channels)} channels · {stats["total"]:,} samples/channel'),bg='#FFF0D8' if self.meta['demo'] else '#DDF1E9')
            if self.last_result and t[-1]-self.last_result['end_s']>max(2.,2*self.config.hop_s):self.publish(unavailable(names,'Previous analysis is stale; waiting for a current result'))
            if not problem and self.job is None and time.monotonic()>=self.next_analysis:
                token=(r,self.revision);self.job=token;self.next_analysis=time.monotonic()+self.config.hop_s
                scales=self.scales(channels);cfg=copy.deepcopy(self.config);rate=self.meta['nominal_srate']
                def worker():
                    try:self.events.put(('analysis',(token,analyze_live_window(x,t,names,scales,rate,cfg))))
                    except Exception as exc:self.events.put(('analysis_error',(token,str(exc))))
                threading.Thread(target=worker,daemon=True).start()
        self.draw_wave(x,t,channels)

    def publish(self,electrodes):
        self.current=electrodes
        state=tuple((e.name,e.metric('live').color,e.metric('live').message,e.metric('live').values.get('persistent_alert')) for e in electrodes)
        if state!=self.last_display_state:
            self.grid.show(electrodes,'live');self.torso.show([e for e in electrodes if e.metric('live').color!='gray'],'live');self.last_display_state=state
        counts={c:sum(e.metric('live').color==c for e in electrodes) for c in ('green','yellow','red','gray')}
        red=[e.name for e in electrodes if e.metric('live').color=='red']
        self.counts.set(f"Green {counts['green']} | Review {counts['yellow']} | Check {counts['red']} | Unassessed {counts['gray']}"+(' | Check: '+', '.join(red[:12]) if red else ''))
        for e in electrodes:
            m=e.metric('live')
            if self.last_colors.get(e.name)!=m.color:
                self.changes.append(dict(local_time=time.strftime('%Y-%m-%d %H:%M:%S'),channel=e.name,color=m.color,reason=m.message));self.changes=self.changes[-500:];self.last_colors[e.name]=m.color
        if electrodes and self.focused not in [e.name for e in electrodes]:self.focused=electrodes[0].name
        alerts=self.alerts()
        if alerts:
            target=alerts[0]
            if (self.alert_target is None or self.alert_target[0] not in [e.name for e in alerts]
                    or (target.metric('live').color=='red' and self.alert_target[1]!='red')):
                self.alert_target=(target.name,target.metric('live').color)
                self.show_detail(target)
                if target.name not in self.torso.positions:self.notebook.select(0)
            self.pause_rotation('Paused: '+', '.join(e.name for e in alerts[:6])+' · inspect reasons below')
        elif self.alert_target:
            self.alert_target=None
            self.rotation_status.set('Alert cleared / unavailable · review status, then resume rotation')
        item=next((e for e in electrodes if e.name==self.focused),None)
        if item:self.show_detail(item,focus=False)
        elif not electrodes:self.set_detail('No channels selected for live monitoring.')

    def set_detail(self,text):
        self.detail.configure(state='normal');self.detail.delete('1.0','end');self.detail.insert('1.0',text);self.detail.configure(state='disabled')

    def show_detail(self,item,focus=True):
        self.focused=item.name
        if focus:
            self.pause_rotation('Paused for inspection: '+item.name)
            self.torso.focus(item.name,turn=True)
        m=item.metric('live');persistent=' | Persistent alert (2+ windows)' if m.values.get('persistent_alert') else ''
        rows=[f'{item.name}: {m.color.upper()}{persistent}',m.message]
        for key in ('gain','shape','frequency','thd','snr','bsqi','psqi','ksqi','bassqi','integrity'):
            if key in item.extra:rows.append(f'{key}: {item.extra[key].message} | {item.extra[key].values}')
        self.set_detail('\n'.join(rows))

    def draw_wave(self,x,t,channels):
        c=self.wave;c.delete('all');w,h=max(200,c.winfo_width()),max(70,c.winfo_height())
        if not len(t) or self.focused not in [ch['name'] for ch in channels]:
            c.create_text(12,20,anchor='w',text='Select an electrode to see its recent waveform.',fill='#657588');return
        idx=next(i for i,ch in enumerate(channels) if ch['name']==self.focused)
        y=x[:,idx].copy();scale=self.scales(channels)[idx]
        if not np.isfinite(y).all():return
        if scale is not None:y*=scale
        y-=y.mean();lo,hi=float(y.min()),float(y.max());span=max(hi-lo,1e-6)
        stride=max(1,len(y)//max(1,w//2));points=[]
        for start in range(0,len(y),stride):
            part=y[start:start+stride]
            for k in sorted(set((start+int(part.argmin()),start+int(part.argmax())))):
                points.extend((12+(w-24)*(t[k]-t[0])/max(t[-1]-t[0],1e-9),h-12-(y[k]-lo)/span*(h-40)))
        if len(points)>3:c.create_line(*points,fill='#1376C7',width=1)
        c.create_text(12,10,anchor='w',text=f'{self.focused} | DC removed for display | raw Vpp {hi-lo:.5g} '+('uV' if scale is not None else 'native units')+f' | {t[-1]-t[0]:.1f} s',fill='#243243')

    def show_metadata(self):
        if not self.meta:return
        win=tk.Toplevel(self);win.title('LSL source metadata');win.geometry('850x620')
        text=tk.Text(win,wrap='word');text.pack(fill='both',expand=True);text.insert('1.0',json.dumps(self.meta,indent=2,ensure_ascii=False));text.configure(state='disabled')

    def save(self,folder=None):
        if not self.receiver or not self.receiver.buffer or not self.meta:
            messagebox.showinfo('No data','Connect and receive samples first.',parent=self);return
        if folder is None:folder=filedialog.askdirectory(title='Save live window and report',parent=self)
        if not folder:return
        try:
            channels=self.selected_channels();x,t,stats=self.receiver.buffer.snapshot([c['index'] for c in channels],seconds=self.config.window_s if self.config else 5)
            if not len(t):raise ValueError('No samples to save')
            scales=self.scales(channels);result=self.last_result
            fresh=bool(self.monitoring and result and result['valid'] and stats['silence_s'] is not None and stats['silence_s']<2 and result['end_s'] is not None and t[-1]-result['end_s']<=max(2.,2*self.config.hop_s))
            report=dict(source=self.meta,selected_channels=channels,scales_to_uV=scales,unit_selection=self.unit.get(),config=asdict(self.config) if self.config else None,
                timestamps='original LSL source clock seconds',source_to_local_clock_offset_s=self.receiver.clock_offset,stats=stats,assessment_current=fresh,
                assessment_window_start_s=result['start_s'] if fresh else None,assessment_window_end_s=result['end_s'] if fresh else None,
                capture_start_s=float(t[0]),capture_end_s=float(t[-1]),electrodes=[asdict(e) for e in self.current] if fresh else [asdict(e) for e in unavailable([c['name'] for c in channels],'No current assessment at export')],recent_status_changes=self.changes)
            folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
            name=('DEMO_' if self.meta['demo'] else 'LIVE_')+time.strftime('%Y%m%d_%H%M%S')+f'_{time.time_ns()%1000000:06d}'
            data=dict(samples_native=x,timestamps_lsl=t,metadata_json=np.array(json.dumps(report,ensure_ascii=False)))
            if all(s is not None for s in scales):data['data_uv']=(x*np.array(scales)).T
            np.savez_compressed(folder/(name+'.npz'),**data);(folder/(name+'.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
            self.status.set('Saved: '+str(folder/(name+'.npz')));return folder/(name+'.npz')
        except Exception as exc:messagebox.showerror('Save failed',str(exc),parent=self)

    def on_destroy(self,event):
        if event.widget is self:self.cleanup()

    def cleanup(self):
        if self.closed:return
        self.closed=True
        if self.receiver:self.receiver.stop()
        if self.demo:self.demo.stop()
        try:self.after_cancel(self.timer)
        except (tk.TclError,AttributeError):pass
        try:self.after_cancel(self.rotation_timer)
        except (tk.TclError,AttributeError):pass

    def close(self):self.cleanup();self.destroy()
