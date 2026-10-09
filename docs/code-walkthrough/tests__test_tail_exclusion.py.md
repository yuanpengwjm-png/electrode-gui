# tests/test_tail_exclusion.py：排除文件末尾的行为测试

用末尾带漂移和削顶的合成数据，核对台架/ECG、时间轴、躯干和导出都只使用保留区间，并验证原文件不变及旧配置兼容。

源码：[tests/test_tail_exclusion.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_tail_exclusion.py>)。本说明对应 153 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `record_with_tail` | [19–31](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_tail_exclusion.py:19>) | 生成两个相同通道的正弦或脉冲，在最后一秒加入偏移和一个削顶样本，返回已知故障的合成记录。 |
| `test_defaults_legacy_migration_and_explicit_settings_roundtrip` | [35–60](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_tail_exclusion.py:35>) | 检查排除秒数/THD/频偏默认值、旧版本空限值迁移，以及新版本显式空限值和关闭裁尾能原样恢复。 |
| `test_sine_and_pulse_match_independent_clean_prefix_including_clipping` | [62–90](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_tail_exclusion.py:62>) | 将裁尾结果与独立写出的干净前段比较，核对指标、窗口、削顶、缓存清理、过零时间和原文件不变。 |
| `test_ecg_and_each_batch_file_are_cropped_separately` | [92–107](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_tail_exclusion.py:92>) | 检查多个 ECG 文件各自裁尾、短文件不产生假窗口，以及保留段结果等于独立前段文件。 |
| `test_short_and_fractional_exclusions_are_explicit` | [109–125](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_tail_exclusion.py:109>) | 检查裁到无样本时报错、拒绝负数/非有限秒数、短记录无完整窗口及小数秒向上取样本整。 |
| `test_gui_3d_and_exports_report_the_retained_interval` | [127–150](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_tail_exclusion.py:127>) | 检查主窗口、躯干和导出报告都显示保留/排除区间，改变排除秒数后清除旧结果。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Tail faults never enter retained metrics, windows, exports or 3D states.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import asdict ` | 从 dataclasses 导入 asdict。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 4 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 5 | ` import unittest ` | 导入模块 unittest。自动验证已知输入的程序行为 |
| 6 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 7 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 8 | ` from config import AnalysisSettings ` | 从 config 导入 AnalysisSettings。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 9 | ` from models import InputRecord ` | 从 models 导入 InputRecord。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 10 | ` from services.analysis_service import AnalysisService ` | 从 services.analysis_service 导入 AnalysisService。验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 |
| 11 | ` from utils.bdf_reader import BdfReader ` | 从 utils.bdf_reader 导入 BdfReader。检查头信息、真实通道及长度，支持 ZIP 内部成员，并通过上下文管理大数组的生命周期。 |
| 12 | ` from utils.demo_bdf import write_demo_bdf ` | 从 utils.demo_bdf 导入 write_demo_bdf。只为演示/测试生成简单的连续 BDF；将已知 µV 数组打包成 24 位字节。 |
| 13 | ` from utils.project_io import load_project, save_project ` | 从 utils.project_io 导入 load_project、save_project。保存文件清单、参数、通道和参考；恢复时适配部分旧配置，并统一幅度单位。保存的是配置，不是复制原始 BDF。 |
| 14 | ` from utils.report_exporter import ReportExporter ` | 从 utils.report_exporter 导入 ReportExporter。生成当前视图的 PNG/CSV，以及完整 JSON、项目配置、各窗口和过零事件表、HTML 报告。 |
| 15 | ` from test_analysis import fixture_folder ` | 从 test_analysis 导入 fixture_folder。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 16 | ` from test_record_scope import app_for ` | 从 test_record_scope 导入 app_for。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 17 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 18 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 19 | ` def record_with_tail(folder, waveform='sine', duration=21, name='tail-fault'): ` | 定义 record_with_tail(folder, waveform='sine', duration=21, name='tail-fault')。生成两个相同通道的正弦或脉冲，在最后一秒加入偏移和一个削顶样本，返回已知故障的合成记录。 定义到这里时不执行函数体。 |
| 20 | `     fs=256 ` | 把结果保存到 fs：256。 |
| 21 | `     t=np.arange(fs*duration)/fs ` | 把结果保存到 t：np.arange(fs * duration) 与 fs 相除。 |
| 22 | `     clean=np.sin(2*np.pi*5*t) ` | 把结果保存到 clean：调用 np.sin；参数：2 * np.pi * 5 * t。 |
| 23 | `     if waveform=='pulse': ` | 检查条件 waveform == 'pulse'；为真时执行下面缩进的一组语句。 |
| 24 | `         clean=np.where(clean>=0,1.,-1.) ` | 把结果保存到 clean：按布尔条件逐元素选择；参数：clean >= 0, 1.0, -1.0。 |
| 25 | `     data=np.repeat((25000*clean+1000)[:,None],2,axis=1) ` | 把结果保存到 data：重复数组元素/列；参数：(25000 * clean + 1000)[:, None], 2, axis=1。 |
| 26 | `     if duration>1: ` | 检查条件 duration > 1；为真时执行下面缩进的一组语句。 |
| 27 | `         data[-fs:]+=18000 ` | 把 data[-fs:] 的原值加上 18000，再写回同一变量。 |
| 28 | `         data[-fs//2,0]=262143  # One digital rail in the discarded final second. ` | 把结果保存到 data[-fs // 2, 0]：262143。 |
| 29 | `     path=folder/(name+'.bdf') ` | 把结果保存到 path：在 Path 路径 folder 后拼接 name + '.bdf'；这里的 / 是路径拼接。 |
| 30 | `     write_demo_bdf(path,data,fs) ` | 调用 write_demo_bdf；参数：path, data, fs。 |
| 31 | `     return InputRecord(name,str(path),5,50,True,False,waveform=waveform),data,fs ` | 结束当前函数并返回：组装元组：(InputRecord(name, str(path), 5, 50, True, False, waveform=waveform), data, fs)。 |
| 32 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 33 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 34 | ` class TailExclusionTests(unittest.TestCase): ` | 定义 TailExclusionTests 类，继承 unittest.TestCase；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 35 | `     def test_defaults_legacy_migration_and_explicit_settings_roundtrip(self): ` | 定义 test_defaults_legacy_migration_and_explicit_settings_roundtrip(self)。检查排除秒数/THD/频偏默认值、旧版本空限值迁移，以及新版本显式空限值和关闭裁尾能原样恢复。 定义到这里时不执行函数体。 |
| 36 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 37 | `             record,_,_=record_with_tail(folder) ` | 把结果保存到 (record, _, _)：调用 record_with_tail；参数：folder。 |
| 38 | `             with app_for([record]) as app: ` | 进入资源上下文：调用 app_for；参数：[record]，对象命名为 app。退出时执行对应清理。 |
| 39 | `                 self.assertEqual(float(app.limit_vars['exclude_last_s'].get()),1) ` | 断言两者相等，不相等则测试失败；参数：float(app.limit_vars['exclude_last_s'].get()), 1。 |
| 40 | `                 self.assertEqual(float(app.limit_vars['frequency_limit_pct'].get()),.1) ` | 断言两者相等，不相等则测试失败；参数：float(app.limit_vars['frequency_limit_pct'].get()), 0.1。 |
| 41 | `                 self.assertEqual(float(app.limit_vars['thd_limit_pct'].get()),1) ` | 断言两者相等，不相等则测试失败；参数：float(app.limit_vars['thd_limit_pct'].get()), 1。 |
| 42 | `                 self.assertEqual(app.prepare()[1].exclude_last_s,1) ` | 断言两者相等，不相等则测试失败；参数：app.prepare()[1].exclude_last_s, 1。 |
| 43 | `                 path=folder/'old.json' ` | 把结果保存到 path：在 Path 路径 folder 后拼接 'old.json'；这里的 / 是路径拼接。 |
| 44 | `                 old=dict(version=2,records=[asdict(record)],settings=dict(thd_limit_pct=None,frequency_limit_pct=None), ` | 把结果保存到 old：组装键值字典；参数：version=2, records=[asdict(record)], settings=dict(thd_limit_pct=None, frequency_limit_pct=None), channels=['EXG1', 'EXG2'], reference='EXG1'。 |
| 45 | `                          channels=['EXG1','EXG2'],reference='EXG1') ` | 接续第 44 行的同一条语句，不是另起一段算法。 把结果保存到 old：组装键值字典；参数：version=2, records=[asdict(record)], settings=dict(thd_limit_pct=None, frequency_limit_pct=None), channels=['EXG1', 'EXG2'], reference='EXG1'。 |
| 46 | `                 path.write_text(json.dumps(old)) ` | 写入文本文件；参数：json.dumps(old)。 |
| 47 | `                 app.load_path(path) ` | 恢复 JSON 项目与躯干显示设置，读取文件头核对，再更新 GUI。；参数：path。 |
| 48 | `                 self.assertEqual(float(app.limit_vars['frequency_limit_pct'].get()),.1) ` | 断言两者相等，不相等则测试失败；参数：float(app.limit_vars['frequency_limit_pct'].get()), 0.1。 |
| 49 | `                 self.assertEqual(float(app.limit_vars['thd_limit_pct'].get()),1) ` | 断言两者相等，不相等则测试失败；参数：float(app.limit_vars['thd_limit_pct'].get()), 1。 |
| 50 | `                 self.assertEqual(app.settings.exclude_last_s,1) ` | 断言两者相等，不相等则测试失败；参数：app.settings.exclude_last_s, 1。 |
| 51 | `             # Existing numeric tolerances are deliberate and must survive. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 52 | `             old['settings']['frequency_limit_pct']=.25 ` | 把结果保存到 old['settings']['frequency_limit_pct']：0.25。 |
| 53 | `             old['settings']['thd_limit_pct']=2 ` | 把结果保存到 old['settings']['thd_limit_pct']：2。 |
| 54 | `             path.write_text(json.dumps(old)) ` | 写入文本文件；参数：json.dumps(old)。 |
| 55 | `             self.assertEqual(load_project(path)[1].frequency_limit_pct,.25) ` | 断言两者相等，不相等则测试失败；参数：load_project(path)[1].frequency_limit_pct, 0.25。 |
| 56 | `             self.assertEqual(load_project(path)[1].thd_limit_pct,2) ` | 断言两者相等，不相等则测试失败；参数：load_project(path)[1].thd_limit_pct, 2。 |
| 57 | `             # In new projects, explicitly blank acceptance and disabled crop persist. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 58 | `             s=AnalysisSettings(exclude_last_s=0,frequency_limit_pct=None,thd_limit_pct=None) ` | 把结果保存到 s：创建一套分析设置；参数：exclude_last_s=0, frequency_limit_pct=None, thd_limit_pct=None。 |
| 59 | `             save_project(path,[record],s,['EXG1','EXG2'],'EXG1') ` | 把记录和设置的数据类转成 JSON，保留通道、参考与可选布局信息。；参数：path, [record], s, ['EXG1', 'EXG2'], 'EXG1'。 |
| 60 | `             self.assertEqual(asdict(load_project(path)[1]),asdict(s)) ` | 断言两者相等，不相等则测试失败；参数：asdict(load_project(path)[1]), asdict(s)。 |
| 61 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 62 | `     def test_sine_and_pulse_match_independent_clean_prefix_including_clipping(self): ` | 定义 test_sine_and_pulse_match_independent_clean_prefix_including_clipping(self)。将裁尾结果与独立写出的干净前段比较，核对指标、窗口、削顶、缓存清理、过零时间和原文件不变。 定义到这里时不执行函数体。 |
| 63 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 64 | `             for waveform,mode in (('sine','bench_sine'),('pulse','bench_pulse')): ` | 遍历 (('sine', 'bench_sine'), ('pulse', 'bench_pulse'))，每次把一项赋给 (waveform, mode)，执行下面缩进的循环体。 |
| 65 | `                 record,data,fs=record_with_tail(folder,waveform,name=waveform) ` | 把结果保存到 (record, data, fs)：调用 record_with_tail；参数：folder, waveform, name=waveform。 |
| 66 | `                 original=Path(record.path).read_bytes() ` | 把结果保存到 original：调用 Path(record.path).read_bytes。 |
| 67 | `                 prefix=folder/(waveform+'-prefix.bdf') ` | 把结果保存到 prefix：在 Path 路径 folder 后拼接 waveform + '-prefix.bdf'；这里的 / 是路径拼接。 |
| 68 | `                 write_demo_bdf(prefix,data[:-fs],fs) ` | 调用 write_demo_bdf；参数：prefix, data[:-fs], fs。 |
| 69 | `                 clean_record=InputRecord(record.id,str(prefix),5,50,True,False,waveform=waveform) ` | 把结果保存到 clean_record：创建一份文件及其输入条件记录；参数：record.id, str(prefix), 5, 50, True, False, waveform=waveform。 |
| 70 | `                 s=AnalysisSettings(analysis_mode=mode,bench_windows=True,bench_hop_s=10) ` | 把结果保存到 s：创建一套分析设置；参数：analysis_mode=mode, bench_windows=True, bench_hop_s=10。 |
| 71 | `                 service=AnalysisService(s) ` | 把结果保存到 service：创建分析调度器，检查设置并准备各个分析模块；参数：s。 |
| 72 | `                 service.reader=BdfReader(folder/'cache',max_memory_bytes=1) ` | 把结果保存到 service.reader：调用 BdfReader；参数：folder / 'cache', max_memory_bytes=1。 |
| 73 | `                 trimmed=service.analyze([record],['EXG1','EXG2'],'EXG1') ` | 把结果保存到 trimmed：调用 service.analyze；参数：[record], ['EXG1', 'EXG2'], 'EXG1'。 |
| 74 | `                 self.assertEqual(list((folder/'cache').iterdir()),[]) ` | 断言两者相等，不相等则测试失败；参数：list((folder / 'cache').iterdir()), []。 |
| 75 | `                 s.exclude_last_s=0 ` | 把结果保存到 s.exclude_last_s：0。 |
| 76 | `                 clean=AnalysisService(s).analyze([clean_record],['EXG1','EXG2'],'EXG1') ` | 把结果保存到 clean：调用 AnalysisService(s).analyze；参数：[clean_record], ['EXG1', 'EXG2'], 'EXG1'。 |
| 77 | `                 untrimmed=AnalysisService(s).analyze([record],['EXG1','EXG2'],'EXG1') ` | 把结果保存到 untrimmed：调用 AnalysisService(s).analyze；参数：[record], ['EXG1', 'EXG2'], 'EXG1'。 |
| 78 | `                 self.assertEqual(trimmed.runs[0].channels,clean.runs[0].channels) ` | 断言两者相等，不相等则测试失败；参数：trimmed.runs[0].channels, clean.runs[0].channels。 |
| 79 | `                 self.assertEqual(trimmed.frames,clean.frames) ` | 断言两者相等，不相等则测试失败；参数：trimmed.frames, clean.frames。 |
| 80 | `                 self.assertEqual([(f['start_s'],f['end_s']) for f in trimmed.frames],[(0,10),(10,20)]) ` | 断言两者相等，不相等则测试失败；参数：[(f['start_s'], f['end_s']) for f in trimmed.frames], [(0, 10), (10, 20)]。 |
| 81 | `                 self.assertEqual(trimmed.runs[0].duration_s,20) ` | 断言两者相等，不相等则测试失败；参数：trimmed.runs[0].duration_s, 20。 |
| 82 | `                 self.assertEqual(trimmed.runs[0].source_duration_s,21) ` | 断言两者相等，不相等则测试失败；参数：trimmed.runs[0].source_duration_s, 21。 |
| 83 | `                 self.assertEqual(trimmed.runs[0].excluded_tail_s,1) ` | 断言两者相等，不相等则测试失败；参数：trimmed.runs[0].excluded_tail_s, 1。 |
| 84 | `                 self.assertEqual(Path(record.path).read_bytes(),original) ` | 断言两者相等，不相等则测试失败；参数：Path(record.path).read_bytes(), original。 |
| 85 | `                 self.assertIn('digital_rail_clipping',untrimmed.runs[0].channels['EXG1']['fit']['quality_reasons']) ` | 断言包含指定项；参数：'digital_rail_clipping', untrimmed.runs[0].channels['EXG1']['fit']['quality_reasons']。 |
| 86 | `                 self.assertNotIn('digital_rail_clipping',trimmed.runs[0].channels['EXG1']['fit']['quality_reasons']) ` | 断言不包含指定项；参数：'digital_rail_clipping', trimmed.runs[0].channels['EXG1']['fit']['quality_reasons']。 |
| 87 | `                 # Every retained crossing uses the original, unshifted time axis. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 88 | `                 for name in ('EXG1','EXG2'): ` | 遍历 ('EXG1', 'EXG2')，每次把一项赋给 name，执行下面缩进的循环体。 |
| 89 | `                     events=trimmed.runs[0].channels[name]['sync'].values ` | 把结果保存到 events：读取 trimmed.runs[0].channels[name]['sync'] 的 values 属性。 |
| 90 | `                     self.assertTrue(all(0<=t<20 for t in events['rising_events_s']+events['falling_events_s'])) ` | 断言条件为真；参数：all((0 <= t < 20 for t in events['rising_events_s'] + events['falling_events_s']))。 |
| 91 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 92 | `     def test_ecg_and_each_batch_file_are_cropped_separately(self): ` | 定义 test_ecg_and_each_batch_file_are_cropped_separately(self)。检查多个 ECG 文件各自裁尾、短文件不产生假窗口，以及保留段结果等于独立前段文件。 定义到这里时不执行函数体。 |
| 93 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 94 | `             a,data,fs=record_with_tail(folder,duration=12,name='a') ` | 把结果保存到 (a, data, fs)：调用 record_with_tail；参数：folder, duration=12, name='a'。 |
| 95 | `             b,_,_=record_with_tail(folder,duration=10,name='b') ` | 把结果保存到 (b, _, _)：调用 record_with_tail；参数：folder, duration=10, name='b'。 |
| 96 | `             for r in (a,b):r.waveform='ecg' ` | 遍历 (a, b)，每次把一项赋给 r，执行下面缩进的循环体。 把结果保存到 r.waveform：'ecg'。 |
| 97 | `             s=AnalysisSettings(analysis_mode='ecg') ` | 把结果保存到 s：创建一套分析设置；参数：analysis_mode='ecg'。 |
| 98 | `             result=AnalysisService(s).analyze([a,b],['EXG1','EXG2'],'') ` | 把结果保存到 result：调用 AnalysisService(s).analyze；参数：[a, b], ['EXG1', 'EXG2'], ''。 |
| 99 | `             self.assertEqual([r.duration_s for r in result.runs],[11,9]) ` | 断言两者相等，不相等则测试失败；参数：[r.duration_s for r in result.runs], [11, 9]。 |
| 100 | `             self.assertEqual([(f['record_id'],f['start_s'],f['end_s']) for f in result.frames],[('a',0,10),('a',1,11)]) ` | 断言两者相等，不相等则测试失败；参数：[(f['record_id'], f['start_s'], f['end_s']) for f in result.frames], [('a', 0, 10), ('a', 1, 11)]。 |
| 101 | `             self.assertEqual(result.runs[1].channels['EXG1']['complete_windows'],0) ` | 断言两者相等，不相等则测试失败；参数：result.runs[1].channels['EXG1']['complete_windows'], 0。 |
| 102 | `             self.assertIn('9.00 s retained',result.runs[1].channels['EXG1']['extra']['integrity'].message) ` | 断言包含指定项；参数：'9.00 s retained', result.runs[1].channels['EXG1']['extra']['integrity'].message。 |
| 103 | `             prefix=folder/'ecg-prefix.bdf';write_demo_bdf(prefix,data[:-fs],fs) ` | 把结果保存到 prefix：在 Path 路径 folder 后拼接 'ecg-prefix.bdf'；这里的 / 是路径拼接。 调用 write_demo_bdf；参数：prefix, data[:-fs], fs。 |
| 104 | `             clean=InputRecord(a.id,str(prefix),waveform='ecg') ` | 把结果保存到 clean：创建一份文件及其输入条件记录；参数：a.id, str(prefix), waveform='ecg'。 |
| 105 | `             s.exclude_last_s=0 ` | 把结果保存到 s.exclude_last_s：0。 |
| 106 | `             reference=AnalysisService(s).analyze([clean],['EXG1','EXG2'],'') ` | 把结果保存到 reference：调用 AnalysisService(s).analyze；参数：[clean], ['EXG1', 'EXG2'], ''。 |
| 107 | `             self.assertEqual(result.frames,reference.frames) ` | 断言两者相等，不相等则测试失败；参数：result.frames, reference.frames。 |
| 108 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 109 | `     def test_short_and_fractional_exclusions_are_explicit(self): ` | 定义 test_short_and_fractional_exclusions_are_explicit(self)。检查裁到无样本时报错、拒绝负数/非有限秒数、短记录无完整窗口及小数秒向上取样本整。 定义到这里时不执行函数体。 |
| 110 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 111 | `             record,_,_=record_with_tail(folder,duration=1) ` | 把结果保存到 (record, _, _)：调用 record_with_tail；参数：folder, duration=1。 |
| 112 | `             service=AnalysisService(AnalysisSettings()) ` | 把结果保存到 service：创建分析调度器，检查设置并准备各个分析模块；参数：AnalysisSettings()。 |
| 113 | `             with self.assertRaisesRegex(ValueError,'leaves no samples'): ` | 进入资源上下文：要求指定异常且消息匹配给定正则；参数：ValueError, 'leaves no samples'。退出时执行对应清理。 |
| 114 | `                 service.analyze([record],['EXG1'],'EXG1') ` | 调用 service.analyze；参数：[record], ['EXG1'], 'EXG1'。 |
| 115 | `             for value in (-1,float('nan'),float('inf')): ` | 遍历 (-1, float('nan'), float('inf'))，每次把一项赋给 value，执行下面缩进的循环体。 |
| 116 | `                 with self.assertRaises(ValueError):AnalysisSettings(exclude_last_s=value).validate() ` | 进入资源上下文：要求代码抛出指定异常，没抛反而测试失败；参数：ValueError。退出时执行对应清理。 调用 AnalysisSettings(exclude_last_s=value).validate。 |
| 117 | `             record,_,_=record_with_tail(folder,duration=3,name='short') ` | 把结果保存到 (record, _, _)：调用 record_with_tail；参数：folder, duration=3, name='short'。 |
| 118 | `             s=AnalysisSettings(bench_windows=True) ` | 把结果保存到 s：创建一套分析设置；参数：bench_windows=True。 |
| 119 | `             result=AnalysisService(s).analyze([record],['EXG1'],'EXG1') ` | 把结果保存到 result：调用 AnalysisService(s).analyze；参数：[record], ['EXG1'], 'EXG1'。 |
| 120 | `             self.assertEqual(result.runs[0].duration_s,2) ` | 断言两者相等，不相等则测试失败；参数：result.runs[0].duration_s, 2。 |
| 121 | `             self.assertEqual(result.frames,[]) ` | 断言两者相等，不相等则测试失败；参数：result.frames, []。 |
| 122 | `             s.exclude_last_s=.101 ` | 把结果保存到 s.exclude_last_s：0.101。 |
| 123 | `             result=AnalysisService(s).analyze([record],['EXG1'],'EXG1') ` | 把结果保存到 result：调用 AnalysisService(s).analyze；参数：[record], ['EXG1'], 'EXG1'。 |
| 124 | `             self.assertEqual(result.runs[0].excluded_tail_s,26/256) ` | 断言两者相等，不相等则测试失败；参数：result.runs[0].excluded_tail_s, 26 / 256。 |
| 125 | `             self.assertEqual(result.runs[0].duration_s,3-26/256) ` | 断言两者相等，不相等则测试失败；参数：result.runs[0].duration_s, 3 - 26 / 256。 |
| 126 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 127 | `     def test_gui_3d_and_exports_report_the_retained_interval(self): ` | 定义 test_gui_3d_and_exports_report_the_retained_interval(self)。检查主窗口、躯干和导出报告都显示保留/排除区间，改变排除秒数后清除旧结果。 定义到这里时不执行函数体。 |
| 128 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 129 | `             record,_,_=record_with_tail(folder) ` | 把结果保存到 (record, _, _)：调用 record_with_tail；参数：folder。 |
| 130 | `             with Path(record.path).open('r+b') as stream: ` | 进入资源上下文：打开文件或归档成员；参数：'r+b'，对象命名为 stream。退出时执行对应清理。 |
| 131 | `                 stream.seek(256);stream.write(b'A1'.ljust(16)+b'D32'.ljust(16)) ` | 调用 stream.seek；参数：256。 向输出流写入字节；参数：b'A1'.ljust(16) + b'D32'.ljust(16)。 |
| 132 | `             s=AnalysisSettings(bench_windows=True,bench_hop_s=10) ` | 把结果保存到 s：创建一套分析设置；参数：bench_windows=True, bench_hop_s=10。 |
| 133 | `             result=AnalysisService(s).analyze([record],['A1','D32'],'A1') ` | 把结果保存到 result：调用 AnalysisService(s).analyze；参数：[record], ['A1', 'D32'], 'A1'。 |
| 134 | `             with app_for([record]) as app: ` | 进入资源上下文：调用 app_for；参数：[record]，对象命名为 app。退出时执行对应清理。 |
| 135 | `                 app.mode.set('Gain error');app.accept_result(result);app.open_torso() ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Gain error'。 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 打开或抬起躯干窗口，连接选择回调，与主窗口共享指标和窗口结果。。 |
| 136 | `                 app.select_window(1) ` | 将时间轴提供的全局窗口索引映射到显示范围，并同步主窗口和躯干窗口。；参数：1。 |
| 137 | `                 self.assertEqual(app.torso_window.timeline.items[-1][2],20) ` | 断言两者相等，不相等则测试失败；参数：app.torso_window.timeline.items[-1][2], 20。 |
| 138 | `                 self.assertIn('analyzed 0-20 s of 21 s',app.detail.get('1.0','end')) ` | 断言包含指定项；参数：'analyzed 0-20 s of 21 s', app.detail.get('1.0', 'end')。 |
| 139 | `                 self.assertIn('excluded 20-21 s',app.torso_window.detail.get('1.0','end')) ` | 断言包含指定项；参数：'excluded 20-21 s', app.torso_window.detail.get('1.0', 'end')。 |
| 140 | `                 ReportExporter().save(result,folder/'export','gain',electrodes=app.displayed_electrodes(),scope=app.scope.get()) ` | 导出当前视图及完整实验结果、窗口表和事件表；HTML 中用户文本先转义。；参数：result, folder / 'export', 'gain', electrodes=app.displayed_electrodes(), scope=app.scope.get()。 |
| 141 | `                 payload=json.loads((folder/'export/results.json').read_text()) ` | 把结果保存到 payload：把 JSON 文本恢复为 Python 数据；参数：(folder / 'export/results.json').read_text()。 |
| 142 | `                 self.assertEqual(payload['runs'][0]['excluded_tail_s'],1) ` | 断言两者相等，不相等则测试失败；参数：payload['runs'][0]['excluded_tail_s'], 1。 |
| 143 | `                 self.assertEqual(payload['runs'][0]['source_duration_s'],21) ` | 断言两者相等，不相等则测试失败；参数：payload['runs'][0]['source_duration_s'], 21。 |
| 144 | `                 self.assertEqual(payload['runs'][0]['duration_s'],20) ` | 断言两者相等，不相等则测试失败；参数：payload['runs'][0]['duration_s'], 20。 |
| 145 | `                 self.assertEqual(payload['settings']['frequency_limit_pct'],.1) ` | 断言两者相等，不相等则测试失败；参数：payload['settings']['frequency_limit_pct'], 0.1。 |
| 146 | `                 page=(folder/'export/report.html').read_text() ` | 把结果保存到 page：读取文本文件。 |
| 147 | `                 self.assertIn('Excluded tail',page);self.assertIn('0-20 s',page) ` | 断言包含指定项；参数：'Excluded tail', page。 断言包含指定项；参数：'0-20 s', page。 |
| 148 | `                 self.assertEqual(load_project(folder/'export/project.json')[1].exclude_last_s,1) ` | 断言两者相等，不相等则测试失败；参数：load_project(folder / 'export/project.json')[1].exclude_last_s, 1。 |
| 149 | `                 app.limit_vars['exclude_last_s'].set('0') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'0'。 |
| 150 | `                 self.assertIsNone(app.result);self.assertEqual(app.torso_window.view.electrodes,{}) ` | 断言结果是 None；参数：app.result。 断言两者相等，不相等则测试失败；参数：app.torso_window.view.electrodes, {}。 |
| 151 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 152 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 153 | ` if __name__=='__main__':unittest.main() ` | 检查条件 __name__ == '__main__'；为真时执行下面缩进的一组语句。 调用 unittest.main。 |
