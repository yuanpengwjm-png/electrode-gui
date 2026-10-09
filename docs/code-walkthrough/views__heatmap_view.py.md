# views/heatmap_view.py：二维通道网格

读取计算完成的颜色，画可点击圆点；另有不依赖 Tk 窗口的 PNG 导出器。网格顺序不是身体坐标。

源码：[views/heatmap_view.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/heatmap_view.py>)。本说明对应 85 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `grid_positions` | [8–9](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/heatmap_view.py:8>) | 通过整数除法和取余，把第 i 个通道转换为网格行列。 |
| `__init__` | [13–22](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/heatmap_view.py:13>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `show` | [24–26](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/heatmap_view.py:24>) | 存下要显示的电极结果和指标，再重画。 |
| `draw` | [28–53](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/heatmap_view.py:28>) | 按画布宽度决定列数，画圆点/标签并绑定点击，不计算信号指标。 |
| `save` | [58–85](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/heatmap_view.py:58>) | 用 Matplotlib 非交互画布生成同样状态的 PNG。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Responsive electrode circles with scrolling and click-to-inspect.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 3 | ` import tkinter as tk ` | 导入模块 tkinter（别名 tk）。桌面窗口、控件、文件选择框和消息框 |
| 4 | ` from tkinter import ttk ` | 从 tkinter 导入 ttk。桌面窗口、控件、文件选择框和消息框 |
| 5 | ` from config import COLORS, COLOR_LABELS ` | 从 config 导入 COLORS、COLOR_LABELS。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 6 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 7 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 8 | ` def grid_positions(count, columns): ` | 定义 grid_positions(count, columns)。通过整数除法和取余，把第 i 个通道转换为网格行列。 定义到这里时不执行函数体。 |
| 9 | `     return [(i//max(1, columns), i % max(1, columns)) for i in range(count)] ` | 结束当前函数并返回：从 range(count) 逐个取 i，为每项生成 (i // max(1, columns), i % max(1, columns))。 |
| 10 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | ` class HeatmapView(ttk.Frame): ` | 定义 HeatmapView 类，继承 ttk.Frame；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 13 | `     def __init__(self, parent, on_select): ` | 定义 __init__(self, parent, on_select)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 14 | `         super().__init__(parent) ` | 调用 super().__init__；参数：parent。 |
| 15 | `         self.on_select, self.electrodes, self.mode = on_select, [], "current" ` | 把结果保存到 (self.on_select, self.electrodes, self.mode)：组装元组：(on_select, [], 'current')。 |
| 16 | `         self.canvas = tk.Canvas(self, bg="#F4F7FA", highlightthickness=0) ` | 把结果保存到 self.canvas：创建绘图画布；参数：self, bg='#F4F7FA', highlightthickness=0。 |
| 17 | `         scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview) ` | 把结果保存到 scroll：创建滚动条；参数：self, orient='vertical', command=self.canvas.yview。 |
| 18 | `         self.canvas.configure(yscrollcommand=scroll.set) ` | 更新控件属性或状态，不计算信号指标；参数：yscrollcommand=scroll.set。 |
| 19 | `         scroll.pack(side="right", fill="y") ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='right', fill='y'。 |
| 20 | `         self.canvas.pack(fill="both", expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 21 | `         self.canvas.bind("<Configure>", lambda _: self.draw()) ` | 绑定界面事件，事件发生时才执行回调；参数：'<Configure>', lambda _: self.draw()。 |
| 22 | `         self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-int(e.delta/120), "units")) ` | 绑定界面事件，事件发生时才执行回调；参数：'<MouseWheel>', lambda e: self.canvas.yview_scroll(-int(e.delta / 120), 'units')。 |
| 23 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 24 | `     def show(self, electrodes, mode): ` | 定义 show(self, electrodes, mode)。存下要显示的电极结果和指标，再重画。 定义到这里时不执行函数体。 |
| 25 | `         self.electrodes, self.mode = electrodes, mode ` | 把结果保存到 (self.electrodes, self.mode)：组装元组：(electrodes, mode)。 |
| 26 | `         self.draw() ` | 按画布宽度决定列数，画圆点/标签并绑定点击，不计算信号指标。。 |
| 27 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 28 | `     def draw(self): ` | 定义 draw(self)。按画布宽度决定列数，画圆点/标签并绑定点击，不计算信号指标。 定义到这里时不执行函数体。 |
| 29 | `         canvas = self.canvas ` | 把结果保存到 canvas：读取 self 的 canvas 属性。 |
| 30 | `         canvas.delete("all") ` | 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：'all'。 |
| 31 | `         width = max(240, canvas.winfo_width()) ` | 把结果保存到 width：取最大值；参数：240, canvas.winfo_width()。 |
| 32 | `         if not self.electrodes: ` | 检查条件 not self.electrodes；为真时执行下面缩进的一组语句。 |
| 33 | `             canvas.create_text(width/2, 100, text="Choose BDF records and channels\nClick Run analysis", fill="#6B7A89", font=("Segoe UI", 15), justify="center") ` | 在画布上画文本；参数：width / 2, 100, text='Choose BDF records and channels\nClick Run analysis', fill='#6B7A89', font=('Segoe UI', 15), justify='center'。 |
| 34 | `             canvas.configure(scrollregion=(0, 0, width, 200)) ` | 更新控件属性或状态，不计算信号指标；参数：scrollregion=(0, 0, width, 200)。 |
| 35 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 36 | `         columns = max(1, min(len(self.electrodes), int(width/120))) ` | 把结果保存到 columns：取最大值；参数：1, min(len(self.electrodes), int(width / 120))。 |
| 37 | `         cell = width/columns ` | 把结果保存到 cell：width 与 columns 相除。 |
| 38 | `         for i, (row, col) in enumerate(grid_positions(len(self.electrodes), columns)): ` | 遍历 enumerate(grid_positions(len(self.electrodes), columns))，每次把一项赋给 (i, (row, col))，执行下面缩进的循环体。 |
| 39 | `             item = self.electrodes[i] ` | 把结果保存到 item：按索引/键 i 取 self.electrodes 的内容。 |
| 40 | `             metric = item.metric(self.mode) ` | 把结果保存到 metric：调用 item.metric；参数：self.mode。 |
| 41 | `             cx, cy, radius = cell*(col+.5), 58+row*128, min(42, cell*.34) ` | 把结果保存到 (cx, cy, radius)：组装元组：(cell * (col + 0.5), 58 + row * 128, min(42, cell * 0.34))。 |
| 42 | `             tag = f"electrode-{i}" ` | 把结果保存到 tag：将变量值插入 f-string 文本；格式如 .3f 表示显示三位小数。 |
| 43 | `             canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, fill=COLORS[metric.color], ` | 在画布上画圆或椭圆；参数：cx - radius, cy - radius, cx + radius, cy + radius, fill=COLORS[metric.color], outline='white', width=3, tags=(tag, 'electrode_circle')。 |
| 44 | `                                outline="white", width=3, tags=(tag, "electrode_circle")) ` | 接续第 43 行的同一条语句，不是另起一段算法。 在画布上画圆或椭圆；参数：cx - radius, cy - radius, cx + radius, cy + radius, fill=COLORS[metric.color], outline='white', width=3, tags=(tag, 'electrode_circle')。 |
| 45 | `             text_color = "#243243" if metric.color == "yellow" else "white" ` | 把结果保存到 text_color：若 metric.color == 'yellow'，用 '#243243'；否则用 'white'。 |
| 46 | `             canvas.create_text(cx, cy-7, text=item.name, fill=text_color, font=("Segoe UI", 12, "bold"), tags=tag) ` | 在画布上画文本；参数：cx, cy - 7, text=item.name, fill=text_color, font=('Segoe UI', 12, 'bold'), tags=tag。 |
| 47 | `             canvas.create_text(cx, cy+16, text="REF" if item.is_reference else str(i+1), fill=text_color, font=("Segoe UI", 9), tags=tag) ` | 在画布上画文本；参数：cx, cy + 16, text='REF' if item.is_reference else str(i + 1), fill=text_color, font=('Segoe UI', 9), tags=tag。 |
| 48 | `             canvas.create_text(cx, cy+radius+14, text={"green":"Within limits", "yellow":"Review", "red":"Check"}[metric.color], ` | 在画布上画文本；参数：cx, cy + radius + 14, text={'green': 'Within limits', 'yellow': 'Review', 'red': 'Check'}[metric.color], fill='#46566A', font=('Segoe UI', 10), t…（完整表达式见左栏）。 |
| 49 | `                                fill="#46566A", font=("Segoe UI", 10), tags=tag) ` | 接续第 48 行的同一条语句，不是另起一段算法。 在画布上画文本；参数：cx, cy + radius + 14, text={'green': 'Within limits', 'yellow': 'Review', 'red': 'Check'}[metric.color], fill='#46566A', font=('Segoe UI', 10), t…（完整表达式见左栏）。 |
| 50 | `             canvas.tag_bind(tag, "<Button-1>", lambda _, electrode=item: self.on_select(electrode)) ` | 给某个画布图元标签绑定事件；参数：tag, '<Button-1>', lambda _, electrode=item: self.on_select(electrode)。 |
| 51 | `             canvas.tag_bind(tag, "<Enter>", lambda _: canvas.configure(cursor="hand2")) ` | 给某个画布图元标签绑定事件；参数：tag, '<Enter>', lambda _: canvas.configure(cursor='hand2')。 |
| 52 | `             canvas.tag_bind(tag, "<Leave>", lambda _: canvas.configure(cursor="")) ` | 给某个画布图元标签绑定事件；参数：tag, '<Leave>', lambda _: canvas.configure(cursor='')。 |
| 53 | `         canvas.configure(scrollregion=(0, 0, width, math.ceil(len(self.electrodes)/columns)*128+10)) ` | 更新控件属性或状态，不计算信号指标；参数：scrollregion=(0, 0, width, math.ceil(len(self.electrodes) / columns) * 128 + 10)。 |
| 54 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 55 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 56 | ` class HeatmapRenderer: ` | 定义 HeatmapRenderer 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 57 | `     """Export the same electrode statuses without needing a Tk window.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 58 | `     def save(self, electrodes, mode, path, title="Electrode QA"): ` | 定义 save(self, electrodes, mode, path, title='Electrode QA')。用 Matplotlib 非交互画布生成同样状态的 PNG。 定义到这里时不执行函数体。 |
| 59 | `         from matplotlib.figure import Figure ` | 从 matplotlib.figure 导入 Figure。不打开主 GUI 也能导出 PNG 图片 |
| 60 | `         from matplotlib.backends.backend_agg import FigureCanvasAgg ` | 从 matplotlib.backends.backend_agg 导入 FigureCanvasAgg。不打开主 GUI 也能导出 PNG 图片 |
| 61 | `         from matplotlib.patches import Circle, Patch ` | 从 matplotlib.patches 导入 Circle、Patch。不打开主 GUI 也能导出 PNG 图片 |
| 62 | `         from matplotlib import font_manager ` | 从 matplotlib 导入 font_manager。不打开主 GUI 也能导出 PNG 图片 |
| 63 | `         installed = {f.name for f in font_manager.fontManager.ttflist} ` | 把结果保存到 installed：从 font_manager.fontManager.ttflist 逐个取 f，为每项生成 f.name。 |
| 64 | `         font = next((f for f in ("Segoe UI", "Arial", "DejaVu Sans") if f in installed), "DejaVu Sans") ` | 把结果保存到 font：取迭代器的下一项或匹配到的第一项；参数：(f for f in ('Segoe UI', 'Arial', 'DejaVu Sans') if f in installed), 'DejaVu Sans'。 |
| 65 | `         n = len(electrodes) ` | 把结果保存到 n：取得元素个数；参数：electrodes。 |
| 66 | `         columns = min(12, max(1, math.ceil(math.sqrt(n*1.5)))) ` | 把结果保存到 columns：取最小值；参数：12, max(1, math.ceil(math.sqrt(n * 1.5)))。 |
| 67 | `         rows = math.ceil(n/columns) ` | 把结果保存到 rows：调用 math.ceil；参数：n / columns。 |
| 68 | `         fig = Figure(figsize=(max(7, columns*1.45), max(4.2, rows*1.5+1.8)), facecolor="#F4F7FA", layout="constrained") ` | 把结果保存到 fig：调用 Figure；参数：figsize=(max(7, columns * 1.45), max(4.2, rows * 1.5 + 1.8)), facecolor='#F4F7FA', layout='constrained'。 |
| 69 | `         FigureCanvasAgg(fig) ` | 调用 FigureCanvasAgg；参数：fig。 |
| 70 | `         ax = fig.add_subplot() ` | 把结果保存到 ax：创建绘图区。 |
| 71 | `         ax.set_aspect("equal") ` | 设置坐标纵横比例；参数：'equal'。 |
| 72 | `         ax.set(xlim=(-.55, columns-.45), ylim=(rows-.4, -.65)) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：xlim=(-0.55, columns - 0.45), ylim=(rows - 0.4, -0.65)。 |
| 73 | `         ax.axis("off") ` | 设置坐标轴显示；参数：'off'。 |
| 74 | `         for i, (row, col) in enumerate(grid_positions(n, columns)): ` | 遍历 enumerate(grid_positions(n, columns))，每次把一项赋给 (i, (row, col))，执行下面缩进的循环体。 |
| 75 | `             item = electrodes[i] ` | 把结果保存到 item：按索引/键 i 取 electrodes 的内容。 |
| 76 | `             color = item.metric(mode).color ` | 把结果保存到 color：读取 item.metric(mode) 的 color 属性。 |
| 77 | `             ax.add_patch(Circle((col, row), .34, facecolor=COLORS[color], edgecolor="white", lw=2)) ` | 在图中加入圆/多边形图元；参数：Circle((col, row), 0.34, facecolor=COLORS[color], edgecolor='white', lw=2)。 |
| 78 | `             text_color = "#243243" if color == "yellow" else "white" ` | 把结果保存到 text_color：若 color == 'yellow'，用 '#243243'；否则用 'white'。 |
| 79 | `             ax.text(col, row-.04, item.name, ha="center", va="center", color=text_color, weight="bold", fontsize=11, fontfamily=font) ` | 给图加入文字；参数：col, row - 0.04, item.name, ha='center', va='center', color=text_color, weight='bold', fontsize=11, fontfamily=font。 |
| 80 | `             ax.text(col, row+.16, "REF" if item.is_reference else str(i+1), ha="center", va="center", color=text_color, fontsize=8) ` | 给图加入文字；参数：col, row + 0.16, 'REF' if item.is_reference else str(i + 1), ha='center', va='center', color=text_color, fontsize=8。 |
| 81 | `             ax.text(col, row+.48, {"green":"Within limits", "yellow":"Review", "red":"Check"}[color], ha="center", va="center", color="#46566A", fontsize=10, fontfamily=font) ` | 给图加入文字；参数：col, row + 0.48, {'green': 'Within limits', 'yellow': 'Review', 'red': 'Check'}[color], ha='center', va='center', color='#46566A', fontsize=10, f…（完整表达式见左栏）。 |
| 82 | `         fig.suptitle(f"{title}\n{n} electrodes · {mode}", fontsize=16, fontfamily=font, color="#243243") ` | 调用 fig.suptitle；参数：f'{title}\n{n} electrodes · {mode}', fontsize=16, fontfamily=font, color='#243243'。 |
| 83 | `         fig.legend(handles=[Patch(color=c, label=COLOR_LABELS[k]) for k, c in COLORS.items()], loc="outside lower center", ` | 调用 fig.legend；参数：handles=[Patch(color=c, label=COLOR_LABELS[k]) for k, c in COLORS.items()], loc='outside lower center', ncol=3, prop={'family': font, 'size': 10}…（完整表达式见左栏）。 |
| 84 | `                    ncol=3, prop={"family":font, "size":10}, frameon=False) ` | 接续第 83 行的同一条语句，不是另起一段算法。 调用 fig.legend；参数：handles=[Patch(color=c, label=COLOR_LABELS[k]) for k, c in COLORS.items()], loc='outside lower center', ncol=3, prop={'family': font, 'size': 10}…（完整表达式见左栏）。 |
| 85 | `         fig.savefig(path, dpi=170) ` | 将图像保存为文件；参数：path, dpi=170。 |
