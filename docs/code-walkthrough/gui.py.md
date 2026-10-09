# gui.py：界面与按钮

创建 Tkinter 窗口，收集用户输入，用后台线程启动分析，并把结果交给热图、时间轴及躯干窗口。这里不直接计算 SQI。

源码：[gui.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py>)。本说明对应 923 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [64–98](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:64>) | 建立应用状态、绑定表单变量、创建界面，并为输入修改注册旧结果失效回调。 |
| `analysis_mode` | [100–101](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:100>) | 把界面可读的工作流名称转换为 bench_sine、bench_pulse 或 ecg。 |
| `button` | [103–106](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:103>) | 创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。 |
| `combo` | [108–111](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:108>) | 创建只读下拉框并登记，便于统一切换可用状态。 |
| `_build` | [113–157](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:113>) | 搭建主窗口、顶部模式选择、可滚动输入栏、结果区和状态栏。 |
| `_build_records` | [159–202](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:159>) | 构建文件列表、每份记录的输入条件、校准确认、项目保存/载入和实验预设。 |
| `_build_results` | [204–303](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:204>) | 构建通道选择、参考、分析范围、窗口设置、运行按钮、热图、结果表和时间轴。 |
| `_build_criteria` | [305–320](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:305>) | 按 CRITERIA 字典生成可滚动的阈值编辑表；改变此处输入会使旧分析结果失效。 |
| `_build_help` | [322–326](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:322>) | 把用户帮助文本写入只读文本框；这段长字符串只用于显示，不执行里面的文字。 |
| `change_profile` | [328–339](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:328>) | 切换工作流后更新指标列表和提示；脉冲移除 SNR/SINAD/THD 选项，然后清空旧结果。 |
| `context_states` | [341–354](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:341>) | 按当前模式和忙碌状态启用/禁用相关控件，ECG 总是使用窗口而不要求同步参考。 |
| `invalidate` | [356–374](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:356>) | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。 |
| `detail_text` | [376–380](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:376>) | 暂时解除详情框只读状态，替换文本后恢复只读。 |
| `suggest_mode` | [382–388](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:382>) | 当导入文件声明为同一类波形时，自动建议对应工作流；名称提示不验证真实波形。 |
| `add_files` | [390–413](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:390>) | 先保存当前表单，再弹出文件选择，建立新记录清单，去重并刷新通道与界面。 |
| `refresh_records` | [415–424](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:415>) | 重新填充文件列表，默认选择第一条，或在空列表时显示无文件。 |
| `select_record` | [426–458](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:426>) | 切换记录时保存上一份编辑，再加载新记录的参数；若它已被分析，切换到该文件自己的结果。 |
| `record_row` | [461–463](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:461>) | 把一份记录转换为列表中的三列：ID、输入 Vpp 和是否已确认。 |
| `apply_record` | [465–493](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:465>) | 把当前输入框转换成合法的 InputRecord；确认框只改变当前文件。 |
| `initialize_channels` | [495–519](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:495>) | 读取第一份文件头，选择实际存在的电压通道，并设置参考和数量。 |
| `update_channel_label` | [521–526](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:521>) | 更新参考下拉框与通道摘要文字。 |
| `apply_count` | [528–538](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:528>) | 把用户填写的数量应用为一组真实通道；数量本身不能创造文件里不存在的电极。 |
| `choose_channels` | [540–567](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:540>) | 打开多选通道对话框；用户确认后更新通道和参考并清除旧结果。 |
| `commit` | [554–564](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:554>) | 保存通道对话框中的选择，然后关闭该对话框。 |
| `remove_record` | [569–576](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:569>) | 从软件的清单中移除选中记录，不删除原始 BDF。 |
| `clear_records` | [578–582](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:578>) | 清空已加载记录及通道状态，不删除硬盘上的数据。 |
| `prepare` | [584–604](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:584>) | 保存待确认的表单编辑，检查参数，选择本次分析范围，并复制输入防止计算期间被修改。 |
| `load_path` | [606–631](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:606>) | 恢复 JSON 项目与躯干显示设置，读取文件头核对，再更新 GUI。 |
| `load_dialog` | [633–636](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:633>) | 弹出 JSON 项目选择框，再调用 load_path。 |
| `load_lab` | [638–653](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:638>) | 根据所选实验预设查找 ZIP，自动选 10 或 128 个通道；输入校准和重复组仍需人工确认。 |
| `save_dialog` | [655–664](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:655>) | 取全部记录及配置，保存项目 JSON；即使分析只选了一份也不丢掉其余记录。 |
| `load_demo` | [666–680](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:666>) | 生成对应模式的合成数据；台架窗口演示使用 10–20 秒幅度故障，随后自动运行。 |
| `set_busy` | [682–695](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:682>) | 分析期间锁定输入并启动进度动画；完成后恢复适用于当前模式的控件。 |
| `run` | [697–715](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:697>) | 取得固定的分析请求，启动后台工作线程，再安排主线程轮询消息。 |
| `worker` | [706–711](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:706>) | 后台调用 AnalysisService，只向队列写进度/成功/错误，不直接操作 Tk 控件。 |
| `poll` | [717–733](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:717>) | 主线程取队列消息，更新进度或接收结果；忙碌时 80 ms 后再次检查。 |
| `accept_result` | [735–758](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:735>) | 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。 |
| `label_for_record` | [760–761](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:760>) | 找到某个记录 ID 对应的显示范围名称。 |
| `change_scope` | [763–776](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:763>) | 用户选择整段/窗口/整批时暂停播放，同步文件选择，再刷新显示。 |
| `select_window` | [778–787](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:778>) | 将时间轴提供的全局窗口索引映射到显示范围，并同步主窗口和躯干窗口。 |
| `displayed_electrodes` | [789–797](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:789>) | 只取当前整段、窗口或整批范围的电极结果；这个函数不重新算指标。 |
| `update_timeline` | [799–821](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:799>) | 按记录和指标缓存窗口最差颜色，并传给时间轴；同步项不把参考自比较算成警告。 |
| `redraw` | [823–845](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:823>) | 从已有结果更新热图、躯干、颜色计数、结果表和详情。 |
| `show_detail` | [847–879](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:847>) | 显示当前通道的颜色、原因、原始指标值及来源窗口/记录，并同步躯干详情。 |
| `open_torso` | [881–890](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:881>) | 打开或抬起躯干窗口，连接选择回调，与主窗口共享指标和窗口结果。 |
| `set_torso_layout` | [892–893](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:892>) | 保存用户调整的示意位置方向，不改变信号数据或质量分数。 |
| `select_result` | [895–898](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:895>) | 把结果表选中的行变成当前电极，再切回热图页。 |
| `export` | [900–919](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py:900>) | 暂停回放，选择输出文件夹，导出当前视图及完整结果；躯干窗口打开时同时保存其图片和布局。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """English two-stage desktop app. Algorithms are separate, GUI-independent classes.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import asdict ` | 从 dataclasses 导入 asdict。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 4 | ` import copy ` | 导入模块 copy。复制本次分析参数以隔离界面修改 |
| 5 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 6 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 7 | ` import queue ` | 导入模块 queue。在线程间安全传递消息 |
| 8 | ` import threading ` | 导入模块 threading。让耗时分析在后台执行 |
| 9 | ` import tkinter as tk ` | 导入模块 tkinter（别名 tk）。桌面窗口、控件、文件选择框和消息框 |
| 10 | ` from tkinter import ttk, filedialog, messagebox ` | 从 tkinter 导入 ttk、filedialog、messagebox。桌面窗口、控件、文件选择框和消息框 |
| 11 | ` from config import AnalysisSettings, COLORS, COLOR_LABELS, BENCH_VIEWS, ECG_VIEWS ` | 从 config 导入 AnalysisSettings、COLORS、COLOR_LABELS、BENCH_VIEWS、ECG_VIEWS。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 12 | ` from services.analysis_service import AnalysisService ` | 从 services.analysis_service 导入 AnalysisService。验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 |
| 13 | ` from services.demo_data import create_mode_demo, create_timeline_demo ` | 从 services.demo_data 导入 create_mode_demo、create_timeline_demo。生成已知故障的合成 BDF：幅度偏差、延迟、非线性、重复变化、ECG 漂移、平线、噪声。演示标签不是实验验证结论。 |
| 14 | ` from utils.bdf_reader import BdfReader ` | 从 utils.bdf_reader 导入 BdfReader。检查头信息、真实通道及长度，支持 ZIP 内部成员，并通过上下文管理大数组的生命周期。 |
| 15 | ` from utils.input_catalog import records_from_paths ` | 从 utils.input_catalog 导入 records_from_paths。枚举 BDF 或 ZIP 中的 BDF；从名称猜测波形、频率、幅度，但默认 input_confirmed=False。 |
| 16 | ` from utils.project_io import UNIT_FACTORS, load_project, save_project ` | 从 utils.project_io 导入 UNIT_FACTORS、load_project、save_project。保存文件清单、参数、通道和参考；恢复时适配部分旧配置，并统一幅度单位。保存的是配置，不是复制原始 BDF。 |
| 17 | ` from utils.report_exporter import ReportExporter ` | 从 utils.report_exporter 导入 ReportExporter。生成当前视图的 PNG/CSV，以及完整 JSON、项目配置、各窗口和过零事件表、HTML 报告。 |
| 18 | ` from views.heatmap_view import HeatmapView ` | 从 views.heatmap_view 导入 HeatmapView。读取计算完成的颜色，画可点击圆点；另有不依赖 Tk 窗口的 PNG 导出器。网格顺序不是身体坐标。 |
| 19 | ` from views.timeline_view import TimelineView ` | 从 views.timeline_view 导入 TimelineView。管理已有窗口结果的滑块、播放/暂停、前后跳转、下一个提醒；不会在播放时重新分析样本。 |
| 20 | ` from views.torso_geometry import TorsoLayout ` | 从 views.torso_geometry 导入 TorsoLayout。生成示意躯干网格和 A1–D32 位置，再做三维到二维的投影；这些坐标不是 CT 重建或患者实测坐标。 |
| 21 | ` from views.torso_window import TorsoWindow ` | 从 views.torso_window 导入 TorsoWindow。把躯干、指标选择、提醒列表、详情及时间轴组合成第二窗口，与主窗口使用同一份结果。 |
| 22 | ` HERE = Path(__file__).resolve().parent ` | 把结果保存到 HERE：读取 Path(__file__).resolve() 的 parent 属性。 |
| 23 | ` PROFILES = {'Stage 1 - Bench / Sine': 'bench_sine', ` | 把结果保存到 PROFILES：组装字典，键用于给数值/设置命名：{'Stage 1 - Bench / Sine': 'bench_sine', 'Stage 1 - Bench / Pulse': 'bench_pulse', 'Stage 2 - ECG quality': 'ecg'}。 |
| 24 | `  'Stage 1 - Bench / Pulse': 'bench_pulse', ` | 接续第 23 行的同一条语句，不是另起一段算法。 把结果保存到 PROFILES：组装字典，键用于给数值/设置命名：{'Stage 1 - Bench / Sine': 'bench_sine', 'Stage 1 - Bench / Pulse': 'bench_pulse', 'Stage 2 - ECG quality': 'ecg'}。 |
| 25 | `  'Stage 2 - ECG quality': 'ecg'} ` | 接续第 23 行的同一条语句，不是另起一段算法。 把结果保存到 PROFILES：组装字典，键用于给数值/设置命名：{'Stage 1 - Bench / Sine': 'bench_sine', 'Stage 1 - Bench / Pulse': 'bench_pulse', 'Stage 2 - ECG quality': 'ecg'}。 |
| 26 | ` CRITERIA = {'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', ` | 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 27 | `  'gain_limit_pct': 'Gain error limit (%)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 28 | `  'linearity_limit_pct': 'Linearity (% of input span)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 29 | `  'sync_delay_limit_ms': 'Event delay P95 (ms)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 30 | `  'sync_jitter_limit_ms': 'Event jitter (ms)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 31 | `  'repeat_cv_limit_pct': 'Repeat amplitude/gain CV (%)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 32 | `  'repeat_delay_sd_limit_ms': 'Between-run delay SD (ms)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 33 | `  'min_repeat_runs': 'Minimum independent repeat runs', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 34 | `  'frequency_limit_pct': 'Frequency error (%) - blank: uncalibrated', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 35 | `  'thd_limit_pct': 'THD (%) - blank: uncalibrated', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 36 | `  'snr_good_db': 'SNR good boundary (dB)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 37 | `  'snr_bad_db': 'SNR bad boundary (dB)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 38 | `  'bench_bandwidth_hz': 'Noise measurement bandwidth (Hz)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 39 | `  'harmonic_count': 'Highest fitted harmonic order', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 40 | `  'max_residual_pct': 'Sine residual gate (% of fundamental RMS)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 41 | `  'max_residual_step_pct': 'Residual step gate (% of Vpp)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 42 | `  'min_cycles': 'Minimum bench signal cycles', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 43 | `  'frequency_search_pct': 'Frequency search range (+/- %)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 44 | `  'bench_window_s': 'Bench window duration (s)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 45 | `  'bench_hop_s': 'Bench window step (s)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 46 | `  'ecg_window_s': 'ECG window duration (s)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 47 | `  'ecg_hop_s': 'ECG window step (s)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 48 | `  'ecg_match_ms': 'Beat matching tolerance (ms)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 49 | `  'ecg_min_beats': 'Minimum beats per detector', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 50 | `  'bsqi_good': 'bSQI good boundary (strictly greater)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 51 | `  'bsqi_bad': 'bSQI bad boundary', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 52 | `  'psqi_low': 'pSQI good range - lower', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 53 | `  'psqi_high': 'pSQI good range - upper', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 54 | `  'psqi_bad': 'pSQI bad lower boundary', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 55 | `  'ksqi_min': 'Pearson kurtosis good boundary (strictly greater)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 56 | `  'bassqi_good': 'basSQI good boundary', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 57 | `  'bassqi_bad': 'basSQI bad boundary', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 58 | `  'flatline_s': 'Sustained near-flat duration (s)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 59 | `  'flat_epsilon_uV': 'Near-flat sample difference (uV)', ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 60 | `  'warning_fraction': 'Warning fraction of upper limits (0 to 1)'} ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 CRITERIA：组装字典，键用于给数值/设置命名：{'exclude_last_s': 'Exclude final seconds per file (0 = keep all)', 'gain_limit_pct': 'Gain error limit (%)', 'linearity_limit_pct': 'Linearity (% of input span…（完整表达式见左栏）。 |
| 61 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 62 | ` class ElectrodeQAApp: ` | 定义 ElectrodeQAApp 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 63 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 64 | `     def __init__(self, root): ` | 定义 __init__(self, root)。建立应用状态、绑定表单变量、创建界面，并为输入修改注册旧结果失效回调。 定义到这里时不执行函数体。 |
| 65 | `         self.root = root ` | 把结果保存到 self.root：root。 |
| 66 | `         self.records, self.channels = ([], []) ` | 把结果保存到 (self.records, self.channels)：组装元组：([], [])。 |
| 67 | `         self.settings = AnalysisSettings(bench_windows=True) ` | 创建当前 GUI 的初始设置，并显式开启台架窗口；数据类自身的默认 bench_windows 是 False。 |
| 68 | `         self.info = self.selected = self.result = None ` | 把结果保存到 self.info、self.selected、self.result：None（未知/未设置）。 |
| 69 | `         self.busy = self.loading = False ` | 把结果保存到 self.busy、self.loading：False（否）。 |
| 70 | `         self.events = queue.Queue() ` | 创建线程安全消息队列；后台放进度/结果，主线程取出来更新界面。 |
| 71 | `         self.controls, self.combos, self.bench_controls = ([], [], []) ` | 把结果保存到 (self.controls, self.combos, self.bench_controls)：组装元组：([], [], [])。 |
| 72 | `         self.count = tk.StringVar(value='8') ` | 把结果保存到 self.count：创建可绑定控件的文本变量；参数：value='8'。 |
| 73 | `         self.pool = tk.StringVar(value='scalp') ` | 把结果保存到 self.pool：创建可绑定控件的文本变量；参数：value='scalp'。 |
| 74 | `         self.reference = tk.StringVar() ` | 把结果保存到 self.reference：创建可绑定控件的文本变量。 |
| 75 | `         self.profile = tk.StringVar(value=next(iter(PROFILES))) ` | 把结果保存到 self.profile：创建可绑定控件的文本变量；参数：value=next(iter(PROFILES))。 |
| 76 | `         self.mode = tk.StringVar(value='Bench summary') ` | 把结果保存到 self.mode：创建可绑定控件的文本变量；参数：value='Bench summary'。 |
| 77 | `         self.scope = tk.StringVar(value='Not analyzed') ` | 把结果保存到 self.scope：创建可绑定控件的文本变量；参数：value='Not analyzed'。 |
| 78 | `         self.analysis_target = tk.StringVar(value='Selected record') ` | 把结果保存到 self.analysis_target：创建可绑定控件的文本变量；参数：value='Selected record'。 |
| 79 | `         self.windowed = tk.BooleanVar(value=self.settings.bench_windows) ` | 把结果保存到 self.windowed：创建可绑定控件的布尔变量；参数：value=self.settings.bench_windows。 |
| 80 | `         self.focused_electrode = None ` | 把结果保存到 self.focused_electrode：None（未知/未设置）。 |
| 81 | `         self.timeline_cache = {} ` | 把结果保存到 self.timeline_cache：组装字典，键用于给数值/设置命名：{}。 |
| 82 | `         self.torso_window = None ` | 把结果保存到 self.torso_window：None（未知/未设置）。 |
| 83 | `         self.torso_layout = TorsoLayout() ` | 把结果保存到 self.torso_layout：创建躯干示意方向设置。 |
| 84 | `         self.status = tk.StringVar(value='Open BDF or ZIP files. Verify the declared waveform and connected channels.') ` | 把结果保存到 self.status：创建可绑定控件的文本变量；参数：value='Open BDF or ZIP files. Verify the declared waveform and connected channels.'。 |
| 85 | `         self.summary = tk.StringVar(value='Not analyzed') ` | 把结果保存到 self.summary：创建可绑定控件的文本变量；参数：value='Not analyzed'。 |
| 86 | `         self.source_label = tk.StringVar(value='No BDF selected') ` | 把结果保存到 self.source_label：创建可绑定控件的文本变量；参数：value='No BDF selected'。 |
| 87 | `         self.hint = tk.StringVar() ` | 把结果保存到 self.hint：创建可绑定控件的文本变量。 |
| 88 | `         self.lab_choice = tk.StringVar(value='10 electrodes - Sine') ` | 把结果保存到 self.lab_choice：创建可绑定控件的文本变量；参数：value='10 electrodes - Sine'。 |
| 89 | `         self.record_vars = {k: tk.StringVar() for k in ('frequency', 'amplitude', 'unit', 'repeat', 'setup', 'waveform')} ` | 把结果保存到 self.record_vars：从 ('frequency', 'amplitude', 'unit', 'repeat', 'setup', 'waveform') 逐个取 k，为每项生成 k: tk.StringVar()。 |
| 90 | `         self.confirmed = tk.BooleanVar(value=False) ` | 把结果保存到 self.confirmed：创建可绑定控件的布尔变量；参数：value=False。 |
| 91 | `         self.sweep = tk.BooleanVar(value=True) ` | 把结果保存到 self.sweep：创建可绑定控件的布尔变量；参数：value=True。 |
| 92 | `         self.limit_vars = {k: tk.StringVar(value='' if getattr(self.settings, k) is None else str(getattr(self.settings, k))) for k in CRITERIA} ` | 把结果保存到 self.limit_vars：从 CRITERIA 逐个取 k，为每项生成 k: tk.StringVar(value='' if getattr(self.settings, k) is None else str(getattr(self.settings, k)))。 |
| 93 | `         self.frame_labels = ['Not analyzed'] ` | 把结果保存到 self.frame_labels：组装列表：['Not analyzed']。 |
| 94 | `         self.result_scopes = {} ` | 把结果保存到 self.result_scopes：组装字典，键用于给数值/设置命名：{}。 |
| 95 | `         self._build() ` | 搭建主窗口、顶部模式选择、可滚动输入栏、结果区和状态栏。。 |
| 96 | `         for variable in (*self.record_vars.values(), self.confirmed, self.sweep, self.windowed, *self.limit_vars.values(), self.count, self.pool, self.reference): ` | 遍历 (*self.record_vars.values(), self.confirmed, self.sweep, self.windowed, *self.limit_vars.values(), self.count, self.pool, self.reference)，每次把一项赋给 variable，执行下面缩进的循环体。 |
| 97 | `             variable.trace_add('write', self.invalidate) ` | 监听界面变量变化，并在改变时调用指定处理函数；参数：'write', self.invalidate。 |
| 98 | `         self.change_profile() ` | 切换工作流后更新指标列表和提示；脉冲移除 SNR/SINAD/THD 选项，然后清空旧结果。。 |
| 99 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 100 | `     def analysis_mode(self): ` | 定义 analysis_mode(self)。把界面可读的工作流名称转换为 bench_sine、bench_pulse 或 ecg。 定义到这里时不执行函数体。 |
| 101 | `         return PROFILES[self.profile.get()] ` | 结束当前函数并返回：按索引/键 self.profile.get() 取 PROFILES 的内容。 |
| 102 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 103 | `     def button(self, parent, text, callback): ` | 定义 button(self, parent, text, callback)。创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。 定义到这里时不执行函数体。 |
| 104 | `         w = ttk.Button(parent, text=text, command=callback) ` | 把结果保存到 w：创建按钮；参数：parent, text=text, command=callback。 |
| 105 | `         self.controls.append(w) ` | 把一项加入列表末尾；参数：w。 |
| 106 | `         return w ` | 结束当前函数并返回：w。 |
| 107 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 108 | `     def combo(self, parent, variable, values, width=18): ` | 定义 combo(self, parent, variable, values, width=18)。创建只读下拉框并登记，便于统一切换可用状态。 定义到这里时不执行函数体。 |
| 109 | `         w = ttk.Combobox(parent, textvariable=variable, values=values, width=width, state='readonly') ` | 把结果保存到 w：创建下拉选择框；参数：parent, textvariable=variable, values=values, width=width, state='readonly'。 |
| 110 | `         self.combos.append(w) ` | 把一项加入列表末尾；参数：w。 |
| 111 | `         return w ` | 结束当前函数并返回：w。 |
| 112 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 113 | `     def _build(self): ` | 定义 _build(self)。搭建主窗口、顶部模式选择、可滚动输入栏、结果区和状态栏。 定义到这里时不执行函数体。 |
| 114 | `         self.root.title('Electrode QA \| Bench validation + ECG quality') ` | 调用 self.root.title；参数：'Electrode QA &#124; Bench validation + ECG quality'。 |
| 115 | `         height = min(950, self.root.winfo_screenheight() - 90) ` | 把结果保存到 height：取最小值；参数：950, self.root.winfo_screenheight() - 90。 |
| 116 | `         self.root.geometry(f'1400x{height}') ` | 调用 self.root.geometry；参数：f'1400x{height}'。 |
| 117 | `         self.root.minsize(1180, 820) ` | 调用 self.root.minsize；参数：1180, 820。 |
| 118 | `         style = ttk.Style(self.root) ` | 把结果保存到 style：创建主题样式管理器；参数：self.root。 |
| 119 | `         style.theme_use('clam') ` | 调用 style.theme_use；参数：'clam'。 |
| 120 | `         for name in ('TFrame', 'TLabel', 'TLabelframe', 'TCheckbutton'): ` | 遍历 ('TFrame', 'TLabel', 'TLabelframe', 'TCheckbutton')，每次把一项赋给 name，执行下面缩进的循环体。 |
| 121 | `             style.configure(name, background='#F4F7FA') ` | 更新控件属性或状态，不计算信号指标；参数：name, background='#F4F7FA'。 |
| 122 | `         style.configure('TLabel', foreground='#243243', font=('Segoe UI', 10)) ` | 更新控件属性或状态，不计算信号指标；参数：'TLabel', foreground='#243243', font=('Segoe UI', 10)。 |
| 123 | `         style.configure('TButton', padding=(8, 5), font=('Segoe UI', 10)) ` | 更新控件属性或状态，不计算信号指标；参数：'TButton', padding=(8, 5), font=('Segoe UI', 10)。 |
| 124 | `         style.configure('Treeview', rowheight=26, font=('Segoe UI', 9)) ` | 更新控件属性或状态，不计算信号指标；参数：'Treeview', rowheight=26, font=('Segoe UI', 9)。 |
| 125 | `         header = tk.Frame(self.root, bg='#182B3A', padx=20, pady=12) ` | 把结果保存到 header：创建布局容器；参数：self.root, bg='#182B3A', padx=20, pady=12。 |
| 126 | `         header.pack(fill='x') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 127 | `         tk.Label(header, text='Electrode QA', bg='#182B3A', fg='white', font=('Segoe UI', 22, 'bold')).pack(side='left') ` | 创建文字标签；参数：header, text='Electrode QA', bg='#182B3A', fg='white', font=('Segoe UI', 22, 'bold')；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 128 | `         tk.Label(header, text='Known-input validation / ECG quality screening', bg='#182B3A', fg='#BECDD9', font=('Segoe UI', 12)).pack(side='left', padx=25) ` | 创建文字标签；参数：header, text='Known-input validation / ECG quality screening', bg='#182B3A', fg='#BECDD9', font=('Segoe UI', 12)；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=25。 |
| 129 | `         flow = ttk.Frame(self.root, padding=(18, 10)) ` | 把结果保存到 flow：创建布局容器；参数：self.root, padding=(18, 10)。 |
| 130 | `         flow.pack(fill='x') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 131 | `         ttk.Label(flow, text='Analysis workflow').pack(side='left') ` | 创建文字标签；参数：flow, text='Analysis workflow'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 132 | `         w = self.combo(flow, self.profile, list(PROFILES), 32) ` | 把结果保存到 w：创建只读下拉框并登记，便于统一切换可用状态。；参数：flow, self.profile, list(PROFILES), 32。 |
| 133 | `         w.pack(side='left', padx=10) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=10。 |
| 134 | `         w.bind('<<ComboboxSelected>>', self.change_profile) ` | 绑定界面事件，事件发生时才执行回调；参数：'<<ComboboxSelected>>', self.change_profile。 |
| 135 | `         ttk.Label(flow, textvariable=self.hint, wraplength=830, foreground='#526A7A').pack(side='left', padx=10) ` | 创建文字标签；参数：flow, textvariable=self.hint, wraplength=830, foreground='#526A7A'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=10。 |
| 136 | `         body = ttk.Frame(self.root, padding=(14, 0, 14, 8)) ` | 把结果保存到 body：创建布局容器；参数：self.root, padding=(14, 0, 14, 8)。 |
| 137 | `         body.pack(fill='both', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 138 | `         # Scroll the input column on smaller screens instead of clipping controls. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 139 | `         left_shell = ttk.Frame(body, width=430) ` | 把结果保存到 left_shell：创建布局容器；参数：body, width=430。 |
| 140 | `         left_shell.pack(side='left', fill='y', padx=(0, 14)) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', fill='y', padx=(0, 14)。 |
| 141 | `         left_shell.pack_propagate(False) ` | 调用 left_shell.pack_propagate；参数：False。 |
| 142 | `         input_canvas = tk.Canvas(left_shell, width=410, bg='#F4F7FA', highlightthickness=0) ` | 把结果保存到 input_canvas：创建绘图画布；参数：left_shell, width=410, bg='#F4F7FA', highlightthickness=0。 |
| 143 | `         input_scroll = ttk.Scrollbar(left_shell, orient='vertical', command=input_canvas.yview) ` | 把结果保存到 input_scroll：创建滚动条；参数：left_shell, orient='vertical', command=input_canvas.yview。 |
| 144 | `         input_canvas.configure(yscrollcommand=input_scroll.set) ` | 更新控件属性或状态，不计算信号指标；参数：yscrollcommand=input_scroll.set。 |
| 145 | `         input_scroll.pack(side='right', fill='y') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='right', fill='y'。 |
| 146 | `         input_canvas.pack(side='left', fill='both', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', fill='both', expand=True。 |
| 147 | `         left = ttk.Frame(input_canvas, width=410) ` | 把结果保存到 left：创建布局容器；参数：input_canvas, width=410。 |
| 148 | `         input_window = input_canvas.create_window((0, 0), window=left, anchor='nw') ` | 把结果保存到 input_window：把一个控件嵌入 Canvas 的指定位置；参数：(0, 0), window=left, anchor='nw'。 |
| 149 | `         left.bind('<Configure>', lambda _: input_canvas.configure(scrollregion=input_canvas.bbox('all'))) ` | 绑定界面事件，事件发生时才执行回调；参数：'<Configure>', lambda _: input_canvas.configure(scrollregion=input_canvas.bbox('all'))。 |
| 150 | `         input_canvas.bind('<Configure>', lambda e: input_canvas.itemconfigure(input_window, width=e.width)) ` | 绑定界面事件，事件发生时才执行回调；参数：'<Configure>', lambda e: input_canvas.itemconfigure(input_window, width=e.width)。 |
| 151 | `         input_canvas.bind('<MouseWheel>', lambda e: input_canvas.yview_scroll(-int(e.delta/120), 'units')) ` | 绑定界面事件，事件发生时才执行回调；参数：'<MouseWheel>', lambda e: input_canvas.yview_scroll(-int(e.delta / 120), 'units')。 |
| 152 | `         right = ttk.Frame(body) ` | 把结果保存到 right：创建布局容器；参数：body。 |
| 153 | `         right.pack(side='left', fill='both', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', fill='both', expand=True。 |
| 154 | `         self._build_records(left) ` | 构建文件列表、每份记录的输入条件、校准确认、项目保存/载入和实验预设。；参数：left。 |
| 155 | `         self._build_results(right) ` | 构建通道选择、参考、分析范围、窗口设置、运行按钮、热图、结果表和时间轴。；参数：right。 |
| 156 | `         self.status_label = ttk.Label(self.root, textvariable=self.status, padding=(18, 8), wraplength=1100) ` | 把结果保存到 self.status_label：创建文字标签；参数：self.root, textvariable=self.status, padding=(18, 8), wraplength=1100。 |
| 157 | `         self.status_label.pack(side='bottom', fill='x', before=body) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='bottom', fill='x', before=body。 |
| 158 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 159 | `     def _build_records(self, parent): ` | 定义 _build_records(self, parent)。构建文件列表、每份记录的输入条件、校准确认、项目保存/载入和实验预设。 定义到这里时不执行函数体。 |
| 160 | `         ttk.Label(parent, text='01  Records and input', font=('Segoe UI', 13, 'bold')).pack(anchor='w') ` | 创建文字标签；参数：parent, text='01  Records and input', font=('Segoe UI', 13, 'bold')；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w'。 |
| 161 | `         bar = ttk.Frame(parent) ` | 把结果保存到 bar：创建布局容器；参数：parent。 |
| 162 | `         bar.pack(fill='x', pady=7) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=7。 |
| 163 | `         for title, fn in (('Open BDF / ZIP', self.add_files), ('Remove', self.remove_record), ('Clear', self.clear_records)): ` | 遍历 (('Open BDF / ZIP', self.add_files), ('Remove', self.remove_record), ('Clear', self.clear_records))，每次把一项赋给 (title, fn)，执行下面缩进的循环体。 |
| 164 | `             self.button(bar, title, fn).pack(side='left', padx=(0, 5)) ` | 创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。；参数：bar, title, fn；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=(0, 5)。 |
| 165 | `         self.record_tree = ttk.Treeview(parent, columns=('file', 'input', 'verified'), show='headings', height=5, selectmode='browse') ` | 把结果保存到 self.record_tree：创建表格/列表；参数：parent, columns=('file', 'input', 'verified'), show='headings', height=5, selectmode='browse'。 |
| 166 | `         for key, title, width in (('file', 'Record', 245), ('input', 'mVpp', 60), ('verified', 'Verified', 65)): ` | 遍历 (('file', 'Record', 245), ('input', 'mVpp', 60), ('verified', 'Verified', 65))，每次把一项赋给 (key, title, width)，执行下面缩进的循环体。 |
| 167 | `             self.record_tree.heading(key, text=title) ` | 设置表格列标题；参数：key, text=title。 |
| 168 | `             self.record_tree.column(key, width=width) ` | 设置表格列宽等属性或按该类定义取信号列；参数：key, width=width。 |
| 169 | `         self.record_tree.pack(fill='x') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 170 | `         self.record_tree.bind('<<TreeviewSelect>>', self.select_record) ` | 绑定界面事件，事件发生时才执行回调；参数：'<<TreeviewSelect>>', self.select_record。 |
| 171 | `         ttk.Label(parent, textvariable=self.source_label, wraplength=395, foreground='#657588').pack(anchor='w', pady=5) ` | 创建文字标签；参数：parent, textvariable=self.source_label, wraplength=395, foreground='#657588'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w', pady=5。 |
| 172 | `         form = ttk.LabelFrame(parent, text='Selected record - verify filename suggestions', padding=8) ` | 把结果保存到 form：创建带标题的分组框；参数：parent, text='Selected record - verify filename suggestions', padding=8。 |
| 173 | `         form.pack(fill='x', pady=5) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=5。 |
| 174 | `         fields = (('waveform', 'Declared waveform'), ('setup', 'Physical setup group'), ('frequency', 'Input frequency (Hz)'), ('amplitude', 'Actual input amplitude'), ('repeat', 'Independent repeat group')) ` | 把结果保存到 fields：组装元组：(('waveform', 'Declared waveform'), ('setup', 'Physical setup group'), ('frequency', 'Input frequency (Hz)'), ('amplitude', 'Actual input amplitude'), ('repeat'…（完整表达式见左栏）。 |
| 175 | `         for row, (key, title) in enumerate(fields): ` | 遍历 enumerate(fields)，每次把一项赋给 (row, (key, title))，执行下面缩进的循环体。 |
| 176 | `             ttk.Label(form, text=title).grid(row=row, column=0, sticky='w', pady=4) ` | 创建文字标签；参数：form, text=title；随后按 row/column 放置控件；sticky 决定靠边或拉伸；参数：row=row, column=0, sticky='w', pady=4。 |
| 177 | `             if key == 'waveform': ` | 检查条件 key == 'waveform'；为真时执行下面缩进的一组语句。 |
| 178 | `                 w = self.combo(form, self.record_vars[key], ('unknown', 'sine', 'pulse', 'ecg'), 13) ` | 把结果保存到 w：创建只读下拉框并登记，便于统一切换可用状态。；参数：form, self.record_vars[key], ('unknown', 'sine', 'pulse', 'ecg'), 13。 |
| 179 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 180 | `                 w = ttk.Entry(form, textvariable=self.record_vars[key], width=16) ` | 把结果保存到 w：创建单行输入框；参数：form, textvariable=self.record_vars[key], width=16。 |
| 181 | `                 self.controls.append(w) ` | 把一项加入列表末尾；参数：w。 |
| 182 | `             w.grid(row=row, column=1, sticky='ew', padx=5) ` | 按 row/column 放置控件；sticky 决定靠边或拉伸；参数：row=row, column=1, sticky='ew', padx=5。 |
| 183 | `             if key in ('frequency', 'amplitude', 'repeat'): ` | 检查条件 key in ('frequency', 'amplitude', 'repeat')；为真时执行下面缩进的一组语句。 |
| 184 | `                 self.bench_controls.append(w) ` | 把一项加入列表末尾；参数：w。 |
| 185 | `         self.unit_combo = self.combo(form, self.record_vars['unit'], list(UNIT_FACTORS), 8) ` | 把结果保存到 self.unit_combo：创建只读下拉框并登记，便于统一切换可用状态。；参数：form, self.record_vars['unit'], list(UNIT_FACTORS), 8。 |
| 186 | `         self.unit_combo.grid(row=3, column=2) ` | 按 row/column 放置控件；sticky 决定靠边或拉伸；参数：row=3, column=2。 |
| 187 | `         self.bench_controls.append(self.unit_combo) ` | 把一项加入列表末尾；参数：self.unit_combo。 |
| 188 | `         for row, title, var in ((5, 'Input Vpp and units verified for THIS record', self.confirmed), (6, 'Include in linearity sweep', self.sweep)): ` | 遍历 ((5, 'Input Vpp and units verified for THIS record', self.confirmed), (6, 'Include in linearity sweep', self.sweep))，每次把一项赋给 (row, title, var)，执行下面缩进的循环体。 |
| 189 | `             w = ttk.Checkbutton(form, text=title, variable=var) ` | 把结果保存到 w：创建勾选框；参数：form, text=title, variable=var。 |
| 190 | `             w.grid(row=row, column=0, columnspan=3, sticky='w', pady=3) ` | 按 row/column 放置控件；sticky 决定靠边或拉伸；参数：row=row, column=0, columnspan=3, sticky='w', pady=3。 |
| 191 | `             self.controls.append(w) ` | 把一项加入列表末尾；参数：w。 |
| 192 | `             self.bench_controls.append(w) ` | 把一项加入列表末尾；参数：w。 |
| 193 | `         self.button(form, 'Apply record', self.apply_record).grid(row=7, column=0, sticky='w', pady=4) ` | 创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。；参数：form, 'Apply record', self.apply_record；随后按 row/column 放置控件；sticky 决定靠边或拉伸；参数：row=7, column=0, sticky='w', pady=4。 |
| 194 | `         bar = ttk.Frame(parent) ` | 把结果保存到 bar：创建布局容器；参数：parent。 |
| 195 | `         bar.pack(fill='x', pady=8) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=8。 |
| 196 | `         for title, fn in (('Load project', self.load_dialog), ('Save project', self.save_dialog), ('Demo', self.load_demo)): ` | 遍历 (('Load project', self.load_dialog), ('Save project', self.save_dialog), ('Demo', self.load_demo))，每次把一项赋给 (title, fn)，执行下面缩进的循环体。 |
| 197 | `             self.button(bar, title, fn).pack(side='left', padx=(0, 5)) ` | 创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。；参数：bar, title, fn；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=(0, 5)。 |
| 198 | `         lab = ttk.LabelFrame(parent, text='Latest lab presets', padding=8) ` | 把结果保存到 lab：创建带标题的分组框；参数：parent, text='Latest lab presets', padding=8。 |
| 199 | `         lab.pack(fill='x', pady=5) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=5。 |
| 200 | `         self.combo(lab, self.lab_choice, ('10 electrodes - Sine', '128 electrodes - Sine', '128 electrodes - Pulse', '10 electrodes - ECG'), 24).pack(side='left') ` | 创建只读下拉框并登记，便于统一切换可用状态。；参数：lab, self.lab_choice, ('10 electrodes - Sine', '128 electrodes - Sine', '128 electrodes - Pulse', '10 electrodes - ECG'), 24；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 201 | `         self.button(lab, 'Load', self.load_lab).pack(side='left', padx=8) ` | 创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。；参数：lab, 'Load', self.load_lab；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=8。 |
| 202 | `         ttk.Label(parent, text='Presets select A1-A10 or A1-D32. Verify the physical wiring.\n\nRepeated cycles are not independent runs. A generator setting or plot scale does not confirm actual input Vpp.', wraplength=395, foreground='#657588').pack(anchor='w', pady=8) ` | 创建文字标签；参数：parent, text='Presets select A1-A10 or A1-D32. Verify the physical wiring.\n\nRepeated cycles are not independent runs. A generator setting or pl…（完整表达式见左栏）；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w', pady=8。 |
| 203 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 204 | `     def _build_results(self, parent): ` | 定义 _build_results(self, parent)。构建通道选择、参考、分析范围、窗口设置、运行按钮、热图、结果表和时间轴。 定义到这里时不执行函数体。 |
| 205 | `         ttk.Label(parent, text='02  Channels and analysis', font=('Segoe UI', 13, 'bold')).pack(anchor='w') ` | 创建文字标签；参数：parent, text='02  Channels and analysis', font=('Segoe UI', 13, 'bold')；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w'。 |
| 206 | `         row = ttk.Frame(parent) ` | 把结果保存到 row：创建布局容器；参数：parent。 |
| 207 | `         row.pack(fill='x', pady=7) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=7。 |
| 208 | `         ttk.Label(row, text='Group').pack(side='left') ` | 创建文字标签；参数：row, text='Group'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 209 | `         self.combo(row, self.pool, ('scalp', 'EXG', 'all'), 7).pack(side='left', padx=5) ` | 创建只读下拉框并登记，便于统一切换可用状态。；参数：row, self.pool, ('scalp', 'EXG', 'all'), 7；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=5。 |
| 210 | `         ttk.Label(row, text='Count').pack(side='left') ` | 创建文字标签；参数：row, text='Count'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 211 | `         w = ttk.Spinbox(row, from_=1, to=4096, textvariable=self.count, width=5) ` | 把结果保存到 w：创建可加减的数字输入框；参数：row, from_=1, to=4096, textvariable=self.count, width=5。 |
| 212 | `         w.pack(side='left', padx=5) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=5。 |
| 213 | `         self.controls.append(w) ` | 把一项加入列表末尾；参数：w。 |
| 214 | `         self.button(row, 'Apply count', self.apply_count).pack(side='left') ` | 创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。；参数：row, 'Apply count', self.apply_count；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 215 | `         self.button(row, 'Choose channels', self.choose_channels).pack(side='left', padx=5) ` | 创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。；参数：row, 'Choose channels', self.choose_channels；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=5。 |
| 216 | `         ttk.Label(row, text='Timing ref.').pack(side='left') ` | 创建文字标签；参数：row, text='Timing ref.'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 217 | `         self.ref_combo = self.combo(row, self.reference, (), 8) ` | 把结果保存到 self.ref_combo：创建只读下拉框并登记，便于统一切换可用状态。；参数：row, self.reference, (), 8。 |
| 218 | `         self.ref_combo.pack(side='left', padx=5) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=5。 |
| 219 | `         self.channel_label = ttk.Label(parent, text='No channels selected', wraplength=870, foreground='#657588') ` | 把结果保存到 self.channel_label：创建文字标签；参数：parent, text='No channels selected', wraplength=870, foreground='#657588'。 |
| 220 | `         self.channel_label.pack(anchor='w', pady=4) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w', pady=4。 |
| 221 | `         target_row = ttk.Frame(parent) ` | 把结果保存到 target_row：创建布局容器；参数：parent。 |
| 222 | `         target_row.pack(fill='x', pady=3) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=3。 |
| 223 | `         ttk.Label(target_row, text='Analyze').pack(side='left') ` | 创建文字标签；参数：target_row, text='Analyze'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 224 | `         self.combo(target_row, self.analysis_target, ('Selected record', 'All loaded records'), 21).pack(side='left', padx=8) ` | 创建只读下拉框并登记，便于统一切换可用状态。；参数：target_row, self.analysis_target, ('Selected record', 'All loaded records'), 21；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=8。 |
| 225 | `         ttk.Label(target_row, text='Linearity and repetition require multiple records.', foreground='#657588').pack(side='left') ` | 创建文字标签；参数：target_row, text='Linearity and repetition require multiple records.', foreground='#657588'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 226 | `         window_row = ttk.Frame(parent) ` | 把结果保存到 window_row：创建布局容器；参数：parent。 |
| 227 | `         window_row.pack(fill='x', pady=3) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=3。 |
| 228 | `         self.window_check = ttk.Checkbutton(window_row, text='Build time windows', variable=self.windowed, ` | 把结果保存到 self.window_check：创建勾选框；参数：window_row, text='Build time windows', variable=self.windowed, command=self.context_states。 |
| 229 | `                                             command=self.context_states) ` | 接续第 228 行的同一条语句，不是另起一段算法。 把结果保存到 self.window_check：创建勾选框；参数：window_row, text='Build time windows', variable=self.windowed, command=self.context_states。 |
| 230 | `         self.window_check.pack(side='left') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 231 | `         self.controls.append(self.window_check) ` | 把一项加入列表末尾；参数：self.window_check。 |
| 232 | `         ttk.Label(window_row, text='Window (s)').pack(side='left', padx=(10, 4)) ` | 创建文字标签；参数：window_row, text='Window (s)'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=(10, 4)。 |
| 233 | `         self.window_entry = ttk.Entry(window_row, width=6) ` | 把结果保存到 self.window_entry：创建单行输入框；参数：window_row, width=6。 |
| 234 | `         self.window_entry.pack(side='left') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 235 | `         ttk.Label(window_row, text='Step (s)').pack(side='left', padx=(10, 4)) ` | 创建文字标签；参数：window_row, text='Step (s)'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=(10, 4)。 |
| 236 | `         self.hop_entry = ttk.Entry(window_row, width=6) ` | 把结果保存到 self.hop_entry：创建单行输入框；参数：window_row, width=6。 |
| 237 | `         self.hop_entry.pack(side='left') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 238 | `         self.controls.extend((self.window_entry, self.hop_entry)) ` | 把多项逐个加入列表；参数：(self.window_entry, self.hop_entry)。 |
| 239 | `         ttk.Label(window_row, text='Complete windows only; no padding.', foreground='#657588').pack(side='left', padx=10) ` | 创建文字标签；参数：window_row, text='Complete windows only; no padding.', foreground='#657588'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=10。 |
| 240 | `         crop_row = ttk.Frame(parent) ` | 把结果保存到 crop_row：创建布局容器；参数：parent。 |
| 241 | `         crop_row.pack(fill='x', pady=3) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=3。 |
| 242 | `         ttk.Label(crop_row, text='Exclude final (s)').pack(side='left') ` | 创建文字标签；参数：crop_row, text='Exclude final (s)'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 243 | `         self.crop_entry = ttk.Entry(crop_row, width=6, textvariable=self.limit_vars['exclude_last_s']) ` | 把结果保存到 self.crop_entry：创建单行输入框；参数：crop_row, width=6, textvariable=self.limit_vars['exclude_last_s']。 |
| 244 | `         self.crop_entry.pack(side='left', padx=8) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=8。 |
| 245 | `         self.controls.append(self.crop_entry) ` | 把一项加入列表末尾；参数：self.crop_entry。 |
| 246 | `         ttk.Label(crop_row, text='Per file, before all checks and windows. Original BDF unchanged.', foreground='#657588').pack(side='left') ` | 创建文字标签；参数：crop_row, text='Per file, before all checks and windows. Original BDF unchanged.', foreground='#657588'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 247 | `         bar = ttk.Frame(parent) ` | 把结果保存到 bar：创建布局容器；参数：parent。 |
| 248 | `         bar.pack(fill='x', pady=7) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=7。 |
| 249 | `         self.run_button = self.button(bar, 'Run analysis', self.run) ` | 把结果保存到 self.run_button：创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。；参数：bar, 'Run analysis', self.run。 |
| 250 | `         self.run_button.pack(side='left') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 251 | `         self.button(bar, 'Export PNG / CSV / report', self.export).pack(side='left', padx=8) ` | 创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。；参数：bar, 'Export PNG / CSV / report', self.export；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=8。 |
| 252 | `         self.progress = ttk.Progressbar(bar, mode='indeterminate', length=90) ` | 把结果保存到 self.progress：创建进度指示；参数：bar, mode='indeterminate', length=90。 |
| 253 | `         self.progress.pack(side='left', padx=8) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=8。 |
| 254 | `         self.notebook = ttk.Notebook(parent) ` | 把结果保存到 self.notebook：创建标签页容器；参数：parent。 |
| 255 | `         self.notebook.pack(fill='both', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 256 | `         tabs = [ttk.Frame(self.notebook, padding=10) for _ in range(4)] ` | 把结果保存到 tabs：从 range(4) 逐个取 _，为每项生成 ttk.Frame(self.notebook, padding=10)。 |
| 257 | `         for tab, title in zip(tabs, ('Electrode heatmap', 'Results', 'Criteria', 'How it works')): ` | 遍历 zip(tabs, ('Electrode heatmap', 'Results', 'Criteria', 'How it works'))，每次把一项赋给 (tab, title)，执行下面缩进的循环体。 |
| 258 | `             self.notebook.add(tab, text=title) ` | 调用 self.notebook.add；参数：tab, text=title。 |
| 259 | `         row = ttk.Frame(tabs[0]) ` | 把结果保存到 row：创建布局容器；参数：tabs[0]。 |
| 260 | `         row.pack(fill='x') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 261 | `         ttk.Label(row, text='Metric').pack(side='left') ` | 创建文字标签；参数：row, text='Metric'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 262 | `         self.view_combo = self.combo(row, self.mode, list(BENCH_VIEWS), 29) ` | 把结果保存到 self.view_combo：创建只读下拉框并登记，便于统一切换可用状态。；参数：row, self.mode, list(BENCH_VIEWS), 29。 |
| 263 | `         self.view_combo.pack(side='left', padx=8) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=8。 |
| 264 | `         self.view_combo.bind('<<ComboboxSelected>>', lambda _: self.redraw()) ` | 绑定界面事件，事件发生时才执行回调；参数：'<<ComboboxSelected>>', lambda _: self.redraw()。 |
| 265 | `         ttk.Label(row, textvariable=self.summary).pack(side='left') ` | 创建文字标签；参数：row, textvariable=self.summary；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 266 | `         self.button(row, '3D torso', self.open_torso).pack(side='right', padx=4) ` | 创建按钮并保存到控件列表，以便分析期间统一禁用；callback 是点击后才执行的函数。；参数：row, '3D torso', self.open_torso；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='right', padx=4。 |
| 267 | `         row = ttk.Frame(tabs[0]) ` | 把结果保存到 row：创建布局容器；参数：tabs[0]。 |
| 268 | `         row.pack(fill='x', pady=6) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=6。 |
| 269 | `         ttk.Label(row, text='Result scope').pack(side='left') ` | 创建文字标签；参数：row, text='Result scope'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left'。 |
| 270 | `         self.window_combo = self.combo(row, self.scope, self.frame_labels, 60) ` | 把结果保存到 self.window_combo：创建只读下拉框并登记，便于统一切换可用状态。；参数：row, self.scope, self.frame_labels, 60。 |
| 271 | `         self.window_combo.pack(side='left', padx=8, fill='x', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=8, fill='x', expand=True。 |
| 272 | `         self.window_combo.bind('<<ComboboxSelected>>', self.change_scope) ` | 绑定界面事件，事件发生时才执行回调；参数：'<<ComboboxSelected>>', self.change_scope。 |
| 273 | `         self.timeline = TimelineView(tabs[0], self.select_window) ` | 把结果保存到 self.timeline：调用 TimelineView；参数：tabs[0], self.select_window。 |
| 274 | `         self.timeline.pack(fill='x', pady=(0, 5)) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=(0, 5)。 |
| 275 | `         ttk.Label(tabs[0], text='Timeline colors: worst channel for the selected metric. Drag to inspect a window.', ` | 创建文字标签；参数：tabs[0], text='Timeline colors: worst channel for the selected metric. Drag to inspect a window.', foreground='#657588'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w'。 |
| 276 | `                   foreground='#657588').pack(anchor='w') ` | 接续第 275 行的同一条语句，不是另起一段算法。 创建文字标签；参数：tabs[0], text='Timeline colors: worst channel for the selected metric. Drag to inspect a window.', foreground='#657588'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w'。 |
| 277 | `         row = ttk.Frame(tabs[0]) ` | 把结果保存到 row：创建布局容器；参数：tabs[0]。 |
| 278 | `         row.pack(fill='x', pady=3) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', pady=3。 |
| 279 | `         for key in COLORS: ` | 遍历 COLORS，每次把一项赋给 key，执行下面缩进的循环体。 |
| 280 | `             tk.Label(row, text='● ' + COLOR_LABELS[key], fg=COLORS[key], bg='#F4F7FA', font=('Segoe UI', 9, 'bold')).pack(side='left', padx=(0, 12)) ` | 创建文字标签；参数：row, text='● ' + COLOR_LABELS[key], fg=COLORS[key], bg='#F4F7FA', font=('Segoe UI', 9, 'bold')；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='left', padx=(0, 12)。 |
| 281 | `         # Reserve the reason panel before letting the scrollable grid expand. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 282 | `         # Otherwise the new timeline can push reasons off small screens. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 283 | `         detail_shell = ttk.Frame(tabs[0]) ` | 把结果保存到 detail_shell：创建布局容器；参数：tabs[0]。 |
| 284 | `         detail_shell.pack(side='bottom', fill='x') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='bottom', fill='x'。 |
| 285 | `         ttk.Label(detail_shell, text='Click an electrode for values and reasons. Grid order is not a physical cap layout.', foreground='#657588').pack(anchor='w', pady=4) ` | 创建文字标签；参数：detail_shell, text='Click an electrode for values and reasons. Grid order is not a physical cap layout.', foreground='#657588'；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：anchor='w', pady=4。 |
| 286 | `         detail_row = ttk.Frame(detail_shell) ` | 把结果保存到 detail_row：创建布局容器；参数：detail_shell。 |
| 287 | `         detail_row.pack(fill='x') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x'。 |
| 288 | `         self.detail = tk.Text(detail_row, height=4, wrap='word', font=('Segoe UI', 10), bg='white', relief='flat', padx=9, pady=6) ` | 把结果保存到 self.detail：创建多行文本框；参数：detail_row, height=4, wrap='word', font=('Segoe UI', 10), bg='white', relief='flat', padx=9, pady=6。 |
| 289 | `         detail_scroll = ttk.Scrollbar(detail_row, orient='vertical', command=self.detail.yview) ` | 把结果保存到 detail_scroll：创建滚动条；参数：detail_row, orient='vertical', command=self.detail.yview。 |
| 290 | `         self.detail.configure(yscrollcommand=detail_scroll.set) ` | 更新控件属性或状态，不计算信号指标；参数：yscrollcommand=detail_scroll.set。 |
| 291 | `         detail_scroll.pack(side='right', fill='y') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='right', fill='y'。 |
| 292 | `         self.detail.pack(fill='x', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='x', expand=True。 |
| 293 | `         self.detail.configure(state='disabled') ` | 更新控件属性或状态，不计算信号指标；参数：state='disabled'。 |
| 294 | `         self.heatmap = HeatmapView(tabs[0], self.show_detail) ` | 把结果保存到 self.heatmap：调用 HeatmapView；参数：tabs[0], self.show_detail。 |
| 295 | `         self.heatmap.pack(fill='both', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 296 | `         self.results_tree = ttk.Treeview(tabs[1], show='headings') ` | 把结果保存到 self.results_tree：创建表格/列表；参数：tabs[1], show='headings'。 |
| 297 | `         sx = ttk.Scrollbar(tabs[1], orient='horizontal', command=self.results_tree.xview) ` | 把结果保存到 sx：创建滚动条；参数：tabs[1], orient='horizontal', command=self.results_tree.xview。 |
| 298 | `         self.results_tree.configure(xscrollcommand=sx.set) ` | 更新控件属性或状态，不计算信号指标；参数：xscrollcommand=sx.set。 |
| 299 | `         sx.pack(side='bottom', fill='x') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='bottom', fill='x'。 |
| 300 | `         self.results_tree.pack(fill='both', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 301 | `         self.results_tree.bind('<<TreeviewSelect>>', self.select_result) ` | 绑定界面事件，事件发生时才执行回调；参数：'<<TreeviewSelect>>', self.select_result。 |
| 302 | `         self._build_criteria(tabs[2]) ` | 按 CRITERIA 字典生成可滚动的阈值编辑表；改变此处输入会使旧分析结果失效。；参数：tabs[2]。 |
| 303 | `         self._build_help(tabs[3]) ` | 把用户帮助文本写入只读文本框；这段长字符串只用于显示，不执行里面的文字。；参数：tabs[3]。 |
| 304 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 305 | `     def _build_criteria(self, parent): ` | 定义 _build_criteria(self, parent)。按 CRITERIA 字典生成可滚动的阈值编辑表；改变此处输入会使旧分析结果失效。 定义到这里时不执行函数体。 |
| 306 | `         canvas = tk.Canvas(parent, bg='#F4F7FA', highlightthickness=0) ` | 把结果保存到 canvas：创建绘图画布；参数：parent, bg='#F4F7FA', highlightthickness=0。 |
| 307 | `         scroll = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview) ` | 把结果保存到 scroll：创建滚动条；参数：parent, orient='vertical', command=canvas.yview。 |
| 308 | `         canvas.configure(yscrollcommand=scroll.set) ` | 更新控件属性或状态，不计算信号指标；参数：yscrollcommand=scroll.set。 |
| 309 | `         scroll.pack(side='right', fill='y') ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：side='right', fill='y'。 |
| 310 | `         canvas.pack(fill='both', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 311 | `         form = ttk.Frame(canvas, padding=10) ` | 把结果保存到 form：创建布局容器；参数：canvas, padding=10。 |
| 312 | `         canvas.create_window((0, 0), window=form, anchor='nw') ` | 把一个控件嵌入 Canvas 的指定位置；参数：(0, 0), window=form, anchor='nw'。 |
| 313 | `         form.bind('<Configure>', lambda _: canvas.configure(scrollregion=canvas.bbox('all'))) ` | 绑定界面事件，事件发生时才执行回调；参数：'<Configure>', lambda _: canvas.configure(scrollregion=canvas.bbox('all'))。 |
| 314 | `         canvas.bind('<MouseWheel>', lambda e: canvas.yview_scroll(-int(e.delta / 120), 'units')) ` | 绑定界面事件，事件发生时才执行回调；参数：'<MouseWheel>', lambda e: canvas.yview_scroll(-int(e.delta / 120), 'units')。 |
| 315 | `         ttk.Label(form, text='Defaults: frequency error 0.1%, THD 1%, exclude final 1 s per file.\nEngineering starting points; blank THD/frequency limits mean uncalibrated.').grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 12)) ` | 创建文字标签；参数：form, text='Defaults: frequency error 0.1%, THD 1%, exclude final 1 s per file.\nEngineering starting points; blank THD/frequency limits mean unc…（完整表达式见左栏）；随后按 row/column 放置控件；sticky 决定靠边或拉伸；参数：row=0, column=0, columnspan=2, sticky='w', pady=(0, 12)。 |
| 316 | `         for row, (key, title) in enumerate(CRITERIA.items(), 1): ` | 遍历 enumerate(CRITERIA.items(), 1)，每次把一项赋给 (row, (key, title))，执行下面缩进的循环体。 |
| 317 | `             ttk.Label(form, text=title).grid(row=row, column=0, sticky='w', pady=6) ` | 创建文字标签；参数：form, text=title；随后按 row/column 放置控件；sticky 决定靠边或拉伸；参数：row=row, column=0, sticky='w', pady=6。 |
| 318 | `             w = ttk.Entry(form, textvariable=self.limit_vars[key], width=12) ` | 把结果保存到 w：创建单行输入框；参数：form, textvariable=self.limit_vars[key], width=12。 |
| 319 | `             w.grid(row=row, column=1, padx=16) ` | 按 row/column 放置控件；sticky 决定靠边或拉伸；参数：row=row, column=1, padx=16。 |
| 320 | `             self.controls.append(w) ` | 把一项加入列表末尾；参数：w。 |
| 321 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 322 | `     def _build_help(self, parent): ` | 定义 _build_help(self, parent)。把用户帮助文本写入只读文本框；这段长字符串只用于显示，不执行里面的文字。 定义到这里时不执行函数体。 |
| 323 | `         w = tk.Text(parent, wrap='word', font=('Segoe UI', 11), padx=12, pady=12, relief='flat') ` | 把结果保存到 w：创建多行文本框；参数：parent, wrap='word', font=('Segoe UI', 11), padx=12, pady=12, relief='flat'。 |
| 324 | `         w.pack(fill='both', expand=True) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True。 |
| 325 | `         w.insert('1.0', 'STAGE 1 - KNOWN INPUT\nSine: gain, multi-level linearity, both zero-crossing directions, repeatability, SNR, SINAD, THD and frequency.\nPulse: plateau amplitude, both midpoint edges, frequency and repeats. Sine distortion metrics are not applied to pulses.\n\nSTAGE 2 - ECG QUALITY\nComplete 10 s windows, every 5 s by default. bSQI compares two different QRS detector methods. pSQI, Pearson kSQI, basSQI and flatline/clipping checks describe other properties. Worst component wins: this is a prototype screen.\n\nCOLORS AND SCOPE\nGreen: evaluated criteria within limits. Yellow: warning, insufficient data, uncalibrated tolerance or descriptive-only metric. Red: check required. No color proves electrode damage.\nAnalyze defaults to Selected record. Input Vpp verification belongs to THIS record only; the list shows Verified Yes/No. Apply record or Run analysis saves edits. Result scope starts at the first complete window when available; otherwise it shows the whole record. For linearity/repetition, choose All loaded records, run, then select All analyzed records / worst case. Batch warnings name their source records. ECG record scope uses the worst complete window within that file; select a Window for its actual values. Only complete windows are used. A final full window covers the tail; short records are not padded or joined.\n\nTIME SLIDER\nBench: enable Build time windows, set Window to 10 s and Step to 1 s (or 10 s for blocks), then Run analysis. ECG always uses windows. Drag the slider, click the colored strip, or Play/Pause. Playback uses cached results and stops at the recording end. The strip shows the worst channel for the selected metric; Next alert finds the next yellow/red interval. Selected electrodes stay selected. Short bench files retain whole-record analysis but cannot supply a full window. A colored window locates an interval, not an exact fault onset. Windows are not independent repetitions.\n\nTIMING\nRising/falling events are matched separately within +/-T/4 windows. Missing events keep their index. Periodic signals cannot resolve whole-cycle absolute delays. REF is not independently verified.\n\nDATA AND LIMITS\nOnly select electrodes connected in the test. Do not pool different physical setups. THD/frequency limits start blank until calibrated. SQI thresholds are provisional. The app reads files offline; it does not connect to ActiView TCP.\n\nCODE\ngui.py -> AnalysisService -> waveform-specific classes -> MetricResult -> heatmap/export.\nDetailed Chinese walkthrough: CODE_GUIDE_ZH.md.') ` | 向列表或文本控件加入显示内容；参数：'1.0', 'STAGE 1 - KNOWN INPUT\nSine: gain, multi-level linearity, both zero-crossing directions, repeatability, SNR, SINAD, THD and frequency.\nP…（完整表达式见左栏）。 |
| 326 | `         w.configure(state='disabled') ` | 更新控件属性或状态，不计算信号指标；参数：state='disabled'。 |
| 327 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 328 | `     def change_profile(self, _=None): ` | 定义 change_profile(self, _=None)。切换工作流后更新指标列表和提示；脉冲移除 SNR/SINAD/THD 选项，然后清空旧结果。 定义到这里时不执行函数体。 |
| 329 | `         mode = self.analysis_mode() ` | 把结果保存到 mode：把界面可读的工作流名称转换为 bench_sine、bench_pulse 或 ecg。。 |
| 330 | `         self.views = dict(ECG_VIEWS if mode == 'ecg' else BENCH_VIEWS) ` | 把结果保存到 self.views：组装键值字典；参数：ECG_VIEWS if mode == 'ecg' else BENCH_VIEWS。 |
| 331 | `         if mode == 'bench_pulse': ` | 检查条件 mode == 'bench_pulse'；为真时执行下面缩进的一组语句。 |
| 332 | `             for key in ('SNR', 'SINAD', 'THD'): ` | 遍历 ('SNR', 'SINAD', 'THD')，每次把一项赋给 key，执行下面缩进的循环体。 |
| 333 | `                 self.views.pop(key) ` | 取出并移除指定项；参数：key。 |
| 334 | `         self.view_combo.configure(values=list(self.views)) ` | 更新控件属性或状态，不计算信号指标；参数：values=list(self.views)。 |
| 335 | `         if self.mode.get() not in self.views: ` | 检查条件 self.mode.get() not in self.views；为真时执行下面缩进的一组语句。 |
| 336 | `             self.mode.set(next(iter(self.views))) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：next(iter(self.views))。 |
| 337 | `         self.hint.set({'bench_sine': 'Verify a known sine through the full acquisition chain. Actual input Vpp is required for absolute gain.', 'bench_pulse': 'Measure pulse plateaus and rising/falling midpoint edges. No sine-fit quality gate is applied.', 'ecg': 'Screen ECG channels in complete windows. Short files are marked insufficient; SQI does not prove electrode damage.'}[mode]) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：{'bench_sine': 'Verify a known sine through the full acquisition chain. Actual input Vpp is required for absolute gain.', 'bench_pulse': 'Measure…（完整表达式见左栏）。 |
| 338 | `         self.context_states() ` | 按当前模式和忙碌状态启用/禁用相关控件，ECG 总是使用窗口而不要求同步参考。。 |
| 339 | `         self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 340 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 341 | `     def context_states(self): ` | 定义 context_states(self)。按当前模式和忙碌状态启用/禁用相关控件，ECG 总是使用窗口而不要求同步参考。 定义到这里时不执行函数体。 |
| 342 | `         ecg = self.analysis_mode() == 'ecg' ` | 把结果保存到 ecg：self.analysis_mode() == 'ecg'。 |
| 343 | `         self.window_check.configure(state='disabled' if ecg or self.busy else 'normal') ` | 更新控件属性或状态，不计算信号指标；参数：state='disabled' if ecg or self.busy else 'normal'。 |
| 344 | `         self.window_check.configure(text='ECG time windows (always on)' if ecg else 'Build time windows') ` | 更新控件属性或状态，不计算信号指标；参数：text='ECG time windows (always on)' if ecg else 'Build time windows'。 |
| 345 | `         prefix = 'ecg' if ecg else 'bench' ` | 把结果保存到 prefix：若 ecg，用 'ecg'；否则用 'bench'。 |
| 346 | `         self.window_entry.configure(textvariable=self.limit_vars[prefix + '_window_s']) ` | 更新控件属性或状态，不计算信号指标；参数：textvariable=self.limit_vars[prefix + '_window_s']。 |
| 347 | `         self.hop_entry.configure(textvariable=self.limit_vars[prefix + '_hop_s']) ` | 更新控件属性或状态，不计算信号指标；参数：textvariable=self.limit_vars[prefix + '_hop_s']。 |
| 348 | `         for w in (self.window_entry, self.hop_entry): ` | 遍历 (self.window_entry, self.hop_entry)，每次把一项赋给 w，执行下面缩进的循环体。 |
| 349 | `             w.configure(state='normal' if not self.busy and (ecg or self.windowed.get()) else 'disabled') ` | 更新控件属性或状态，不计算信号指标；参数：state='normal' if not self.busy and (ecg or self.windowed.get()) else 'disabled'。 |
| 350 | `         self.ref_combo.configure(state='disabled' if ecg or self.busy else 'readonly') ` | 更新控件属性或状态，不计算信号指标；参数：state='disabled' if ecg or self.busy else 'readonly'。 |
| 351 | `         self.window_combo.configure(state='readonly' if self.result is not None and not self.busy else 'disabled') ` | 更新控件属性或状态，不计算信号指标；参数：state='readonly' if self.result is not None and (not self.busy) else 'disabled'。 |
| 352 | `         for w in self.bench_controls: ` | 遍历 self.bench_controls，每次把一项赋给 w，执行下面缩进的循环体。 |
| 353 | `             w.configure(state='disabled' if ecg or self.busy else 'readonly' if isinstance(w, ttk.Combobox) else 'normal') ` | 更新控件属性或状态，不计算信号指标；参数：state='disabled' if ecg or self.busy else 'readonly' if isinstance(w, ttk.Combobox) else 'normal'。 |
| 354 | `         self.unit_combo.configure(values=list(UNIT_FACTORS) if self.analysis_mode() == 'bench_sine' else ['mVpp', 'uVpp', 'Vpp']) ` | 更新控件属性或状态，不计算信号指标；参数：values=list(UNIT_FACTORS) if self.analysis_mode() == 'bench_sine' else ['mVpp', 'uVpp', 'Vpp']。 |
| 355 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 356 | `     def invalidate(self, *_): ` | 定义 invalidate(self, *_)。丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。 定义到这里时不执行函数体。 |
| 357 | `         if self.loading or self.busy: ` | 检查条件 self.loading or self.busy；为真时执行下面缩进的一组语句。 |
| 358 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 359 | `         self.timeline.clear() ` | 清空容器，或调用该视图定义的清除方法。 |
| 360 | `         self.timeline_cache.clear() ` | 清空容器，或调用该视图定义的清除方法。 |
| 361 | `         self.focused_electrode = None ` | 把结果保存到 self.focused_electrode：None（未知/未设置）。 |
| 362 | `         self.result = None ` | 清除对旧分析结果的引用，防止继续显示不适用于当前参数的结果。 |
| 363 | `         self.heatmap.show([], 'current') ` | 调用 self.heatmap.show；参数：[], 'current'。 |
| 364 | `         if self.torso_window is not None: ` | 检查条件 self.torso_window is not None；为真时执行下面缩进的一组语句。 |
| 365 | `             self.torso_window.clear() ` | 清空容器，或调用该视图定义的清除方法。 |
| 366 | `         self.results_tree.delete(*self.results_tree.get_children()) ` | 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：*self.results_tree.get_children()。 |
| 367 | `         self.detail_text('') ` | 暂时解除详情框只读状态，替换文本后恢复只读。；参数：''。 |
| 368 | `         self.summary.set('Not analyzed') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Not analyzed'。 |
| 369 | `         self.frame_labels = ['Not analyzed'] ` | 把结果保存到 self.frame_labels：组装列表：['Not analyzed']。 |
| 370 | `         self.result_scopes = {} ` | 把结果保存到 self.result_scopes：组装字典，键用于给数值/设置命名：{}。 |
| 371 | `         self.scope.set(self.frame_labels[0]) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：self.frame_labels[0]。 |
| 372 | `         self.window_combo.configure(values=self.frame_labels, state='disabled') ` | 更新控件属性或状态，不计算信号指标；参数：values=self.frame_labels, state='disabled'。 |
| 373 | `         if self.records: ` | 检查条件 self.records；为真时执行下面缩进的一组语句。 |
| 374 | `             self.status.set('Inputs changed. Run analysis again to refresh the results.') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Inputs changed. Run analysis again to refresh the results.'。 |
| 375 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 376 | `     def detail_text(self, text): ` | 定义 detail_text(self, text)。暂时解除详情框只读状态，替换文本后恢复只读。 定义到这里时不执行函数体。 |
| 377 | `         self.detail.configure(state='normal') ` | 更新控件属性或状态，不计算信号指标；参数：state='normal'。 |
| 378 | `         self.detail.delete('1.0', 'end') ` | 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：'1.0', 'end'。 |
| 379 | `         self.detail.insert('1.0', text) ` | 向列表或文本控件加入显示内容；参数：'1.0', text。 |
| 380 | `         self.detail.configure(state='disabled') ` | 更新控件属性或状态，不计算信号指标；参数：state='disabled'。 |
| 381 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 382 | `     def suggest_mode(self, records): ` | 定义 suggest_mode(self, records)。当导入文件声明为同一类波形时，自动建议对应工作流；名称提示不验证真实波形。 定义到这里时不执行函数体。 |
| 383 | `         kinds = {r.waveform for r in records} - {'unknown'} ` | 把结果保存到 kinds：{r.waveform for r in records} 与 {'unknown'} 相减。 |
| 384 | `         if len(kinds) == 1: ` | 检查条件 len(kinds) == 1；为真时执行下面缩进的一组语句。 |
| 385 | `             kind = next(iter(kinds)) ` | 把结果保存到 kind：取迭代器的下一项或匹配到的第一项；参数：iter(kinds)。 |
| 386 | `             mode = {'ecg': 'ecg', 'pulse': 'bench_pulse', 'sine': 'bench_sine'}[kind] ` | 把结果保存到 mode：按索引/键 kind 取 {'ecg': 'ecg', 'pulse': 'bench_pulse', 'sine': 'bench_sine'} 的内容。 |
| 387 | `             self.profile.set(next((k for k, v in PROFILES.items() if v == mode))) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：next((k for k, v in PROFILES.items() if v == mode))。 |
| 388 | `             self.change_profile() ` | 切换工作流后更新指标列表和提示；脉冲移除 SNR/SINAD/THD 选项，然后清空旧结果。。 |
| 389 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 390 | `     def add_files(self): ` | 定义 add_files(self)。先保存当前表单，再弹出文件选择，建立新记录清单，去重并刷新通道与界面。 定义到这里时不执行函数体。 |
| 391 | `         if not self.apply_record(): ` | 检查条件 not self.apply_record()；为真时执行下面缩进的一组语句。 |
| 392 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 393 | `         paths = filedialog.askopenfilenames(filetypes=[('BDF recordings / ZIP archives', '*.bdf *.zip')]) ` | 把结果保存到 paths：调用 filedialog.askopenfilenames；参数：filetypes=[('BDF recordings / ZIP archives', '*.bdf *.zip')]。 |
| 394 | `         if not paths: ` | 检查条件 not paths；为真时执行下面缩进的一组语句。 |
| 395 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 396 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 397 | `             additions = records_from_paths(paths) ` | 把结果保存到 additions：调用 records_from_paths；参数：paths。 |
| 398 | `             seen = {(r.path.lower(), r.member) for r in self.records} ` | 把结果保存到 seen：从 self.records 逐个取 r，为每项生成 (r.path.lower(), r.member)。 |
| 399 | `             additions = [r for r in additions if (r.path.lower(), r.member) not in seen] ` | 把结果保存到 additions：从 additions 逐个取 r，仅保留 (r.path.lower(), r.member) not in seen，为每项生成 r。 |
| 400 | `             if not self.records and additions: ` | 检查条件 not self.records and additions；为真时执行下面缩进的一组语句。 |
| 401 | `                 self.suggest_mode(additions) ` | 当导入文件声明为同一类波形时，自动建议对应工作流；名称提示不验证真实波形。；参数：additions。 |
| 402 | `             used = {r.id for r in self.records} ` | 把结果保存到 used：从 self.records 逐个取 r，为每项生成 r.id。 |
| 403 | `             for r in additions: ` | 遍历 additions，每次把一项赋给 r，执行下面缩进的循环体。 |
| 404 | `                 while r.id in used: ` | 只要 r.id in used 为真就重复循环；退出依靠条件改变、break 或异常。 |
| 405 | `                     r.id += '_new' ` | 把 r.id 的原值加上 '_new'，再写回同一变量。 |
| 406 | `                 used.add(r.id) ` | 调用 used.add；参数：r.id。 |
| 407 | `             self.records.extend(additions) ` | 把多项逐个加入列表；参数：additions。 |
| 408 | `             self.refresh_records() ` | 重新填充文件列表，默认选择第一条，或在空列表时显示无文件。。 |
| 409 | `             if not self.channels: ` | 检查条件 not self.channels；为真时执行下面缩进的一组语句。 |
| 410 | `                 self.initialize_channels() ` | 读取第一份文件头，选择实际存在的电压通道，并设置参考和数量。。 |
| 411 | `             self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 412 | `         except (ValueError, OSError, KeyError) as exc: ` | 捕获 (ValueError, OSError, KeyError) 异常，保存到 exc，执行错误处理。 |
| 413 | `             messagebox.showerror('Cannot read recording', str(exc)) ` | 弹出错误提示；参数：'Cannot read recording', str(exc)。 |
| 414 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 415 | `     def refresh_records(self): ` | 定义 refresh_records(self)。重新填充文件列表，默认选择第一条，或在空列表时显示无文件。 定义到这里时不执行函数体。 |
| 416 | `         self.selected = None ` | 把结果保存到 self.selected：None（未知/未设置）。 |
| 417 | `         self.record_tree.delete(*self.record_tree.get_children()) ` | 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：*self.record_tree.get_children()。 |
| 418 | `         for i, r in enumerate(self.records): ` | 遍历 enumerate(self.records)，每次把一项赋给 (i, r)，执行下面缩进的循环体。 |
| 419 | `             self.record_tree.insert('', 'end', iid=str(i), values=self.record_row(r)) ` | 向列表或文本控件加入显示内容；参数：'', 'end', iid=str(i), values=self.record_row(r)。 |
| 420 | `         if self.records: ` | 检查条件 self.records；为真时执行下面缩进的一组语句。 |
| 421 | `             self.record_tree.selection_set('0') ` | 设置选中行；参数：'0'。 |
| 422 | `             self.select_record() ` | 切换记录时保存上一份编辑，再加载新记录的参数；若它已被分析，切换到该文件自己的结果。。 |
| 423 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 424 | `             self.source_label.set('No BDF selected') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'No BDF selected'。 |
| 425 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 426 | `     def select_record(self, _=None): ` | 定义 select_record(self, _=None)。切换记录时保存上一份编辑，再加载新记录的参数；若它已被分析，切换到该文件自己的结果。 定义到这里时不执行函数体。 |
| 427 | `         if self.busy or not self.record_tree.selection(): ` | 检查条件 self.busy or not self.record_tree.selection()；为真时执行下面缩进的一组语句。 |
| 428 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 429 | `         index = int(self.record_tree.selection()[0]) ` | 把结果保存到 index：转换为整数；参数：self.record_tree.selection()[0]。 |
| 430 | `         if index == self.selected: ` | 检查条件 index == self.selected；为真时执行下面缩进的一组语句。 |
| 431 | `             return  # A duplicate selection event must not overwrite pending edits. ` | 结束当前函数并返回：None（没有值）。 |
| 432 | `         self.timeline.pause() ` | 调用 self.timeline.pause。 |
| 433 | `         if self.torso_window is not None: ` | 检查条件 self.torso_window is not None；为真时执行下面缩进的一组语句。 |
| 434 | `             self.torso_window.timeline.pause() ` | 调用 self.torso_window.timeline.pause。 |
| 435 | `         if self.selected is not None and self.selected != index and (not self.apply_record()): ` | 检查条件 self.selected is not None and self.selected != index and (not self.apply_record())；为真时执行下面缩进的一组语句。 |
| 436 | `             self.record_tree.selection_set(str(self.selected)) ` | 设置选中行；参数：str(self.selected)。 |
| 437 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 438 | `         self.selected = index ` | 把结果保存到 self.selected：index。 |
| 439 | `         r = self.records[index] ` | 把结果保存到 r：按索引/键 index 取 self.records 的内容。 |
| 440 | `         self.loading = True ` | 把结果保存到 self.loading：True（是）。 |
| 441 | `         for key, value in dict(frequency=str(r.frequency_hz), amplitude='' if r.input_mVpp is None else str(r.input_mVpp), unit='mVpp', repeat=r.repeat_group, setup=r.setup_group, waveform=r.waveform).items(): ` | 遍历 dict(frequency=str(r.frequency_hz), amplitude='' if r.input_mVpp is None else str(r.input_mVpp), unit='mVpp', repeat=r.repeat_group, setup=r.setup_group, waveform=r.waveform).items…（完整表达式见左栏），每次把一项赋给 (key, value)，执行下面缩进的循环体。 |
| 442 | `             self.record_vars[key].set(value) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：value。 |
| 443 | `         self.confirmed.set(r.input_confirmed) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：r.input_confirmed。 |
| 444 | `         self.sweep.set(r.sweep) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：r.sweep。 |
| 445 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 446 | `             info = BdfReader().inspect(r) ` | 把结果保存到 info：只读头信息，核对格式/长度，返回通道名、采样率、时长，过滤 Status/Annotations。；参数：r。 |
| 447 | `             self.source_label.set(f'{Path(r.member or r.path).name}\n{info.duration_s:g} s \| {next(iter(info.sample_rates.values())):g} Hz \| {len(info.voltage_labels)} saved voltage channels') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：f'{Path(r.member or r.path).name}\n{info.duration_s:g} s &#124; {next(iter(info.sample_rates.values())):g} Hz &#124; {len(info.voltage_labels)} saved volta…（完整表达式见左栏）。 |
| 448 | `         except (ValueError, OSError) as exc: ` | 捕获 (ValueError, OSError) 异常，保存到 exc，执行错误处理。 |
| 449 | `             self.source_label.set(str(exc)) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：str(exc)。 |
| 450 | `         self.loading = False ` | 把结果保存到 self.loading：False（否）。 |
| 451 | `         if self.result is not None: ` | 检查条件 self.result is not None；为真时执行下面缩进的一组语句。 |
| 452 | `             label = self.label_for_record(r.id) ` | 把结果保存到 label：找到某个记录 ID 对应的显示范围名称。；参数：r.id。 |
| 453 | `             if label is None: ` | 检查条件 label is None；为真时执行下面缩进的一组语句。 |
| 454 | `                 self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 455 | `                 self.status.set('Selected record has not been analyzed. Click Run analysis.') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Selected record has not been analyzed. Click Run analysis.'。 |
| 456 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 457 | `                 self.scope.set(label) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：label。 |
| 458 | `                 self.redraw() ` | 从已有结果更新热图、躯干、颜色计数、结果表和详情。。 |
| 459 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 460 | `     @staticmethod ` | @staticmethod 表示该方法不依赖 self，可直接通过类调用。 |
| 461 | `     def record_row(record): ` | 定义 record_row(record)。把一份记录转换为列表中的三列：ID、输入 Vpp 和是否已确认。 定义到这里时不执行函数体。 |
| 462 | `         return (record.id, record.input_mVpp if record.input_mVpp is not None else '?', ` | 结束当前函数并返回：组装元组：(record.id, record.input_mVpp if record.input_mVpp is not None else '?', 'Yes' if record.input_confirmed else 'No')。 |
| 463 | `                 'Yes' if record.input_confirmed else 'No') ` | 接续第 462 行的同一条语句，不是另起一段算法。 结束当前函数并返回：组装元组：(record.id, record.input_mVpp if record.input_mVpp is not None else '?', 'Yes' if record.input_confirmed else 'No')。 |
| 464 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 465 | `     def apply_record(self): ` | 定义 apply_record(self)。把当前输入框转换成合法的 InputRecord；确认框只改变当前文件。 定义到这里时不执行函数体。 |
| 466 | `         if self.selected is None: ` | 检查条件 self.selected is None；为真时执行下面缩进的一组语句。 |
| 467 | `             return True ` | 结束当前函数并返回：True（是）。 |
| 468 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 469 | `             r = copy.deepcopy(self.records[self.selected]) ` | 把结果保存到 r：深复制嵌套对象，避免改动与当前 GUI 状态共用对象；参数：self.records[self.selected]。 |
| 470 | `             if self.analysis_mode() != 'ecg': ` | 检查条件 self.analysis_mode() != 'ecg'；为真时执行下面缩进的一组语句。 |
| 471 | `                 r.frequency_hz = float(self.record_vars['frequency'].get()) ` | 把结果保存到 r.frequency_hz：转换为浮点数；参数：self.record_vars['frequency'].get()。 |
| 472 | `                 value = self.record_vars['amplitude'].get().strip() ` | 把结果保存到 value：去掉文本两端空白。 |
| 473 | `                 unit = self.record_vars['unit'].get() ` | 把结果保存到 unit：读取当前值；若是 dict.get，缺少键时可返回指定默认值。 |
| 474 | `                 if self.analysis_mode() == 'bench_pulse' and unit not in ('mVpp', 'uVpp', 'Vpp'): ` | 检查条件 self.analysis_mode() == 'bench_pulse' and unit not in ('mVpp', 'uVpp', 'Vpp')；为真时执行下面缩进的一组语句。 |
| 475 | `                     raise ValueError('Pulse input must be specified as peak-to-peak voltage') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Pulse input must be specified as peak-to-peak voltage'；上层可捕获并显示原因。 |
| 476 | `                 r.input_mVpp = float(value) * UNIT_FACTORS[unit] if value else None ` | 把结果保存到 r.input_mVpp：若 value，用 float(value) * UNIT_FACTORS[unit]；否则用 None。 |
| 477 | `                 if not math.isfinite(r.frequency_hz) or r.frequency_hz <= 0: ` | 检查条件 not math.isfinite(r.frequency_hz) or r.frequency_hz <= 0；为真时执行下面缩进的一组语句。 |
| 478 | `                     raise ValueError('Frequency must be positive') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Frequency must be positive'；上层可捕获并显示原因。 |
| 479 | `                 if r.input_mVpp is not None and (not math.isfinite(r.input_mVpp) or r.input_mVpp <= 0): ` | 检查条件 r.input_mVpp is not None and (not math.isfinite(r.input_mVpp) or r.input_mVpp <= 0)；为真时执行下面缩进的一组语句。 |
| 480 | `                     raise ValueError('Input amplitude must be positive') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Input amplitude must be positive'；上层可捕获并显示原因。 |
| 481 | `                 r.input_confirmed = bool(self.confirmed.get()) ` | 把结果保存到 r.input_confirmed：转换为真/假；参数：self.confirmed.get()。 |
| 482 | `                 if r.input_confirmed and r.input_mVpp is None: ` | 检查条件 r.input_confirmed and r.input_mVpp is None；为真时执行下面缩进的一组语句。 |
| 483 | `                     raise ValueError('A confirmed input needs a value') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'A confirmed input needs a value'；上层可捕获并显示原因。 |
| 484 | `                 r.sweep = bool(self.sweep.get()) ` | 把结果保存到 r.sweep：转换为真/假；参数：self.sweep.get()。 |
| 485 | `                 r.repeat_group = self.record_vars['repeat'].get().strip() ` | 把结果保存到 r.repeat_group：去掉文本两端空白。 |
| 486 | `             r.setup_group = self.record_vars['setup'].get().strip() or 'default' ` | 把结果保存到 r.setup_group：self.record_vars['setup'].get().strip() or 'default'。 |
| 487 | `             r.waveform = self.record_vars['waveform'].get() or 'unknown' ` | 把结果保存到 r.waveform：self.record_vars['waveform'].get() or 'unknown'。 |
| 488 | `             self.records[self.selected] = r ` | 把结果保存到 self.records[self.selected]：r。 |
| 489 | `             self.record_tree.item(str(self.selected), values=self.record_row(r)) ` | 调用 self.record_tree.item；参数：str(self.selected), values=self.record_row(r)。 |
| 490 | `             return True ` | 结束当前函数并返回：True（是）。 |
| 491 | `         except (ValueError, KeyError) as exc: ` | 捕获 (ValueError, KeyError) 异常，保存到 exc，执行错误处理。 |
| 492 | `             messagebox.showerror('Invalid record settings', str(exc)) ` | 弹出错误提示；参数：'Invalid record settings', str(exc)。 |
| 493 | `             return False ` | 在普通函数中返回布尔 False；若属于 __exit__，表示不吞掉原有异常，清理后让其继续向上传递。 |
| 494 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 495 | `     def initialize_channels(self, channels=None, reference=''): ` | 定义 initialize_channels(self, channels=None, reference='')。读取第一份文件头，选择实际存在的电压通道，并设置参考和数量。 定义到这里时不执行函数体。 |
| 496 | `         if not self.records: ` | 检查条件 not self.records；为真时执行下面缩进的一组语句。 |
| 497 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 498 | `         self.info = BdfReader().inspect(self.records[0]) ` | 把结果保存到 self.info：只读头信息，核对格式/长度，返回通道名、采样率、时长，过滤 Status/Annotations。；参数：self.records[0]。 |
| 499 | `         scalp = [c for c in self.info.voltage_labels if not c.upper().startswith('EXG')] ` | 把结果保存到 scalp：从 self.info.voltage_labels 逐个取 c，仅保留 not c.upper().startswith('EXG')，为每项生成 c。 |
| 500 | `         pool = 'scalp' if scalp else 'EXG' ` | 把结果保存到 pool：若 scalp，用 'scalp'；否则用 'EXG'。 |
| 501 | `         if channels and any((c not in self.info.voltage_labels for c in channels)): ` | 检查条件 channels and any((c not in self.info.voltage_labels for c in channels))；为真时执行下面缩进的一组语句。 |
| 502 | `             raise ValueError('Project channels are missing from the BDF') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Project channels are missing from the BDF'；上层可捕获并显示原因。 |
| 503 | `         self.loading = True ` | 把结果保存到 self.loading：True（是）。 |
| 504 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 505 | `             self.pool.set(pool) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：pool。 |
| 506 | `             if channels: ` | 检查条件 channels；为真时执行下面缩进的一组语句。 |
| 507 | `                 self.channels = list(channels) ` | 把结果保存到 self.channels：构造列表；参数：channels。 |
| 508 | `                 if all((c.upper().startswith('EXG') for c in channels)): ` | 检查条件 all((c.upper().startswith('EXG') for c in channels))；为真时执行下面缩进的一组语句。 |
| 509 | `                     self.pool.set('EXG') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'EXG'。 |
| 510 | `                 elif any((c.upper().startswith('EXG') for c in channels)): ` | 检查条件 any((c.upper().startswith('EXG') for c in channels))；为真时执行下面缩进的一组语句。 |
| 511 | `                     self.pool.set('all') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'all'。 |
| 512 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 513 | `                 size = len(scalp) if scalp else len(self.info.voltage_labels) ` | 把结果保存到 size：若 scalp，用 len(scalp)；否则用 len(self.info.voltage_labels)。 |
| 514 | `                 self.channels = BdfReader.choose_channels(self.info, min(int(self.count.get()), size), pool) ` | 把结果保存到 self.channels：从实际电压通道按 EXG/scalp/all 分组选择前 count 个，数量不合法就报错。；参数：self.info, min(int(self.count.get()), size), pool。 |
| 515 | `             self.count.set(str(len(self.channels))) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：str(len(self.channels))。 |
| 516 | `             self.reference.set(reference if reference in self.channels else self.channels[0]) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：reference if reference in self.channels else self.channels[0]。 |
| 517 | `             self.update_channel_label() ` | 更新参考下拉框与通道摘要文字。。 |
| 518 | `         finally: ` | 不管前面的操作成功还是抛异常，都执行这里的收尾/资源清理。 |
| 519 | `             self.loading = False ` | 把结果保存到 self.loading：False（否）。 |
| 520 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 521 | `     def update_channel_label(self): ` | 定义 update_channel_label(self)。更新参考下拉框与通道摘要文字。 定义到这里时不执行函数体。 |
| 522 | `         self.ref_combo.configure(values=self.channels) ` | 更新控件属性或状态，不计算信号指标；参数：values=self.channels。 |
| 523 | `         text = ', '.join(self.channels[:12]) ` | 把结果保存到 text：调用 ', '.join；参数：self.channels[:12]。 |
| 524 | `         if len(self.channels) > 12: ` | 检查条件 len(self.channels) > 12；为真时执行下面缩进的一组语句。 |
| 525 | `             text += f' ... ({len(self.channels)} selected)' ` | 把 text 的原值加上 f' ... ({len(self.channels)} selected)'，再写回同一变量。 |
| 526 | `         self.channel_label.configure(text=text or 'No channels selected') ` | 更新控件属性或状态，不计算信号指标；参数：text=text or 'No channels selected'。 |
| 527 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 528 | `     def apply_count(self): ` | 定义 apply_count(self)。把用户填写的数量应用为一组真实通道；数量本身不能创造文件里不存在的电极。 定义到这里时不执行函数体。 |
| 529 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 530 | `             if self.info is None: ` | 检查条件 self.info is None；为真时执行下面缩进的一组语句。 |
| 531 | `                 raise ValueError('Open a BDF first') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Open a BDF first'；上层可捕获并显示原因。 |
| 532 | `             self.channels = BdfReader.choose_channels(self.info, int(self.count.get()), self.pool.get()) ` | 把结果保存到 self.channels：从实际电压通道按 EXG/scalp/all 分组选择前 count 个，数量不合法就报错。；参数：self.info, int(self.count.get()), self.pool.get()。 |
| 533 | `             if self.reference.get() not in self.channels: ` | 检查条件 self.reference.get() not in self.channels；为真时执行下面缩进的一组语句。 |
| 534 | `                 self.reference.set(self.channels[0]) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：self.channels[0]。 |
| 535 | `             self.update_channel_label() ` | 更新参考下拉框与通道摘要文字。。 |
| 536 | `             self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 537 | `         except ValueError as exc: ` | 捕获 ValueError 异常，保存到 exc，执行错误处理。 |
| 538 | `             messagebox.showerror('Channel selection', str(exc)) ` | 弹出错误提示；参数：'Channel selection', str(exc)。 |
| 539 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 540 | `     def choose_channels(self): ` | 定义 choose_channels(self)。打开多选通道对话框；用户确认后更新通道和参考并清除旧结果。 定义到这里时不执行函数体。 |
| 541 | `         if self.info is None: ` | 检查条件 self.info is None；为真时执行下面缩进的一组语句。 |
| 542 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 543 | `         dialog = tk.Toplevel(self.root) ` | 把结果保存到 dialog：创建子窗口；参数：self.root。 |
| 544 | `         dialog.title('Select connected electrode channels') ` | 调用 dialog.title；参数：'Select connected electrode channels'。 |
| 545 | `         dialog.geometry('370x480') ` | 调用 dialog.geometry；参数：'370x480'。 |
| 546 | `         ttk.Label(dialog, text='Ctrl / Shift: multi-select. Status is excluded.', padding=10).pack() ` | 创建文字标签；参数：dialog, text='Ctrl / Shift: multi-select. Status is excluded.', padding=10；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展。 |
| 547 | `         choices = tk.Listbox(dialog, selectmode='extended', exportselection=False) ` | 把结果保存到 choices：调用 tk.Listbox；参数：dialog, selectmode='extended', exportselection=False。 |
| 548 | `         choices.pack(fill='both', expand=True, padx=12) ` | 用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：fill='both', expand=True, padx=12。 |
| 549 | `         for i, name in enumerate(self.info.voltage_labels): ` | 遍历 enumerate(self.info.voltage_labels)，每次把一项赋给 (i, name)，执行下面缩进的循环体。 |
| 550 | `             choices.insert('end', name) ` | 向列表或文本控件加入显示内容；参数：'end', name。 |
| 551 | `             if name in self.channels: ` | 检查条件 name in self.channels；为真时执行下面缩进的一组语句。 |
| 552 | `                 choices.selection_set(i) ` | 设置选中行；参数：i。 |
| 553 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 554 | `         def commit(): ` | 定义 commit()。保存通道对话框中的选择，然后关闭该对话框。 定义到这里时不执行函数体。 |
| 555 | `             selected = [self.info.voltage_labels[i] for i in choices.curselection()] ` | 把结果保存到 selected：从 choices.curselection() 逐个取 i，为每项生成 self.info.voltage_labels[i]。 |
| 556 | `             if not selected: ` | 检查条件 not selected；为真时执行下面缩进的一组语句。 |
| 557 | `                 return ` | 结束当前函数并返回：None（没有值）。 |
| 558 | `             self.channels = selected ` | 把结果保存到 self.channels：selected。 |
| 559 | `             self.count.set(str(len(selected))) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：str(len(selected))。 |
| 560 | `             if self.reference.get() not in selected: ` | 检查条件 self.reference.get() not in selected；为真时执行下面缩进的一组语句。 |
| 561 | `                 self.reference.set(selected[0]) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：selected[0]。 |
| 562 | `             self.update_channel_label() ` | 更新参考下拉框与通道摘要文字。。 |
| 563 | `             self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 564 | `             dialog.destroy() ` | 销毁窗口及控件。 |
| 565 | `         ttk.Button(dialog, text='Use selected channels', command=commit).pack(pady=12) ` | 创建按钮；参数：dialog, text='Use selected channels', command=commit；随后用顺序布局安排控件；side 决定方向，fill 决定填充，expand 决定随窗口扩展；参数：pady=12。 |
| 566 | `         dialog.transient(self.root) ` | 调用 dialog.transient；参数：self.root。 |
| 567 | `         dialog.grab_set() ` | 调用 dialog.grab_set。 |
| 568 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 569 | `     def remove_record(self): ` | 定义 remove_record(self)。从软件的清单中移除选中记录，不删除原始 BDF。 定义到这里时不执行函数体。 |
| 570 | `         if self.selected is not None: ` | 检查条件 self.selected is not None；为真时执行下面缩进的一组语句。 |
| 571 | `             self.records.pop(self.selected) ` | 取出并移除指定项；参数：self.selected。 |
| 572 | `             self.refresh_records() ` | 重新填充文件列表，默认选择第一条，或在空列表时显示无文件。。 |
| 573 | `             if not self.records: ` | 检查条件 not self.records；为真时执行下面缩进的一组语句。 |
| 574 | `                 self.channels, self.info = ([], None) ` | 把结果保存到 (self.channels, self.info)：组装元组：([], None)。 |
| 575 | `                 self.update_channel_label() ` | 更新参考下拉框与通道摘要文字。。 |
| 576 | `             self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 577 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 578 | `     def clear_records(self): ` | 定义 clear_records(self)。清空已加载记录及通道状态，不删除硬盘上的数据。 定义到这里时不执行函数体。 |
| 579 | `         self.records, self.channels, self.info = ([], [], None) ` | 把结果保存到 (self.records, self.channels, self.info)：组装元组：([], [], None)。 |
| 580 | `         self.refresh_records() ` | 重新填充文件列表，默认选择第一条，或在空列表时显示无文件。。 |
| 581 | `         self.update_channel_label() ` | 更新参考下拉框与通道摘要文字。。 |
| 582 | `         self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 583 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 584 | `     def prepare(self, all_records=False): ` | 定义 prepare(self, all_records=False)。保存待确认的表单编辑，检查参数，选择本次分析范围，并复制输入防止计算期间被修改。 定义到这里时不执行函数体。 |
| 585 | `         if not self.apply_record(): ` | 检查条件 not self.apply_record()；为真时执行下面缩进的一组语句。 |
| 586 | `             return None ` | 结束当前函数并返回：None（未知/未设置）。 |
| 587 | `         values = asdict(self.settings) ` | 把结果保存到 values：把数据类递归转换成字典；参数：self.settings。 |
| 588 | `         for key, var in self.limit_vars.items(): ` | 遍历 self.limit_vars.items()，每次把一项赋给 (key, var)，执行下面缩进的循环体。 |
| 589 | `             raw = var.get().strip() ` | 把结果保存到 raw：去掉文本两端空白。 |
| 590 | `             values[key] = None if raw == '' and key in ('thd_limit_pct', 'frequency_limit_pct') else float(raw) ` | 把结果保存到 values[key]：若 raw == '' and key in ('thd_limit_pct', 'frequency_limit_pct')，用 None；否则用 float(raw)。 |
| 591 | `         values['analysis_mode'] = self.analysis_mode() ` | 把结果保存到 values['analysis_mode']：把界面可读的工作流名称转换为 bench_sine、bench_pulse 或 ecg。。 |
| 592 | `         values['bench_windows'] = self.windowed.get() ` | 把结果保存到 values['bench_windows']：读取当前值；若是 dict.get，缺少键时可返回指定默认值。 |
| 593 | `         settings = AnalysisSettings(**values) ` | 把结果保存到 settings：创建一套分析设置；参数：None=values。 |
| 594 | `         settings.validate() ` | 调用 settings.validate。 |
| 595 | `         if int(self.count.get()) != len(self.channels): ` | 检查条件 int(self.count.get()) != len(self.channels)；为真时执行下面缩进的一组语句。 |
| 596 | `             raise ValueError('Count changed. Click Apply count to select actual BDF channels') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Count changed. Click Apply count to select actual BDF channels'；上层可捕获并显示原因。 |
| 597 | `         reference = self.reference.get() if settings.analysis_mode != 'ecg' else '' ` | 把结果保存到 reference：若 settings.analysis_mode != 'ecg'，用 self.reference.get()；否则用 ''。 |
| 598 | `         records = self.records ` | 把结果保存到 records：读取 self 的 records 属性。 |
| 599 | `         if not all_records and self.analysis_target.get() == 'Selected record': ` | 检查条件 not all_records and self.analysis_target.get() == 'Selected record'；为真时执行下面缩进的一组语句。 |
| 600 | `             if self.selected is None: ` | 检查条件 self.selected is None；为真时执行下面缩进的一组语句。 |
| 601 | `                 raise ValueError('Select a record in the left-hand list') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Select a record in the left-hand list'；上层可捕获并显示原因。 |
| 602 | `             records = [self.records[self.selected]] ` | 把结果保存到 records：组装列表：[self.records[self.selected]]。 |
| 603 | `         AnalysisService(settings)._validate(records, self.channels, reference) ` | 调用 AnalysisService(settings)._validate；参数：records, self.channels, reference。 |
| 604 | `         return (copy.deepcopy(records), settings, list(self.channels), reference) ` | 结束当前函数并返回：组装元组：(copy.deepcopy(records), settings, list(self.channels), reference)。 |
| 605 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 606 | `     def load_path(self, path): ` | 定义 load_path(self, path)。恢复 JSON 项目与躯干显示设置，读取文件头核对，再更新 GUI。 定义到这里时不执行函数体。 |
| 607 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 608 | `             records, settings, channels, reference = load_project(path) ` | 把结果保存到 (records, settings, channels, reference)：读取 JSON、兼容旧字段、解析相对路径、过滤允许的设置字段并校验。；参数：path。 |
| 609 | `             display = json.loads(Path(path).read_text(encoding='utf-8-sig')).get('display', {}) ` | 把结果保存到 display：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：'display', {}。 |
| 610 | `             layout = TorsoLayout(**display.get('torso', {})) ` | 把结果保存到 layout：创建躯干示意方向设置；参数：None=display.get('torso', {})。 |
| 611 | `             if not records: ` | 检查条件 not records；为真时执行下面缩进的一组语句。 |
| 612 | `                 raise ValueError('Project contains no BDF records') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Project contains no BDF records'；上层可捕获并显示原因。 |
| 613 | `             BdfReader().inspect(records[0]) ` | 只读头信息，核对格式/长度，返回通道名、采样率、时长，过滤 Status/Annotations。；参数：records[0]。 |
| 614 | `             self.records, self.settings = (records, settings) ` | 把结果保存到 (self.records, self.settings)：组装元组：(records, settings)。 |
| 615 | `             self.torso_layout = layout ` | 把结果保存到 self.torso_layout：layout。 |
| 616 | `             if self.torso_window is not None: ` | 检查条件 self.torso_window is not None；为真时执行下面缩进的一组语句。 |
| 617 | `                 self.torso_window.set_layout(layout) ` | 调用 self.torso_window.set_layout；参数：layout。 |
| 618 | `             self.loading = True ` | 把结果保存到 self.loading：True（是）。 |
| 619 | `             self.windowed.set(settings.bench_windows) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：settings.bench_windows。 |
| 620 | `             for key, var in self.limit_vars.items(): ` | 遍历 self.limit_vars.items()，每次把一项赋给 (key, var)，执行下面缩进的循环体。 |
| 621 | `                 var.set('' if getattr(settings, key) is None else str(getattr(settings, key))) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'' if getattr(settings, key) is None else str(getattr(settings, key))。 |
| 622 | `             self.profile.set(next((k for k, v in PROFILES.items() if v == settings.analysis_mode))) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：next((k for k, v in PROFILES.items() if v == settings.analysis_mode))。 |
| 623 | `             self.loading = False ` | 把结果保存到 self.loading：False（否）。 |
| 624 | `             self.change_profile() ` | 切换工作流后更新指标列表和提示；脉冲移除 SNR/SINAD/THD 选项，然后清空旧结果。。 |
| 625 | `             self.refresh_records() ` | 重新填充文件列表，默认选择第一条，或在空列表时显示无文件。。 |
| 626 | `             self.initialize_channels(channels, reference) ` | 读取第一份文件头，选择实际存在的电压通道，并设置参考和数量。；参数：channels, reference。 |
| 627 | `             self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 628 | `             self.status.set(f'Loaded {len(records)} records. Verify wiring and input calibration.') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：f'Loaded {len(records)} records. Verify wiring and input calibration.'。 |
| 629 | `         except (ValueError, OSError, KeyError, TypeError) as exc: ` | 捕获 (ValueError, OSError, KeyError, TypeError) 异常，保存到 exc，执行错误处理。 |
| 630 | `             self.loading = False ` | 把结果保存到 self.loading：False（否）。 |
| 631 | `             messagebox.showerror('Project load failed', str(exc)) ` | 弹出错误提示；参数：'Project load failed', str(exc)。 |
| 632 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 633 | `     def load_dialog(self): ` | 定义 load_dialog(self)。弹出 JSON 项目选择框，再调用 load_path。 定义到这里时不执行函数体。 |
| 634 | `         path = filedialog.askopenfilename(filetypes=[('JSON project', '*.json')]) ` | 把结果保存到 path：调用 filedialog.askopenfilename；参数：filetypes=[('JSON project', '*.json')]。 |
| 635 | `         if path: ` | 检查条件 path；为真时执行下面缩进的一组语句。 |
| 636 | `             self.load_path(path) ` | 恢复 JSON 项目与躯干显示设置，读取文件头核对，再更新 GUI。；参数：path。 |
| 637 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 638 | `     def load_lab(self): ` | 定义 load_lab(self)。根据所选实验预设查找 ZIP，自动选 10 或 128 个通道；输入校准和重复组仍需人工确认。 定义到这里时不执行函数体。 |
| 639 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 640 | `             label = self.lab_choice.get() ` | 把结果保存到 label：读取当前值；若是 dict.get，缺少键时可返回指定默认值。 |
| 641 | `             patterns = {'10 electrodes - Sine': '*10 Active*Sine*.zip', '128 electrodes - Sine': '*All electrodes_Sine*.zip', '128 electrodes - Pulse': '*All electrodes_Pulse*.zip', '10 electrodes - ECG': '*10 Active*ECG*.zip'} ` | 把结果保存到 patterns：组装字典，键用于给数值/设置命名：{'10 electrodes - Sine': '*10 Active*Sine*.zip', '128 electrodes - Sine': '*All electrodes_Sine*.zip', '128 electrodes - Pulse': '*All electrodes_Pulse*.zip', '…（完整表达式见左栏）。 |
| 642 | `             paths = list((HERE.parent / 'latest lab check').glob(patterns[label])) ` | 把结果保存到 paths：构造列表；参数：(HERE.parent / 'latest lab check').glob(patterns[label])。 |
| 643 | `             if not paths: ` | 检查条件 not paths；为真时执行下面缩进的一组语句。 |
| 644 | `                 raise ValueError('Latest lab archive not found. Use Open BDF / ZIP instead') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Latest lab archive not found. Use Open BDF / ZIP instead'；上层可捕获并显示原因。 |
| 645 | `             self.records = records_from_paths([sorted(paths)[-1]]) ` | 把结果保存到 self.records：调用 records_from_paths；参数：[sorted(paths)[-1]]。 |
| 646 | `             self.count.set('128' if label.startswith('128') else '10') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'128' if label.startswith('128') else '10'。 |
| 647 | `             self.suggest_mode(self.records) ` | 当导入文件声明为同一类波形时，自动建议对应工作流；名称提示不验证真实波形。；参数：self.records。 |
| 648 | `             self.refresh_records() ` | 重新填充文件列表，默认选择第一条，或在空列表时显示无文件。。 |
| 649 | `             self.initialize_channels() ` | 读取第一份文件头，选择实际存在的电压通道，并设置参考和数量。。 |
| 650 | `             self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 651 | `             self.status.set('Latest lab loaded. Input amplitudes are unconfirmed; no repeat groups were assigned automatically.') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Latest lab loaded. Input amplitudes are unconfirmed; no repeat groups were assigned automatically.'。 |
| 652 | `         except (ValueError, OSError) as exc: ` | 捕获 (ValueError, OSError) 异常，保存到 exc，执行错误处理。 |
| 653 | `             messagebox.showerror('Lab preset', str(exc)) ` | 弹出错误提示；参数：'Lab preset', str(exc)。 |
| 654 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 655 | `     def save_dialog(self): ` | 定义 save_dialog(self)。取全部记录及配置，保存项目 JSON；即使分析只选了一份也不丢掉其余记录。 定义到这里时不执行函数体。 |
| 656 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 657 | `             request = self.prepare(all_records=True) ` | 把结果保存到 request：保存待确认的表单编辑，检查参数，选择本次分析范围，并复制输入防止计算期间被修改。；参数：all_records=True。 |
| 658 | `             if request is None: ` | 检查条件 request is None；为真时执行下面缩进的一组语句。 |
| 659 | `                 return ` | 结束当前函数并返回：None（没有值）。 |
| 660 | `             path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON project', '*.json')]) ` | 把结果保存到 path：调用 filedialog.asksaveasfilename；参数：defaultextension='.json', filetypes=[('JSON project', '*.json')]。 |
| 661 | `             if path: ` | 检查条件 path；为真时执行下面缩进的一组语句。 |
| 662 | `                 save_project(path, *request, display={'torso':asdict(self.torso_layout)}) ` | 把记录和设置的数据类转成 JSON，保留通道、参考与可选布局信息。；参数：path, *request, display={'torso': asdict(self.torso_layout)}。 |
| 663 | `         except (ValueError, OSError) as exc: ` | 捕获 (ValueError, OSError) 异常，保存到 exc，执行错误处理。 |
| 664 | `             messagebox.showerror('Save failed', str(exc)) ` | 弹出错误提示；参数：'Save failed', str(exc)。 |
| 665 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 666 | `     def load_demo(self): ` | 定义 load_demo(self)。生成对应模式的合成数据；台架窗口演示使用 10–20 秒幅度故障，随后自动运行。 定义到这里时不执行函数体。 |
| 667 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 668 | `             count = int(self.count.get()) ` | 把结果保存到 count：转换为整数；参数：self.count.get()。 |
| 669 | `             if not 1 <= count <= 256: ` | 检查条件 not 1 <= count <= 256；为真时执行下面缩进的一组语句。 |
| 670 | `                 raise ValueError('Demo supports 1 to 256 electrodes') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Demo supports 1 to 256 electrodes'；上层可捕获并显示原因。 |
| 671 | `             if self.analysis_mode() == 'bench_sine' and self.windowed.get(): ` | 检查条件 self.analysis_mode() == 'bench_sine' and self.windowed.get()；为真时执行下面缩进的一组语句。 |
| 672 | `                 self.records = create_timeline_demo(HERE / 'output/synthetic_inputs', count) ` | 把结果保存到 self.records：调用 create_timeline_demo；参数：HERE / 'output/synthetic_inputs', count。 |
| 673 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 674 | `                 self.records = create_mode_demo(HERE / 'output/synthetic_inputs', count, self.analysis_mode()) ` | 把结果保存到 self.records：按模式选择正弦演示，或生成 30 秒脉冲/ECG 数据并注入特定故障。；参数：HERE / 'output/synthetic_inputs', count, self.analysis_mode()。 |
| 675 | `             self.refresh_records() ` | 重新填充文件列表，默认选择第一条，或在空列表时显示无文件。。 |
| 676 | `             self.initialize_channels() ` | 读取第一份文件头，选择实际存在的电压通道，并设置参考和数量。。 |
| 677 | `             self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 678 | `             self.run() ` | 取得固定的分析请求，启动后台工作线程，再安排主线程轮询消息。。 |
| 679 | `         except (ValueError, OSError) as exc: ` | 捕获 (ValueError, OSError) 异常，保存到 exc，执行错误处理。 |
| 680 | `             messagebox.showerror('Demo', str(exc)) ` | 弹出错误提示；参数：'Demo', str(exc)。 |
| 681 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 682 | `     def set_busy(self, busy): ` | 定义 set_busy(self, busy)。分析期间锁定输入并启动进度动画；完成后恢复适用于当前模式的控件。 定义到这里时不执行函数体。 |
| 683 | `         self.busy = busy ` | 把结果保存到 self.busy：busy。 |
| 684 | `         if busy: ` | 检查条件 busy；为真时执行下面缩进的一组语句。 |
| 685 | `             self.timeline.clear('Calculating windows in the background...') ` | 清空容器，或调用该视图定义的清除方法；参数：'Calculating windows in the background...'。 |
| 686 | `         self.record_tree.configure(selectmode='none' if busy else 'browse') ` | 更新控件属性或状态，不计算信号指标；参数：selectmode='none' if busy else 'browse'。 |
| 687 | `         for w in self.controls: ` | 遍历 self.controls，每次把一项赋给 w，执行下面缩进的循环体。 |
| 688 | `             w.configure(state='disabled' if busy else 'normal') ` | 更新控件属性或状态，不计算信号指标；参数：state='disabled' if busy else 'normal'。 |
| 689 | `         for w in self.combos: ` | 遍历 self.combos，每次把一项赋给 w，执行下面缩进的循环体。 |
| 690 | `             w.configure(state='disabled' if busy else 'readonly') ` | 更新控件属性或状态，不计算信号指标；参数：state='disabled' if busy else 'readonly'。 |
| 691 | `         self.context_states() ` | 按当前模式和忙碌状态启用/禁用相关控件，ECG 总是使用窗口而不要求同步参考。。 |
| 692 | `         if busy: ` | 检查条件 busy；为真时执行下面缩进的一组语句。 |
| 693 | `             self.progress.start(15) ` | 调用 self.progress.start；参数：15。 |
| 694 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 695 | `             self.progress.stop() ` | 调用 self.progress.stop。 |
| 696 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 697 | `     def run(self): ` | 定义 run(self)。取得固定的分析请求，启动后台工作线程，再安排主线程轮询消息。 定义到这里时不执行函数体。 |
| 698 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 699 | `             request = self.prepare() ` | 把结果保存到 request：保存待确认的表单编辑，检查参数，选择本次分析范围，并复制输入防止计算期间被修改。。 |
| 700 | `             if request is None: ` | 检查条件 request is None；为真时执行下面缩进的一组语句。 |
| 701 | `                 return ` | 结束当前函数并返回：None（没有值）。 |
| 702 | `             records, settings, channels, reference = request ` | 把结果保存到 (records, settings, channels, reference)：request。 |
| 703 | `             self.invalidate() ` | 丢弃当前结果、时间轴缓存、选点及显示，避免输入变了还显示旧的绿色。。 |
| 704 | `             self.set_busy(True) ` | 分析期间锁定输入并启动进度动画；完成后恢复适用于当前模式的控件。；参数：True。 |
| 705 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 706 | `             def worker(): ` | 定义 worker()。后台调用 AnalysisService，只向队列写进度/成功/错误，不直接操作 Tk 控件。 定义到这里时不执行函数体。 |
| 707 | `                 try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 708 | `                     result = AnalysisService(settings).analyze(records, channels, reference, lambda text: self.events.put(('progress', text))) ` | 把结果保存到 result：台架分支先测整段，再按需逐窗口重复同样的测量，最后做跨记录线性/重复性；ECG 走独立分支。；参数：records, channels, reference, lambda text: self.events.put(('progress', text))。 |
| 709 | `                     self.events.put(('done', result)) ` | 向线程安全消息队列提交一条消息；参数：('done', result)。 |
| 710 | `                 except Exception as exc: ` | 捕获 Exception 异常，保存到 exc，执行错误处理。 |
| 711 | `                     self.events.put(('error', str(exc))) ` | 向线程安全消息队列提交一条消息；参数：('error', str(exc))。 |
| 712 | `             threading.Thread(target=worker, daemon=True).start() ` | 启动后台工作线程运行 worker；主线程继续处理窗口事件。daemon 让进程退出时不被该线程阻止。 |
| 713 | `             self.root.after(80, self.poll) ` | 请 Tk 在约 80 ms 后调用 poll；立即返回，不阻塞窗口。 |
| 714 | `         except (ValueError, OSError, KeyError) as exc: ` | 捕获 (ValueError, OSError, KeyError) 异常，保存到 exc，执行错误处理。 |
| 715 | `             messagebox.showerror('Cannot start analysis', str(exc)) ` | 弹出错误提示；参数：'Cannot start analysis', str(exc)。 |
| 716 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 717 | `     def poll(self): ` | 定义 poll(self)。主线程取队列消息，更新进度或接收结果；忙碌时 80 ms 后再次检查。 定义到这里时不执行函数体。 |
| 718 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 719 | `             while True: ` | 只要 True 为真就重复循环；退出依靠条件改变、break 或异常。 |
| 720 | `                 event, payload = self.events.get_nowait() ` | 把结果保存到 (event, payload)：非阻塞读取队列；空队列抛 queue.Empty。 |
| 721 | `                 if event == 'progress': ` | 检查条件 event == 'progress'；为真时执行下面缩进的一组语句。 |
| 722 | `                     self.status.set(payload) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：payload。 |
| 723 | `                 else: ` | 前面对应条件不成立时，进入此分支。 |
| 724 | `                     self.set_busy(False) ` | 分析期间锁定输入并启动进度动画；完成后恢复适用于当前模式的控件。；参数：False。 |
| 725 | `                     if event == 'error': ` | 检查条件 event == 'error'；为真时执行下面缩进的一组语句。 |
| 726 | `                         self.status.set('Analysis failed. Check record, channel and mode settings.') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Analysis failed. Check record, channel and mode settings.'。 |
| 727 | `                         messagebox.showerror('Analysis failed', payload) ` | 弹出错误提示；参数：'Analysis failed', payload。 |
| 728 | `                     else: ` | 前面对应条件不成立时，进入此分支。 |
| 729 | `                         self.accept_result(payload) ` | 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：payload。 |
| 730 | `         except queue.Empty: ` | 捕获 queue.Empty 异常，执行错误处理。 |
| 731 | `             pass ` | 此分支不额外操作，用 pass 保留合法语法。 |
| 732 | `         if self.busy: ` | 检查条件 self.busy；为真时执行下面缩进的一组语句。 |
| 733 | `             self.root.after(80, self.poll) ` | 请 Tk 在约 80 ms 后调用 poll；立即返回，不阻塞窗口。 |
| 734 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 735 | `     def accept_result(self, result): ` | 定义 accept_result(self, result)。保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。 定义到这里时不执行函数体。 |
| 736 | `         self.result = result ` | 把结果保存到 self.result：result。 |
| 737 | `         self.settings = AnalysisSettings(**result.settings) ` | 把结果保存到 self.settings：创建一套分析设置；参数：None=result.settings。 |
| 738 | `         self.result_scopes = {f'Record: {r.record.id}': ('record', r.record.id) for r in result.runs} ` | 把结果保存到 self.result_scopes：从 result.runs 逐个取 r，为每项生成 f'Record: {r.record.id}': ('record', r.record.id)。 |
| 739 | `         for i, frame in enumerate(result.frames): ` | 遍历 enumerate(result.frames)，每次把一项赋给 (i, frame)，执行下面缩进的循环体。 |
| 740 | `             self.result_scopes[f"Window: {frame['record_id']} \| {frame['start_s']:g}-{frame['end_s']:g} s"] = ('frame', i) ` | 把结果保存到 self.result_scopes[f"Window: {frame['record_id']} &#124; {frame['start_s']:g}-{frame['end_s']:g} s"]：组装元组：('frame', i)。 |
| 741 | `         # Only an explicit choice displays the worst case across multiple files. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 742 | `         if len(result.runs) > 1: ` | 检查条件 len(result.runs) > 1；为真时执行下面缩进的一组语句。 |
| 743 | `             self.result_scopes['All analyzed records / worst case'] = ('all', None) ` | 把结果保存到 self.result_scopes['All analyzed records / worst case']：组装元组：('all', None)。 |
| 744 | `         self.frame_labels = list(self.result_scopes) ` | 把结果保存到 self.frame_labels：构造列表；参数：self.result_scopes。 |
| 745 | `         self.window_combo.configure(values=self.frame_labels, state='readonly') ` | 更新控件属性或状态，不计算信号指标；参数：values=self.frame_labels, state='readonly'。 |
| 746 | `         record_id = self.records[self.selected].id if self.selected is not None else result.runs[0].record.id ` | 把结果保存到 record_id：若 self.selected is not None，用 self.records[self.selected].id；否则用 result.runs[0].record.id。 |
| 747 | `         self.scope.set(self.label_for_record(record_id) or self.frame_labels[0]) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：self.label_for_record(record_id) or self.frame_labels[0]。 |
| 748 | `         first_window = next((label for label, (kind, value) in self.result_scopes.items() ` | 把结果保存到 first_window：取迭代器的下一项或匹配到的第一项；参数：(label for label, (kind, value) in self.result_scopes.items() if kind == 'frame' and result.frames[value]['record_id'] == record_id), None。 |
| 749 | `                              if kind == 'frame' and result.frames[value]['record_id'] == record_id), None) ` | 接续第 748 行的同一条语句，不是另起一段算法。 把结果保存到 first_window：取迭代器的下一项或匹配到的第一项；参数：(label for label, (kind, value) in self.result_scopes.items() if kind == 'frame' and result.frames[value]['record_id'] == record_id), None。 |
| 750 | `         if first_window: ` | 检查条件 first_window；为真时执行下面缩进的一组语句。 |
| 751 | `             self.scope.set(first_window) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：first_window。 |
| 752 | `         demo = all((r.record.id.startswith('DEMO_') for r in result.runs)) ` | 把结果保存到 demo：要求所有条件为真；参数：(r.record.id.startswith('DEMO_') for r in result.runs)。 |
| 753 | `         tail = sum((r.channels[result.electrodes[0].name].get('unassessed_tail_s', 0) for r in result.runs)) ` | 把结果保存到 tail：求和；参数：(r.channels[result.electrodes[0].name].get('unassessed_tail_s', 0) for r in result.runs)。 |
| 754 | `         excluded = sum(r.excluded_tail_s for r in result.runs) ` | 把结果保存到 excluded：求和；参数：(r.excluded_tail_s for r in result.runs)。 |
| 755 | `         windowed = self.analysis_mode() == 'ecg' or result.settings.get('bench_windows', False) ` | 把结果保存到 windowed：self.analysis_mode() == 'ecg' or result.settings.get('bench_windows', False)。 |
| 756 | `         self.status.set(('SYNTHETIC DEMO \| ' if demo else '') + f'{len(result.runs)} BDF \| {len(result.electrodes)} electrodes \| {result.elapsed_s:.2f} s analysis' + (f' \| {len(result.frames)} complete windows \| {tail:g} s without a complete window' if windowed else '') + f' \| {excluded:g} s excluded in total') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：('SYNTHETIC DEMO &#124; ' if demo else '') + f'{len(result.runs)} BDF &#124; {len(result.electrodes)} electrodes &#124; {result.elapsed_s:.2f} s analysis' + (f'…（完整表达式见左栏）。 |
| 757 | `         self.notebook.select(0) ` | 调用 self.notebook.select；参数：0。 |
| 758 | `         self.redraw() ` | 从已有结果更新热图、躯干、颜色计数、结果表和详情。。 |
| 759 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 760 | `     def label_for_record(self, record_id): ` | 定义 label_for_record(self, record_id)。找到某个记录 ID 对应的显示范围名称。 定义到这里时不执行函数体。 |
| 761 | `         return next((label for label, value in self.result_scopes.items() if value == ('record', record_id)), None) ` | 结束当前函数并返回：取迭代器的下一项或匹配到的第一项；参数：(label for label, value in self.result_scopes.items() if value == ('record', record_id)), None。 |
| 762 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 763 | `     def change_scope(self, _=None): ` | 定义 change_scope(self, _=None)。用户选择整段/窗口/整批时暂停播放，同步文件选择，再刷新显示。 定义到这里时不执行函数体。 |
| 764 | `         self.timeline.pause() ` | 调用 self.timeline.pause。 |
| 765 | `         if self.torso_window is not None: ` | 检查条件 self.torso_window is not None；为真时执行下面缩进的一组语句。 |
| 766 | `             self.torso_window.timeline.pause() ` | 调用 self.torso_window.timeline.pause。 |
| 767 | `         label = self.scope.get() ` | 把结果保存到 label：读取当前值；若是 dict.get，缺少键时可返回指定默认值。 |
| 768 | `         kind, value = self.result_scopes.get(self.scope.get(), ('all', None)) ` | 把结果保存到 (kind, value)：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：self.scope.get(), ('all', None)。 |
| 769 | `         if kind in ('record', 'frame'): ` | 检查条件 kind in ('record', 'frame')；为真时执行下面缩进的一组语句。 |
| 770 | `             record_id = value if kind == 'record' else self.result.frames[value]['record_id'] ` | 把结果保存到 record_id：若 kind == 'record'，用 value；否则用 self.result.frames[value]['record_id']。 |
| 771 | `             index = next((i for i, r in enumerate(self.records) if r.id == record_id), None) ` | 把结果保存到 index：取迭代器的下一项或匹配到的第一项；参数：(i for i, r in enumerate(self.records) if r.id == record_id), None。 |
| 772 | `             if index is not None: ` | 检查条件 index is not None；为真时执行下面缩进的一组语句。 |
| 773 | `                 self.record_tree.selection_set(str(index)) ` | 设置选中行；参数：str(index)。 |
| 774 | `                 self.select_record() ` | 切换记录时保存上一份编辑，再加载新记录的参数；若它已被分析，切换到该文件自己的结果。。 |
| 775 | `             self.scope.set(label) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：label。 |
| 776 | `         self.redraw() ` | 从已有结果更新热图、躯干、颜色计数、结果表和详情。。 |
| 777 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 778 | `     def select_window(self, index, source='main'): ` | 定义 select_window(self, index, source='main')。将时间轴提供的全局窗口索引映射到显示范围，并同步主窗口和躯干窗口。 定义到这里时不执行函数体。 |
| 779 | `         if self.result is None: ` | 检查条件 self.result is None；为真时执行下面缩进的一组语句。 |
| 780 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 781 | `         if source == 'torso': ` | 检查条件 source == 'torso'；为真时执行下面缩进的一组语句。 |
| 782 | `             self.timeline.pause() ` | 调用 self.timeline.pause。 |
| 783 | `         elif self.torso_window is not None: ` | 检查条件 self.torso_window is not None；为真时执行下面缩进的一组语句。 |
| 784 | `             self.torso_window.timeline.pause() ` | 调用 self.torso_window.timeline.pause。 |
| 785 | `         label = next(label for label, value in self.result_scopes.items() if value == ('frame', index)) ` | 把结果保存到 label：取迭代器的下一项或匹配到的第一项；参数：(label for label, value in self.result_scopes.items() if value == ('frame', index))。 |
| 786 | `         self.scope.set(label) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：label。 |
| 787 | `         self.redraw() ` | 从已有结果更新热图、躯干、颜色计数、结果表和详情。。 |
| 788 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 789 | `     def displayed_electrodes(self): ` | 定义 displayed_electrodes(self)。只取当前整段、窗口或整批范围的电极结果；这个函数不重新算指标。 定义到这里时不执行函数体。 |
| 790 | `         if self.result is None: ` | 检查条件 self.result is None；为真时执行下面缩进的一组语句。 |
| 791 | `             return [] ` | 结束当前函数并返回：组装列表：[]。 |
| 792 | `         kind, value = self.result_scopes.get(self.scope.get(), ('all', None)) ` | 把结果保存到 (kind, value)：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：self.scope.get(), ('all', None)。 |
| 793 | `         if kind == 'record': ` | 检查条件 kind == 'record'；为真时执行下面缩进的一组语句。 |
| 794 | `             return self.result.record_electrodes(value) ` | 结束当前函数并返回：调用 self.result.record_electrodes；参数：value。 |
| 795 | `         if kind == 'frame': ` | 检查条件 kind == 'frame'；为真时执行下面缩进的一组语句。 |
| 796 | `             return self.result.window_electrodes(value) ` | 结束当前函数并返回：调用 self.result.window_electrodes；参数：value。 |
| 797 | `         return self.result.electrodes ` | 结束当前函数并返回：读取 self.result 的 electrodes 属性。 |
| 798 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 799 | `     def update_timeline(self, mode): ` | 定义 update_timeline(self, mode)。按记录和指标缓存窗口最差颜色，并传给时间轴；同步项不把参考自比较算成警告。 定义到这里时不执行函数体。 |
| 800 | `         kind, value = self.result_scopes.get(self.scope.get(), ('all', None)) ` | 把结果保存到 (kind, value)：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：self.scope.get(), ('all', None)。 |
| 801 | `         record_id = (self.result.frames[value]['record_id'] if kind == 'frame' else value if kind == 'record' ` | 把结果保存到 record_id：若 kind == 'frame'，用 self.result.frames[value]['record_id']；否则用 value if kind == 'record' else self.records[self.selected].id if self.selected is not None…（完整表达式见左栏）。 |
| 802 | `                      else self.records[self.selected].id if self.selected is not None else self.result.runs[0].record.id) ` | 接续第 801 行的同一条语句，不是另起一段算法。 把结果保存到 record_id：若 kind == 'frame'，用 self.result.frames[value]['record_id']；否则用 value if kind == 'record' else self.records[self.selected].id if self.selected is not None…（完整表达式见左栏）。 |
| 803 | `         key = (id(self.result), record_id, mode) ` | 把结果保存到 key：组装元组：(id(self.result), record_id, mode)。 |
| 804 | `         if key not in self.timeline_cache: ` | 检查条件 key not in self.timeline_cache；为真时执行下面缩进的一组语句。 |
| 805 | `             rank = {'green': 0, 'yellow': 1, 'red': 2} ` | 把结果保存到 rank：组装字典，键用于给数值/设置命名：{'green': 0, 'yellow': 1, 'red': 2}。 |
| 806 | `             items = [] ` | 把结果保存到 items：组装列表：[]。 |
| 807 | `             for i, frame in enumerate(self.result.frames): ` | 遍历 enumerate(self.result.frames)，每次把一项赋给 (i, frame)，执行下面缩进的循环体。 |
| 808 | `                 if frame['record_id'] != record_id: ` | 检查条件 frame['record_id'] != record_id；为真时执行下面缩进的一组语句。 |
| 809 | `                     continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 810 | `                 colors = [e.metric(mode).color for e in self.result.window_electrodes(i) ` | 把结果保存到 colors：从 self.result.window_electrodes(i) 逐个取 e，仅保留 not (mode == 'synchronization' and e.is_reference)，为每项生成 e.metric(mode).color。 |
| 811 | `                           if not (mode == 'synchronization' and e.is_reference)] ` | 接续第 810 行的同一条语句，不是另起一段算法。 把结果保存到 colors：从 self.result.window_electrodes(i) 逐个取 e，仅保留 not (mode == 'synchronization' and e.is_reference)，为每项生成 e.metric(mode).color。 |
| 812 | `                 color = max(colors, key=rank.get) if colors else 'yellow' ` | 把结果保存到 color：若 colors，用 max(colors, key=rank.get)；否则用 'yellow'。 |
| 813 | `                 items.append((i, frame['start_s'], frame['end_s'], color)) ` | 把一项加入列表末尾；参数：(i, frame['start_s'], frame['end_s'], color)。 |
| 814 | `             self.timeline_cache[key] = items ` | 把结果保存到 self.timeline_cache[key]：items。 |
| 815 | `         ecg = self.analysis_mode() == 'ecg' ` | 把结果保存到 ecg：self.analysis_mode() == 'ecg'。 |
| 816 | `         run = next(r for r in self.result.runs if r.record.id == record_id) ` | 把结果保存到 run：取迭代器的下一项或匹配到的第一项；参数：(r for r in self.result.runs if r.record.id == record_id)。 |
| 817 | `         duration = self.result.settings['ecg_window_s' if ecg else 'bench_window_s'] ` | 把结果保存到 duration：按索引/键 'ecg_window_s' if ecg else 'bench_window_s' 取 self.result.settings 的内容。 |
| 818 | `         message = (f'Recorded {run.recorded_duration_s:g} s; retained {run.duration_s:g} s after excluding {run.excluded_tail_s:g} s; need {duration:g} s. No complete windows.' ` | 把结果保存到 message：若 run.duration_s < duration，用 f'Recorded {run.recorded_duration_s:g} s; retained {run.duration_s:g} s after excluding {r…（完整表达式见左栏）；否则用 'Enable Build time windows and run analysis.'。 |
| 819 | `                    if run.duration_s < duration else 'Enable Build time windows and run analysis.') ` | 接续第 818 行的同一条语句，不是另起一段算法。 把结果保存到 message：若 run.duration_s < duration，用 f'Recorded {run.recorded_duration_s:g} s; retained {run.duration_s:g} s after excluding {r…（完整表达式见左栏）；否则用 'Enable Build time windows and run analysis.'。 |
| 820 | `         self.timeline.show((id(self.result), record_id), self.timeline_cache[key], ` | 调用 self.timeline.show；参数：(id(self.result), record_id), self.timeline_cache[key], current=value if kind == 'frame' else None, message=message。 |
| 821 | `                            current=value if kind == 'frame' else None, message=message) ` | 接续第 820 行的同一条语句，不是另起一段算法。 调用 self.timeline.show；参数：(id(self.result), record_id), self.timeline_cache[key], current=value if kind == 'frame' else None, message=message。 |
| 822 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 823 | `     def redraw(self): ` | 定义 redraw(self)。从已有结果更新热图、躯干、颜色计数、结果表和详情。 定义到这里时不执行函数体。 |
| 824 | `         if self.result is None: ` | 检查条件 self.result is None；为真时执行下面缩进的一组语句。 |
| 825 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 826 | `         electrodes = self.displayed_electrodes() ` | 把结果保存到 electrodes：只取当前整段、窗口或整批范围的电极结果；这个函数不重新算指标。。 |
| 827 | `         mode = self.views[self.mode.get()] ` | 把结果保存到 mode：按索引/键 self.mode.get() 取 self.views 的内容。 |
| 828 | `         self.update_timeline(mode) ` | 按记录和指标缓存窗口最差颜色，并传给时间轴；同步项不把参考自比较算成警告。；参数：mode。 |
| 829 | `         self.heatmap.show(electrodes, mode) ` | 调用 self.heatmap.show；参数：electrodes, mode。 |
| 830 | `         if self.torso_window is not None: ` | 检查条件 self.torso_window is not None；为真时执行下面缩进的一组语句。 |
| 831 | `             kind,value = self.result_scopes.get(self.scope.get(), ('all',None)) ` | 把结果保存到 (kind, value)：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：self.scope.get(), ('all', None)。 |
| 832 | `             self.torso_window.show(electrodes,mode,self.scope.get(),list(self.views),self.timeline.key, ` | 调用 self.torso_window.show；参数：electrodes, mode, self.scope.get(), list(self.views), self.timeline.key, self.timeline.items, value if kind == 'frame' else None, self.timeline.c…（完整表达式见左栏）。 |
| 833 | `                                    self.timeline.items,value if kind=='frame' else None,self.timeline.caption.get()) ` | 接续第 832 行的同一条语句，不是另起一段算法。 读取当前值；若是 dict.get，缺少键时可返回指定默认值。 |
| 834 | `         counts = {c: sum((e.metric(mode).color == c for e in electrodes)) for c in COLORS} ` | 把结果保存到 counts：从 COLORS 逐个取 c，为每项生成 c: sum((e.metric(mode).color == c for e in electrodes))。 |
| 835 | `         self.summary.set(f"Green {counts['green']} \| Yellow {counts['yellow']} \| Red {counts['red']}") ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：f"Green {counts['green']} &#124; Yellow {counts['yellow']} &#124; Red {counts['red']}"。 |
| 836 | `         self.results_tree.delete(*self.results_tree.get_children()) ` | 删除控件中的行/图元/文本，不等于删除原始 BDF；参数：*self.results_tree.get_children()。 |
| 837 | `         columns = ['name'] + list(dict.fromkeys(self.views.values())) ` | 把结果保存到 columns：拼接 ['name'] 和 list(dict.fromkeys(self.views.values()))。 |
| 838 | `         self.results_tree.configure(columns=columns) ` | 更新控件属性或状态，不计算信号指标；参数：columns=columns。 |
| 839 | `         for key in columns: ` | 遍历 columns，每次把一项赋给 key，执行下面缩进的循环体。 |
| 840 | `             self.results_tree.heading(key, text='Electrode' if key == 'name' else next((k for k, v in self.views.items() if v == key))) ` | 设置表格列标题；参数：key, text='Electrode' if key == 'name' else next((k for k, v in self.views.items() if v == key))。 |
| 841 | `             self.results_tree.column(key, width=145, minwidth=90) ` | 设置表格列宽等属性或按该类定义取信号列；参数：key, width=145, minwidth=90。 |
| 842 | `         for i, e in enumerate(electrodes): ` | 遍历 enumerate(electrodes)，每次把一项赋给 (i, e)，执行下面缩进的循环体。 |
| 843 | `             self.results_tree.insert('', 'end', iid=str(i), values=(e.name, *[COLOR_LABELS[e.metric(k).color] for k in columns[1:]])) ` | 向列表或文本控件加入显示内容；参数：'', 'end', iid=str(i), values=(e.name, *[COLOR_LABELS[e.metric(k).color] for k in columns[1:]])。 |
| 844 | `         if electrodes: ` | 检查条件 electrodes；为真时执行下面缩进的一组语句。 |
| 845 | `             self.show_detail(next((e for e in electrodes if e.name == self.focused_electrode), electrodes[0])) ` | 显示当前通道的颜色、原因、原始指标值及来源窗口/记录，并同步躯干详情。；参数：next((e for e in electrodes if e.name == self.focused_electrode), electrodes[0])。 |
| 846 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 847 | `     def show_detail(self, electrode): ` | 定义 show_detail(self, electrode)。显示当前通道的颜色、原因、原始指标值及来源窗口/记录，并同步躯干详情。 定义到这里时不执行函数体。 |
| 848 | `         self.focused_electrode = electrode.name ` | 把结果保存到 self.focused_electrode：读取 electrode 的 name 属性。 |
| 849 | `         mode = self.views[self.mode.get()] ` | 把结果保存到 mode：按索引/键 self.mode.get() 取 self.views 的内容。 |
| 850 | `         metric = electrode.metric(mode) ` | 把结果保存到 metric：调用 electrode.metric；参数：mode。 |
| 851 | `         lines = [electrode.name + (' \| REF (not independently verified)' if electrode.is_reference else ''), ` | 把结果保存到 lines：组装列表：[electrode.name + (' &#124; REF (not independently verified)' if electrode.is_reference else ''), 'Scope: ' + self.scope.get(), self.mode.get() + ' &#124; ' + COLOR_LABEL…（完整表达式见左栏）。 |
| 852 | `                  'Scope: ' + self.scope.get(), self.mode.get() + ' \| ' + COLOR_LABELS[metric.color], metric.message] ` | 接续第 851 行的同一条语句，不是另起一段算法。 读取当前值；若是 dict.get，缺少键时可返回指定默认值。 |
| 853 | `         if self.result: ` | 检查条件 self.result；为真时执行下面缩进的一组语句。 |
| 854 | `             kind, value = self.result_scopes.get(self.scope.get(), ('all', None)) ` | 把结果保存到 (kind, value)：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：self.scope.get(), ('all', None)。 |
| 855 | `             record_id = self.result.frames[value]['record_id'] if kind == 'frame' else value ` | 把结果保存到 record_id：若 kind == 'frame'，用 self.result.frames[value]['record_id']；否则用 value。 |
| 856 | `             for run in self.result.runs: ` | 遍历 self.result.runs，每次把一项赋给 run，执行下面缩进的循环体。 |
| 857 | `                 if kind != 'all' and run.record.id != record_id: ` | 检查条件 kind != 'all' and run.record.id != record_id；为真时执行下面缩进的一组语句。 |
| 858 | `                     continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 859 | `                 lines.append(f'{run.record.id}: analyzed 0-{run.duration_s:g} s of {run.recorded_duration_s:g} s recorded' ` | 把一项加入列表末尾；参数：f'{run.record.id}: analyzed 0-{run.duration_s:g} s of {run.recorded_duration_s:g} s recorded' + (f'; excluded {run.duration_s:g}-{run.recorded_du…（完整表达式见左栏）。 |
| 860 | `                              + (f'; excluded {run.duration_s:g}-{run.recorded_duration_s:g} s (final {run.excluded_tail_s:g} s)' if run.excluded_tail_s else '; no tail excluded')) ` | 接续第 859 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：f'{run.record.id}: analyzed 0-{run.duration_s:g} s of {run.recorded_duration_s:g} s recorded' + (f'; excluded {run.duration_s:g}-{run.recorded_du…（完整表达式见左栏）。 |
| 861 | `         if metric.values: ` | 检查条件 metric.values；为真时执行下面缩进的一组语句。 |
| 862 | `             lines.append(json.dumps(metric.values, indent=2, ensure_ascii=False, allow_nan=False)) ` | 把一项加入列表末尾；参数：json.dumps(metric.values, indent=2, ensure_ascii=False, allow_nan=False)。 |
| 863 | `         if self.result and self.analysis_mode() != 'ecg': ` | 检查条件 self.result and self.analysis_mode() != 'ecg'；为真时执行下面缩进的一组语句。 |
| 864 | `             kind, record_id = self.result_scopes.get(self.scope.get(), ('all', None)) ` | 把结果保存到 (kind, record_id)：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：self.scope.get(), ('all', None)。 |
| 865 | `             if kind == 'frame': ` | 检查条件 kind == 'frame'；为真时执行下面缩进的一组语句。 |
| 866 | `                 frame = self.result.frames[record_id] ` | 把结果保存到 frame：按索引/键 record_id 取 self.result.frames 的内容。 |
| 867 | `                 value = frame['metrics'][electrode.name]['synchronization'].values ` | 把结果保存到 value：读取 frame['metrics'][electrode.name]['synchronization'] 的 values 属性。 |
| 868 | `                 lines.append(f"Window only: {frame['start_s']:g}-{frame['end_s']:g} s \| rising {value['rising_count']} / falling {value['falling_count']}") ` | 把一项加入列表末尾；参数：f"Window only: {frame['start_s']:g}-{frame['end_s']:g} s &#124; rising {value['rising_count']} / falling {value['falling_count']}"。 |
| 869 | `             for run in self.result.runs: ` | 遍历 self.result.runs，每次把一项赋给 run，执行下面缩进的循环体。 |
| 870 | `                 if kind == 'frame': ` | 检查条件 kind == 'frame'；为真时执行下面缩进的一组语句。 |
| 871 | `                     continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 872 | `                 if kind == 'record' and run.record.id != record_id: ` | 检查条件 kind == 'record' and run.record.id != record_id；为真时执行下面缩进的一组语句。 |
| 873 | `                     continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 874 | `                 value = run.channels[electrode.name]['sync'].values ` | 把结果保存到 value：读取 run.channels[electrode.name]['sync'] 的 values 属性。 |
| 875 | `                 verified = 'Yes' if run.record.input_confirmed else 'No' ` | 把结果保存到 verified：若 run.record.input_confirmed，用 'Yes'；否则用 'No'。 |
| 876 | `                 lines.append(f"{run.record.id}: Vpp verified: {verified} \| {run.duration_s:g} s, {run.sample_rate_hz:g} Hz \| rising {value['rising_count']} / falling {value['falling_count']}") ` | 把一项加入列表末尾；参数：f"{run.record.id}: Vpp verified: {verified} &#124; {run.duration_s:g} s, {run.sample_rate_hz:g} Hz &#124; rising {value['rising_count']} / falling {value['…（完整表达式见左栏）。 |
| 877 | `         self.detail_text('\n'.join(lines)) ` | 暂时解除详情框只读状态，替换文本后恢复只读。；参数：'\n'.join(lines)。 |
| 878 | `         if self.torso_window is not None: ` | 检查条件 self.torso_window is not None；为真时执行下面缩进的一组语句。 |
| 879 | `             self.torso_window.set_detail('\n'.join(lines),electrode.name) ` | 调用 self.torso_window.set_detail；参数：'\n'.join(lines), electrode.name。 |
| 880 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 881 | `     def open_torso(self): ` | 定义 open_torso(self)。打开或抬起躯干窗口，连接选择回调，与主窗口共享指标和窗口结果。 定义到这里时不执行函数体。 |
| 882 | `         self.timeline.pause() ` | 调用 self.timeline.pause。 |
| 883 | `         if self.torso_window is None: ` | 检查条件 self.torso_window is None；为真时执行下面缩进的一组语句。 |
| 884 | `             self.torso_window = TorsoWindow(self.root,self.mode,list(self.views),self.redraw,self.show_detail, ` | 把结果保存到 self.torso_window：调用 TorsoWindow；参数：self.root, self.mode, list(self.views), self.redraw, self.show_detail, lambda index: self.select_window(index, source='torso'), self.torso_layout…（完整表达式见左栏）。 |
| 885 | `                 lambda index:self.select_window(index,source='torso'),self.torso_layout, ` | 接续第 884 行的同一条语句，不是另起一段算法。 将时间轴提供的全局窗口索引映射到显示范围，并同步主窗口和躯干窗口。；参数：index, source='torso'。 |
| 886 | `                 self.set_torso_layout,lambda:setattr(self,'torso_window',None)) ` | 接续第 884 行的同一条语句，不是另起一段算法。 按字段名写对象属性；参数：self, 'torso_window', None。 |
| 887 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 888 | `             self.torso_window.lift() ` | 调用 self.torso_window.lift。 |
| 889 | `         if self.result is not None: ` | 检查条件 self.result is not None；为真时执行下面缩进的一组语句。 |
| 890 | `             self.redraw() ` | 从已有结果更新热图、躯干、颜色计数、结果表和详情。。 |
| 891 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 892 | `     def set_torso_layout(self,layout): ` | 定义 set_torso_layout(self, layout)。保存用户调整的示意位置方向，不改变信号数据或质量分数。 定义到这里时不执行函数体。 |
| 893 | `         self.torso_layout=layout ` | 把结果保存到 self.torso_layout：layout。 |
| 894 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 895 | `     def select_result(self, _=None): ` | 定义 select_result(self, _=None)。把结果表选中的行变成当前电极，再切回热图页。 定义到这里时不执行函数体。 |
| 896 | `         if self.result is not None and self.results_tree.selection(): ` | 检查条件 self.result is not None and self.results_tree.selection()；为真时执行下面缩进的一组语句。 |
| 897 | `             self.show_detail(self.displayed_electrodes()[int(self.results_tree.selection()[0])]) ` | 显示当前通道的颜色、原因、原始指标值及来源窗口/记录，并同步躯干详情。；参数：self.displayed_electrodes()[int(self.results_tree.selection()[0])]。 |
| 898 | `             self.notebook.select(0) ` | 调用 self.notebook.select；参数：0。 |
| 899 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 900 | `     def export(self): ` | 定义 export(self)。暂停回放，选择输出文件夹，导出当前视图及完整结果；躯干窗口打开时同时保存其图片和布局。 定义到这里时不执行函数体。 |
| 901 | `         if self.result is None: ` | 检查条件 self.result is None；为真时执行下面缩进的一组语句。 |
| 902 | `             messagebox.showinfo('Export', 'Run analysis for the current settings first') ` | 弹出信息提示；参数：'Export', 'Run analysis for the current settings first'。 |
| 903 | `             return ` | 结束当前函数并返回：None（没有值）。 |
| 904 | `         self.timeline.pause() ` | 调用 self.timeline.pause。 |
| 905 | `         if self.torso_window is not None: ` | 检查条件 self.torso_window is not None；为真时执行下面缩进的一组语句。 |
| 906 | `             self.torso_window.timeline.pause() ` | 调用 self.torso_window.timeline.pause。 |
| 907 | `         folder = filedialog.askdirectory(title='Choose report folder') ` | 把结果保存到 folder：调用 filedialog.askdirectory；参数：title='Choose report folder'。 |
| 908 | `         if folder: ` | 检查条件 folder；为真时执行下面缩进的一组语句。 |
| 909 | `             try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 910 | `                 demo = all((r.record.id.startswith('DEMO_') for r in self.result.runs)) ` | 把结果保存到 demo：要求所有条件为真；参数：(r.record.id.startswith('DEMO_') for r in self.result.runs)。 |
| 911 | `                 title = ('SYNTHETIC DEMO \| ' if demo else '') + self.profile.get() ` | 把结果保存到 title：'SYNTHETIC DEMO &#124; ' if demo else '' 与 self.profile.get() 相加。 |
| 912 | `                 scope = self.scope.get() ` | 把结果保存到 scope：读取当前值；若是 dict.get，缺少键时可返回指定默认值。 |
| 913 | `                 path = ReportExporter().save(self.result, folder, self.views[self.mode.get()], title, electrodes=self.displayed_electrodes(), scope=scope, ` | 把结果保存到 path：导出当前视图及完整实验结果、窗口表和事件表；HTML 中用户文本先转义。；参数：self.result, folder, self.views[self.mode.get()], title, electrodes=self.displayed_electrodes(), scope=scope, display={'torso': asdict(self.torso…（完整表达式见左栏）。 |
| 914 | `                                              display={'torso':asdict(self.torso_layout)}) ` | 接续第 913 行的同一条语句，不是另起一段算法。 把数据类递归转换成字典；参数：self.torso_layout。 |
| 915 | `                 if self.torso_window is not None: ` | 检查条件 self.torso_window is not None；为真时执行下面缩进的一组语句。 |
| 916 | `                     self.torso_window.save(folder) ` | 调用 self.torso_window.save；参数：folder。 |
| 917 | `                 self.status.set(f'Exported: {path}') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：f'Exported: {path}'。 |
| 918 | `             except (ValueError, OSError) as exc: ` | 捕获 (ValueError, OSError) 异常，保存到 exc，执行错误处理。 |
| 919 | `                 messagebox.showerror('Export failed', str(exc)) ` | 弹出错误提示；参数：'Export failed', str(exc)。 |
| 920 | ` if __name__ == '__main__': ` | 只有直接运行这个文件时才进入启动代码；被 import 时不自动打开窗口。 |
| 921 | `     root = tk.Tk() ` | 创建 Tkinter 的根窗口；按钮和其他控件都挂在这个窗口或其子容器里。 |
| 922 | `     ElectrodeQAApp(root) ` | 用根窗口创建应用对象，执行 __init__，从而搭好界面和状态。 |
| 923 | `     root.mainloop() ` | 进入 GUI 事件循环，持续响应点击、重画和定时回调；不是再次运行信号分析。 |
