"""Expanded torso view linked to the main GUI's metric and window selection."""
from dataclasses import asdict
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from config import COLORS
from views.torso_geometry import TorsoLayout
from views.torso_view import TorsoView
from views.timeline_view import TimelineView


class TorsoWindow(tk.Toplevel):
    def __init__(self, parent, metric_var, metric_labels, on_metric, on_select, on_window,
                 layout, on_layout, on_close):
        super().__init__(parent)
        self.title('Electrode QA | 3D torso')
        self.geometry(f'1180x{min(950,self.winfo_screenheight()-90)}')
        self.minsize(950,720)
        self.on_select,self.on_layout,self.on_close=on_select,on_layout,on_close
        self.electrodes={};self.mode='current';self.context='Not analyzed';self.layout=layout
        self.protocol('WM_DELETE_WINDOW',self.close)
        header=ttk.Frame(self,padding=(14,10));header.pack(fill='x')
        ttk.Label(header,text='3D electrode layout',font=('Segoe UI',18,'bold')).pack(side='left')
        ttk.Label(header,text='Metric').pack(side='left',padx=(25,7))
        self.metric_combo=ttk.Combobox(header,textvariable=metric_var,values=metric_labels,state='readonly',width=28)
        self.metric_combo.pack(side='left');self.metric_combo.bind('<<ComboboxSelected>>',lambda _:on_metric())
        self.scope=tk.StringVar(value='Not analyzed')
        scope_label=ttk.Label(self,textvariable=self.scope,padding=(14,0),wraplength=1080)
        scope_label.pack(fill='x')
        scope_label.bind('<Configure>',lambda event:scope_label.configure(wraplength=max(200,event.width-28)))
        # Reserve playback controls before the expandable 3D surface.
        footer=ttk.Frame(self,padding=(14,7));footer.pack(side='bottom',fill='x')
        self.timeline=TimelineView(footer,on_window);self.timeline.pack(fill='x')
        ttk.Label(footer,text='Timeline: worst selected channel. Gray electrode = not selected / not analyzed.',
                  foreground='#657588').pack(anchor='w',pady=(4,0))
        body=ttk.Frame(self,padding=12);body.pack(fill='both',expand=True)
        right=ttk.Frame(body,width=310);right.pack(side='right',fill='y',padx=(12,0));right.pack_propagate(False)
        left=ttk.Frame(body);left.pack(fill='both',expand=True)
        actions=ttk.Frame(left);actions.pack(fill='x')
        self.view=TorsoView(left,self._pick,layout)
        for face in ('Front','Back'):
            ttk.Button(actions,text=face,command=lambda f=face:self.view.face(f)).pack(side='left',padx=(0,5))
        ttk.Button(actions,text='Angle',command=self.angle).pack(side='left',padx=(0,5))
        ttk.Button(actions,text='Reset',command=lambda:self.view.face('Front')).pack(side='left')
        self.view.pack(fill='both',expand=True)
        layout_row=ttk.Frame(left);layout_row.pack(fill='x',pady=(4,0))
        self.side=tk.StringVar(value="A/C: person's right" if layout.front_b_on_right else "A/C: person's left")
        self.order=tk.StringVar(value='Outer low at bottom' if not layout.top_to_bottom else 'Outer low at top')
        for variable,values,width in ((self.side,("A/C: person's left","A/C: person's right"),23),
                                      (self.order,('Outer low at bottom','Outer low at top'),23)):
            combo=ttk.Combobox(layout_row,textvariable=variable,values=values,state='readonly',width=width)
            combo.pack(side='left',padx=(0,6));combo.bind('<<ComboboxSelected>>',self.change_layout)
        layout_note=ttk.Label(left,text='R/L = person\'s sides. Middle column reversed (serpentine). C behind A; D behind B. DRL * = unscored orientation marker. Schematic; verify wiring.',
                              foreground='#657588',wraplength=700)
        layout_note.pack(anchor='w',pady=(3,0))
        left.bind('<Configure>',lambda event:layout_note.configure(wraplength=max(200,event.width)))
        self.bank_summary=tk.StringVar()
        ttk.Label(right,textvariable=self.bank_summary,wraplength=305,font=('Segoe UI',10,'bold')).pack(fill='x')
        self.mapping_notice=tk.StringVar()
        ttk.Label(right,textvariable=self.mapping_notice,wraplength=305,foreground='#86640B').pack(fill='x',pady=6)
        ttk.Label(right,text='Channels to review',font=('Segoe UI',11,'bold')).pack(anchor='w')
        alert_box=ttk.Frame(right);alert_box.pack(fill='x',pady=(5,7))
        self.alerts=ttk.Treeview(alert_box,columns=('channel','face','state'),show='headings',height=7)
        for key,title,width in (('channel','Electrode',83),('face','Surface',80),('state','Status',125)):
            self.alerts.heading(key,text=title);self.alerts.column(key,width=width,stretch=True)
        alert_scroll=ttk.Scrollbar(alert_box,command=self.alerts.yview)
        self.alerts.configure(yscrollcommand=alert_scroll.set)
        alert_scroll.pack(side='right',fill='y');self.alerts.pack(fill='x')
        self.alerts.bind('<<TreeviewSelect>>',self.pick_alert)
        for color in COLORS: self.alerts.tag_configure(color,foreground=COLORS[color])
        ttk.Label(right,text='Selected electrode',font=('Segoe UI',11,'bold')).pack(anchor='w')
        detail_box=ttk.Frame(right);detail_box.pack(fill='both',expand=True,pady=5)
        self.detail=tk.Text(detail_box,wrap='word',width=30,height=8,relief='flat',padx=8,pady=8,font=('Segoe UI',10))
        scroll=ttk.Scrollbar(detail_box,command=self.detail.yview)
        self.detail.configure(yscrollcommand=scroll.set,state='disabled')
        scroll.pack(side='right',fill='y');self.detail.pack(fill='both',expand=True)
        self.clear()

    def angle(self):
        self.view.yaw=35.;self.view.pitch=12.;self.view.zoom=1.;self.view.draw()

    def change_layout(self,_=None):
        self.layout=TorsoLayout('C behind A',self.order.get()=='Outer low at top',self.side.get()=="A/C: person's right")
        self.view.set_layout(self.layout);self.on_layout(self.layout)

    def set_layout(self,layout):
        self.layout=layout;self.view.set_layout(layout)
        self.side.set("A/C: person's right" if layout.front_b_on_right else "A/C: person's left")
        self.order.set('Outer low at top' if layout.top_to_bottom else 'Outer low at bottom')

    def show(self,electrodes,mode,context,metric_labels,key,items,current,notice):
        self.electrodes={e.name:e for e in electrodes};self.mode=mode;self.context=context
        self.scope.set(context);self.metric_combo.configure(values=metric_labels)
        self.view.show(electrodes,mode)
        rows=[]
        for banks,label in (('AB','Front A/B'),('CD','Back C/D')):
            selected=[e for e in electrodes if e.name in self.view.positions and e.name[0] in banks]
            counts={c:sum(e.metric(mode).color==c for e in selected) for c in COLORS}
            rows.append(f"{label}: {len(selected)} selected\nGreen {counts['green']} | Yellow {counts['yellow']} | Red {counts['red']}")
        self.bank_summary.set('\n\n'.join(rows))
        missing=[e.name for e in electrodes if e.name not in self.view.positions]
        self.mapping_notice.set(('Unmapped: '+', '.join(missing[:8])+(' ...' if len(missing)>8 else '')+
                                 '. Use the grid for these channels.') if missing else 'A1-D32 mapped to the sketch. Auxiliary/reference hardware positions are not scored here.')
        self.alerts.delete(*self.alerts.get_children())
        rank={'red':0,'yellow':1,'green':2}
        for e in sorted(electrodes,key=lambda e:rank[e.metric(mode).color]):
            color=e.metric(mode).color
            if color!='green':
                self.alerts.insert('', 'end',iid=e.name,values=(e.name,self.view.positions.get(e.name,{}).get('face','Unmapped'),
                                   'Check required' if color=='red' else 'Review'),tags=(color,))
        self.timeline.show(key,items,current,notice)

    def clear(self):
        self.timeline.clear();self.electrodes={};self.view.show([],self.mode)
        self.scope.set('Not analyzed — placement preview only')
        self.bank_summary.set('Front: A / B\nBack: C / D')
        self.mapping_notice.set('Gray dots have no current analysis result.')
        self.alerts.delete(*self.alerts.get_children());self.set_detail('Run analysis to display electrode states.')

    def _pick(self,electrode):
        self.on_select(electrode)

    def pick_alert(self,_=None):
        selected=self.alerts.selection()
        if selected and selected[0] in self.electrodes:
            self.view.focus(selected[0],turn=True);self.on_select(self.electrodes[selected[0]])

    def set_detail(self,text,name=None):
        self.detail.configure(state='normal');self.detail.delete('1.0','end');self.detail.insert('1.0',text)
        self.detail.configure(state='disabled')
        if name: self.view.focus(name)

    def save(self,folder):
        folder=Path(folder)
        title=self.context+'\n'+self.mode
        self.view.save(folder/'torso_view.png',title)
        metadata=dict(layout=asdict(self.layout),numbering='Serpentine: middle (11-21) column reversed relative to outer columns',
                      coordinate_system='x = front-screen right, y = back, z = up',
                      schematic=True,scope=self.context,metric=self.mode,camera=dict(yaw=self.view.yaw,pitch=self.view.pitch,zoom=self.view.zoom),
                      positions=self.view.positions)
        (folder/'torso_layout.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')

    def close(self):
        self.timeline.pause();self.on_close();self.destroy()
