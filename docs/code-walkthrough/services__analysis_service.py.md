# services/analysis_service.py：分析调度

验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。

源码：[services/analysis_service.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/analysis_service.py>)。本说明对应 210 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [21–32](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/analysis_service.py:21>) | 校验并保存设置，创建可复用的读取器及各类分析器。 |
| `_validate` | [34–58](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/analysis_service.py:34>) | 检查记录/通道非空、参考存在、重复文件、接线组、波形模式与输入参数。 |
| `analyze` | [60–109](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/analysis_service.py:60>) | 台架分支先测整段，再按需逐窗口重复同样的测量，最后做跨记录线性/重复性；ECG 走独立分支。 |
| `_retained_data` | [111–127](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/analysis_service.py:111>) | 按每份文件排除尾部样本，向上取整保证至少排除指定秒数；保留原始时间轴并返回数组视图、原时长和排除时长。 |
| `_clipped_counts` | [130–137](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/analysis_service.py:130>) | 仅在传入的保留段或窗口内重新计数数字上下限样本，避免已排除的尾部削顶影响结果。 |
| `_measure_bench` | [139–166](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/analysis_service.py:139>) | 选择正弦或脉冲拟合，检测削顶，测同步，再加入该波形适用的频谱/频率结果。 |
| `_analyze_ecg` | [168–210](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/analysis_service.py:168>) | 对每个完整窗口、每个通道算 SQI，保存窗口结果，并分别汇总文件与整批最差颜色。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Route BDF data to the appropriate analysis. No Tkinter dependency.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import asdict ` | 从 dataclasses 导入 asdict。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 4 | ` from time import perf_counter ` | 从 time 导入 perf_counter。测量耗时或给测试循环计时 |
| 5 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 6 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 7 | ` from models import AnalysisResult, ElectrodeResult, RunResult, MetricResult, combine ` | 从 models 导入 AnalysisResult、ElectrodeResult、RunResult、MetricResult、combine。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 8 | ` from utils.bdf_reader import BdfReader ` | 从 utils.bdf_reader 导入 BdfReader。检查头信息、真实通道及长度，支持 ZIP 内部成员，并通过上下文管理大数组的生命周期。 |
| 9 | ` from modules.sine_fitter import SineFitter ` | 从 modules.sine_fitter 导入 SineFitter。调用底层正弦拟合，返回幅度等结果和按需去基线的通道对象，供过零检测使用。 |
| 10 | ` from modules.gain_error import AmplitudePeakGainError ` | 从 modules.gain_error 导入 AmplitudePeakGainError。用输出基频/平台 Vpp 与确认过的实际输入比较；没有可靠波形或输入校准时，不把结果判为幅度合格。 |
| 11 | ` from modules.linearity import LinearityAnalyzer ` | 从 modules.linearity 导入 LinearityAnalyzer。按频率分组，要求至少三个已确认的输入幅度等级，拟合直线并计算最大偏差占输入跨度的百分比。 |
| 12 | ` from modules.time_synchronization import TimeSynchronizationAnalyzer ` | 从 modules.time_synchronization 导入 TimeSynchronizationAnalyzer。先找上升、下降过零事件，再分别匹配；不移动波形，不用后面的周期补漏检。输出事件表、延迟 P95 和 jitter。 |
| 13 | ` from modules.repeatability import RepeatabilityAnalyzer ` | 从 modules.repeatability 导入 RepeatabilityAnalyzer。按人工声明的 repeat_group 与频率比较独立记录；计算增益或输出幅度 CV，以及各次延迟中位数的 SD。 |
| 14 | ` from modules.bench_spectrum import BenchSpectrumAnalyzer ` | 从 modules.bench_spectrum 导入 BenchSpectrumAnalyzer。独立估计每通道频率，拟合基频和指定谐波，把残差噪声与谐波功率分开，用于 SNR、THD、SINAD。 |
| 15 | ` from modules.pulse_analyzer import PulseAnalyzer ` | 从 modules.pulse_analyzer 导入 PulseAnalyzer。估计高低平台与中点；复用同步匹配器，但不套用正弦拟合或正弦 THD。 |
| 16 | ` from modules.ecg_quality import ECGQualityAnalyzer ` | 从 modules.ecg_quality 导入 ECGQualityAnalyzer。两个不同的心搏检测器加一对一匹配，计算 bSQI；Welch 频谱计算 pSQI/basSQI；另算 Pearson 峰度和平线/削顶。 |
| 17 | ` from modules.windowing import WindowPlan ` | 从 modules.windowing 导入 WindowPlan。把秒数转换成采样索引，给出完整窗口；不足长度不补零；必要时补一个贴齐传入数据末端的完整窗口（当前先按设置排除文件尾部）。 |
| 18 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 19 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 20 | ` class AnalysisService: ` | 定义 AnalysisService 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 21 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。校验并保存设置，创建可复用的读取器及各类分析器。 定义到这里时不执行函数体。 |
| 22 | `         settings.validate() ` | 调用 settings.validate。 |
| 23 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 24 | `         self.reader = BdfReader() ` | 把结果保存到 self.reader：调用 BdfReader。 |
| 25 | `         self.fitter = SineFitter(settings) ` | 把结果保存到 self.fitter：调用 SineFitter；参数：settings。 |
| 26 | `         self.gain = AmplitudePeakGainError(settings) ` | 把结果保存到 self.gain：调用 AmplitudePeakGainError；参数：settings。 |
| 27 | `         self.linearity = LinearityAnalyzer(settings) ` | 把结果保存到 self.linearity：调用 LinearityAnalyzer；参数：settings。 |
| 28 | `         self.synchronization = TimeSynchronizationAnalyzer(settings) ` | 把结果保存到 self.synchronization：调用 TimeSynchronizationAnalyzer；参数：settings。 |
| 29 | `         self.repetition = RepeatabilityAnalyzer(settings) ` | 把结果保存到 self.repetition：调用 RepeatabilityAnalyzer；参数：settings。 |
| 30 | `         self.spectrum = BenchSpectrumAnalyzer(settings) ` | 把结果保存到 self.spectrum：调用 BenchSpectrumAnalyzer；参数：settings。 |
| 31 | `         self.pulse = PulseAnalyzer(settings) ` | 把结果保存到 self.pulse：调用 PulseAnalyzer；参数：settings。 |
| 32 | `         self.ecg = ECGQualityAnalyzer(settings) ` | 把结果保存到 self.ecg：调用 ECGQualityAnalyzer；参数：settings。 |
| 33 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 34 | `     def _validate(self, records, channels, reference): ` | 定义 _validate(self, records, channels, reference)。检查记录/通道非空、参考存在、重复文件、接线组、波形模式与输入参数。 定义到这里时不执行函数体。 |
| 35 | `         if not records or not channels or len(set(channels)) != len(channels): ` | 检查条件 not records or not channels or len(set(channels)) != len(channels)；为真时执行下面缩进的一组语句。 |
| 36 | `             raise ValueError("Add BDF records and select unique electrode channels") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Add BDF records and select unique electrode channels'；上层可捕获并显示原因。 |
| 37 | `         if self.settings.analysis_mode != "ecg" and reference not in channels: ` | 检查条件 self.settings.analysis_mode != 'ecg' and reference not in channels；为真时执行下面缩进的一组语句。 |
| 38 | `             raise ValueError("Select a timing reference from the selected channels") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Select a timing reference from the selected channels'；上层可捕获并显示原因。 |
| 39 | `         sources = [(str(Path(r.path).resolve()).lower(), r.member) for r in records] ` | 把结果保存到 sources：从 records 逐个取 r，为每项生成 (str(Path(r.path).resolve()).lower(), r.member)。 |
| 40 | `         if len(set(sources)) != len(sources) or len({r.id for r in records}) != len(records): ` | 检查条件 len(set(sources)) != len(sources) or len({r.id for r in records}) != len(records)；为真时执行下面缩进的一组语句。 |
| 41 | `             raise ValueError("A BDF source or record ID cannot appear twice") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'A BDF source or record ID cannot appear twice'；上层可捕获并显示原因。 |
| 42 | `         if len({r.setup_group for r in records}) != 1: ` | 检查条件 len({r.setup_group for r in records}) != 1；为真时执行下面缩进的一组语句。 |
| 43 | `             raise ValueError("Different physical setups must be analyzed as separate projects") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Different physical setups must be analyzed as separate projects'；上层可捕获并显示原因。 |
| 44 | `         expected = {"bench_sine":"sine", "bench_pulse":"pulse", "ecg":"ecg"}[self.settings.analysis_mode] ` | 把结果保存到 expected：按索引/键 self.settings.analysis_mode 取 {'bench_sine': 'sine', 'bench_pulse': 'pulse', 'ecg': 'ecg'} 的内容。 |
| 45 | `         for r in records: ` | 遍历 records，每次把一项赋给 r，执行下面缩进的循环体。 |
| 46 | `             if r.waveform not in ("unknown", expected): ` | 检查条件 r.waveform not in ('unknown', expected)；为真时执行下面缩进的一组语句。 |
| 47 | `                 raise ValueError(f"{r.id}: declared {r.waveform} waveform does not match {expected} analysis") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'{r.id}: declared {r.waveform} waveform does not match {expected} analysis'；上层可捕获并显示原因。 |
| 48 | `             if not isinstance(r.input_confirmed, bool) or not isinstance(r.sweep, bool): ` | 检查条件 not isinstance(r.input_confirmed, bool) or not isinstance(r.sweep, bool)；为真时执行下面缩进的一组语句。 |
| 49 | `                 raise ValueError("input_confirmed and sweep must be boolean") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'input_confirmed and sweep must be boolean'；上层可捕获并显示原因。 |
| 50 | `             if expected == "ecg": ` | 检查条件 expected == 'ecg'；为真时执行下面缩进的一组语句。 |
| 51 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 52 | `             if not math.isfinite(r.frequency_hz) or r.frequency_hz <= 0: ` | 检查条件 not math.isfinite(r.frequency_hz) or r.frequency_hz <= 0；为真时执行下面缩进的一组语句。 |
| 53 | `                 raise ValueError(f"{r.id}: frequency must be positive") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'{r.id}: frequency must be positive'；上层可捕获并显示原因。 |
| 54 | `             for value in (r.input_mVpp, r.nominal_mV): ` | 遍历 (r.input_mVpp, r.nominal_mV)，每次把一项赋给 value，执行下面缩进的循环体。 |
| 55 | `                 if value is not None and (not math.isfinite(value) or value <= 0): ` | 检查条件 value is not None and (not math.isfinite(value) or value <= 0)；为真时执行下面缩进的一组语句。 |
| 56 | `                     raise ValueError(f"{r.id}: input amplitude must be positive") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'{r.id}: input amplitude must be positive'；上层可捕获并显示原因。 |
| 57 | `             if r.input_confirmed and r.input_mVpp is None: ` | 检查条件 r.input_confirmed and r.input_mVpp is None；为真时执行下面缩进的一组语句。 |
| 58 | `                 raise ValueError(f"{r.id}: confirmed input requires a value") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'{r.id}: confirmed input requires a value'；上层可捕获并显示原因。 |
| 59 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 60 | `     def analyze(self, records, channels, reference, progress=lambda _: None): ` | 定义 analyze(self, records, channels, reference, progress=lambda _: None)。台架分支先测整段，再按需逐窗口重复同样的测量，最后做跨记录线性/重复性；ECG 走独立分支。 定义到这里时不执行函数体。 |
| 61 | `         self._validate(records, channels, reference) ` | 检查记录/通道非空、参考存在、重复文件、接线组、波形模式与输入参数。；参数：records, channels, reference。 |
| 62 | `         start = perf_counter() ` | 把结果保存到 start：读取高精度计时值，用于计算分析耗时。 |
| 63 | `         if self.settings.analysis_mode == "ecg": ` | 检查条件 self.settings.analysis_mode == 'ecg'；为真时执行下面缩进的一组语句。 |
| 64 | `             return self._analyze_ecg(records, channels, progress, start) ` | 结束当前函数并返回：对每个完整窗口、每个通道算 SQI，保存窗口结果，并分别汇总文件与整批最差颜色。；参数：records, channels, progress, start。 |
| 65 | `         runs, frames = [], [] ` | 把结果保存到 (runs, frames)：组装元组：([], [])。 |
| 66 | `         for index, record in enumerate(records): ` | 遍历 enumerate(records)，每次把一项赋给 (index, record)，执行下面缩进的循环体。 |
| 67 | `             progress(f"{index+1}/{len(records)}: reading {record.id}") ` | 调用 progress；参数：f'{index + 1}/{len(records)}: reading {record.id}'。 |
| 68 | `             with self.reader.open_data(record, channels, progress) as (x, fs, metadata): ` | 进入资源上下文：调用 self.reader.open_data；参数：record, channels, progress，对象命名为 (x, fs, metadata)。退出时执行对应清理。 |
| 69 | `                 x, source_duration, excluded = self._retained_data(x, fs, record, progress) ` | 把结果保存到 (x, source_duration, excluded)：调用 self._retained_data；参数：x, fs, record, progress。 |
| 70 | `                 clipped = (self._clipped_counts(x, channels, metadata) if excluded ` | 把结果保存到 clipped：若 excluded，用 self._clipped_counts(x, channels, metadata)；否则用 metadata['clipped_samples_full_record']。 |
| 71 | `                            else metadata["clipped_samples_full_record"]) ` | 接续第 70 行的同一条语句，不是另起一段算法。 把结果保存到 clipped：若 excluded，用 self._clipped_counts(x, channels, metadata)；否则用 metadata['clipped_samples_full_record']。 |
| 72 | `                 data = self._measure_bench(record, channels, reference, x, fs, ` | 把结果保存到 data：选择正弦或脉冲拟合，检测削顶，测同步，再加入该波形适用的频谱/频率结果。；参数：record, channels, reference, x, fs, clipped, progress。 |
| 73 | `                                            clipped, progress) ` | 接续第 72 行的同一条语句，不是另起一段算法。 把结果保存到 data：选择正弦或脉冲拟合，检测削顶，测同步，再加入该波形适用的频谱/频率结果。；参数：record, channels, reference, x, fs, clipped, progress。 |
| 74 | `                 if self.settings.bench_windows: ` | 检查条件 self.settings.bench_windows；为真时执行下面缩进的一组语句。 |
| 75 | `                     spans = WindowPlan(self.settings.bench_window_s, self.settings.bench_hop_s).spans(len(x), fs) ` | 把结果保存到 spans：调用 WindowPlan(self.settings.bench_window_s, self.settings.bench_hop_s).spans；参数：len(x), fs。 |
| 76 | `                     for number, (left, right) in enumerate(spans): ` | 遍历 enumerate(spans)，每次把一项赋给 (number, (left, right))，执行下面缩进的循环体。 |
| 77 | `                         progress(f"{record.id}: window {number+1}/{len(spans)} \| {left/fs:g}-{right/fs:g} s") ` | 调用 progress；参数：f'{record.id}: window {number + 1}/{len(spans)} &#124; {left / fs:g}-{right / fs:g} s'。 |
| 78 | `                         segment = x[left:right] ` | 把结果保存到 segment：按索引/键 left:right 取 x 的内容；切片包含起点、不包含终点。 |
| 79 | `                         clipped = self._clipped_counts(segment, channels, metadata) ` | 把结果保存到 clipped：调用 self._clipped_counts；参数：segment, channels, metadata。 |
| 80 | `                         measured = self._measure_bench(record, channels, reference, segment, fs, clipped) ` | 把结果保存到 measured：选择正弦或脉冲拟合，检测削顶，测同步，再加入该波形适用的频谱/频率结果。；参数：record, channels, reference, segment, fs, clipped。 |
| 81 | `                         metrics = {} ` | 把结果保存到 metrics：组装字典，键用于给数值/设置命名：{}。 |
| 82 | `                         for name, values in measured.items(): ` | 遍历 measured.items()，每次把一项赋给 (name, values)，执行下面缩进的循环体。 |
| 83 | `                             # Store summaries per window. Whole-record event pairs remain available. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 84 | `                             timing = values["sync"] ` | 把结果保存到 timing：按索引/键 'sync' 取 values 的内容。 |
| 85 | `                             timing.values = {k: v for k, v in timing.values.items() ` | 把结果保存到 timing.values：从 timing.values.items() 逐个取 (k, v)，仅保留 k not in ('pairs', 'rising_events_s', 'falling_events_s')，为每项生成 k: v。 |
| 86 | `                                              if k not in ("pairs", "rising_events_s", "falling_events_s")} ` | 接续第 85 行的同一条语句，不是另起一段算法。 把结果保存到 timing.values：从 timing.values.items() 逐个取 (k, v)，仅保留 k not in ('pairs', 'rising_events_s', 'falling_events_s')，为每项生成 k: v。 |
| 87 | `                             timing.values["window_start_s"] = left/fs ` | 把结果保存到 timing.values['window_start_s']：left 与 fs 相除。 |
| 88 | `                             timing.values["window_end_s"] = right/fs ` | 把结果保存到 timing.values['window_end_s']：right 与 fs 相除。 |
| 89 | `                             metrics[name] = dict(gain=values["gain"], synchronization=timing, **values["extra"]) ` | 把结果保存到 metrics[name]：组装键值字典；参数：gain=values['gain'], synchronization=timing, None=values['extra']。 |
| 90 | `                         frames.append(dict(record_id=record.id, start_s=left/fs, end_s=right/fs, ` | 把一项加入列表末尾；参数：dict(record_id=record.id, start_s=left / fs, end_s=right / fs, analysis_mode=self.settings.analysis_mode, metrics=metrics)。 |
| 91 | `                                            analysis_mode=self.settings.analysis_mode, metrics=metrics)) ` | 接续第 90 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(record_id=record.id, start_s=left / fs, end_s=right / fs, analysis_mode=self.settings.analysis_mode, metrics=metrics)。 |
| 92 | `                     for name in channels: ` | 遍历 channels，每次把一项赋给 name，执行下面缩进的循环体。 |
| 93 | `                         data[name]["complete_windows"] = len(spans) ` | 把结果保存到 data[name]['complete_windows']：取得元素个数；参数：spans。 |
| 94 | `                         data[name]["unassessed_tail_s"] = 0 if spans else len(x)/fs ` | 把结果保存到 data[name]['unassessed_tail_s']：若 spans，用 0；否则用 len(x) / fs。 |
| 95 | `                 runs.append(RunResult(record, data, fs, len(x)/fs, source_duration, excluded)) ` | 把一项加入列表末尾；参数：RunResult(record, data, fs, len(x) / fs, source_duration, excluded)。 |
| 96 | `         electrodes = [] ` | 把结果保存到 electrodes：组装列表：[]。 |
| 97 | `         for name in channels: ` | 遍历 channels，每次把一项赋给 name，执行下面缩进的循环体。 |
| 98 | `             labels = [r.record.id for r in runs] ` | 把结果保存到 labels：从 runs 逐个取 r，为每项生成 r.record.id。 |
| 99 | `             gain = combine([r.channels[name]["gain"] for r in runs], labels=labels) ` | 把结果保存到 gain：调用 combine；参数：[r.channels[name]['gain'] for r in runs], labels=labels。 |
| 100 | `             gain.values = {"records": {r.record.id:r.channels[name]["gain"].values for r in runs}} ` | 把结果保存到 gain.values：组装字典，键用于给数值/设置命名：{'records': {r.record.id: r.channels[name]['gain'].values for r in runs}}。 |
| 101 | `             sync = combine([r.channels[name]["sync"] for r in runs], labels=labels) ` | 把结果保存到 sync：调用 combine；参数：[r.channels[name]['sync'] for r in runs], labels=labels。 |
| 102 | `             sync.values = {"records": {r.record.id:r.channels[name]["sync"].values for r in runs}} ` | 把结果保存到 sync.values：组装字典，键用于给数值/设置命名：{'records': {r.record.id: r.channels[name]['sync'].values for r in runs}}。 |
| 103 | `             extra = {} ` | 把结果保存到 extra：组装字典，键用于给数值/设置命名：{}。 |
| 104 | `             for key in runs[0].channels[name]["extra"]: ` | 遍历 runs[0].channels[name]['extra']，每次把一项赋给 key，执行下面缩进的循环体。 |
| 105 | `                 extra[key] = combine([r.channels[name]["extra"][key] for r in runs], labels=labels) ` | 把结果保存到 extra[key]：调用 combine；参数：[r.channels[name]['extra'][key] for r in runs], labels=labels。 |
| 106 | `                 extra[key].values = {"records":{r.record.id:r.channels[name]["extra"][key].values for r in runs}} ` | 把结果保存到 extra[key].values：组装字典，键用于给数值/设置命名：{'records': {r.record.id: r.channels[name]['extra'][key].values for r in runs}}。 |
| 107 | `             electrodes.append(ElectrodeResult(name, gain, self.linearity.evaluate(runs, name), sync, ` | 把一项加入列表末尾；参数：ElectrodeResult(name, gain, self.linearity.evaluate(runs, name), sync, self.repetition.evaluate(runs, name, reference), name == reference, extra)。 |
| 108 | `                                               self.repetition.evaluate(runs, name, reference), name == reference, extra)) ` | 接续第 107 行的同一条语句，不是另起一段算法。 调用 self.repetition.evaluate；参数：runs, name, reference。 |
| 109 | `         return AnalysisResult(electrodes, runs, reference, perf_counter()-start, asdict(self.settings), frames) ` | 结束当前函数并返回：打包完整分析结果、参数、耗时和窗口列表；参数：electrodes, runs, reference, perf_counter() - start, asdict(self.settings), frames。 |
| 110 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 111 | `     def _retained_data(self, x, fs, record, progress): ` | 定义 _retained_data(self, x, fs, record, progress)。按每份文件排除尾部样本，向上取整保证至少排除指定秒数；保留原始时间轴并返回数组视图、原时长和排除时长。 定义到这里时不执行函数体。 |
| 112 | `         """Apply one per-file crop before any fitting, event detection or windows. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 113 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 114 | `         The stop boundary is exclusive and stays on the original time axis. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 115 | `         Ceil excludes at least the requested duration, rounded up to one sample. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 116 | `         The slice is a view, including when the source is disk-backed. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 117 | `         """ ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 118 | `         source_duration = len(x)/fs ` | 把结果保存到 source_duration：len(x) 与 fs 相除。 |
| 119 | `         excluded_samples = math.ceil(self.settings.exclude_last_s*fs) ` | 排除秒数乘采样率并向上取整，得到至少应排除的样本数；因此实际排除时长可能多出不到一个采样间隔。 |
| 120 | `         stop = len(x)-excluded_samples ` | 把结果保存到 stop：len(x) 与 excluded_samples 相减。 |
| 121 | `         if stop <= 0: ` | 检查条件 stop <= 0；为真时执行下面缩进的一组语句。 |
| 122 | `             raise ValueError(f"{record.id}: recorded {source_duration:g} s; excluding the final " ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'{record.id}: recorded {source_duration:g} s; excluding the final {self.settings.exclude_last_s:g} s leaves no samples. Reduce Exclude final (s)…（完整表达式见左栏）；上层可捕获并显示原因。 |
| 123 | `                              f"{self.settings.exclude_last_s:g} s leaves no samples. " ` | 接续第 122 行的同一条语句，不是另起一段算法。 抛出异常并停止当前正常流程：调用 ValueError；参数：f'{record.id}: recorded {source_duration:g} s; excluding the final {self.settings.exclude_last_s:g} s leaves no samples. Reduce Exclude final (s)…（完整表达式见左栏）；上层可捕获并显示原因。 |
| 124 | `                              "Reduce Exclude final (s), or set it to 0.") ` | 接续第 122 行的同一条语句，不是另起一段算法。 抛出异常并停止当前正常流程：调用 ValueError；参数：f'{record.id}: recorded {source_duration:g} s; excluding the final {self.settings.exclude_last_s:g} s leaves no samples. Reduce Exclude final (s)…（完整表达式见左栏）；上层可捕获并显示原因。 |
| 125 | `         excluded = excluded_samples/fs ` | 把结果保存到 excluded：excluded_samples 与 fs 相除。 |
| 126 | `         progress(f"{record.id}: analyze 0-{stop/fs:g} s of {source_duration:g} s; excluded final {excluded:g} s") ` | 调用 progress；参数：f'{record.id}: analyze 0-{stop / fs:g} s of {source_duration:g} s; excluded final {excluded:g} s'。 |
| 127 | `         return x[:stop], source_duration, excluded ` | 返回保留的 [0,stop) 样本视图、原记录时长和实际排除秒数；不删除或重写原始 BDF。 |
| 128 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 129 | `     @staticmethod ` | @staticmethod 表示该方法不依赖 self，可直接通过类调用。 |
| 130 | `     def _clipped_counts(x, channels, metadata): ` | 定义 _clipped_counts(x, channels, metadata)。仅在传入的保留段或窗口内重新计数数字上下限样本，避免已排除的尾部削顶影响结果。 定义到这里时不执行函数体。 |
| 131 | `         # Recount inside the retained interval: clipping in an excluded tail ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 132 | `         # must not contaminate whole-record quality or any retained window. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 133 | `         counts = {} ` | 把结果保存到 counts：组装字典，键用于给数值/设置命名：{}。 |
| 134 | `         for i, name in enumerate(channels): ` | 遍历 enumerate(channels)，每次把一项赋给 (i, name)，执行下面缩进的循环体。 |
| 135 | `             lo, hi = metadata["physical_limits_uV"][name] ` | 把结果保存到 (lo, hi)：按索引/键 name 取 metadata['physical_limits_uV'] 的内容。 |
| 136 | `             counts[name] = int(np.count_nonzero((x[:, i] <= lo) \| (x[:, i] >= hi))) ` | 把结果保存到 counts[name]：转换为整数；参数：np.count_nonzero((x[:, i] <= lo) &#124; (x[:, i] >= hi))。 |
| 137 | `         return counts ` | 结束当前函数并返回：counts。 |
| 138 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 139 | `     def _measure_bench(self, record, channels, reference, x, fs, clipped, progress=lambda _: None): ` | 定义 _measure_bench(self, record, channels, reference, x, fs, clipped, progress=lambda _: None)。选择正弦或脉冲拟合，检测削顶，测同步，再加入该波形适用的频谱/频率结果。 定义到这里时不执行函数体。 |
| 140 | `         """Identical algorithms for the whole record and an isolated window.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 141 | `         is_pulse = self.settings.analysis_mode == "bench_pulse" ` | 把结果保存到 is_pulse：self.settings.analysis_mode == 'bench_pulse'。 |
| 142 | `         fitter = self.pulse if is_pulse else self.fitter ` | 把结果保存到 fitter：若 is_pulse，用 self.pulse；否则用 self.fitter。 |
| 143 | `         fits, centred = fitter.fit(x, fs, record.frequency_hz, lazy=True, progress=progress) ` | 把结果保存到 (fits, centred)：调用 fitter.fit；参数：x, fs, record.frequency_hz, lazy=True, progress=progress。 |
| 144 | `         for i, name in enumerate(channels): ` | 遍历 enumerate(channels)，每次把一项赋给 (i, name)，执行下面缩进的循环体。 |
| 145 | `             if clipped[name]: ` | 检查条件 clipped[name]；为真时执行下面缩进的一组语句。 |
| 146 | `                 fits[i]["quality_reasons"].append("digital_rail_clipping") ` | 把一项加入列表末尾；参数：'digital_rail_clipping'。 |
| 147 | `         timings = self.synchronization.evaluate_all(centred, fits, channels, reference, fs, record.frequency_hz) ` | 把结果保存到 timings：调用 self.synchronization.evaluate_all；参数：centred, fits, channels, reference, fs, record.frequency_hz。 |
| 148 | `         pulse_frequencies = self.pulse.frequencies(timings, record.frequency_hz) if is_pulse else {} ` | 把结果保存到 pulse_frequencies：若 is_pulse，用 self.pulse.frequencies(timings, record.frequency_hz)；否则用 {}。 |
| 149 | `         data = {} ` | 把结果保存到 data：组装字典，键用于给数值/设置命名：{}。 |
| 150 | `         for i, name in enumerate(channels): ` | 遍历 enumerate(channels)，每次把一项赋给 (i, name)，执行下面缩进的循环体。 |
| 151 | `             progress(f"{record.id}: {name} / {len(channels)} channels") ` | 调用 progress；参数：f'{record.id}: {name} / {len(channels)} channels'。 |
| 152 | `             extra = dict(frequency=pulse_frequencies[name]) if is_pulse else self.spectrum.analyze(x[:, i], fs, record.frequency_hz) ` | 把结果保存到 extra：若 is_pulse，用 dict(frequency=pulse_frequencies[name])；否则用 self.spectrum.analyze(x[:, i], fs, record.frequency_hz)。 |
| 153 | `             if clipped[name]: ` | 检查条件 clipped[name]；为真时执行下面缩进的一组语句。 |
| 154 | `                 for metric in extra.values(): ` | 遍历 extra.values()，每次把一项赋给 metric，执行下面缩进的循环体。 |
| 155 | `                     if metric.color == "green": ` | 检查条件 metric.color == 'green'；为真时执行下面缩进的一组语句。 |
| 156 | `                         metric.color = "yellow" ` | 把结果保存到 metric.color：'yellow'。 |
| 157 | `                     metric.message += "; digital clipping detected" ` | 把 metric.message 的原值加上 '; digital clipping detected'，再写回同一变量。 |
| 158 | `             timing = timings[name] ` | 把结果保存到 timing：按索引/键 name 取 timings 的内容。 |
| 159 | `             timing.values["sample_period_ms"] = 1000/fs ` | 把结果保存到 timing.values['sample_period_ms']：1000 与 fs 相除。 |
| 160 | `             timing.values["event_definition"] = "pulse plateau midpoint" if is_pulse else "detrended sine zero" ` | 把结果保存到 timing.values['event_definition']：若 is_pulse，用 'pulse plateau midpoint'；否则用 'detrended sine zero'。 |
| 161 | `             if name != reference and 1000/fs > min(self.settings.sync_delay_limit_ms, self.settings.sync_jitter_limit_ms): ` | 检查条件 name != reference and 1000 / fs > min(self.settings.sync_delay_limit_ms, self.settings.sync_jitter_limit_ms)；为真时执行下面缩进的一组语句。 |
| 162 | `                 if timing.color == "green": ` | 检查条件 timing.color == 'green'；为真时执行下面缩进的一组语句。 |
| 163 | `                     timing.color = "yellow" ` | 把结果保存到 timing.color：'yellow'。 |
| 164 | `                 timing.message += f"; sample interval {1000/fs:.4f} ms exceeds a timing limit: interpolation needs calibration" ` | 把 timing.message 的原值加上 f'; sample interval {1000 / fs:.4f} ms exceeds a timing limit: interpolation needs calibration'，再写回同一变量。 |
| 165 | `             data[name] = dict(fit=fits[i], gain=self.gain.evaluate(fits[i], record), sync=timing, extra=extra) ` | 把结果保存到 data[name]：组装键值字典；参数：fit=fits[i], gain=self.gain.evaluate(fits[i], record), sync=timing, extra=extra。 |
| 166 | `         return data ` | 结束当前函数并返回：data。 |
| 167 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 168 | `     def _analyze_ecg(self, records, channels, progress, start): ` | 定义 _analyze_ecg(self, records, channels, progress, start)。对每个完整窗口、每个通道算 SQI，保存窗口结果，并分别汇总文件与整批最差颜色。 定义到这里时不执行函数体。 |
| 169 | `         runs, frames = [], [] ` | 把结果保存到 (runs, frames)：组装元组：([], [])。 |
| 170 | `         for index, record in enumerate(records): ` | 遍历 enumerate(records)，每次把一项赋给 (index, record)，执行下面缩进的循环体。 |
| 171 | `             progress(f"{index+1}/{len(records)}: reading ECG {record.id}") ` | 调用 progress；参数：f'{index + 1}/{len(records)}: reading ECG {record.id}'。 |
| 172 | `             with self.reader.open_data(record, channels, progress) as (x, fs, metadata): ` | 进入资源上下文：调用 self.reader.open_data；参数：record, channels, progress，对象命名为 (x, fs, metadata)。退出时执行对应清理。 |
| 173 | `                 x, source_duration, excluded = self._retained_data(x, fs, record, progress) ` | 把结果保存到 (x, source_duration, excluded)：调用 self._retained_data；参数：x, fs, record, progress。 |
| 174 | `                 window = round(self.settings.ecg_window_s*fs) ` | 把结果保存到 window：四舍五入；参数：self.settings.ecg_window_s * fs。 |
| 175 | `                 spans = WindowPlan(self.settings.ecg_window_s, self.settings.ecg_hop_s).spans(len(x), fs) ` | 把结果保存到 spans：调用 WindowPlan(self.settings.ecg_window_s, self.settings.ecg_hop_s).spans；参数：len(x), fs。 |
| 176 | `                 starts = [left for left, _ in spans] ` | 把结果保存到 starts：从 spans 逐个取 (left, _)，为每项生成 left。 |
| 177 | `                 channel_windows = {name:[] for name in channels} ` | 把结果保存到 channel_windows：从 channels 逐个取 name，为每项生成 name: []。 |
| 178 | `                 for number, offset in enumerate(starts): ` | 遍历 enumerate(starts)，每次把一项赋给 (number, offset)，执行下面缩进的循环体。 |
| 179 | `                     progress(f"{record.id}: ECG window {number+1}/{len(starts)}") ` | 调用 progress；参数：f'{record.id}: ECG window {number + 1}/{len(starts)}'。 |
| 180 | `                     measurements = {name:self.ecg.analyze_window(x[offset:offset+window, i], fs, ` | 把结果保存到 measurements：从 enumerate(channels) 逐个取 (i, name)，为每项生成 name: self.ecg.analyze_window(x[offset:offset + window, i], fs, metadata['physical_limits_uV'][name])。 |
| 181 | `                                     metadata["physical_limits_uV"][name]) for i, name in enumerate(channels)} ` | 接续第 180 行的同一条语句，不是另起一段算法。 同时取序号和值；参数：channels。 |
| 182 | `                     frames.append(dict(record_id=record.id, start_s=offset/fs, end_s=(offset+window)/fs, ` | 把一项加入列表末尾；参数：dict(record_id=record.id, start_s=offset / fs, end_s=(offset + window) / fs, metrics=measurements)。 |
| 183 | `                                        metrics=measurements)) ` | 接续第 182 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(record_id=record.id, start_s=offset / fs, end_s=(offset + window) / fs, metrics=measurements)。 |
| 184 | `                     for name in channels: ` | 遍历 channels，每次把一项赋给 name，执行下面缩进的循环体。 |
| 185 | `                         channel_windows[name].append(measurements[name]) ` | 把一项加入列表末尾；参数：measurements[name]。 |
| 186 | `                 data = {} ` | 把结果保存到 data：组装字典，键用于给数值/设置命名：{}。 |
| 187 | `                 for name in channels: ` | 遍历 channels，每次把一项赋给 name，执行下面缩进的循环体。 |
| 188 | `                     windows = channel_windows[name] ` | 把结果保存到 windows：按索引/键 name 取 channel_windows 的内容。 |
| 189 | `                     if windows: ` | 检查条件 windows；为真时执行下面缩进的一组语句。 |
| 190 | `                         metrics = {k:combine([w[k] for w in windows]) for k in windows[0]} ` | 把结果保存到 metrics：从 windows[0] 逐个取 k，为每项生成 k: combine([w[k] for w in windows])。 |
| 191 | `                         for key, metric in metrics.items(): ` | 遍历 metrics.items()，每次把一项赋给 (key, metric)，执行下面缩进的循环体。 |
| 192 | `                             metric.values = dict(complete_windows=len(windows), ` | 把结果保存到 metric.values：组装键值字典；参数：complete_windows=len(windows), green_windows=sum((w[key].color == 'green' for w in windows)), yellow_windows=sum((w[key].color == 'yellow' for w …（完整表达式见左栏）。 |
| 193 | `                                 green_windows=sum(w[key].color == "green" for w in windows), ` | 接续第 192 行的同一条语句，不是另起一段算法。 求和；参数：(w[key].color == 'green' for w in windows)。 |
| 194 | `                                 yellow_windows=sum(w[key].color == "yellow" for w in windows), ` | 接续第 192 行的同一条语句，不是另起一段算法。 求和；参数：(w[key].color == 'yellow' for w in windows)。 |
| 195 | `                                 red_windows=sum(w[key].color == "red" for w in windows)) ` | 接续第 192 行的同一条语句，不是另起一段算法。 求和；参数：(w[key].color == 'red' for w in windows)。 |
| 196 | `                     else: ` | 前面对应条件不成立时，进入此分支。 |
| 197 | `                         metrics = self.ecg.unavailable(f"Insufficient data: {source_duration:.2f} s recorded; " ` | 把结果保存到 metrics：调用 self.ecg.unavailable；参数：f'Insufficient data: {source_duration:.2f} s recorded; {len(x) / fs:.2f} s retained after excluding {excluded:g} s; {self.settings.ecg_window_s:g…（完整表达式见左栏）。 |
| 198 | `                             f"{len(x)/fs:.2f} s retained after excluding {excluded:g} s; " ` | 接续第 197 行的同一条语句，不是另起一段算法。 取得元素个数；参数：x。 |
| 199 | `                             f"{self.settings.ecg_window_s:g} s required") ` | 接续第 197 行的同一条语句，不是另起一段算法。 把结果保存到 metrics：调用 self.ecg.unavailable；参数：f'Insufficient data: {source_duration:.2f} s recorded; {len(x) / fs:.2f} s retained after excluding {excluded:g} s; {self.settings.ecg_window_s:g…（完整表达式见左栏）。 |
| 200 | `                     data[name] = dict(extra=metrics, complete_windows=len(starts), ` | 把结果保存到 data[name]：组装键值字典；参数：extra=metrics, complete_windows=len(starts), unassessed_tail_s=(len(x) - (starts[-1] + window)) / fs if starts else len(x) / fs。 |
| 201 | `                                       unassessed_tail_s=(len(x)-(starts[-1]+window))/fs if starts else len(x)/fs) ` | 接续第 200 行的同一条语句，不是另起一段算法。 取得元素个数；参数：x。 |
| 202 | `                 runs.append(RunResult(record, data, fs, len(x)/fs, source_duration, excluded)) ` | 把一项加入列表末尾；参数：RunResult(record, data, fs, len(x) / fs, source_duration, excluded)。 |
| 203 | `         electrodes = [] ` | 把结果保存到 electrodes：组装列表：[]。 |
| 204 | `         for name in channels: ` | 遍历 channels，每次把一项赋给 name，执行下面缩进的循环体。 |
| 205 | `             extra = {k:combine([r.channels[name]["extra"][k] for r in runs], labels=[r.record.id for r in runs]) for k in runs[0].channels[name]["extra"]} ` | 把结果保存到 extra：从 runs[0].channels[name]['extra'] 逐个取 k，为每项生成 k: combine([r.channels[name]['extra'][k] for r in runs], labels=[r.record.id for r in runs])。 |
| 206 | `             for k in extra: ` | 遍历 extra，每次把一项赋给 k，执行下面缩进的循环体。 |
| 207 | `                 extra[k].values = {"records":{r.record.id:r.channels[name]["extra"][k].values for r in runs}} ` | 把结果保存到 extra[k].values：组装字典，键用于给数值/设置命名：{'records': {r.record.id: r.channels[name]['extra'][k].values for r in runs}}。 |
| 208 | `             na = MetricResult("yellow", "Not applicable to ECG quality mode") ` | 把结果保存到 na：打包颜色、原因和指标数值；参数：'yellow', 'Not applicable to ECG quality mode'。 |
| 209 | `             electrodes.append(ElectrodeResult(name, na, na, na, na, False, extra)) ` | 把一项加入列表末尾；参数：ElectrodeResult(name, na, na, na, na, False, extra)。 |
| 210 | `         return AnalysisResult(electrodes, runs, "", perf_counter()-start, asdict(self.settings), frames) ` | 结束当前函数并返回：打包完整分析结果、参数、耗时和窗口列表；参数：electrodes, runs, '', perf_counter() - start, asdict(self.settings), frames。 |
