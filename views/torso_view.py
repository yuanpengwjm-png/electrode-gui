"""Lightweight interactive 3-D projection; metrics remain owned by the analyzers."""
import math
import tkinter as tk
from tkinter import ttk
import numpy as np
from config import COLORS, COLOR_LABELS
from views.torso_geometry import TorsoLayout, MESH, project, visible


class TorsoView(ttk.Frame):
    def __init__(self, parent, on_select, layout=None):
        super().__init__(parent)
        self.on_select = on_select
        self.layout = layout or TorsoLayout()
        self.positions = self.layout.positions()
        self.electrodes = {}; self.mode = 'current'; self.selected = None
        self.yaw, self.pitch, self.zoom = 0., 6., 1.
        self.drag = None; self.moved = False; self.hits = []
        self.canvas = tk.Canvas(self, bg='#F4F7FA', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', lambda _: self.draw())
        self.canvas.bind('<ButtonPress-1>', self.press)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<ButtonRelease-1>', self.release)
        self.canvas.bind('<Motion>', self.hover)
        self.canvas.bind('<MouseWheel>', self.wheel)

    def show(self, electrodes, mode):
        self.electrodes = {e.name:e for e in electrodes}; self.mode = mode
        self.draw()

    def set_layout(self, layout):
        self.layout = layout; self.positions = layout.positions(); self.draw()

    def face(self, name):
        self.yaw = {'Front':0., 'Back':180., 'Left side':90., 'Right side':-90.}[name]
        self.pitch = 6.; self.zoom = 1.; self.draw()

    def focus(self, name, turn=False):
        self.selected = name
        if turn and name in self.positions:
            self.face(self.positions[name]['face'])
        else:
            self.draw()

    def scene(self, width, height):
        scale = min(width/3.35, max(80,height-76)/2.9)*self.zoom
        centre = (width/2, height/2+12)
        def xy(point):
            u,v,d = project((point[0],point[1],point[2]-1.34),self.yaw,self.pitch)
            return (centre[0]+u*scale, centre[1]-v*scale, d)
        polygons = []
        for face in MESH:
            vertices = [xy(p) for p in face]
            normal = np.cross(np.subtract(face[1],face[0]),np.subtract(face[2],face[0]))
            norm = np.linalg.norm(normal)
            normal = normal/norm if norm else normal
            brightness = .68+.20*abs(project(normal,self.yaw,self.pitch)[2])+.09*max(0,float(normal[2]))
            shade = tuple(min(255,round(c*brightness)) for c in (224,237,243))
            polygons.append((sum(v[2] for v in vertices)/len(vertices),
                             [(v[0],v[1]) for v in vertices], '#%02x%02x%02x'%shade))
        markers = []
        for name, pos in self.positions.items():
            if not visible(pos['normal'],self.yaw,self.pitch):
                continue
            px,py,depth = xy(pos['point'])
            electrode = self.electrodes.get(name)
            color = COLORS[electrode.metric(self.mode).color] if electrode else '#DFE6EC'
            markers.append(dict(name=name,x=px,y=py,depth=depth,color=color,
                                active=electrode is not None,radius=max(3,min(20,scale*.070))))
        return sorted(polygons), sorted(markers,key=lambda m:m['depth'])

    def guides(self,width,height):
        scale=min(width/3.35,max(80,height-76)/2.9)*self.zoom
        points=[('R (person)',(-1.23,0,2.32)),('L (person)',(1.23,0,2.32))]
        if visible((0,-1,0),self.yaw,self.pitch):
            points.append(('DRL *',(-1.03,-.15,.10)))
        result=[]
        for label,point in points:
            u,v,_=project((point[0],point[1],point[2]-1.34),self.yaw,self.pitch)
            result.append((label,width/2+u*scale,height/2+12-v*scale))
        return result

    def draw(self):
        c = self.canvas; c.delete('all'); self.hits=[]
        width,height = max(200,c.winfo_width()),max(180,c.winfo_height())
        polygons,markers = self.scene(width,height)
        for _,vertices,color in polygons:
            c.create_polygon(*[v for p in vertices for v in p],fill=color,outline=color)
        for m in markers:
            x,y,r = m['x'],m['y'],m['radius']
            selected = m['name']==self.selected
            c.create_oval(x-r,y-r,x+r,y+r,fill=m['color'],outline='#132F45' if selected else '#FFFFFF',
                          width=3 if selected else 1,tags=('torso_electrode',m['name']))
            if m['active']:
                self.hits.append(m)
                if height>=430 or selected:
                    ink = '#243243' if m['color']==COLORS['yellow'] else 'white'
                    c.create_text(x,y,text=m['name'],fill=ink,font=('Segoe UI',max(7,min(10,round(r*.65))),'bold'),tags=('electrode_label',))
        for label,x,y in self.guides(width,height):
            c.create_text(x,y,text=label,fill='#405766',font=('Segoe UI',9,'bold'))
        frontness = math.cos(math.radians(self.yaw))
        if abs(frontness) < .5:
            direction = "Person's left side" if math.sin(math.radians(self.yaw)) > 0 else "Person's right side"
        else:
            direction = 'Front / A + B' if frontness>=0 else 'Back / C + D'
        c.create_text(width/2,18,text=direction,fill='#19384D',font=('Segoe UI',13,'bold'))
        c.create_text(width/2,height-13,text='Drag to rotate  |  Wheel to zoom  |  Click a colored electrode',fill='#526A7A',font=('Segoe UI',9))
        if not self.electrodes:
            c.create_text(width/2,42,text='Not analyzed — gray points are placement only',fill='#657588',font=('Segoe UI',10))

    def hit(self,x,y):
        return next((m for m in reversed(self.hits) if (x-m['x'])**2+(y-m['y'])**2<=(m['radius']+4)**2),None)

    def press(self,event):
        self.drag=(event.x,event.y,self.yaw,self.pitch); self.moved=False

    def motion(self,event):
        if self.drag:
            x,y,yaw,pitch=self.drag
            if abs(event.x-x)+abs(event.y-y)>4:
                self.moved=True
                self.yaw=yaw+(event.x-x)*.5
                self.pitch=max(-35,min(35,pitch+(event.y-y)*.3))
                self.draw()

    def release(self,event):
        if self.drag and not self.moved:
            item=self.hit(event.x,event.y)
            if item:
                self.focus(item['name']); self.on_select(self.electrodes[item['name']])
        self.drag=None

    def hover(self,event):
        self.canvas.delete('hover_label')
        item=self.hit(event.x,event.y)
        self.canvas.configure(cursor='hand2' if item else 'fleur')
        if item and not self.drag:
            metric=self.electrodes[item['name']].metric(self.mode)
            self.canvas.create_text(10,64,anchor='nw',text=f"{item['name']} | {COLOR_LABELS[metric.color]}",
                                    fill='#243243',font=('Segoe UI',10,'bold'),tags='hover_label')

    def wheel(self,event):
        self.zoom=max(.65,min(2.5,self.zoom*(1.10 if event.delta>0 else 1/1.10)))
        self.draw()

    def save(self,path,title):
        """Render the same camera and electrode colors to a standalone PNG."""
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.patches import Polygon,Circle
        fig=Figure(figsize=(8,10),facecolor='#F4F7FA'); FigureCanvasAgg(fig)
        ax=fig.add_axes((0,.035,1,.89));ax.set(xlim=(0,800),ylim=(1000,0));ax.set_aspect('equal');ax.axis('off')
        polygons,markers=self.scene(800,1000)
        for _,vertices,color in polygons: ax.add_patch(Polygon(vertices,facecolor=color,edgecolor=color))
        for m in markers:
            ax.add_patch(Circle((m['x'],m['y']),m['radius'],facecolor=m['color'],edgecolor='white'))
            if m['active']:
                ax.text(m['x'],m['y'],m['name'],ha='center',va='center',fontsize=8,weight='bold',
                        color='#243243' if m['color']==COLORS['yellow'] else 'white')
        for label,x,y in self.guides(800,1000):
            ax.text(x,y,label,ha='center',va='center',fontsize=9,color='#405766',weight='bold')
        fig.suptitle(title,fontsize=11)
        fig.text(.5,.015,'Schematic torso; verify wiring. Gray = not analyzed / not selected. DRL * = orientation only.',ha='center',fontsize=8)
        fig.savefig(path,dpi=150)
