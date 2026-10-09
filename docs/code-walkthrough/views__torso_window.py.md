# views/torso_window.py：独立躯干窗口

把躯干、指标选择、提醒列表、详情及时间轴组合成第二窗口，与主窗口使用同一份结果。

源码：[views/torso_window.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py>)。本说明对应 145 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [14–78](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:14>) | 构建独立窗口及与主窗口共享的指标变量、选择和关闭回调。 |
| `angle` | [80–81](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:80>) | 切到固定斜视角，方便看立体外形。 |
| `change_layout` | [83–85](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:83>) | 根据编号方向和左右选项更新示意布局，并回传主窗口。 |
| `set_layout` | [87–90](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:87>) | 从外部恢复布局及其表单选项。 |
| `show` | [92–112](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:92>) | 刷新躯干、前后分组统计、未映射提示、待检查列表及时间轴。 |
| `clear` | [114–119](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:114>) | 只显示灰色布置示意，没有质量结果。 |
| `_pick` | [121–122](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:121>) | 把躯干选点转交主窗口的同一详情处理函数。 |
| `pick_alert` | [124–127](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:124>) | 点击提醒列表时转到对应身体面，并选中该电极。 |
| `set_detail` | [129–132](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:129>) | 更新只读详情文本和选中电极。 |
| `save` | [134–142](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:134>) | 导出躯干 PNG 及带 schematic=True 的布局 JSON。 |
| `close` | [144–145](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py:144>) | 暂停播放，通知主窗口解除引用，再销毁子窗口。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Expanded torso view linked to the main GUI's metric and window selection.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import asdict ` | 从 dataclasses 导入 asdict。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 4 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 5 | ` import tkinter as tk ` | 导入模块 tkinter（别名 tk）。桌面窗口、控件、文件选择框和消息框 |
| 6 | ` from tkinter import ttk ` | 从 tkinter 导入 ttk。桌面窗口、控件、文件选择框和消息框 |
| 7 | ` from config import COLORS ` | 从 config 导入 COLORS。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 8 | ` from views.torso_geometry import TorsoLayout ` | 从 views.torso_geometry 导入 TorsoLayout。生成示意躯干网格和 A1–D32 位置，再做三维到二维的投影；这些坐标不是 CT 重建或患者实测坐标。 |
| 9 | ` from views.torso_view import TorsoView ` | 从 views.torso_view 导入 TorsoView。画示意躯干，按已有指标上色，处理旋转、缩放、选点、悬停和图片导出；不计算电极质量。 |
| 10 | ` from views.timeline_view import TimelineView ` | 从 views.timeline_view 导入 TimelineView。管理已有窗口结果的滑块、播放/暂停、前后跳转、下一个提醒；不会在播放时重新分析样本。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 13 | ` class TorsoWindow(tk.Toplevel): ` | 定义 TorsoWindow 类，继承 tk.Toplevel；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 14 | `     def __init__(self, parent, metric_var, metric_labels, on_metric, on_select, on_window, ` | 定义 __init__(self, parent, metric_var, metric_labels, on_metric, on_select, on_window, layout, on_layout, on_close)。构建独立窗口及与主窗口共享的指标变量、选择和关闭回调。 定义到这里时不执行函数体。 |
| 15 | `                  layout, on_layout, on_close): ` | 接续第 14 行的同一条语句，不是另起一段算法。 定义 __init__(self, parent, metric_var, metric_labels, on_metric, on_select, on_window, layout, on_layout, on_close)。构建独立窗口及与主窗口共享的指标变量、选择和关闭回调。 定义到这里时不执行函数体。 |
| 16 | `         super().__init__(parent) ` | 调用 super().__init__；参数：parent。 |
| 17 | `         self.title('Electrode QA \| 3D torso') ` | 调用 self.title；参数：'Electrode QA &#124; 3D torso'。 |
| 18 | `         self.geometry(f'1180x{min(950,self.winfo_screenheight()-90)}') ` | 调用 self.geometry；参数：f'1180x{min(950, self.winfo_screenheight() - 90)}'。 |
| 19 | `         self.minsize(950,720) ` | 调用 self.minsize；参数：950, 720。 |
| 20 | `         self.on_select,self.on_layout,self.on_close=on_select,on_layout,on_close ` | 把结果保存到 (self.on_select, self.on_layout, self.on_close)：组装元组：(on_select, on_layout, on_close)。 |
| 21 | `         self.electrodes={};self.mode='current';self.context='Not analyzed';self.layout=layout ` | 把结果保存到 self.electrodes：组装字典，键用于给数值/设置命名：{}。 把结果保存到 self.mode：'current'。 把结果保存到 self.context：'Not analyzed'。 把结果保存到 self.layout：layout。 |
| 22 | `         self.protocol('WM_DELETE_WINDOW',self.close) ` | 调用 self.protocol；参数：'WM_DELETE_WINDOW', self.close。 |
| 23 | `         header=ttk.Frame(self,padding=(14,10));header.pack(fill='x') ` | 把结果保存到 header：创建布局容器；参数：self, padding=(14, 10)。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 24 | `         ttk.Label(header,text='3D electrode layout',font=('Segoe UI',18,'bold')).pack(side='left') ` | 创建文字标签；参数：header, text='3D electrode layout', font=('Segoe UI', 18, 'bold')；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 25 | `         ttk.Label(header,text='Metric').pack(side='left',padx=(25,7)) ` | 创建文字标签；参数：header, text='Metric'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=(25, 7)。 |
| 26 | `         self.metric_combo=ttk.Combobox(header,textvariable=metric_var,values=metric_labels,state='readonly',width=28) ` | 把结果保存到 self.metric_combo：创建下拉选择框；参数：header, textvariable=metric_var, values=metric_labels, state='readonly', width=28。 |
| 27 | `         self.metric_combo.pack(side='left');self.metric_combo.bind('<<ComboboxSelected>>',lambda _:on_metric()) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 绑定界面事件，事件发生时才执行回调；参数：'<<ComboboxSelected>>', lambda _: on_metric()。 |
| 28 | `         self.scope=tk.StringVar(value='Not analyzed') ` | 把结果保存到 self.scope：创建可绑定控件的文本变量；参数：value='Not analyzed'。 |
| 29 | `         scope_label=ttk.Label(self,textvariable=self.scope,padding=(14,0),wraplength=1080) ` | 把结果保存到 scope_label：创建文字标签；参数：self, textvariable=self.scope, padding=(14, 0), wraplength=1080。 |
| 30 | `         scope_label.pack(fill='x') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 31 | `         scope_label.bind('<Configure>',lambda event:scope_label.configure(wraplength=max(200,event.width-28))) ` | 绑定界面事件，事件发生时才执行回调；参数：'<Configure>', lambda event: scope_label.configure(wraplength=max(200, event.width - 28))。 |
| 32 | `         # Reserve playback controls before the expandable 3D surface. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 33 | `         footer=ttk.Frame(self,padding=(14,7));footer.pack(side='bottom',fill='x') ` | 把结果保存到 footer：创建布局容器；参数：self, padding=(14, 7)。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='bottom', fill='x'。 |
| 34 | `         self.timeline=TimelineView(footer,on_window);self.timeline.pack(fill='x') ` | 把结果保存到 self.timeline：调用 TimelineView；参数：footer, on_window。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 35 | `         ttk.Label(footer,text='Timeline: worst selected channel. Gray electrode = not selected / not analyzed.', ` | 创建文字标签；参数：footer, text='Timeline: worst selected channel. Gray electrode = not selected / not analyzed.', foreground='#657588'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w', pady=(4, 0)。 |
| 36 | `                   foreground='#657588').pack(anchor='w',pady=(4,0)) ` | 接续第 35 行的同一条语句，不是另起一段算法。 创建文字标签；参数：footer, text='Timeline: worst selected channel. Gray electrode = not selected / not analyzed.', foreground='#657588'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w', pady=(4, 0)。 |
| 37 | `         body=ttk.Frame(self,padding=12);body.pack(fill='both',expand=True) ` | 把结果保存到 body：创建布局容器；参数：self, padding=12。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 38 | `         right=ttk.Frame(body,width=310);right.pack(side='right',fill='y',padx=(12,0));right.pack_propagate(False) ` | 把结果保存到 right：创建布局容器；参数：body, width=310。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='right', fill='y', padx=(12, 0)。 调用 right.pack_propagate；参数：False。 |
| 39 | `         left=ttk.Frame(body);left.pack(fill='both',expand=True) ` | 把结果保存到 left：创建布局容器；参数：body。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 40 | `         actions=ttk.Frame(left);actions.pack(fill='x') ` | 把结果保存到 actions：创建布局容器；参数：left。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 41 | `         self.view=TorsoView(left,self._pick,layout) ` | 把结果保存到 self.view：调用 TorsoView；参数：left, self._pick, layout。 |
| 42 | `         for face in ('Front','Back'): ` | 遍历 ('Front', 'Back')，每次把一项赋给 face，执行下面缩进的循环体。 |
| 43 | `             ttk.Button(actions,text=face,command=lambda f=face:self.view.face(f)).pack(side='left',padx=(0,5)) ` | 创建按钮；参数：actions, text=face, command=lambda f=face: self.view.face(f)；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=(0, 5)。 |
| 44 | `         ttk.Button(actions,text='Angle',command=self.angle).pack(side='left',padx=(0,5)) ` | 创建按钮；参数：actions, text='Angle', command=self.angle；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=(0, 5)。 |
| 45 | `         ttk.Button(actions,text='Reset',command=lambda:self.view.face('Front')).pack(side='left') ` | 创建按钮；参数：actions, text='Reset', command=lambda: self.view.face('Front')；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 46 | `         self.view.pack(fill='both',expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 47 | `         layout_row=ttk.Frame(left);layout_row.pack(fill='x',pady=(4,0)) ` | 把结果保存到 layout_row：创建布局容器；参数：left。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=(4, 0)。 |
| 48 | `         self.side=tk.StringVar(value="A/C: person's right" if layout.front_b_on_right else "A/C: person's left") ` | 把结果保存到 self.side：创建可绑定控件的文本变量；参数：value="A/C: person's right" if layout.front_b_on_right else "A/C: person's left"。 |
| 49 | `         self.order=tk.StringVar(value='Outer low at bottom' if not layout.top_to_bottom else 'Outer low at top') ` | 把结果保存到 self.order：创建可绑定控件的文本变量；参数：value='Outer low at bottom' if not layout.top_to_bottom else 'Outer low at top'。 |
| 50 | `         for variable,values,width in ((self.side,("A/C: person's left","A/C: person's right"),23), ` | 遍历 ((self.side, ("A/C: person's left", "A/C: person's right"), 23), (self.order, ('Outer low at bottom', 'Outer low at top'), 23))，每次把一项赋给 (variable, values, width)，执行下面缩进的循环体。 |
| 51 | `                                       (self.order,('Outer low at bottom','Outer low at top'),23)): ` | 接续第 50 行的同一条语句，不是另起一段算法。 遍历 ((self.side, ("A/C: person's left", "A/C: person's right"), 23), (self.order, ('Outer low at bottom', 'Outer low at top'), 23))，每次把一项赋给 (variable, values, width)，执行下面缩进的循环体。 |
| 52 | `             combo=ttk.Combobox(layout_row,textvariable=variable,values=values,state='readonly',width=width) ` | 把结果保存到 combo：创建下拉选择框；参数：layout_row, textvariable=variable, values=values, state='readonly', width=width。 |
| 53 | `             combo.pack(side='left',padx=(0,6));combo.bind('<<ComboboxSelected>>',self.change_layout) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=(0, 6)。 绑定界面事件，事件发生时才执行回调；参数：'<<ComboboxSelected>>', self.change_layout。 |
| 54 | `         layout_note=ttk.Label(left,text='R/L = person\'s sides. Middle column reversed (serpentine). C behind A; D behind B. DRL * = unscored orientation marker. Schematic; verify wiring.', ` | 把结果保存到 layout_note：创建文字标签；参数：left, text="R/L = person's sides. Middle column reversed (serpentine). C behind A; D behind B. DRL * = unscored orientation marker. Schematic; ve…（完整表达式见左栏）。 |
| 55 | `                               foreground='#657588',wraplength=700) ` | 接续第 54 行的同一条语句，不是另起一段算法。 把结果保存到 layout_note：创建文字标签；参数：left, text="R/L = person's sides. Middle column reversed (serpentine). C behind A; D behind B. DRL * = unscored orientation marker. Schematic; ve…（完整表达式见左栏）。 |
| 56 | `         layout_note.pack(anchor='w',pady=(3,0)) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w', pady=(3, 0)。 |
| 57 | `         left.bind('<Configure>',lambda event:layout_note.configure(wraplength=max(200,event.width))) ` | 绑定界面事件，事件发生时才执行回调；参数：'<Configure>', lambda event: layout_note.configure(wraplength=max(200, event.width))。 |
| 58 | `         self.bank_summary=tk.StringVar() ` | 把结果保存到 self.bank_summary：创建可绑定控件的文本变量。 |
| 59 | `         ttk.Label(right,textvariable=self.bank_summary,wraplength=305,font=('Segoe UI',10,'bold')).pack(fill='x') ` | 创建文字标签；参数：right, textvariable=self.bank_summary, wraplength=305, font=('Segoe UI', 10, 'bold')；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 60 | `         self.mapping_notice=tk.StringVar() ` | 把结果保存到 self.mapping_notice：创建可绑定控件的文本变量。 |
| 61 | `         ttk.Label(right,textvariable=self.mapping_notice,wraplength=305,foreground='#86640B').pack(fill='x',pady=6) ` | 创建文字标签；参数：right, textvariable=self.mapping_notice, wraplength=305, foreground='#86640B'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=6。 |
| 62 | `         ttk.Label(right,text='Channels to review',font=('Segoe UI',11,'bold')).pack(anchor='w') ` | 创建文字标签；参数：right, text='Channels to review', font=('Segoe UI', 11, 'bold')；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w'。 |
| 63 | `         alert_box=ttk.Frame(right);alert_box.pack(fill='x',pady=(5,7)) ` | 把结果保存到 alert_box：创建布局容器；参数：right。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=(5, 7)。 |
| 64 | `         self.alerts=ttk.Treeview(alert_box,columns=('channel','face','state'),show='headings',height=7) ` | 把结果保存到 self.alerts：创建表格/列表；参数：alert_box, columns=('channel', 'face', 'state'), show='headings', height=7。 |
| 65 | `         for key,title,width in (('channel','Electrode',83),('face','Surface',80),('state','Status',125)): ` | 遍历 (('channel', 'Electrode', 83), ('face', 'Surface', 80), ('state', 'Status', 125))，每次把一项赋给 (key, title, width)，执行下面缩进的循环体。 |
| 66 | `             self.alerts.heading(key,text=title);self.alerts.column(key,width=width,stretch=True) ` | 设置表格列标题；参数：key, text=title。 设置表格列宽等属性或按该类定义取信号列；参数：key, width=width, stretch=True。 |
| 67 | `         alert_scroll=ttk.Scrollbar(alert_box,command=self.alerts.yview) ` | 把结果保存到 alert_scroll：创建滚动条；参数：alert_box, command=self.alerts.yview。 |
| 68 | `         self.alerts.configure(yscrollcommand=alert_scroll.set) ` | 更新控件属性或状态，不计算信号指标；参数：yscrollcommand=alert_scroll.set。 |
| 69 | `         alert_scroll.pack(side='right',fill='y');self.alerts.pack(fill='x') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='right', fill='y'。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 70 | `         self.alerts.bind('<<TreeviewSelect>>',self.pick_alert) ` | 绑定界面事件，事件发生时才执行回调；参数：'<<TreeviewSelect>>', self.pick_alert。 |
| 71 | `         for color in COLORS: self.alerts.tag_configure(color,foreground=COLORS[color]) ` | 遍历 COLORS，每次把一项赋给 color，执行下面缩进的循环体。 调用 self.alerts.tag_configure；参数：color, foreground=COLORS[color]。 |
| 72 | `         ttk.Label(right,text='Selected electrode',font=('Segoe UI',11,'bold')).pack(anchor='w') ` | 创建文字标签；参数：right, text='Selected electrode', font=('Segoe UI', 11, 'bold')；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w'。 |
| 73 | `         detail_box=ttk.Frame(right);detail_box.pack(fill='both',expand=True,pady=5) ` | 把结果保存到 detail_box：创建布局容器；参数：right。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True, pady=5。 |
| 74 | `         self.detail=tk.Text(detail_box,wrap='word',width=30,height=8,relief='flat',padx=8,pady=8,font=('Segoe UI',10)) ` | 把结果保存到 self.detail：创建多行文本框；参数：detail_box, wrap='word', width=30, height=8, relief='flat', padx=8, pady=8, font=('Segoe UI', 10)。 |
| 75 | `         scroll=ttk.Scrollbar(detail_box,command=self.detail.yview) ` | 把结果保存到 scroll：创建滚动条；参数：detail_box, command=self.detail.yview。 |
| 76 | `         self.detail.configure(yscrollcommand=scroll.set,state='disabled') ` | 更新控件属性或状态，不计算信号指标；参数：yscrollcommand=scroll.set, state='disabled'。 |
| 77 | `         scroll.pack(side='right',fill='y');self.detail.pack(fill='both',expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='right', fill='y'。 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 78 | `         self.clear() ` | 只显示灰色布置示意，没有质量结果。。 |
| 79 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 80 | `     def angle(self): ` | 定义 angle(self)。切到固定斜视角，方便看立体外形。 定义到这里时不执行函数体。 |
| 81 | `         self.view.yaw=35.;self.view.pitch=12.;self.view.zoom=1.;self.view.draw() ` | 把结果保存到 self.view.yaw：35.0。 把结果保存到 self.view.pitch：12.0。 把结果保存到 self.view.zoom：1.0。 调用 self.view.draw。 |
| 82 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 83 | `     def change_layout(self,_=None): ` | 定义 change_layout(self, _=None)。根据编号方向和左右选项更新示意布局，并回传主窗口。 定义到这里时不执行函数体。 |
| 84 | `         self.layout=TorsoLayout('C behind A',self.order.get()=='Outer low at top',self.side.get()=="A/C: person's right") ` | 把结果保存到 self.layout：创建躯干示意方向设置；参数：'C behind A', self.order.get() == 'Outer low at top', self.side.get() == "A/C: person's right"。 |
| 85 | `         self.view.set_layout(self.layout);self.on_layout(self.layout) ` | 调用 self.view.set_layout；参数：self.layout。 调用 self.on_layout；参数：self.layout。 |
| 86 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 87 | `     def set_layout(self,layout): ` | 定义 set_layout(self, layout)。从外部恢复布局及其表单选项。 定义到这里时不执行函数体。 |
| 88 | `         self.layout=layout;self.view.set_layout(layout) ` | 把结果保存到 self.layout：layout。 调用 self.view.set_layout；参数：layout。 |
| 89 | `         self.side.set("A/C: person's right" if layout.front_b_on_right else "A/C: person's left") ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数："A/C: person's right" if layout.front_b_on_right else "A/C: person's left"。 |
| 90 | `         self.order.set('Outer low at top' if layout.top_to_bottom else 'Outer low at bottom') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Outer low at top' if layout.top_to_bottom else 'Outer low at bottom'。 |
| 91 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 92 | `     def show(self,electrodes,mode,context,metric_labels,key,items,current,notice): ` | 定义 show(self, electrodes, mode, context, metric_labels, key, items, current, notice)。刷新躯干、前后分组统计、未映射提示、待检查列表及时间轴。 定义到这里时不执行函数体。 |
| 93 | `         self.electrodes={e.name:e for e in electrodes};self.mode=mode;self.context=context ` | 把结果保存到 self.electrodes：从 electrodes 逐个取 e，为每项生成 e.name: e。 把结果保存到 self.mode：mode。 把结果保存到 self.context：context。 |
| 94 | `         self.scope.set(context);self.metric_combo.configure(values=metric_labels) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：context。 更新控件属性或状态，不计算信号指标；参数：values=metric_labels。 |
| 95 | `         self.view.show(electrodes,mode) ` | 调用 self.view.show；参数：electrodes, mode。 |
| 96 | `         rows=[] ` | 把结果保存到 rows：组装列表：[]。 |
| 97 | `         for banks,label in (('AB','Front A/B'),('CD','Back C/D')): ` | 遍历 (('AB', 'Front A/B'), ('CD', 'Back C/D'))，每次把一项赋给 (banks, label)，执行下面缩进的循环体。 |
| 98 | `             selected=[e for e in electrodes if e.name in self.view.positions and e.name[0] in banks] ` | 把结果保存到 selected：从 electrodes 逐个取 e，仅保留 e.name in self.view.positions and e.name[0] in banks，为每项生成 e。 |
| 99 | `             counts={c:sum(e.metric(mode).color==c for e in selected) for c in COLORS} ` | 把结果保存到 counts：从 COLORS 逐个取 c，为每项生成 c: sum((e.metric(mode).color == c for e in selected))。 |
| 100 | `             rows.append(f"{label}: {len(selected)} selected\nGreen {counts['green']} \| Yellow {counts['yellow']} \| Red {counts['red']}") ` | 把一项加入列表末尾；参数：f"{label}: {len(selected)} selected\nGreen {counts['green']} &#124; Yellow {counts['yellow']} &#124; Red {counts['red']}"。 |
| 101 | `         self.bank_summary.set('\n\n'.join(rows)) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'\n\n'.join(rows)。 |
| 102 | `         missing=[e.name for e in electrodes if e.name not in self.view.positions] ` | 把结果保存到 missing：从 electrodes 逐个取 e，仅保留 e.name not in self.view.positions，为每项生成 e.name。 |
| 103 | `         self.mapping_notice.set(('Unmapped: '+', '.join(missing[:8])+(' ...' if len(missing)>8 else '')+ ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Unmapped: ' + ', '.join(missing[:8]) + (' ...' if len(missing) > 8 else '') + '. Use the grid for these channels.' if missing else 'A1-D32 mappe…（完整表达式见左栏）。 |
| 104 | `                                  '. Use the grid for these channels.') if missing else 'A1-D32 mapped to the sketch. Auxiliary/reference hardware positions are not scored here.') ` | 接续第 103 行的同一条语句，不是另起一段算法。 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Unmapped: ' + ', '.join(missing[:8]) + (' ...' if len(missing) > 8 else '') + '. Use the grid for these channels.' if missing else 'A1-D32 mappe…（完整表达式见左栏）。 |
| 105 | `         self.alerts.delete(*self.alerts.get_children()) ` | 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：*self.alerts.get_children()。 |
| 106 | `         rank={'red':0,'yellow':1,'green':2} ` | 把结果保存到 rank：组装字典，键用于给数值/设置命名：{'red': 0, 'yellow': 1, 'green': 2}。 |
| 107 | `         for e in sorted(electrodes,key=lambda e:rank[e.metric(mode).color]): ` | 遍历 sorted(electrodes, key=lambda e: rank[e.metric(mode).color])，每次把一项赋给 e，执行下面缩进的循环体。 |
| 108 | `             color=e.metric(mode).color ` | 把结果保存到 color：读取 e.metric(mode) 的 color 属性。 |
| 109 | `             if color!='green': ` | 检查条件 color != 'green'；为真时执行下面缩进的一组语句。 |
| 110 | `                 self.alerts.insert('', 'end',iid=e.name,values=(e.name,self.view.positions.get(e.name,{}).get('face','Unmapped'), ` | 向列表或文本控件加入显示内容；参数：'', 'end', iid=e.name, values=(e.name, self.view.positions.get(e.name, {}).get('face', 'Unmapped'), 'Check required' if color == 'red' else 'Revi…（完整表达式见左栏）。 |
| 111 | `                                    'Check required' if color=='red' else 'Review'),tags=(color,)) ` | 接续第 110 行的同一条语句，不是另起一段算法。 向列表或文本控件加入显示内容；参数：'', 'end', iid=e.name, values=(e.name, self.view.positions.get(e.name, {}).get('face', 'Unmapped'), 'Check required' if color == 'red' else 'Revi…（完整表达式见左栏）。 |
| 112 | `         self.timeline.show(key,items,current,notice) ` | 调用 self.timeline.show；参数：key, items, current, notice。 |
| 113 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 114 | `     def clear(self): ` | 定义 clear(self)。只显示灰色布置示意，没有质量结果。 定义到这里时不执行函数体。 |
| 115 | `         self.timeline.clear();self.electrodes={};self.view.show([],self.mode) ` | 清空容器，或调用该视图定义的清除方法。 把结果保存到 self.electrodes：组装字典，键用于给数值/设置命名：{}。 调用 self.view.show；参数：[], self.mode。 |
| 116 | `         self.scope.set('Not analyzed — placement preview only') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Not analyzed — placement preview only'。 |
| 117 | `         self.bank_summary.set('Front: A / B\nBack: C / D') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Front: A / B\nBack: C / D'。 |
| 118 | `         self.mapping_notice.set('Gray dots have no current analysis result.') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Gray dots have no current analysis result.'。 |
| 119 | `         self.alerts.delete(*self.alerts.get_children());self.set_detail('Run analysis to display electrode states.') ` | 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：*self.alerts.get_children()。 更新只读详情文本和选中电极。；参数：'Run analysis to display electrode states.'。 |
| 120 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 121 | `     def _pick(self,electrode): ` | 定义 _pick(self, electrode)。把躯干选点转交主窗口的同一详情处理函数。 定义到这里时不执行函数体。 |
| 122 | `         self.on_select(electrode) ` | 调用 self.on_select；参数：electrode。 |
| 123 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 124 | `     def pick_alert(self,_=None): ` | 定义 pick_alert(self, _=None)。点击提醒列表时转到对应身体面，并选中该电极。 定义到这里时不执行函数体。 |
| 125 | `         selected=self.alerts.selection() ` | 把结果保存到 selected：读取所选行。 |
| 126 | `         if selected and selected[0] in self.electrodes: ` | 检查条件 selected and selected[0] in self.electrodes；为真时执行下面缩进的一组语句。 |
| 127 | `             self.view.focus(selected[0],turn=True);self.on_select(self.electrodes[selected[0]]) ` | 调用 self.view.focus；参数：selected[0], turn=True。 调用 self.on_select；参数：self.electrodes[selected[0]]。 |
| 128 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 129 | `     def set_detail(self,text,name=None): ` | 定义 set_detail(self, text, name=None)。更新只读详情文本和选中电极。 定义到这里时不执行函数体。 |
| 130 | `         self.detail.configure(state='normal');self.detail.delete('1.0','end');self.detail.insert('1.0',text) ` | 更新控件属性或状态，不计算信号指标；参数：state='normal'。 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：'1.0', 'end'。 向列表或文本控件加入显示内容；参数：'1.0', text。 |
| 131 | `         self.detail.configure(state='disabled') ` | 更新控件属性或状态，不计算信号指标；参数：state='disabled'。 |
| 132 | `         if name: self.view.focus(name) ` | 检查条件 name；为真时执行下面缩进的一组语句。 调用 self.view.focus；参数：name。 |
| 133 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 134 | `     def save(self,folder): ` | 定义 save(self, folder)。导出躯干 PNG 及带 schematic=True 的布局 JSON。 定义到这里时不执行函数体。 |
| 135 | `         folder=Path(folder) ` | 把结果保存到 folder：构造路径对象；参数：folder。 |
| 136 | `         title=self.context+'\n'+self.mode ` | 把结果保存到 title：self.context + '\n' 与 self.mode 相加。 |
| 137 | `         self.view.save(folder/'torso_view.png',title) ` | 调用 self.view.save；参数：folder / 'torso_view.png', title。 |
| 138 | `         metadata=dict(layout=asdict(self.layout),numbering='Serpentine: middle (11-21) column reversed relative to outer columns', ` | 把结果保存到 metadata：组装键值字典；参数：layout=asdict(self.layout), numbering='Serpentine: middle (11-21) column reversed relative to outer columns', coordinate_system='x = front-screen…（完整表达式见左栏）。 |
| 139 | `                       coordinate_system='x = front-screen right, y = back, z = up', ` | 接续第 138 行的同一条语句，不是另起一段算法。 把结果保存到 metadata：组装键值字典；参数：layout=asdict(self.layout), numbering='Serpentine: middle (11-21) column reversed relative to outer columns', coordinate_system='x = front-screen…（完整表达式见左栏）。 |
| 140 | `                       schematic=True,scope=self.context,metric=self.mode,camera=dict(yaw=self.view.yaw,pitch=self.view.pitch,zoom=self.view.zoom), ` | 接续第 138 行的同一条语句，不是另起一段算法。 组装键值字典；参数：yaw=self.view.yaw, pitch=self.view.pitch, zoom=self.view.zoom。 |
| 141 | `                       positions=self.view.positions) ` | 接续第 138 行的同一条语句，不是另起一段算法。 把结果保存到 metadata：组装键值字典；参数：layout=asdict(self.layout), numbering='Serpentine: middle (11-21) column reversed relative to outer columns', coordinate_system='x = front-screen…（完整表达式见左栏）。 |
| 142 | `         (folder/'torso_layout.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8') ` | 写入文本文件；参数：json.dumps(metadata, indent=2), encoding='utf-8'。 |
| 143 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 144 | `     def close(self): ` | 定义 close(self)。暂停播放，通知主窗口解除引用，再销毁子窗口。 定义到这里时不执行函数体。 |
| 145 | `         self.timeline.pause();self.on_close();self.destroy() ` | 调用 self.timeline.pause。 调用 self.on_close。 销毁窗口及控件。 |
