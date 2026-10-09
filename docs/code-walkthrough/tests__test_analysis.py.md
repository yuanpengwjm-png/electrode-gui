# tests/test_analysis.py：基础行为测试

用已知输入检查 BDF 单位、幅度/同步/线性/重复性、配置往返、GUI 状态及导出。

源码：[tests/test_analysis.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py>)。本说明对应 189 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `fixture_folder` | [26–38](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:26>) | 为测试创建独立临时文件夹，并在 finally 中核验路径后清理，仅用于测试。 |
| `test_bdf_metadata_scaling_and_dynamic_channel_count` | [42–56](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:42>) | 检查头信息、实际通道数量、采样率和从数字量到物理幅度的换算。 |
| `test_known_fault_classes_and_full_export` | [58–83](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:58>) | 注入已知幅度、同步、线性与重复故障，核对颜色和导出的文件。 |
| `test_single_bdf_is_not_linearity_or_independent_repetition` | [85–92](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:85>) | 保证单份记录不能冒充多个输入等级或多次独立实验。 |
| `test_unknown_input_cannot_show_green_gain` | [94–98](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:94>) | 实际输入未确认时，即使输出相等也不能给绿色增益结论。 |
| `test_three_color_threshold_boundaries` | [100–105](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:100>) | 核对 80% 预警边界及超限边界，包含负误差。 |
| `test_actual_crossings_both_directions_and_signed_time` | [107–118](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:107>) | 核对双向过零插值时刻及提前/滞后的正负号。 |
| `test_missing_period_is_not_reindexed_onto_next_cycle` | [120–130](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:120>) | 漏掉周期后保持参考索引，不能错配下一周期。 |
| `test_bad_reference_invalidates_relative_timing` | [132–139](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:132>) | 参考通道不可靠时，同步评价应降为待复核。 |
| `test_duplicate_records_rejected_and_project_roundtrip` | [141–152](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:141>) | 拒绝把同一文件重复加载，并验证配置保存后能恢复。 |
| `test_gui_dynamic_count_background_analysis_and_stale_result_clear` | [154–185](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py:154>) | 检查通道数量、后台运行、圆点数量及改参数后的结果清除。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Known-input tests: real BDF bytes, fault classes, matching and UI wiring.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from contextlib import contextmanager ` | 从 contextlib 导入 contextmanager。管理 with 的进入/退出和资源清理 |
| 3 | ` from dataclasses import asdict ` | 从 dataclasses 导入 asdict。自动生成数据类并在数据类/字典之间转换 |
| 4 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 5 | ` import copy ` | 导入模块 copy。复制本次分析参数以隔离界面修改 |
| 6 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 7 | ` import shutil ` | 导入模块 shutil。磁盘空间检查和测试缓存清理 |
| 8 | ` import time ` | 导入模块 time。测量耗时或给测试循环计时 |
| 9 | ` import unittest ` | 导入模块 unittest。自动验证已知输入的程序行为 |
| 10 | ` import uuid ` | 导入模块 uuid。生成本次缓存/测试目录的唯一名称 |
| 11 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 12 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 13 | ` from config import AnalysisSettings ` | 从 config 导入 AnalysisSettings。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 14 | ` from models import InputRecord ` | 从 models 导入 InputRecord。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 15 | ` from modules.gain_error import AmplitudePeakGainError ` | 从 modules.gain_error 导入 AmplitudePeakGainError。用输出基频/平台 Vpp 与确认过的实际输入比较；没有可靠波形或输入校准时，不把结果判为幅度合格。 |
| 16 | ` from modules.sine_fitter import SineFitter ` | 从 modules.sine_fitter 导入 SineFitter。调用底层正弦拟合，返回幅度等结果和按需去基线的通道对象，供过零检测使用。 |
| 17 | ` from modules.time_synchronization import TimeSynchronizationAnalyzer, ZeroCrossingDetector ` | 从 modules.time_synchronization 导入 TimeSynchronizationAnalyzer、ZeroCrossingDetector。先找上升、下降过零事件，再分别匹配；不移动波形，不用后面的周期补漏检。输出事件表、延迟 P95 和 jitter。 |
| 18 | ` from services.analysis_service import AnalysisService ` | 从 services.analysis_service 导入 AnalysisService。验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 |
| 19 | ` from services.demo_data import create_demo ` | 从 services.demo_data 导入 create_demo。生成已知故障的合成 BDF：幅度偏差、延迟、非线性、重复变化、ECG 漂移、平线、噪声。演示标签不是实验验证结论。 |
| 20 | ` from utils.bdf_reader import BdfReader ` | 从 utils.bdf_reader 导入 BdfReader。检查头信息、真实通道及长度，支持 ZIP 内部成员，并通过上下文管理大数组的生命周期。 |
| 21 | ` from utils.project_io import save_project, load_project ` | 从 utils.project_io 导入 save_project、load_project。保存文件清单、参数、通道和参考；恢复时适配部分旧配置，并统一幅度单位。保存的是配置，不是复制原始 BDF。 |
| 22 | ` from utils.report_exporter import ReportExporter ` | 从 utils.report_exporter 导入 ReportExporter。生成当前视图的 PNG/CSV，以及完整 JSON、项目配置、各窗口和过零事件表、HTML 报告。 |
| 23 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 24 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 25 | ` @contextmanager ` | @contextmanager 将含 yield 的函数变为 with 可用的资源管理器。 |
| 26 | ` def fixture_folder(): ` | 定义 fixture_folder()。为测试创建独立临时文件夹，并在 finally 中核验路径后清理，仅用于测试。 定义到这里时不执行函数体。 |
| 27 | `     # Inherit the workspace ACL; Windows Python 3.13's tempfile 0700 ACL can ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 28 | `     # exclude a restricted process token from its own temporary directory. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 29 | `     root = (Path(__file__).resolve().parents[1]/"output/test-fixtures").resolve() ` | 把结果保存到 root：解析绝对路径。 |
| 30 | `     root.mkdir(parents=True, exist_ok=True) ` | 创建目录；参数：parents=True, exist_ok=True。 |
| 31 | `     folder = root/uuid.uuid4().hex ` | 把结果保存到 folder：在 Path 路径 root 后拼接 uuid.uuid4().hex；这里的 / 是路径拼接。 |
| 32 | `     folder.mkdir() ` | 创建目录。 |
| 33 | `     try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 34 | `         yield folder ` | 把 folder 暂时交给调用者；上下文退出后继续执行清理。 |
| 35 | `     finally: ` | 不管前面的操作成功还是抛异常，都执行这里的收尾/资源清理。 |
| 36 | `         if folder.resolve().parent != root: ` | 检查条件 folder.resolve().parent != root；为真时执行下面缩进的一组语句。 |
| 37 | `             raise RuntimeError("Refusing cleanup outside fixture root") ` | 抛出异常并停止当前正常流程：调用 RuntimeError；参数：'Refusing cleanup outside fixture root'；上层可捕获并显示原因。 |
| 38 | `         shutil.rmtree(folder) ` | 调用 shutil.rmtree；参数：folder。 |
| 39 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 40 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 41 | ` class AnalysisTests(unittest.TestCase): ` | 定义 AnalysisTests 类，继承 unittest.TestCase；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 42 | `     def test_bdf_metadata_scaling_and_dynamic_channel_count(self): ` | 定义 test_bdf_metadata_scaling_and_dynamic_channel_count(self)。检查头信息、实际通道数量、采样率和从数字量到物理幅度的换算。 定义到这里时不执行函数体。 |
| 43 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 44 | `             records = create_demo(folder, 12) ` | 把结果保存到 records：调用 create_demo；参数：folder, 12。 |
| 45 | `             reader = BdfReader() ` | 把结果保存到 reader：调用 BdfReader。 |
| 46 | `             info = reader.inspect(records[0]) ` | 把结果保存到 info：调用 reader.inspect；参数：records[0]。 |
| 47 | `             self.assertEqual(len(info.voltage_labels), 12) ` | 断言两者相等，不相等则测试失败；参数：len(info.voltage_labels), 12。 |
| 48 | `             self.assertEqual(info.sample_rates["EXG1"], 2048) ` | 断言两者相等，不相等则测试失败；参数：info.sample_rates['EXG1'], 2048。 |
| 49 | `             self.assertEqual(info.duration_s, 4) ` | 断言两者相等，不相等则测试失败；参数：info.duration_s, 4。 |
| 50 | `             chosen = reader.choose_channels(info, 3) ` | 把结果保存到 chosen：调用 reader.choose_channels；参数：info, 3。 |
| 51 | `             x, fs, _ = reader.read(records[0], chosen) ` | 把结果保存到 (x, fs, _)：从文件流读取字节；参数：records[0], chosen。 |
| 52 | `             self.assertEqual(x.shape, (8192, 3)) ` | 断言两者相等，不相等则测试失败；参数：x.shape, (8192, 3)。 |
| 53 | `             fits, _ = SineFitter(AnalysisSettings()).fit(x, fs, 5) ` | 把结果保存到 (fits, _)：调用 SineFitter(AnalysisSettings()).fit；参数：x, fs, 5。 |
| 54 | `             self.assertAlmostEqual(fits[0]["amplitude_pp_mV"], 50, places=3) ` | 在指定小数位或容差内比较数值；参数：fits[0]['amplitude_pp_mV'], 50, places=3。 |
| 55 | `             with self.assertRaises(ValueError): ` | 进入资源上下文：要求代码抛出指定异常，没抛反而测试失败；参数：ValueError。退出时执行对应清理。 |
| 56 | `                 reader.choose_channels(info, 13) ` | 调用 reader.choose_channels；参数：info, 13。 |
| 57 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 58 | `     def test_known_fault_classes_and_full_export(self): ` | 定义 test_known_fault_classes_and_full_export(self)。注入已知幅度、同步、线性与重复故障，核对颜色和导出的文件。 定义到这里时不执行函数体。 |
| 59 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 60 | `             records = create_demo(folder/"inputs", 8) ` | 把结果保存到 records：调用 create_demo；参数：folder / 'inputs', 8。 |
| 61 | `             # This original four-second fixture checks its full event counts. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 62 | `             result = AnalysisService(AnalysisSettings(exclude_last_s=0)).analyze(records, [f"EXG{i}" for i in range(1,9)], "EXG1") ` | 把结果保存到 result：调用 AnalysisService(AnalysisSettings(exclude_last_s=0)).analyze；参数：records, [f'EXG{i}' for i in range(1, 9)], 'EXG1'。 |
| 63 | `             a = {e.name:e for e in result.electrodes} ` | 把结果保存到 a：从 result.electrodes 逐个取 e，为每项生成 e.name: e。 |
| 64 | `             self.assertEqual(a["EXG1"].gain.color, "green") ` | 断言两者相等，不相等则测试失败；参数：a['EXG1'].gain.color, 'green'。 |
| 65 | `             self.assertEqual(a["EXG1"].synchronization.color, "yellow") ` | 断言两者相等，不相等则测试失败；参数：a['EXG1'].synchronization.color, 'yellow'。 |
| 66 | `             self.assertEqual(a["EXG2"].gain.color, "red") ` | 断言两者相等，不相等则测试失败；参数：a['EXG2'].gain.color, 'red'。 |
| 67 | `             self.assertEqual(a["EXG2"].linearity.color, "green") ` | 断言两者相等，不相等则测试失败；参数：a['EXG2'].linearity.color, 'green'。 |
| 68 | `             self.assertEqual(a["EXG3"].gain.color, "yellow") ` | 断言两者相等，不相等则测试失败；参数：a['EXG3'].gain.color, 'yellow'。 |
| 69 | `             self.assertEqual(a["EXG4"].synchronization.color, "red") ` | 断言两者相等，不相等则测试失败；参数：a['EXG4'].synchronization.color, 'red'。 |
| 70 | `             self.assertEqual(a["EXG5"].synchronization.color, "yellow") ` | 断言两者相等，不相等则测试失败；参数：a['EXG5'].synchronization.color, 'yellow'。 |
| 71 | `             self.assertEqual(a["EXG6"].linearity.color, "red") ` | 断言两者相等，不相等则测试失败；参数：a['EXG6'].linearity.color, 'red'。 |
| 72 | `             self.assertEqual(a["EXG7"].gain.color, "yellow") ` | 断言两者相等，不相等则测试失败；参数：a['EXG7'].gain.color, 'yellow'。 |
| 73 | `             self.assertEqual(a["EXG8"].repetition.color, "red") ` | 断言两者相等，不相等则测试失败；参数：a['EXG8'].repetition.color, 'red'。 |
| 74 | `             ReportExporter().save(result, folder/"export", title="TEST DATA") ` | 导出当前视图及完整实验结果、窗口表和事件表；HTML 中用户文本先转义。；参数：result, folder / 'export', title='TEST DATA'。 |
| 75 | `             for name in ("heatmap.png", "results.json", "report.html", "electrodes.csv", "zero_pairs.csv", "zero_counts_and_time.csv", "project.json"): ` | 遍历 ('heatmap.png', 'results.json', 'report.html', 'electrodes.csv', 'zero_pairs.csv', 'zero_counts_and_time.csv', 'project.json')，每次把一项赋给 name，执行下面缩进的循环体。 |
| 76 | `                 self.assertTrue((folder/"export"/name).exists()) ` | 断言条件为真；参数：(folder / 'export' / name).exists()。 |
| 77 | `             payload = json.loads((folder/"export/results.json").read_text(encoding="utf-8")) ` | 把结果保存到 payload：把 JSON 文本恢复为 Python 数据；参数：(folder / 'export/results.json').read_text(encoding='utf-8')。 |
| 78 | `             self.assertEqual(len(payload["electrodes"]), 8) ` | 断言两者相等，不相等则测试失败；参数：len(payload['electrodes']), 8。 |
| 79 | `             run = result.runs[0].channels["EXG4"]["sync"].values ` | 把结果保存到 run：读取 result.runs[0].channels['EXG4']['sync'] 的 values 属性。 |
| 80 | `             self.assertGreater(run["rising_count"], 15) ` | 断言左值大于右值；参数：run['rising_count'], 15。 |
| 81 | `             self.assertGreater(run["falling_count"], 15) ` | 断言左值大于右值；参数：run['falling_count'], 15。 |
| 82 | `             for d in ("rising", "falling"): ` | 遍历 ('rising', 'falling')，每次把一项赋给 d，执行下面缩进的循环体。 |
| 83 | `                 self.assertAlmostEqual(run["directions"][d]["median_ms"], 3, delta=.002) ` | 在指定小数位或容差内比较数值；参数：run['directions'][d]['median_ms'], 3, delta=0.002。 |
| 84 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 85 | `     def test_single_bdf_is_not_linearity_or_independent_repetition(self): ` | 定义 test_single_bdf_is_not_linearity_or_independent_repetition(self)。保证单份记录不能冒充多个输入等级或多次独立实验。 定义到这里时不执行函数体。 |
| 86 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 87 | `             records = create_demo(folder, 8)[:1] ` | 把结果保存到 records：按索引/键 :1 取 create_demo(folder, 8) 的内容；切片包含起点、不包含终点。 |
| 88 | `             result = AnalysisService(AnalysisSettings()).analyze(records, ["EXG1", "EXG2"], "EXG1") ` | 把结果保存到 result：调用 AnalysisService(AnalysisSettings()).analyze；参数：records, ['EXG1', 'EXG2'], 'EXG1'。 |
| 89 | `             self.assertEqual(len(result.electrodes), 2) ` | 断言两者相等，不相等则测试失败；参数：len(result.electrodes), 2。 |
| 90 | `             self.assertTrue(all(e.linearity.color == "yellow" and e.repetition.color == "yellow" for e in result.electrodes)) ` | 断言条件为真；参数：all((e.linearity.color == 'yellow' and e.repetition.color == 'yellow' for e in result.electrodes))。 |
| 91 | `             self.assertEqual(result.electrodes[0].metric("current").color, "green") ` | 断言两者相等，不相等则测试失败；参数：result.electrodes[0].metric('current').color, 'green'。 |
| 92 | `             self.assertEqual(result.electrodes[0].metric("overall").color, "yellow") ` | 断言两者相等，不相等则测试失败；参数：result.electrodes[0].metric('overall').color, 'yellow'。 |
| 93 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 94 | `     def test_unknown_input_cannot_show_green_gain(self): ` | 定义 test_unknown_input_cannot_show_green_gain(self)。实际输入未确认时，即使输出相等也不能给绿色增益结论。 定义到这里时不执行函数体。 |
| 95 | `         record = InputRecord("unknown", "x.bdf", input_mVpp=100, input_confirmed=False) ` | 把结果保存到 record：创建一份文件及其输入条件记录；参数：'unknown', 'x.bdf', input_mVpp=100, input_confirmed=False。 |
| 96 | `         fit = dict(amplitude_pp_mV=100, quality_reasons=[]) ` | 把结果保存到 fit：组装键值字典；参数：amplitude_pp_mV=100, quality_reasons=[]。 |
| 97 | `         result = AmplitudePeakGainError(AnalysisSettings()).evaluate(fit, record) ` | 把结果保存到 result：调用 AmplitudePeakGainError(AnalysisSettings()).evaluate；参数：fit, record。 |
| 98 | `         self.assertEqual(result.color, "yellow") ` | 断言两者相等，不相等则测试失败；参数：result.color, 'yellow'。 |
| 99 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 100 | `     def test_three_color_threshold_boundaries(self): ` | 定义 test_three_color_threshold_boundaries(self)。核对 80% 预警边界及超限边界，包含负误差。 定义到这里时不执行函数体。 |
| 101 | `         settings = AnalysisSettings() ` | 把结果保存到 settings：创建一套分析设置。 |
| 102 | `         self.assertEqual(settings.color(3.99, 5), "green") ` | 断言两者相等，不相等则测试失败；参数：settings.color(3.99, 5), 'green'。 |
| 103 | `         self.assertEqual(settings.color(4, 5), "yellow") ` | 断言两者相等，不相等则测试失败；参数：settings.color(4, 5), 'yellow'。 |
| 104 | `         self.assertEqual(settings.color(5, 5), "yellow") ` | 断言两者相等，不相等则测试失败；参数：settings.color(5, 5), 'yellow'。 |
| 105 | `         self.assertEqual(settings.color(-5.01, 5), "red") ` | 断言两者相等，不相等则测试失败；参数：settings.color(-5.01, 5), 'red'。 |
| 106 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 107 | `     def test_actual_crossings_both_directions_and_signed_time(self): ` | 定义 test_actual_crossings_both_directions_and_signed_time(self)。核对双向过零插值时刻及提前/滞后的正负号。 定义到这里时不执行函数体。 |
| 108 | `         settings = AnalysisSettings() ` | 把结果保存到 settings：创建一套分析设置。 |
| 109 | `         fs = 4096 ` | 把结果保存到 fs：4096。 |
| 110 | `         t = np.arange(fs*3)/fs ` | 把结果保存到 t：np.arange(fs * 3) 与 fs 相除。 |
| 111 | `         x = 50000*np.sin(2*np.pi*5*(t[:, None]-np.array([0., -.002]))) + 6000+100*t[:, None] ` | 把结果保存到 x：50000 * np.sin(2 * np.pi * 5 * (t[:, None] - np.array([0.0, -0.002]))) + 6000 与 100 * t[:, None] 相加。 |
| 112 | `         fits, centred = SineFitter(settings).fit(x, fs, 5) ` | 把结果保存到 (fits, centred)：调用 SineFitter(settings).fit；参数：x, fs, 5。 |
| 113 | `         data = TimeSynchronizationAnalyzer(settings).evaluate_all(centred, fits, ["EXG1", "EXG2"], "EXG1", fs, 5) ` | 把结果保存到 data：调用 TimeSynchronizationAnalyzer(settings).evaluate_all；参数：centred, fits, ['EXG1', 'EXG2'], 'EXG1', fs, 5。 |
| 114 | `         for direction in ("rising", "falling"): ` | 遍历 ('rising', 'falling')，每次把一项赋给 direction，执行下面缩进的循环体。 |
| 115 | `             self.assertAlmostEqual(data["EXG2"].values["directions"][direction]["median_ms"], -2, delta=.001) ` | 在指定小数位或容差内比较数值；参数：data['EXG2'].values['directions'][direction]['median_ms'], -2, delta=0.001。 |
| 116 | `         detector = ZeroCrossingDetector(settings) ` | 把结果保存到 detector：调用 ZeroCrossingDetector；参数：settings。 |
| 117 | `         np.testing.assert_allclose(detector.detect(np.array([-4., -1., 3., 5.]), 1000, 5, 5, "rising"), [.00125]) ` | 按数值容差逐元素检查数组一致；参数：detector.detect(np.array([-4.0, -1.0, 3.0, 5.0]), 1000, 5, 5, 'rising'), [0.00125]。 |
| 118 | `         np.testing.assert_allclose(detector.detect(np.array([4., 1., -3., -5.]), 1000, 5, 5, "falling"), [.00125]) ` | 按数值容差逐元素检查数组一致；参数：detector.detect(np.array([4.0, 1.0, -3.0, -5.0]), 1000, 5, 5, 'falling'), [0.00125]。 |
| 119 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 120 | `     def test_missing_period_is_not_reindexed_onto_next_cycle(self): ` | 定义 test_missing_period_is_not_reindexed_onto_next_cycle(self)。漏掉周期后保持参考索引，不能错配下一周期。 定义到这里时不执行函数体。 |
| 121 | `         analyzer = TimeSynchronizationAnalyzer(AnalysisSettings()) ` | 把结果保存到 analyzer：调用 TimeSynchronizationAnalyzer；参数：AnalysisSettings()。 |
| 122 | `         reference = np.array([.2, .4, .6, .8]) ` | 把结果保存到 reference：构造 NumPy 数组；参数：[0.2, 0.4, 0.6, 0.8]。 |
| 123 | `         target = np.array([.202, .402, .802]) ` | 把结果保存到 target：构造 NumPy 数组；参数：[0.202, 0.402, 0.802]。 |
| 124 | `         pairs, counts = analyzer.match_direction(reference, target, 5, 1) ` | 把结果保存到 (pairs, counts)：调用 analyzer.match_direction；参数：reference, target, 5, 1。 |
| 125 | `         self.assertEqual(counts["missing"], 1) ` | 断言两者相等，不相等则测试失败；参数：counts['missing'], 1。 |
| 126 | `         self.assertEqual([p["reference_event_index"] for p in pairs], [0, 1, 3]) ` | 断言两者相等，不相等则测试失败；参数：[p['reference_event_index'] for p in pairs], [0, 1, 3]。 |
| 127 | `         self.assertTrue(all(abs(p["delay_ms"]-2) < 1e-8 for p in pairs)) ` | 断言条件为真；参数：all((abs(p['delay_ms'] - 2) < 1e-08 for p in pairs))。 |
| 128 | `         reversed_pairs, counts = analyzer.match_direction(reference, reference+.1, 5, 1) ` | 把结果保存到 (reversed_pairs, counts)：调用 analyzer.match_direction；参数：reference, reference + 0.1, 5, 1。 |
| 129 | `         self.assertEqual(reversed_pairs, []) ` | 断言两者相等，不相等则测试失败；参数：reversed_pairs, []。 |
| 130 | `         self.assertEqual(counts["missing"], 4) ` | 断言两者相等，不相等则测试失败；参数：counts['missing'], 4。 |
| 131 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 132 | `     def test_bad_reference_invalidates_relative_timing(self): ` | 定义 test_bad_reference_invalidates_relative_timing(self)。参考通道不可靠时，同步评价应降为待复核。 定义到这里时不执行函数体。 |
| 133 | `         settings = AnalysisSettings() ` | 把结果保存到 settings：创建一套分析设置。 |
| 134 | `         t = np.arange(4096)/1024 ` | 把结果保存到 t：np.arange(4096) 与 1024 相除。 |
| 135 | `         x = 50000*np.sin(2*np.pi*5*t) ` | 把结果保存到 x：50000 与 np.sin(2 * np.pi * 5 * t) 相乘。 |
| 136 | `         fits = [dict(amplitude_pp_mV=100., quality_reasons=["bad_reference"]), dict(amplitude_pp_mV=100., quality_reasons=[])] ` | 把结果保存到 fits：组装列表：[dict(amplitude_pp_mV=100.0, quality_reasons=['bad_reference']), dict(amplitude_pp_mV=100.0, quality_reasons=[])]。 |
| 137 | `         result = TimeSynchronizationAnalyzer(settings).evaluate_all(np.column_stack((x,x)), fits, ["EXG1","EXG2"], "EXG1", 1024, 5) ` | 把结果保存到 result：调用 TimeSynchronizationAnalyzer(settings).evaluate_all；参数：np.column_stack((x, x)), fits, ['EXG1', 'EXG2'], 'EXG1', 1024, 5。 |
| 138 | `         self.assertEqual(result["EXG2"].color, "yellow") ` | 断言两者相等，不相等则测试失败；参数：result['EXG2'].color, 'yellow'。 |
| 139 | `         self.assertIn("Reference", result["EXG2"].message) ` | 断言包含指定项；参数：'Reference', result['EXG2'].message。 |
| 140 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 141 | `     def test_duplicate_records_rejected_and_project_roundtrip(self): ` | 定义 test_duplicate_records_rejected_and_project_roundtrip(self)。拒绝把同一文件重复加载，并验证配置保存后能恢复。 定义到这里时不执行函数体。 |
| 142 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 143 | `             records = create_demo(folder, 3) ` | 把结果保存到 records：调用 create_demo；参数：folder, 3。 |
| 144 | `             duplicate = copy.deepcopy(records[0]) ` | 把结果保存到 duplicate：深复制嵌套对象，避免改动与当前 GUI 状态共用对象；参数：records[0]。 |
| 145 | `             duplicate.id += "copy" ` | 把 duplicate.id 的原值加上 'copy'，再写回同一变量。 |
| 146 | `             with self.assertRaises(ValueError): ` | 进入资源上下文：要求代码抛出指定异常，没抛反而测试失败；参数：ValueError。退出时执行对应清理。 |
| 147 | `                 AnalysisService(AnalysisSettings()).analyze([records[0],duplicate], ["EXG1"], "EXG1") ` | 调用 AnalysisService(AnalysisSettings()).analyze；参数：[records[0], duplicate], ['EXG1'], 'EXG1'。 |
| 148 | `             save_project(folder/"project.json", records, AnalysisSettings(), ["EXG1","EXG2"], "EXG1") ` | 把记录和设置的数据类转成 JSON，保留通道、参考与可选布局信息。；参数：folder / 'project.json', records, AnalysisSettings(), ['EXG1', 'EXG2'], 'EXG1'。 |
| 149 | `             loaded, settings, channels, reference = load_project(folder/"project.json") ` | 把结果保存到 (loaded, settings, channels, reference)：读取 JSON、兼容旧字段、解析相对路径、过滤允许的设置字段并校验。；参数：folder / 'project.json'。 |
| 150 | `             self.assertEqual([asdict(r) for r in records], [asdict(r) for r in loaded]) ` | 断言两者相等，不相等则测试失败；参数：[asdict(r) for r in records], [asdict(r) for r in loaded]。 |
| 151 | `             self.assertEqual(channels, ["EXG1","EXG2"]) ` | 断言两者相等，不相等则测试失败；参数：channels, ['EXG1', 'EXG2']。 |
| 152 | `             self.assertEqual(reference, "EXG1") ` | 断言两者相等，不相等则测试失败；参数：reference, 'EXG1'。 |
| 153 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 154 | `     def test_gui_dynamic_count_background_analysis_and_stale_result_clear(self): ` | 定义 test_gui_dynamic_count_background_analysis_and_stale_result_clear(self)。检查通道数量、后台运行、圆点数量及改参数后的结果清除。 定义到这里时不执行函数体。 |
| 155 | `         import tkinter as tk ` | 导入模块 tkinter（别名 tk）。桌面窗口、控件、文件选择框和消息框 |
| 156 | `         from gui import ElectrodeQAApp ` | 从 gui 导入 ElectrodeQAApp。创建 Tkinter 窗口，收集用户输入，用后台线程启动分析，并把结果交给热图、时间轴及躯干窗口。这里不直接计算 SQI。 |
| 157 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 158 | `             root = tk.Tk() ` | 创建 Tkinter 的根窗口；按钮和其他控件都挂在这个窗口或其子容器里。 |
| 159 | `         except tk.TclError: ` | 捕获 tk.TclError 异常，执行错误处理。 |
| 160 | `             self.skipTest("Tk display unavailable") ` | 环境不支持时明确跳过该测试；参数：'Tk display unavailable'。 |
| 161 | `         root.withdraw() ` | 隐藏测试窗口。 |
| 162 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 163 | `             with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 164 | `                 app = ElectrodeQAApp(root) ` | 把结果保存到 app：创建主应用对象，立即运行 __init__ 搭建控件并连接按钮回调；参数：root。 |
| 165 | `                 app.records = create_demo(folder, 12)[:1] ` | 把结果保存到 app.records：按索引/键 :1 取 create_demo(folder, 12) 的内容；切片包含起点、不包含终点。 |
| 166 | `                 app.refresh_records() ` | 重新填充文件列表，默认选择第一条，或在空列表时显示无文件。。 |
| 167 | `                 app.initialize_channels() ` | 读取第一份文件头，选择实际存在的电压通道，并设置参考和数量。。 |
| 168 | `                 app.count.set("3") ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'3'。 |
| 169 | `                 app.apply_count() ` | 把用户填写的数量应用为一组真实通道；数量本身不能创造文件里不存在的电极。。 |
| 170 | `                 self.assertEqual(app.channels, ["EXG1", "EXG2", "EXG3"]) ` | 断言两者相等，不相等则测试失败；参数：app.channels, ['EXG1', 'EXG2', 'EXG3']。 |
| 171 | `                 app.run() ` | 取得固定的分析请求，启动后台工作线程，再安排主线程轮询消息。。 |
| 172 | `                 deadline = time.monotonic()+15 ` | 把结果保存到 deadline：time.monotonic() 与 15 相加。 |
| 173 | `                 while app.busy and time.monotonic() < deadline: ` | 只要 app.busy and time.monotonic() < deadline 为真就重复循环；退出依靠条件改变、break 或异常。 |
| 174 | `                     root.update() ` | 调用 root.update。 |
| 175 | `                     time.sleep(.01) ` | 调用 time.sleep；参数：0.01。 |
| 176 | `                 self.assertFalse(app.busy) ` | 断言条件为假；参数：app.busy。 |
| 177 | `                 self.assertIsNotNone(app.result) ` | 断言有实际结果；参数：app.result。 |
| 178 | `                 root.update_idletasks() ` | 调用 root.update_idletasks。 |
| 179 | `                 self.assertEqual(len(app.heatmap.canvas.find_withtag("electrode_circle")), 3) ` | 断言两者相等，不相等则测试失败；参数：len(app.heatmap.canvas.find_withtag('electrode_circle')), 3。 |
| 180 | `                 self.assertEqual(len(app.results_tree.get_children()), 3) ` | 断言两者相等，不相等则测试失败；参数：len(app.results_tree.get_children()), 3。 |
| 181 | `                 app.limit_vars["gain_limit_pct"].set("6") ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'6'。 |
| 182 | `                 self.assertIsNone(app.result) ` | 断言结果是 None；参数：app.result。 |
| 183 | `                 self.assertEqual(len(app.heatmap.canvas.find_withtag("electrode_circle")), 0) ` | 断言两者相等，不相等则测试失败；参数：len(app.heatmap.canvas.find_withtag('electrode_circle')), 0。 |
| 184 | `         finally: ` | 不管前面的操作成功还是抛异常，都执行这里的收尾/资源清理。 |
| 185 | `             root.destroy() ` | 销毁窗口及控件。 |
| 186 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 187 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 188 | ` if __name__ == "__main__": ` | 只有直接运行这个文件时才执行下方入口；导入模块只定义类和函数。 |
| 189 | `     unittest.main() ` | 调用 unittest.main。 |
