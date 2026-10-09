# views/torso_view.py：躯干绘制与交互

画示意躯干，按已有指标上色，处理旋转、缩放、选点、悬停和图片导出；不计算电极质量。

源码：[views/torso_view.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py>)。本说明对应 165 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [11–26](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:11>) | 初始化相机、布局、鼠标状态和画布事件。 |
| `show` | [28–30](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:28>) | 按通道名保存已有结果并重画。 |
| `set_layout` | [32–33](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:32>) | 替换示意坐标并重画。 |
| `face` | [35–37](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:35>) | 设置正面/背面/侧面的预设角度。 |
| `focus` | [39–44](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:39>) | 选中电极，必要时转向它所在的身体表面。 |
| `scene` | [46–71](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:46>) | 将模型和电极投影到画布；计算示意明暗并按深度排序。 |
| `xy` | [49–51](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:49>) | 把相机坐标转换为像素坐标，屏幕 y 轴向下因此要反号。 |
| `guides` | [73–82](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:73>) | 投影人体左右及 DRL 方向标记；这些标记不参与质量评分。 |
| `draw` | [84–110](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:84>) | 按远近顺序画多边形和可见电极，再画标签与提示。 |
| `hit` | [112–113](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:112>) | 从前到后找鼠标是否落在某个可点击电极圆内。 |
| `press` | [115–116](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:115>) | 记住鼠标按下时的位置与相机角度。 |
| `motion` | [118–125](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:118>) | 拖动超过阈值时改变 yaw/pitch 并刷新；限制俯仰角。 |
| `release` | [127–132](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:127>) | 若没有形成拖动则视为点击电极，通知主窗口显示详情。 |
| `hover` | [134–141](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:134>) | 悬停时更新鼠标形状及该电极颜色说明。 |
| `wheel` | [143–145](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:143>) | 按滚轮方向调整缩放并限制在 0.65–2.5 倍。 |
| `save` | [147–165](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py:147>) | 用相同投影生成静态躯干 PNG。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Lightweight interactive 3-D projection; metrics remain owned by the analyzers.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 3 | ` import tkinter as tk ` | 导入模块 tkinter（别名 tk）。桌面窗口、控件、文件选择框和消息框 |
| 4 | ` from tkinter import ttk ` | 从 tkinter 导入 ttk。桌面窗口、控件、文件选择框和消息框 |
| 5 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 6 | ` from config import COLORS, COLOR_LABELS ` | 从 config 导入 COLORS、COLOR_LABELS。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 7 | ` from views.torso_geometry import TorsoLayout, MESH, project, visible ` | 从 views.torso_geometry 导入 TorsoLayout、MESH、project、visible。生成示意躯干网格和 A1–D32 位置，再做三维到二维的投影；这些坐标不是 CT 重建或患者实测坐标。 |
| 8 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 9 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 10 | ` class TorsoView(ttk.Frame): ` | 定义 TorsoView 类，继承 ttk.Frame；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 11 | `     def __init__(self, parent, on_select, layout=None): ` | 定义 __init__(self, parent, on_select, layout=None)。初始化相机、布局、鼠标状态和画布事件。 定义到这里时不执行函数体。 |
| 12 | `         super().__init__(parent) ` | 调用 super().__init__；参数：parent。 |
| 13 | `         self.on_select = on_select ` | 把结果保存到 self.on_select：on_select。 |
| 14 | `         self.layout = layout or TorsoLayout() ` | 把结果保存到 self.layout：layout or TorsoLayout()。 |
| 15 | `         self.positions = self.layout.positions() ` | 把结果保存到 self.positions：调用 self.layout.positions。 |
| 16 | `         self.electrodes = {}; self.mode = 'current'; self.selected = None ` | 把结果保存到 self.electrodes：组装字典，键用于给数值/设置命名：{}。 把结果保存到 self.mode：'current'。 把结果保存到 self.selected：None（未知/未设置）。 |
| 17 | `         self.yaw, self.pitch, self.zoom = 0., 6., 1. ` | 把结果保存到 (self.yaw, self.pitch, self.zoom)：组装元组：(0.0, 6.0, 1.0)。 |
| 18 | `         self.drag = None; self.moved = False; self.hits = [] ` | 把结果保存到 self.drag：None（未知/未设置）。 把结果保存到 self.moved：False（否）。 把结果保存到 self.hits：组装列表：[]。 |
| 19 | `         self.canvas = tk.Canvas(self, bg='#F4F7FA', highlightthickness=0) ` | 把结果保存到 self.canvas：创建绘图画布；参数：self, bg='#F4F7FA', highlightthickness=0。 |
| 20 | `         self.canvas.pack(fill='both', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 21 | `         self.canvas.bind('<Configure>', lambda _: self.draw()) ` | 绑定界面事件，事件发生时才执行回调；参数：'<Configure>', lambda _: self.draw()。 |
| 22 | `         self.canvas.bind('<ButtonPress-1>', self.press) ` | 绑定界面事件，事件发生时才执行回调；参数：'<ButtonPress-1>', self.press。 |
| 23 | `         self.canvas.bind('<B1-Motion>', self.motion) ` | 绑定界面事件，事件发生时才执行回调；参数：'<B1-Motion>', self.motion。 |
| 24 | `         self.canvas.bind('<ButtonRelease-1>', self.release) ` | 绑定界面事件，事件发生时才执行回调；参数：'<ButtonRelease-1>', self.release。 |
| 25 | `         self.canvas.bind('<Motion>', self.hover) ` | 绑定界面事件，事件发生时才执行回调；参数：'<Motion>', self.hover。 |
| 26 | `         self.canvas.bind('<MouseWheel>', self.wheel) ` | 绑定界面事件，事件发生时才执行回调；参数：'<MouseWheel>', self.wheel。 |
| 27 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 28 | `     def show(self, electrodes, mode): ` | 定义 show(self, electrodes, mode)。按通道名保存已有结果并重画。 定义到这里时不执行函数体。 |
| 29 | `         self.electrodes = {e.name:e for e in electrodes}; self.mode = mode ` | 把结果保存到 self.electrodes：从 electrodes 逐个取 e，为每项生成 e.name: e。 把结果保存到 self.mode：mode。 |
| 30 | `         self.draw() ` | 按远近顺序画多边形和可见电极，再画标签与提示。。 |
| 31 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 32 | `     def set_layout(self, layout): ` | 定义 set_layout(self, layout)。替换示意坐标并重画。 定义到这里时不执行函数体。 |
| 33 | `         self.layout = layout; self.positions = layout.positions(); self.draw() ` | 把结果保存到 self.layout：layout。 把结果保存到 self.positions：调用 layout.positions。 按远近顺序画多边形和可见电极，再画标签与提示。。 |
| 34 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 35 | `     def face(self, name): ` | 定义 face(self, name)。设置正面/背面/侧面的预设角度。 定义到这里时不执行函数体。 |
| 36 | `         self.yaw = {'Front':0., 'Back':180., 'Left side':90., 'Right side':-90.}[name] ` | 把结果保存到 self.yaw：按索引/键 name 取 {'Front': 0.0, 'Back': 180.0, 'Left side': 90.0, 'Right side': -90.0} 的内容。 |
| 37 | `         self.pitch = 6.; self.zoom = 1.; self.draw() ` | 把结果保存到 self.pitch：6.0。 把结果保存到 self.zoom：1.0。 按远近顺序画多边形和可见电极，再画标签与提示。。 |
| 38 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 39 | `     def focus(self, name, turn=False): ` | 定义 focus(self, name, turn=False)。选中电极，必要时转向它所在的身体表面。 定义到这里时不执行函数体。 |
| 40 | `         self.selected = name ` | 把结果保存到 self.selected：name。 |
| 41 | `         if turn and name in self.positions: ` | 检查条件 turn and name in self.positions；为真时执行下面缩进的一组语句。 |
| 42 | `             self.face(self.positions[name]['face']) ` | 设置正面/背面/侧面的预设角度。；参数：self.positions[name]['face']。 |
| 43 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 44 | `             self.draw() ` | 按远近顺序画多边形和可见电极，再画标签与提示。。 |
| 45 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 46 | `     def scene(self, width, height): ` | 定义 scene(self, width, height)。将模型和电极投影到画布；计算示意明暗并按深度排序。 定义到这里时不执行函数体。 |
| 47 | `         scale = min(width/3.35, max(80,height-76)/2.9)*self.zoom ` | 把结果保存到 scale：min(width / 3.35, max(80, height - 76) / 2.9) 与 self.zoom 相乘。 |
| 48 | `         centre = (width/2, height/2+12) ` | 把结果保存到 centre：组装元组：(width / 2, height / 2 + 12)。 |
| 49 | `         def xy(point): ` | 定义 xy(point)。把相机坐标转换为像素坐标，屏幕 y 轴向下因此要反号。 定义到这里时不执行函数体。 |
| 50 | `             u,v,d = project((point[0],point[1],point[2]-1.34),self.yaw,self.pitch) ` | 把结果保存到 (u, v, d)：调用 project；参数：(point[0], point[1], point[2] - 1.34), self.yaw, self.pitch。 |
| 51 | `             return (centre[0]+u*scale, centre[1]-v*scale, d) ` | 结束当前函数并返回：组装元组：(centre[0] + u * scale, centre[1] - v * scale, d)。 |
| 52 | `         polygons = [] ` | 把结果保存到 polygons：组装列表：[]。 |
| 53 | `         for face in MESH: ` | 遍历 MESH，每次把一项赋给 face，执行下面缩进的循环体。 |
| 54 | `             vertices = [xy(p) for p in face] ` | 把结果保存到 vertices：从 face 逐个取 p，为每项生成 xy(p)。 |
| 55 | `             normal = np.cross(np.subtract(face[1],face[0]),np.subtract(face[2],face[0])) ` | 把结果保存到 normal：计算三维叉积得到表面法向量；参数：np.subtract(face[1], face[0]), np.subtract(face[2], face[0])。 |
| 56 | `             norm = np.linalg.norm(normal) ` | 把结果保存到 norm：计算向量长度；参数：normal。 |
| 57 | `             normal = normal/norm if norm else normal ` | 把结果保存到 normal：若 norm，用 normal / norm；否则用 normal。 |
| 58 | `             brightness = .68+.20*abs(project(normal,self.yaw,self.pitch)[2])+.09*max(0,float(normal[2])) ` | 把结果保存到 brightness：0.68 + 0.2 * abs(project(normal, self.yaw, self.pitch)[2]) 与 0.09 * max(0, float(normal[2])) 相加。 |
| 59 | `             shade = tuple(min(255,round(c*brightness)) for c in (224,237,243)) ` | 把结果保存到 shade：构造元组；参数：(min(255, round(c * brightness)) for c in (224, 237, 243))。 |
| 60 | `             polygons.append((sum(v[2] for v in vertices)/len(vertices), ` | 把一项加入列表末尾；参数：(sum((v[2] for v in vertices)) / len(vertices), [(v[0], v[1]) for v in vertices], '#%02x%02x%02x' % shade)。 |
| 61 | `                              [(v[0],v[1]) for v in vertices], '#%02x%02x%02x'%shade)) ` | 接续第 60 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：(sum((v[2] for v in vertices)) / len(vertices), [(v[0], v[1]) for v in vertices], '#%02x%02x%02x' % shade)。 |
| 62 | `         markers = [] ` | 把结果保存到 markers：组装列表：[]。 |
| 63 | `         for name, pos in self.positions.items(): ` | 遍历 self.positions.items()，每次把一项赋给 (name, pos)，执行下面缩进的循环体。 |
| 64 | `             if not visible(pos['normal'],self.yaw,self.pitch): ` | 检查条件 not visible(pos['normal'], self.yaw, self.pitch)；为真时执行下面缩进的一组语句。 |
| 65 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 66 | `             px,py,depth = xy(pos['point']) ` | 把结果保存到 (px, py, depth)：调用 xy；参数：pos['point']。 |
| 67 | `             electrode = self.electrodes.get(name) ` | 把结果保存到 electrode：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：name。 |
| 68 | `             color = COLORS[electrode.metric(self.mode).color] if electrode else '#DFE6EC' ` | 把结果保存到 color：若 electrode，用 COLORS[electrode.metric(self.mode).color]；否则用 '#DFE6EC'。 |
| 69 | `             markers.append(dict(name=name,x=px,y=py,depth=depth,color=color, ` | 把一项加入列表末尾；参数：dict(name=name, x=px, y=py, depth=depth, color=color, active=electrode is not None, radius=max(3, min(20, scale * 0.07)))。 |
| 70 | `                                 active=electrode is not None,radius=max(3,min(20,scale*.070)))) ` | 接续第 69 行的同一条语句，不是另起一段算法。 取最大值；参数：3, min(20, scale * 0.07)。 |
| 71 | `         return sorted(polygons), sorted(markers,key=lambda m:m['depth']) ` | 结束当前函数并返回：组装元组：(sorted(polygons), sorted(markers, key=lambda m: m['depth']))。 |
| 72 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 73 | `     def guides(self,width,height): ` | 定义 guides(self, width, height)。投影人体左右及 DRL 方向标记；这些标记不参与质量评分。 定义到这里时不执行函数体。 |
| 74 | `         scale=min(width/3.35,max(80,height-76)/2.9)*self.zoom ` | 把结果保存到 scale：min(width / 3.35, max(80, height - 76) / 2.9) 与 self.zoom 相乘。 |
| 75 | `         points=[('R (person)',(-1.23,0,2.32)),('L (person)',(1.23,0,2.32))] ` | 把结果保存到 points：组装列表：[('R (person)', (-1.23, 0, 2.32)), ('L (person)', (1.23, 0, 2.32))]。 |
| 76 | `         if visible((0,-1,0),self.yaw,self.pitch): ` | 检查条件 visible((0, -1, 0), self.yaw, self.pitch)；为真时执行下面缩进的一组语句。 |
| 77 | `             points.append(('DRL *',(-1.03,-.15,.10))) ` | 把一项加入列表末尾；参数：('DRL *', (-1.03, -0.15, 0.1))。 |
| 78 | `         result=[] ` | 把结果保存到 result：组装列表：[]。 |
| 79 | `         for label,point in points: ` | 遍历 points，每次把一项赋给 (label, point)，执行下面缩进的循环体。 |
| 80 | `             u,v,_=project((point[0],point[1],point[2]-1.34),self.yaw,self.pitch) ` | 把结果保存到 (u, v, _)：调用 project；参数：(point[0], point[1], point[2] - 1.34), self.yaw, self.pitch。 |
| 81 | `             result.append((label,width/2+u*scale,height/2+12-v*scale)) ` | 把一项加入列表末尾；参数：(label, width / 2 + u * scale, height / 2 + 12 - v * scale)。 |
| 82 | `         return result ` | 结束当前函数并返回：result。 |
| 83 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 84 | `     def draw(self): ` | 定义 draw(self)。按远近顺序画多边形和可见电极，再画标签与提示。 定义到这里时不执行函数体。 |
| 85 | `         c = self.canvas; c.delete('all'); self.hits=[] ` | 把结果保存到 c：读取 self 的 canvas 属性。 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：'all'。 把结果保存到 self.hits：组装列表：[]。 |
| 86 | `         width,height = max(200,c.winfo_width()),max(180,c.winfo_height()) ` | 把结果保存到 (width, height)：组装元组：(max(200, c.winfo_width()), max(180, c.winfo_height()))。 |
| 87 | `         polygons,markers = self.scene(width,height) ` | 把结果保存到 (polygons, markers)：将模型和电极投影到画布；计算示意明暗并按深度排序。；参数：width, height。 |
| 88 | `         for _,vertices,color in polygons: ` | 遍历 polygons，每次把一项赋给 (_, vertices, color)，执行下面缩进的循环体。 |
| 89 | `             c.create_polygon(*[v for p in vertices for v in p],fill=color,outline=color) ` | 在画布上画多边形；参数：*[v for p in vertices for v in p], fill=color, outline=color。 |
| 90 | `         for m in markers: ` | 遍历 markers，每次把一项赋给 m，执行下面缩进的循环体。 |
| 91 | `             x,y,r = m['x'],m['y'],m['radius'] ` | 把结果保存到 (x, y, r)：组装元组：(m['x'], m['y'], m['radius'])。 |
| 92 | `             selected = m['name']==self.selected ` | 把结果保存到 selected：m['name'] == self.selected。 |
| 93 | `             c.create_oval(x-r,y-r,x+r,y+r,fill=m['color'],outline='#132F45' if selected else '#FFFFFF', ` | 在画布上画圆或椭圆；参数：x - r, y - r, x + r, y + r, fill=m['color'], outline='#132F45' if selected else '#FFFFFF', width=3 if selected else 1, tags=('torso_electrode', m…（完整表达式见左栏）。 |
| 94 | `                           width=3 if selected else 1,tags=('torso_electrode',m['name'])) ` | 接续第 93 行的同一条语句，不是另起一段算法。 在画布上画圆或椭圆；参数：x - r, y - r, x + r, y + r, fill=m['color'], outline='#132F45' if selected else '#FFFFFF', width=3 if selected else 1, tags=('torso_electrode', m…（完整表达式见左栏）。 |
| 95 | `             if m['active']: ` | 检查条件 m['active']；为真时执行下面缩进的一组语句。 |
| 96 | `                 self.hits.append(m) ` | 把一项加入列表末尾；参数：m。 |
| 97 | `                 if height>=430 or selected: ` | 检查条件 height >= 430 or selected；为真时执行下面缩进的一组语句。 |
| 98 | `                     ink = '#243243' if m['color']==COLORS['yellow'] else 'white' ` | 把结果保存到 ink：若 m['color'] == COLORS['yellow']，用 '#243243'；否则用 'white'。 |
| 99 | `                     c.create_text(x,y,text=m['name'],fill=ink,font=('Segoe UI',max(7,min(10,round(r*.65))),'bold'),tags=('electrode_label',)) ` | 在画布上画文本；参数：x, y, text=m['name'], fill=ink, font=('Segoe UI', max(7, min(10, round(r * 0.65))), 'bold'), tags=('electrode_label',)。 |
| 100 | `         for label,x,y in self.guides(width,height): ` | 遍历 self.guides(width, height)，每次把一项赋给 (label, x, y)，执行下面缩进的循环体。 |
| 101 | `             c.create_text(x,y,text=label,fill='#405766',font=('Segoe UI',9,'bold')) ` | 在画布上画文本；参数：x, y, text=label, fill='#405766', font=('Segoe UI', 9, 'bold')。 |
| 102 | `         frontness = math.cos(math.radians(self.yaw)) ` | 把结果保存到 frontness：调用 math.cos；参数：math.radians(self.yaw)。 |
| 103 | `         if abs(frontness) < .5: ` | 检查条件 abs(frontness) < 0.5；为真时执行下面缩进的一组语句。 |
| 104 | `             direction = "Person's left side" if math.sin(math.radians(self.yaw)) > 0 else "Person's right side" ` | 把结果保存到 direction：若 math.sin(math.radians(self.yaw)) > 0，用 "Person's left side"；否则用 "Person's right side"。 |
| 105 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 106 | `             direction = 'Front / A + B' if frontness>=0 else 'Back / C + D' ` | 把结果保存到 direction：若 frontness >= 0，用 'Front / A + B'；否则用 'Back / C + D'。 |
| 107 | `         c.create_text(width/2,18,text=direction,fill='#19384D',font=('Segoe UI',13,'bold')) ` | 在画布上画文本；参数：width / 2, 18, text=direction, fill='#19384D', font=('Segoe UI', 13, 'bold')。 |
| 108 | `         c.create_text(width/2,height-13,text='Drag to rotate  \|  Wheel to zoom  \|  Click a colored electrode',fill='#526A7A',font=('Segoe UI',9)) ` | 在画布上画文本；参数：width / 2, height - 13, text='Drag to rotate  &#124;  Wheel to zoom  &#124;  Click a colored electrode', fill='#526A7A', font=('Segoe UI', 9)。 |
| 109 | `         if not self.electrodes: ` | 检查条件 not self.electrodes；为真时执行下面缩进的一组语句。 |
| 110 | `             c.create_text(width/2,42,text='Not analyzed — gray points are placement only',fill='#657588',font=('Segoe UI',10)) ` | 在画布上画文本；参数：width / 2, 42, text='Not analyzed — gray points are placement only', fill='#657588', font=('Segoe UI', 10)。 |
| 111 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 112 | `     def hit(self,x,y): ` | 定义 hit(self, x, y)。从前到后找鼠标是否落在某个可点击电极圆内。 定义到这里时不执行函数体。 |
| 113 | `         return next((m for m in reversed(self.hits) if (x-m['x'])**2+(y-m['y'])**2<=(m['radius']+4)**2),None) ` | 结束当前函数并返回：取迭代器的下一项或匹配到的第一项；参数：(m for m in reversed(self.hits) if (x - m['x']) ** 2 + (y - m['y']) ** 2 <= (m['radius'] + 4) ** 2), None。 |
| 114 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 115 | `     def press(self,event): ` | 定义 press(self, event)。记住鼠标按下时的位置与相机角度。 定义到这里时不执行函数体。 |
| 116 | `         self.drag=(event.x,event.y,self.yaw,self.pitch); self.moved=False ` | 把结果保存到 self.drag：组装元组：(event.x, event.y, self.yaw, self.pitch)。 把结果保存到 self.moved：False（否）。 |
| 117 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 118 | `     def motion(self,event): ` | 定义 motion(self, event)。拖动超过阈值时改变 yaw/pitch 并刷新；限制俯仰角。 定义到这里时不执行函数体。 |
| 119 | `         if self.drag: ` | 检查条件 self.drag；为真时执行下面缩进的一组语句。 |
| 120 | `             x,y,yaw,pitch=self.drag ` | 把结果保存到 (x, y, yaw, pitch)：读取 self 的 drag 属性。 |
| 121 | `             if abs(event.x-x)+abs(event.y-y)>4: ` | 检查条件 abs(event.x - x) + abs(event.y - y) > 4；为真时执行下面缩进的一组语句。 |
| 122 | `                 self.moved=True ` | 把结果保存到 self.moved：True（是）。 |
| 123 | `                 self.yaw=yaw+(event.x-x)*.5 ` | 把结果保存到 self.yaw：yaw 与 (event.x - x) * 0.5 相加。 |
| 124 | `                 self.pitch=max(-35,min(35,pitch+(event.y-y)*.3)) ` | 把结果保存到 self.pitch：取最大值；参数：-35, min(35, pitch + (event.y - y) * 0.3)。 |
| 125 | `                 self.draw() ` | 按远近顺序画多边形和可见电极，再画标签与提示。。 |
| 126 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 127 | `     def release(self,event): ` | 定义 release(self, event)。若没有形成拖动则视为点击电极，通知主窗口显示详情。 定义到这里时不执行函数体。 |
| 128 | `         if self.drag and not self.moved: ` | 检查条件 self.drag and (not self.moved)；为真时执行下面缩进的一组语句。 |
| 129 | `             item=self.hit(event.x,event.y) ` | 把结果保存到 item：从前到后找鼠标是否落在某个可点击电极圆内。；参数：event.x, event.y。 |
| 130 | `             if item: ` | 检查条件 item；为真时执行下面缩进的一组语句。 |
| 131 | `                 self.focus(item['name']); self.on_select(self.electrodes[item['name']]) ` | 选中电极，必要时转向它所在的身体表面。；参数：item['name']。 调用 self.on_select；参数：self.electrodes[item['name']]。 |
| 132 | `         self.drag=None ` | 把结果保存到 self.drag：None（未知/未设置）。 |
| 133 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 134 | `     def hover(self,event): ` | 定义 hover(self, event)。悬停时更新鼠标形状及该电极颜色说明。 定义到这里时不执行函数体。 |
| 135 | `         self.canvas.delete('hover_label') ` | 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：'hover_label'。 |
| 136 | `         item=self.hit(event.x,event.y) ` | 把结果保存到 item：从前到后找鼠标是否落在某个可点击电极圆内。；参数：event.x, event.y。 |
| 137 | `         self.canvas.configure(cursor='hand2' if item else 'fleur') ` | 更新控件属性或状态，不计算信号指标；参数：cursor='hand2' if item else 'fleur'。 |
| 138 | `         if item and not self.drag: ` | 检查条件 item and (not self.drag)；为真时执行下面缩进的一组语句。 |
| 139 | `             metric=self.electrodes[item['name']].metric(self.mode) ` | 把结果保存到 metric：调用 self.electrodes[item['name']].metric；参数：self.mode。 |
| 140 | `             self.canvas.create_text(10,64,anchor='nw',text=f"{item['name']} \| {COLOR_LABELS[metric.color]}", ` | 在画布上画文本；参数：10, 64, anchor='nw', text=f"{item['name']} &#124; {COLOR_LABELS[metric.color]}", fill='#243243', font=('Segoe UI', 10, 'bold'), tags='hover_label'。 |
| 141 | `                                     fill='#243243',font=('Segoe UI',10,'bold'),tags='hover_label') ` | 接续第 140 行的同一条语句，不是另起一段算法。 在画布上画文本；参数：10, 64, anchor='nw', text=f"{item['name']} &#124; {COLOR_LABELS[metric.color]}", fill='#243243', font=('Segoe UI', 10, 'bold'), tags='hover_label'。 |
| 142 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 143 | `     def wheel(self,event): ` | 定义 wheel(self, event)。按滚轮方向调整缩放并限制在 0.65–2.5 倍。 定义到这里时不执行函数体。 |
| 144 | `         self.zoom=max(.65,min(2.5,self.zoom*(1.10 if event.delta>0 else 1/1.10))) ` | 把结果保存到 self.zoom：取最大值；参数：0.65, min(2.5, self.zoom * (1.1 if event.delta > 0 else 1 / 1.1))。 |
| 145 | `         self.draw() ` | 按远近顺序画多边形和可见电极，再画标签与提示。。 |
| 146 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 147 | `     def save(self,path,title): ` | 定义 save(self, path, title)。用相同投影生成静态躯干 PNG。 定义到这里时不执行函数体。 |
| 148 | `         """Render the same camera and electrode colors to a standalone PNG.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 149 | `         from matplotlib.figure import Figure ` | 从 matplotlib.figure 导入 Figure。不打开主 GUI 也能导出 PNG 图片 |
| 150 | `         from matplotlib.backends.backend_agg import FigureCanvasAgg ` | 从 matplotlib.backends.backend_agg 导入 FigureCanvasAgg。不打开主 GUI 也能导出 PNG 图片 |
| 151 | `         from matplotlib.patches import Polygon,Circle ` | 从 matplotlib.patches 导入 Polygon、Circle。不打开主 GUI 也能导出 PNG 图片 |
| 152 | `         fig=Figure(figsize=(8,10),facecolor='#F4F7FA'); FigureCanvasAgg(fig) ` | 把结果保存到 fig：调用 Figure；参数：figsize=(8, 10), facecolor='#F4F7FA'。 调用 FigureCanvasAgg；参数：fig。 |
| 153 | `         ax=fig.add_axes((0,.035,1,.89));ax.set(xlim=(0,800),ylim=(1000,0));ax.set_aspect('equal');ax.axis('off') ` | 把结果保存到 ax：调用 fig.add_axes；参数：(0, 0.035, 1, 0.89)。 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：xlim=(0, 800), ylim=(1000, 0)。 设置坐标纵横比例；参数：'equal'。 设置坐标轴显示；参数：'off'。 |
| 154 | `         polygons,markers=self.scene(800,1000) ` | 把结果保存到 (polygons, markers)：将模型和电极投影到画布；计算示意明暗并按深度排序。；参数：800, 1000。 |
| 155 | `         for _,vertices,color in polygons: ax.add_patch(Polygon(vertices,facecolor=color,edgecolor=color)) ` | 遍历 polygons，每次把一项赋给 (_, vertices, color)，执行下面缩进的循环体。 在图中加入圆/多边形图元；参数：Polygon(vertices, facecolor=color, edgecolor=color)。 |
| 156 | `         for m in markers: ` | 遍历 markers，每次把一项赋给 m，执行下面缩进的循环体。 |
| 157 | `             ax.add_patch(Circle((m['x'],m['y']),m['radius'],facecolor=m['color'],edgecolor='white')) ` | 在图中加入圆/多边形图元；参数：Circle((m['x'], m['y']), m['radius'], facecolor=m['color'], edgecolor='white')。 |
| 158 | `             if m['active']: ` | 检查条件 m['active']；为真时执行下面缩进的一组语句。 |
| 159 | `                 ax.text(m['x'],m['y'],m['name'],ha='center',va='center',fontsize=8,weight='bold', ` | 给图加入文字；参数：m['x'], m['y'], m['name'], ha='center', va='center', fontsize=8, weight='bold', color='#243243' if m['color'] == COLORS['yellow'] else 'white'。 |
| 160 | `                         color='#243243' if m['color']==COLORS['yellow'] else 'white') ` | 接续第 159 行的同一条语句，不是另起一段算法。 给图加入文字；参数：m['x'], m['y'], m['name'], ha='center', va='center', fontsize=8, weight='bold', color='#243243' if m['color'] == COLORS['yellow'] else 'white'。 |
| 161 | `         for label,x,y in self.guides(800,1000): ` | 遍历 self.guides(800, 1000)，每次把一项赋给 (label, x, y)，执行下面缩进的循环体。 |
| 162 | `             ax.text(x,y,label,ha='center',va='center',fontsize=9,color='#405766',weight='bold') ` | 给图加入文字；参数：x, y, label, ha='center', va='center', fontsize=9, color='#405766', weight='bold'。 |
| 163 | `         fig.suptitle(title,fontsize=11) ` | 调用 fig.suptitle；参数：title, fontsize=11。 |
| 164 | `         fig.text(.5,.015,'Schematic torso; verify wiring. Gray = not analyzed / not selected. DRL * = orientation only.',ha='center',fontsize=8) ` | 给图加入文字；参数：0.5, 0.015, 'Schematic torso; verify wiring. Gray = not analyzed / not selected. DRL * = orientation only.', ha='center', fontsize=8。 |
| 165 | `         fig.savefig(path,dpi=150) ` | 将图像保存为文件；参数：path, dpi=150。 |
