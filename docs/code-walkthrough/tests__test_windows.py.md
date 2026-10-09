# tests/test_windows.py：窗口和播放测试

检查局部故障只影响对应窗口、短文件不拼接、末尾覆盖、播放与导出范围一致。

源码：[tests/test_windows.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py>)。本说明对应 163 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `sine_record` | [17–28](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py:17>) | 写入带有局部幅度故障或指定削顶样本的合成记录。 |
| `settings` | [31–36](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py:31>) | 返回当前测试用的窗口和阈值组合，不修改应用默认值。 |
| `test_full_windows_cover_end_without_padding_or_crossing_files` | [40–47](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py:40>) | 窗口包含末尾完整片段，短文件不补零。 |
| `test_local_amplitude_fault_is_absent_from_other_windows` | [49–63](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py:49>) | 第二窗口幅度减半只在对应窗口出现，其他窗口保持各自状态。 |
| `test_clipping_is_checked_inside_each_window` | [65–72](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py:65>) | 削顶只标记包含该样本的窗口。 |
| `test_two_short_files_never_become_one_complete_window` | [74–83](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py:74>) | 两份短记录不能拼成一个完整分析窗。 |
| `test_pulse_windows_use_pulse_measurements` | [85–94](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py:85>) | 脉冲窗口仍走脉冲算法，不能出现正弦频谱指标。 |
| `test_gui_drag_play_focus_invalidation_and_export_scope` | [96–138](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py:96>) | 检查拖动、播放、保持选点、参数失效和导出窗口的一致性。 |
| `test_switching_files_stops_playback_and_keeps_windows_separate` | [140–159](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py:140>) | 切换文件停止旧定时器，不串用另一文件的帧。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Window isolation, localized fault detection, playback and export integration.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` import csv ` | 导入模块 csv。读写表格 CSV |
| 3 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 4 | ` import unittest ` | 导入模块 unittest。自动验证已知输入的程序行为 |
| 5 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 6 | ` from config import AnalysisSettings ` | 从 config 导入 AnalysisSettings。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 7 | ` from models import InputRecord ` | 从 models 导入 InputRecord。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 8 | ` from modules.windowing import WindowPlan ` | 从 modules.windowing 导入 WindowPlan。把秒数转换成采样索引，给出完整窗口；不足长度不补零；必要时补一个贴齐传入数据末端的完整窗口（当前先按设置排除文件尾部）。 |
| 9 | ` from services.analysis_service import AnalysisService ` | 从 services.analysis_service 导入 AnalysisService。验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 |
| 10 | ` from services.demo_data import create_mode_demo ` | 从 services.demo_data 导入 create_mode_demo。生成已知故障的合成 BDF：幅度偏差、延迟、非线性、重复变化、ECG 漂移、平线、噪声。演示标签不是实验验证结论。 |
| 11 | ` from utils.demo_bdf import write_demo_bdf ` | 从 utils.demo_bdf 导入 write_demo_bdf。只为演示/测试生成简单的连续 BDF；将已知 µV 数组打包成 24 位字节。 |
| 12 | ` from utils.report_exporter import ReportExporter ` | 从 utils.report_exporter 导入 ReportExporter。生成当前视图的 PNG/CSV，以及完整 JSON、项目配置、各窗口和过零事件表、HTML 报告。 |
| 13 | ` from test_analysis import fixture_folder ` | 从 test_analysis 导入 fixture_folder。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 14 | ` from test_record_scope import app_for ` | 从 test_record_scope 导入 app_for。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 15 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 16 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 17 | ` def sine_record(folder, duration=30, name='window-sine', clip=False): ` | 定义 sine_record(folder, duration=30, name='window-sine', clip=False)。写入带有局部幅度故障或指定削顶样本的合成记录。 定义到这里时不执行函数体。 |
| 18 | `     fs = 512 ` | 把结果保存到 fs：512。 |
| 19 | `     t = np.arange(duration*fs)/fs ` | 把结果保存到 t：np.arange(duration * fs) 与 fs 相除。 |
| 20 | `     y = np.repeat((50000*np.sin(2*np.pi*2*t)+2200)[:, None], 2, axis=1) ` | 把结果保存到 y：重复数组元素/列；参数：(50000 * np.sin(2 * np.pi * 2 * t) + 2200)[:, None], 2, axis=1。 |
| 21 | `     if duration >= 20: ` | 检查条件 duration >= 20；为真时执行下面缩进的一组语句。 |
| 22 | `         mask = (t >= 10) & (t < 20) ` | 把结果保存到 mask：t >= 10 与 t < 20 按位与。 |
| 23 | `         y[mask, 1] = 25000*np.sin(2*np.pi*2*t[mask])+2200 ` | 把结果保存到 y[mask, 1]：25000 * np.sin(2 * np.pi * 2 * t[mask]) 与 2200 相加。 |
| 24 | `     if clip: ` | 检查条件 clip；为真时执行下面缩进的一组语句。 |
| 25 | `         y[12*fs, 1] = 262143  # Exact BDF digital rail, confined to the second window. ` | 把结果保存到 y[12 * fs, 1]：262143。 |
| 26 | `     path = folder/(name+'.bdf') ` | 把结果保存到 path：在 Path 路径 folder 后拼接 name + '.bdf'；这里的 / 是路径拼接。 |
| 27 | `     write_demo_bdf(path, y, fs) ` | 调用 write_demo_bdf；参数：path, y, fs。 |
| 28 | `     return InputRecord(name, str(path), 2., 100., True, False, waveform='sine') ` | 结束当前函数并返回：创建一份文件及其输入条件记录；参数：name, str(path), 2.0, 100.0, True, False, waveform='sine'。 |
| 29 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 30 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 31 | ` def settings(): ` | 定义 settings()。返回当前测试用的窗口和阈值组合，不修改应用默认值。 定义到这里时不执行函数体。 |
| 32 | `     # These fixtures test exact 0-10 / 10-20 / 20-30 boundaries. Cropping has ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 33 | `     # separate end-to-end tests and is explicitly disabled for this control. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 34 | `     return AnalysisSettings(exclude_last_s=0, bench_windows=True, bench_window_s=10, bench_hop_s=10, ` | 结束当前函数并返回：创建一套分析设置；参数：exclude_last_s=0, bench_windows=True, bench_window_s=10, bench_hop_s=10, thd_limit_pct=1, frequency_limit_pct=0.1, sync_delay_limit_ms=3, sync_ji…（完整表达式见左栏）。 |
| 35 | `                             thd_limit_pct=1, frequency_limit_pct=.1, ` | 接续第 34 行的同一条语句，不是另起一段算法。 结束当前函数并返回：创建一套分析设置；参数：exclude_last_s=0, bench_windows=True, bench_window_s=10, bench_hop_s=10, thd_limit_pct=1, frequency_limit_pct=0.1, sync_delay_limit_ms=3, sync_ji…（完整表达式见左栏）。 |
| 36 | `                             sync_delay_limit_ms=3, sync_jitter_limit_ms=3) ` | 接续第 34 行的同一条语句，不是另起一段算法。 结束当前函数并返回：创建一套分析设置；参数：exclude_last_s=0, bench_windows=True, bench_window_s=10, bench_hop_s=10, thd_limit_pct=1, frequency_limit_pct=0.1, sync_delay_limit_ms=3, sync_ji…（完整表达式见左栏）。 |
| 37 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 38 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 39 | ` class WindowTests(unittest.TestCase): ` | 定义 WindowTests 类，继承 unittest.TestCase；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 40 | `     def test_full_windows_cover_end_without_padding_or_crossing_files(self): ` | 定义 test_full_windows_cover_end_without_padding_or_crossing_files(self)。窗口包含末尾完整片段，短文件不补零。 定义到这里时不执行函数体。 |
| 41 | `         plan = WindowPlan(10, 5) ` | 把结果保存到 plan：创建窗口长度和步长规则；参数：10, 5。 |
| 42 | `         self.assertEqual(plan.spans(30, 10), []) ` | 断言两者相等，不相等则测试失败；参数：plan.spans(30, 10), []。 |
| 43 | `         self.assertEqual(plan.spans(100, 10), [(0, 100)]) ` | 断言两者相等，不相等则测试失败；参数：plan.spans(100, 10), [(0, 100)]。 |
| 44 | `         spans = plan.spans(213, 10) ` | 把结果保存到 spans：调用 plan.spans；参数：213, 10。 |
| 45 | `         self.assertEqual(spans, [(0, 100), (50, 150), (100, 200), (113, 213)]) ` | 断言两者相等，不相等则测试失败；参数：spans, [(0, 100), (50, 150), (100, 200), (113, 213)]。 |
| 46 | `         with self.assertRaises(ValueError): ` | 进入资源上下文：要求代码抛出指定异常，没抛反而测试失败；参数：ValueError。退出时执行对应清理。 |
| 47 | `             WindowPlan(10, 11).spans(300, 10) ` | 调用 WindowPlan(10, 11).spans；参数：300, 10。 |
| 48 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 49 | `     def test_local_amplitude_fault_is_absent_from_other_windows(self): ` | 定义 test_local_amplitude_fault_is_absent_from_other_windows(self)。第二窗口幅度减半只在对应窗口出现，其他窗口保持各自状态。 定义到这里时不执行函数体。 |
| 50 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 51 | `             record = sine_record(folder) ` | 把结果保存到 record：调用 sine_record；参数：folder。 |
| 52 | `             result = AnalysisService(settings()).analyze([record], ['EXG1', 'EXG2'], 'EXG1') ` | 把结果保存到 result：调用 AnalysisService(settings()).analyze；参数：[record], ['EXG1', 'EXG2'], 'EXG1'。 |
| 53 | `             self.assertEqual([(f['start_s'],f['end_s']) for f in result.frames], [(0,10),(10,20),(20,30)]) ` | 断言两者相等，不相等则测试失败；参数：[(f['start_s'], f['end_s']) for f in result.frames], [(0, 10), (10, 20), (20, 30)]。 |
| 54 | `             electrodes = [result.window_electrodes(i)[1] for i in range(3)] ` | 把结果保存到 electrodes：从 range(3) 逐个取 i，为每项生成 result.window_electrodes(i)[1]。 |
| 55 | `             self.assertEqual([e.gain.color for e in electrodes], ['green','red','green']) ` | 断言两者相等，不相等则测试失败；参数：[e.gain.color for e in electrodes], ['green', 'red', 'green']。 |
| 56 | `             self.assertAlmostEqual(electrodes[1].gain.values['gain_error_pct'], -50, delta=.01) ` | 在指定小数位或容差内比较数值；参数：electrodes[1].gain.values['gain_error_pct'], -50, delta=0.01。 |
| 57 | `             # A rising crossing exactly at the left boundary lacks preceding ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 58 | `             # negative samples to confirm the detector's hysteresis condition. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 59 | `             self.assertIn(electrodes[0].synchronization.values['rising_count'], (19, 20)) ` | 断言包含指定项；参数：electrodes[0].synchronization.values['rising_count'], (19, 20)。 |
| 60 | `             self.assertEqual(electrodes[0].synchronization.values['falling_count'], 20) ` | 断言两者相等，不相等则测试失败；参数：electrodes[0].synchronization.values['falling_count'], 20。 |
| 61 | `             self.assertNotIn('pairs', electrodes[0].synchronization.values) ` | 断言不包含指定项；参数：'pairs', electrodes[0].synchronization.values。 |
| 62 | `             self.assertEqual(electrodes[0].linearity.color, 'yellow') ` | 断言两者相等，不相等则测试失败；参数：electrodes[0].linearity.color, 'yellow'。 |
| 63 | `             self.assertEqual(electrodes[0].repetition.color, 'yellow') ` | 断言两者相等，不相等则测试失败；参数：electrodes[0].repetition.color, 'yellow'。 |
| 64 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 65 | `     def test_clipping_is_checked_inside_each_window(self): ` | 定义 test_clipping_is_checked_inside_each_window(self)。削顶只标记包含该样本的窗口。 定义到这里时不执行函数体。 |
| 66 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 67 | `             record = sine_record(folder, clip=True) ` | 把结果保存到 record：调用 sine_record；参数：folder, clip=True。 |
| 68 | `             result = AnalysisService(settings()).analyze([record], ['EXG1', 'EXG2'], 'EXG1') ` | 把结果保存到 result：调用 AnalysisService(settings()).analyze；参数：[record], ['EXG1', 'EXG2'], 'EXG1'。 |
| 69 | `             first = result.window_electrodes(0)[1].gain.values['quality_reasons'] ` | 把结果保存到 first：按索引/键 'quality_reasons' 取 result.window_electrodes(0)[1].gain.values 的内容。 |
| 70 | `             middle = result.window_electrodes(1)[1].gain.values['quality_reasons'] ` | 把结果保存到 middle：按索引/键 'quality_reasons' 取 result.window_electrodes(1)[1].gain.values 的内容。 |
| 71 | `             self.assertNotIn('digital_rail_clipping', first) ` | 断言不包含指定项；参数：'digital_rail_clipping', first。 |
| 72 | `             self.assertIn('digital_rail_clipping', middle) ` | 断言包含指定项；参数：'digital_rail_clipping', middle。 |
| 73 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 74 | `     def test_two_short_files_never_become_one_complete_window(self): ` | 定义 test_two_short_files_never_become_one_complete_window(self)。两份短记录不能拼成一个完整分析窗。 定义到这里时不执行函数体。 |
| 75 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 76 | `             records = [sine_record(folder, 3, 'short3'), sine_record(folder, 7, 'short7')] ` | 把结果保存到 records：组装列表：[sine_record(folder, 3, 'short3'), sine_record(folder, 7, 'short7')]。 |
| 77 | `             result = AnalysisService(settings()).analyze(records, ['EXG1','EXG2'], 'EXG1') ` | 把结果保存到 result：调用 AnalysisService(settings()).analyze；参数：records, ['EXG1', 'EXG2'], 'EXG1'。 |
| 78 | `             self.assertEqual(result.frames, []) ` | 断言两者相等，不相等则测试失败；参数：result.frames, []。 |
| 79 | `             self.assertEqual([r.channels['EXG1']['unassessed_tail_s'] for r in result.runs], [3,7]) ` | 断言两者相等，不相等则测试失败；参数：[r.channels['EXG1']['unassessed_tail_s'] for r in result.runs], [3, 7]。 |
| 80 | `             with app_for(records) as app: ` | 进入资源上下文：调用 app_for；参数：records，对象命名为 app。退出时执行对应清理。 |
| 81 | `                 app.accept_result(result) ` | 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 |
| 82 | `                 self.assertIn('No complete windows', app.timeline.caption.get()) ` | 断言包含指定项；参数：'No complete windows', app.timeline.caption.get()。 |
| 83 | `                 self.assertEqual(str(app.timeline.play.cget('state')), 'disabled') ` | 断言两者相等，不相等则测试失败；参数：str(app.timeline.play.cget('state')), 'disabled'。 |
| 84 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 85 | `     def test_pulse_windows_use_pulse_measurements(self): ` | 定义 test_pulse_windows_use_pulse_measurements(self)。脉冲窗口仍走脉冲算法，不能出现正弦频谱指标。 定义到这里时不执行函数体。 |
| 86 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 87 | `             records = create_mode_demo(folder, 2, 'bench_pulse') ` | 把结果保存到 records：按模式选择正弦演示，或生成 30 秒脉冲/ECG 数据并注入特定故障。；参数：folder, 2, 'bench_pulse'。 |
| 88 | `             s = settings(); s.analysis_mode = 'bench_pulse' ` | 把结果保存到 s：调用 settings。 把结果保存到 s.analysis_mode：'bench_pulse'。 |
| 89 | `             result = AnalysisService(s).analyze(records, ['EXG1','EXG2'], 'EXG1') ` | 把结果保存到 result：调用 AnalysisService(s).analyze；参数：records, ['EXG1', 'EXG2'], 'EXG1'。 |
| 90 | `             self.assertEqual(len(result.frames), 3) ` | 断言两者相等，不相等则测试失败；参数：len(result.frames), 3。 |
| 91 | `             for frame in result.frames: ` | 遍历 result.frames，每次把一项赋给 frame，执行下面缩进的循环体。 |
| 92 | `                 self.assertNotIn('snr', frame['metrics']['EXG2']) ` | 断言不包含指定项；参数：'snr', frame['metrics']['EXG2']。 |
| 93 | `                 self.assertEqual(frame['metrics']['EXG2']['gain'].color, 'red') ` | 断言两者相等，不相等则测试失败；参数：frame['metrics']['EXG2']['gain'].color, 'red'。 |
| 94 | `                 self.assertEqual(frame['metrics']['EXG2']['synchronization'].values['event_definition'], 'pulse plateau midpoint') ` | 断言两者相等，不相等则测试失败；参数：frame['metrics']['EXG2']['synchronization'].values['event_definition'], 'pulse plateau midpoint'。 |
| 95 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 96 | `     def test_gui_drag_play_focus_invalidation_and_export_scope(self): ` | 定义 test_gui_drag_play_focus_invalidation_and_export_scope(self)。检查拖动、播放、保持选点、参数失效和导出窗口的一致性。 定义到这里时不执行函数体。 |
| 97 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 98 | `             record = sine_record(folder) ` | 把结果保存到 record：调用 sine_record；参数：folder。 |
| 99 | `             result = AnalysisService(settings()).analyze([record], ['EXG1','EXG2'], 'EXG1') ` | 把结果保存到 result：调用 AnalysisService(settings()).analyze；参数：[record], ['EXG1', 'EXG2'], 'EXG1'。 |
| 100 | `             with app_for([record]) as app: ` | 进入资源上下文：调用 app_for；参数：[record]，对象命名为 app。退出时执行对应清理。 |
| 101 | `                 app.mode.set('Gain error') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Gain error'。 |
| 102 | `                 app.accept_result(result) ` | 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 |
| 103 | `                 self.assertEqual(app.result_scopes[app.scope.get()], ('frame',0)) ` | 断言两者相等，不相等则测试失败；参数：app.result_scopes[app.scope.get()], ('frame', 0)。 |
| 104 | `                 app.show_detail(app.displayed_electrodes()[1]) ` | 显示当前通道的颜色、原因、原始指标值及来源窗口/记录，并同步躯干详情。；参数：app.displayed_electrodes()[1]。 |
| 105 | `                 app.timeline.next_alert() ` | 调用 app.timeline.next_alert。 |
| 106 | `                 self.assertEqual(app.result_scopes[app.scope.get()], ('frame',1)) ` | 断言两者相等，不相等则测试失败；参数：app.result_scopes[app.scope.get()], ('frame', 1)。 |
| 107 | `                 self.assertEqual(app.focused_electrode, 'EXG2') ` | 断言两者相等，不相等则测试失败；参数：app.focused_electrode, 'EXG2'。 |
| 108 | `                 self.assertIn('Window only: 10-20 s', app.detail.get('1.0','end')) ` | 断言包含指定项；参数：'Window only: 10-20 s', app.detail.get('1.0', 'end')。 |
| 109 | `                 self.assertEqual(app.displayed_electrodes()[1].gain.color, 'red') ` | 断言两者相等，不相等则测试失败；参数：app.displayed_electrodes()[1].gain.color, 'red'。 |
| 110 | `                 ReportExporter().save(result, folder/'export', 'gain', ` | 导出当前视图及完整实验结果、窗口表和事件表；HTML 中用户文本先转义。；参数：result, folder / 'export', 'gain', electrodes=app.displayed_electrodes(), scope=app.scope.get()。 |
| 111 | `                                       electrodes=app.displayed_electrodes(), scope=app.scope.get()) ` | 接续第 110 行的同一条语句，不是另起一段算法。 只取当前整段、窗口或整批范围的电极结果；这个函数不重新算指标。。 |
| 112 | `                 payload = json.loads((folder/'export/results.json').read_text(encoding='utf-8')) ` | 把结果保存到 payload：把 JSON 文本恢复为 Python 数据；参数：(folder / 'export/results.json').read_text(encoding='utf-8')。 |
| 113 | `                 self.assertIn('10-20 s', payload['export_view']['scope']) ` | 断言包含指定项；参数：'10-20 s', payload['export_view']['scope']。 |
| 114 | `                 with (folder/'export/window_summary.csv').open(encoding='utf-8-sig') as handle: ` | 进入资源上下文：打开文件或归档成员；参数：encoding='utf-8-sig'，对象命名为 handle。退出时执行对应清理。 |
| 115 | `                     rows = list(csv.DictReader(handle)) ` | 把结果保存到 rows：构造列表；参数：csv.DictReader(handle)。 |
| 116 | `                 self.assertEqual(len(rows),6) ` | 断言两者相等，不相等则测试失败；参数：len(rows), 6。 |
| 117 | `                 self.assertEqual([(float(r['start_s']), r['electrode']) for r in rows if r['color']=='red'], [(10.,'EXG2')]) ` | 断言两者相等，不相等则测试失败；参数：[(float(r['start_s']), r['electrode']) for r in rows if r['color'] == 'red'], [(10.0, 'EXG2')]。 |
| 118 | `                 with (folder/'export/ecg_windows.csv').open(encoding='utf-8-sig') as handle: ` | 进入资源上下文：打开文件或归档成员；参数：encoding='utf-8-sig'，对象命名为 handle。退出时执行对应清理。 |
| 119 | `                     self.assertEqual(len(list(csv.DictReader(handle))), 0) ` | 断言两者相等，不相等则测试失败；参数：len(list(csv.DictReader(handle))), 0。 |
| 120 | `                 app.timeline._scrub('0') ` | 调用 app.timeline._scrub；参数：'0'。 |
| 121 | `                 self.assertEqual(app.result_scopes[app.scope.get()], ('frame',0)) ` | 断言两者相等，不相等则测试失败；参数：app.result_scopes[app.scope.get()], ('frame', 0)。 |
| 122 | `                 app.timeline.toggle() ` | 调用 app.timeline.toggle。 |
| 123 | `                 self.assertTrue(app.timeline.playing) ` | 断言条件为真；参数：app.timeline.playing。 |
| 124 | `                 # Execute the scheduled callback without waiting ten seconds. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 125 | `                 app.timeline.after_cancel(app.timeline.timer); app.timeline.timer = None ` | 取消尚未执行的 Tk 定时回调；参数：app.timeline.timer。 把结果保存到 app.timeline.timer：None（未知/未设置）。 |
| 126 | `                 app.timeline._tick() ` | 调用 app.timeline._tick。 |
| 127 | `                 self.assertEqual(app.result_scopes[app.scope.get()], ('frame',1)) ` | 断言两者相等，不相等则测试失败；参数：app.result_scopes[app.scope.get()], ('frame', 1)。 |
| 128 | `                 app.timeline.after_cancel(app.timeline.timer); app.timeline.timer = None ` | 取消尚未执行的 Tk 定时回调；参数：app.timeline.timer。 把结果保存到 app.timeline.timer：None（未知/未设置）。 |
| 129 | `                 app.timeline._tick() ` | 调用 app.timeline._tick。 |
| 130 | `                 self.assertFalse(app.timeline.playing) ` | 断言条件为假；参数：app.timeline.playing。 |
| 131 | `                 self.assertEqual(app.result_scopes[app.scope.get()], ('frame',2)) ` | 断言两者相等，不相等则测试失败；参数：app.result_scopes[app.scope.get()], ('frame', 2)。 |
| 132 | `                 app.timeline.toggle() ` | 调用 app.timeline.toggle。 |
| 133 | `                 self.assertTrue(app.timeline.playing) ` | 断言条件为真；参数：app.timeline.playing。 |
| 134 | `                 app.limit_vars['bench_window_s'].set('8') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'8'。 |
| 135 | `                 self.assertIsNone(app.result) ` | 断言结果是 None；参数：app.result。 |
| 136 | `                 self.assertFalse(app.timeline.playing) ` | 断言条件为假；参数：app.timeline.playing。 |
| 137 | `                 self.assertIsNone(app.timeline.timer) ` | 断言结果是 None；参数：app.timeline.timer。 |
| 138 | `                 self.assertEqual(app.timeline.items, []) ` | 断言两者相等，不相等则测试失败；参数：app.timeline.items, []。 |
| 139 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 140 | `     def test_switching_files_stops_playback_and_keeps_windows_separate(self): ` | 定义 test_switching_files_stops_playback_and_keeps_windows_separate(self)。切换文件停止旧定时器，不串用另一文件的帧。 定义到这里时不执行函数体。 |
| 141 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 142 | `             records = [sine_record(folder, name='record-a'), sine_record(folder, name='record-b')] ` | 把结果保存到 records：组装列表：[sine_record(folder, name='record-a'), sine_record(folder, name='record-b')]。 |
| 143 | `             result = AnalysisService(settings()).analyze(records, ['EXG1', 'EXG2'], 'EXG1') ` | 把结果保存到 result：调用 AnalysisService(settings()).analyze；参数：records, ['EXG1', 'EXG2'], 'EXG1'。 |
| 144 | `             with app_for(records) as app: ` | 进入资源上下文：调用 app_for；参数：records，对象命名为 app。退出时执行对应清理。 |
| 145 | `                 app.mode.set('Gain error') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Gain error'。 |
| 146 | `                 app.accept_result(result) ` | 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 |
| 147 | `                 app.timeline.toggle() ` | 调用 app.timeline.toggle。 |
| 148 | `                 self.assertTrue(app.timeline.playing) ` | 断言条件为真；参数：app.timeline.playing。 |
| 149 | `                 app.record_tree.selection_set('1') ` | 设置选中行；参数：'1'。 |
| 150 | `                 app.select_record() ` | 切换记录时保存上一份编辑，再加载新记录的参数；若它已被分析，切换到该文件自己的结果。。 |
| 151 | `                 self.assertFalse(app.timeline.playing) ` | 断言条件为假；参数：app.timeline.playing。 |
| 152 | `                 self.assertIsNone(app.timeline.timer) ` | 断言结果是 None；参数：app.timeline.timer。 |
| 153 | `                 self.assertEqual(app.result_scopes[app.scope.get()], ('record', 'record-b')) ` | 断言两者相等，不相等则测试失败；参数：app.result_scopes[app.scope.get()], ('record', 'record-b')。 |
| 154 | `                 self.assertEqual([item[0] for item in app.timeline.items], [3, 4, 5]) ` | 断言两者相等，不相等则测试失败；参数：[item[0] for item in app.timeline.items], [3, 4, 5]。 |
| 155 | `                 app.timeline.next_alert() ` | 调用 app.timeline.next_alert。 |
| 156 | `                 self.assertEqual(app.result_scopes[app.scope.get()], ('frame', 4)) ` | 断言两者相等，不相等则测试失败；参数：app.result_scopes[app.scope.get()], ('frame', 4)。 |
| 157 | `                 self.assertEqual(app.selected, 1) ` | 断言两者相等，不相等则测试失败；参数：app.selected, 1。 |
| 158 | `                 self.assertIn('record-b', app.detail.get('1.0', 'end')) ` | 断言包含指定项；参数：'record-b', app.detail.get('1.0', 'end')。 |
| 159 | `                 self.assertNotIn('record-a', app.detail.get('1.0', 'end')) ` | 断言不包含指定项；参数：'record-a', app.detail.get('1.0', 'end')。 |
| 160 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 161 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 162 | ` if __name__ == '__main__': ` | 只有直接运行这个文件时才进入启动代码；被 import 时不自动打开窗口。 |
| 163 | `     unittest.main() ` | 调用 unittest.main。 |
