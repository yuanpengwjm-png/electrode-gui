# tests/test_stages.py：分析模式测试

检查正弦谐波分离、脉冲不走正弦拟合、ECG 窗口与 SQI、错误模式拒绝。

源码：[tests/test_stages.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py>)。本说明对应 142 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `test_harmonics_are_separated_from_noise_and_frequency_is_individual` | [22–33](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:22>) | 合成 10% 二次谐波和 2% 频偏，核对 THD、频率与 SNR/SINAD 差别。 |
| `test_unset_acceptance_is_not_green` | [35–39](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:35>) | THD/频率容差没设置时应显示黄色。 |
| `test_pulse_bypasses_sine_fit_and_measures_both_edges` | [41–53](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:41>) | 保证脉冲不调用正弦拟合，并能测平台幅度和双边沿延迟。 |
| `test_mode_mismatch_and_mixed_setups_are_rejected` | [55–60](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:55>) | 拒绝把 ECG 当正弦，或混合不同物理实验组。 |
| `test_short_ecg_is_never_padded_into_valid_windows` | [62–72](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:62>) | 短 ECG 返回数据不足，不能补零获得完整窗口。 |
| `test_two_detectors_and_flatline_baseline_faults` | [74–85](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:74>) | 检查两个心搏检测器，以及已知平线、漂移和宽带噪声的分项结果。 |
| `test_matching_is_one_to_one_and_no_beats_is_undefined` | [87–91](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:87>) | 一个心搏不能配两次；双方都无事件时不返回满分。 |
| `test_constant_ecg_flatline_and_clipping_are_explicit` | [93–100](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:93>) | 常数和数字量程端点要有明确完整性提示。 |
| `test_ecg_export_keeps_window_scope_and_project_mode` | [102–115](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:102>) | ECG 导出保留所选窗口、真实指标及模式。 |
| `test_gui_switch_clears_result_and_english_controls` | [117–138](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:117>) | 切换工作流时旧结果清除，并检查界面文本。 |
| `check_widgets` | [132–135](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py:132>) | 递归遍历测试窗口控件，检查其显示文字。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Signal-level checks for the stage split, new algorithms and English UI.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import replace ` | 从 dataclasses 导入 replace。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 4 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 5 | ` import re ` | 导入模块 re。从名称解析频率/幅度并筛选通道 |
| 6 | ` import unittest ` | 导入模块 unittest。自动验证已知输入的程序行为 |
| 7 | ` from unittest.mock import patch ` | 从 unittest.mock 导入 patch。临时替换对象模拟异常或禁止某条路径 |
| 8 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 9 | ` from config import AnalysisSettings ` | 从 config 导入 AnalysisSettings。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 10 | ` from models import InputRecord ` | 从 models 导入 InputRecord。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 11 | ` from modules.bench_spectrum import BenchSpectrumAnalyzer ` | 从 modules.bench_spectrum 导入 BenchSpectrumAnalyzer。独立估计每通道频率，拟合基频和指定谐波，把残差噪声与谐波功率分开，用于 SNR、THD、SINAD。 |
| 12 | ` from modules.ecg_quality import ECGQualityAnalyzer, BeatAgreement ` | 从 modules.ecg_quality 导入 ECGQualityAnalyzer、BeatAgreement。两个不同的心搏检测器加一对一匹配，计算 bSQI；Welch 频谱计算 pSQI/basSQI；另算 Pearson 峰度和平线/削顶。 |
| 13 | ` from services.analysis_service import AnalysisService ` | 从 services.analysis_service 导入 AnalysisService。验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 |
| 14 | ` from services.demo_data import create_mode_demo ` | 从 services.demo_data 导入 create_mode_demo。生成已知故障的合成 BDF：幅度偏差、延迟、非线性、重复变化、ECG 漂移、平线、噪声。演示标签不是实验验证结论。 |
| 15 | ` from utils.demo_bdf import write_demo_bdf ` | 从 utils.demo_bdf 导入 write_demo_bdf。只为演示/测试生成简单的连续 BDF；将已知 µV 数组打包成 24 位字节。 |
| 16 | ` from utils.project_io import save_project, load_project ` | 从 utils.project_io 导入 save_project、load_project。保存文件清单、参数、通道和参考；恢复时适配部分旧配置，并统一幅度单位。保存的是配置，不是复制原始 BDF。 |
| 17 | ` from utils.report_exporter import ReportExporter ` | 从 utils.report_exporter 导入 ReportExporter。生成当前视图的 PNG/CSV，以及完整 JSON、项目配置、各窗口和过零事件表、HTML 报告。 |
| 18 | ` from test_analysis import fixture_folder ` | 从 test_analysis 导入 fixture_folder。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 19 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 20 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 21 | ` class StageTests(unittest.TestCase): ` | 定义 StageTests 类，继承 unittest.TestCase；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 22 | `     def test_harmonics_are_separated_from_noise_and_frequency_is_individual(self): ` | 定义 test_harmonics_are_separated_from_noise_and_frequency_is_individual(self)。合成 10% 二次谐波和 2% 频偏，核对 THD、频率与 SNR/SINAD 差别。 定义到这里时不执行函数体。 |
| 23 | `         fs = 2048 ` | 把结果保存到 fs：2048。 |
| 24 | `         t = np.arange(fs*10)/fs ` | 把结果保存到 t：np.arange(fs * 10) 与 fs 相除。 |
| 25 | `         rng = np.random.default_rng(3) ` | 把结果保存到 rng：创建固定种子随机发生器，让演示可重复；参数：3。 |
| 26 | `         y = 2000*np.sin(2*np.pi*5.1*t) + 200*np.sin(2*np.pi*10.2*t) + rng.normal(0, 1, len(t)) ` | 把结果保存到 y：2000 * np.sin(2 * np.pi * 5.1 * t) + 200 * np.sin(2 * np.pi * 10.2 * t) 与 rng.normal(0, 1, len(t)) 相加。 |
| 27 | `         analyzer = BenchSpectrumAnalyzer(AnalysisSettings(thd_limit_pct=2, frequency_limit_pct=.5)) ` | 把结果保存到 analyzer：调用 BenchSpectrumAnalyzer；参数：AnalysisSettings(thd_limit_pct=2, frequency_limit_pct=0.5)。 |
| 28 | `         result = analyzer.analyze(y, fs, 5) ` | 把结果保存到 result：调用 analyzer.analyze；参数：y, fs, 5。 |
| 29 | `         self.assertAlmostEqual(result['thd'].values['thd_pct'], 10, delta=.15) ` | 在指定小数位或容差内比较数值；参数：result['thd'].values['thd_pct'], 10, delta=0.15。 |
| 30 | `         self.assertAlmostEqual(result['frequency'].values['error_pct'], 2, delta=.05) ` | 在指定小数位或容差内比较数值；参数：result['frequency'].values['error_pct'], 2, delta=0.05。 |
| 31 | `         self.assertEqual(result['frequency'].color, 'red') ` | 断言两者相等，不相等则测试失败；参数：result['frequency'].color, 'red'。 |
| 32 | `         self.assertEqual(result['thd'].color, 'red') ` | 断言两者相等，不相等则测试失败；参数：result['thd'].color, 'red'。 |
| 33 | `         self.assertGreater(result['snr'].values['snr_db'], result['sinad'].values['sinad_db']+20) ` | 断言左值大于右值；参数：result['snr'].values['snr_db'], result['sinad'].values['sinad_db'] + 20。 |
| 34 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 35 | `     def test_unset_acceptance_is_not_green(self): ` | 定义 test_unset_acceptance_is_not_green(self)。THD/频率容差没设置时应显示黄色。 定义到这里时不执行函数体。 |
| 36 | `         t = np.arange(4096)/1024 ` | 把结果保存到 t：np.arange(4096) 与 1024 相除。 |
| 37 | `         result = BenchSpectrumAnalyzer(AnalysisSettings(thd_limit_pct=None, frequency_limit_pct=None)).analyze(1000*np.sin(2*np.pi*5*t), 1024, 5) ` | 把结果保存到 result：调用 BenchSpectrumAnalyzer(AnalysisSettings(thd_limit_pct=None, frequency_limit_pct=None)).analyze；参数：1000 * np.sin(2 * np.pi * 5 * t), 1024, 5。 |
| 38 | `         self.assertEqual(result['thd'].color, 'yellow') ` | 断言两者相等，不相等则测试失败；参数：result['thd'].color, 'yellow'。 |
| 39 | `         self.assertEqual(result['frequency'].color, 'yellow') ` | 断言两者相等，不相等则测试失败；参数：result['frequency'].color, 'yellow'。 |
| 40 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 41 | `     def test_pulse_bypasses_sine_fit_and_measures_both_edges(self): ` | 定义 test_pulse_bypasses_sine_fit_and_measures_both_edges(self)。保证脉冲不调用正弦拟合，并能测平台幅度和双边沿延迟。 定义到这里时不执行函数体。 |
| 42 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 43 | `             records = create_mode_demo(folder, 3, 'bench_pulse') ` | 把结果保存到 records：按模式选择正弦演示，或生成 30 秒脉冲/ECG 数据并注入特定故障。；参数：folder, 3, 'bench_pulse'。 |
| 44 | `             service = AnalysisService(AnalysisSettings(analysis_mode='bench_pulse', frequency_limit_pct=1)) ` | 把结果保存到 service：创建分析调度器，检查设置并准备各个分析模块；参数：AnalysisSettings(analysis_mode='bench_pulse', frequency_limit_pct=1)。 |
| 45 | `             with patch.object(service.fitter, 'fit', side_effect=AssertionError('Sine fit must not run')): ` | 进入资源上下文：调用 patch.object；参数：service.fitter, 'fit', side_effect=AssertionError('Sine fit must not run')。退出时执行对应清理。 |
| 46 | `                 result = service.analyze(records, ['EXG1','EXG2','EXG3'], 'EXG1') ` | 把结果保存到 result：调用 service.analyze；参数：records, ['EXG1', 'EXG2', 'EXG3'], 'EXG1'。 |
| 47 | `             a = result.runs[0].channels ` | 把结果保存到 a：读取 result.runs[0] 的 channels 属性。 |
| 48 | `             self.assertAlmostEqual(a['EXG1']['gain'].values['output_mVpp'], 100, delta=.01) ` | 在指定小数位或容差内比较数值；参数：a['EXG1']['gain'].values['output_mVpp'], 100, delta=0.01。 |
| 49 | `             self.assertEqual(a['EXG2']['gain'].color, 'red') ` | 断言两者相等，不相等则测试失败；参数：a['EXG2']['gain'].color, 'red'。 |
| 50 | `             self.assertNotIn('thd', a['EXG1']['extra']) ` | 断言不包含指定项；参数：'thd', a['EXG1']['extra']。 |
| 51 | `             for direction in ('rising','falling'): ` | 遍历 ('rising', 'falling')，每次把一项赋给 direction，执行下面缩进的循环体。 |
| 52 | `                 self.assertAlmostEqual(a['EXG3']['sync'].values['directions'][direction]['median_ms'], 4, delta=1) ` | 在指定小数位或容差内比较数值；参数：a['EXG3']['sync'].values['directions'][direction]['median_ms'], 4, delta=1。 |
| 53 | `             self.assertEqual(a['EXG3']['sync'].color, 'red') ` | 断言两者相等，不相等则测试失败；参数：a['EXG3']['sync'].color, 'red'。 |
| 54 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 55 | `     def test_mode_mismatch_and_mixed_setups_are_rejected(self): ` | 定义 test_mode_mismatch_and_mixed_setups_are_rejected(self)。拒绝把 ECG 当正弦，或混合不同物理实验组。 定义到这里时不执行函数体。 |
| 56 | `         r = InputRecord('r','no-file.bdf',waveform='ecg') ` | 把结果保存到 r：创建一份文件及其输入条件记录；参数：'r', 'no-file.bdf', waveform='ecg'。 |
| 57 | `         with self.assertRaisesRegex(ValueError, 'does not match'): ` | 进入资源上下文：要求指定异常且消息匹配给定正则；参数：ValueError, 'does not match'。退出时执行对应清理。 |
| 58 | `             AnalysisService(AnalysisSettings()).analyze([r],['A1'],'A1') ` | 调用 AnalysisService(AnalysisSettings()).analyze；参数：[r], ['A1'], 'A1'。 |
| 59 | `         with self.assertRaisesRegex(ValueError, 'setups'): ` | 进入资源上下文：要求指定异常且消息匹配给定正则；参数：ValueError, 'setups'。退出时执行对应清理。 |
| 60 | `             AnalysisService(AnalysisSettings()).analyze([replace(r,waveform='sine'),InputRecord('r2','other.bdf',setup_group='other')],['A1'],'A1') ` | 调用 AnalysisService(AnalysisSettings()).analyze；参数：[replace(r, waveform='sine'), InputRecord('r2', 'other.bdf', setup_group='other')], ['A1'], 'A1'。 |
| 61 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 62 | `     def test_short_ecg_is_never_padded_into_valid_windows(self): ` | 定义 test_short_ecg_is_never_padded_into_valid_windows(self)。短 ECG 返回数据不足，不能补零获得完整窗口。 定义到这里时不执行函数体。 |
| 63 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 64 | `             path = folder/'short.bdf' ` | 把结果保存到 path：在 Path 路径 folder 后拼接 'short.bdf'；这里的 / 是路径拼接。 |
| 65 | `             write_demo_bdf(path, np.zeros((512,2)), 256) ` | 调用 write_demo_bdf；参数：path, np.zeros((512, 2)), 256。 |
| 66 | `             r = InputRecord('short',str(path),waveform='ecg') ` | 把结果保存到 r：创建一份文件及其输入条件记录；参数：'short', str(path), waveform='ecg'。 |
| 67 | `             service = AnalysisService(AnalysisSettings(analysis_mode='ecg')) ` | 把结果保存到 service：创建分析调度器，检查设置并准备各个分析模块；参数：AnalysisSettings(analysis_mode='ecg')。 |
| 68 | `             with patch.object(service.fitter, 'fit', side_effect=AssertionError('No sine fitting on ECG')): ` | 进入资源上下文：调用 patch.object；参数：service.fitter, 'fit', side_effect=AssertionError('No sine fitting on ECG')。退出时执行对应清理。 |
| 69 | `                 result = service.analyze([r],['EXG1','EXG2'],'') ` | 把结果保存到 result：调用 service.analyze；参数：[r], ['EXG1', 'EXG2'], ''。 |
| 70 | `             self.assertEqual(result.frames, []) ` | 断言两者相等，不相等则测试失败；参数：result.frames, []。 |
| 71 | `             self.assertTrue(all(e.metric('ecg_quality').color == 'yellow' for e in result.electrodes)) ` | 断言条件为真；参数：all((e.metric('ecg_quality').color == 'yellow' for e in result.electrodes))。 |
| 72 | `             self.assertIn('2.00 s', result.electrodes[0].metric('ecg_quality').message) ` | 断言包含指定项；参数：'2.00 s', result.electrodes[0].metric('ecg_quality').message。 |
| 73 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 74 | `     def test_two_detectors_and_flatline_baseline_faults(self): ` | 定义 test_two_detectors_and_flatline_baseline_faults(self)。检查两个心搏检测器，以及已知平线、漂移和宽带噪声的分项结果。 定义到这里时不执行函数体。 |
| 75 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 76 | `             records = create_mode_demo(folder, 4, 'ecg') ` | 把结果保存到 records：按模式选择正弦演示，或生成 30 秒脉冲/ECG 数据并注入特定故障。；参数：folder, 4, 'ecg'。 |
| 77 | `             result = AnalysisService(AnalysisSettings(analysis_mode='ecg')).analyze(records,['EXG1','EXG2','EXG3','EXG4'],'') ` | 把结果保存到 result：调用 AnalysisService(AnalysisSettings(analysis_mode='ecg')).analyze；参数：records, ['EXG1', 'EXG2', 'EXG3', 'EXG4'], ''。 |
| 78 | `             self.assertEqual(len(result.frames), 5) ` | 断言两者相等，不相等则测试失败；参数：len(result.frames), 5。 |
| 79 | `             first = result.frames[0]['metrics'] ` | 把结果保存到 first：按索引/键 'metrics' 取 result.frames[0] 的内容。 |
| 80 | `             self.assertEqual(first['EXG1']['ecg_quality'].color, 'green') ` | 断言两者相等，不相等则测试失败；参数：first['EXG1']['ecg_quality'].color, 'green'。 |
| 81 | `             self.assertGreater(first['EXG1']['bsqi'].values['value'], .9) ` | 断言左值大于右值；参数：first['EXG1']['bsqi'].values['value'], 0.9。 |
| 82 | `             self.assertEqual(first['EXG2']['bassqi'].color,'red') ` | 断言两者相等，不相等则测试失败；参数：first['EXG2']['bassqi'].color, 'red'。 |
| 83 | `             self.assertEqual(result.frames[1]['metrics']['EXG3']['integrity'].color, 'red') ` | 断言两者相等，不相等则测试失败；参数：result.frames[1]['metrics']['EXG3']['integrity'].color, 'red'。 |
| 84 | `             self.assertEqual(first['EXG3']['integrity'].color, 'green') ` | 断言两者相等，不相等则测试失败；参数：first['EXG3']['integrity'].color, 'green'。 |
| 85 | `             self.assertEqual(first['EXG4']['ksqi'].color,'red') ` | 断言两者相等，不相等则测试失败；参数：first['EXG4']['ksqi'].color, 'red'。 |
| 86 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 87 | `     def test_matching_is_one_to_one_and_no_beats_is_undefined(self): ` | 定义 test_matching_is_one_to_one_and_no_beats_is_undefined(self)。一个心搏不能配两次；双方都无事件时不返回满分。 定义到这里时不执行函数体。 |
| 88 | `         score, matched = BeatAgreement.score([1.,1.02,2.], [1.01,2.], .05) ` | 把结果保存到 (score, matched)：调用 BeatAgreement.score；参数：[1.0, 1.02, 2.0], [1.01, 2.0], 0.05。 |
| 89 | `         self.assertEqual(matched, 2) ` | 断言两者相等，不相等则测试失败；参数：matched, 2。 |
| 90 | `         self.assertAlmostEqual(score, 2/3) ` | 在指定小数位或容差内比较数值；参数：score, 2 / 3。 |
| 91 | `         self.assertEqual(BeatAgreement.score([], [], .05), (None, 0)) ` | 断言两者相等，不相等则测试失败；参数：BeatAgreement.score([], [], 0.05), (None, 0)。 |
| 92 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 93 | `     def test_constant_ecg_flatline_and_clipping_are_explicit(self): ` | 定义 test_constant_ecg_flatline_and_clipping_are_explicit(self)。常数和数字量程端点要有明确完整性提示。 定义到这里时不执行函数体。 |
| 94 | `         analyzer = ECGQualityAnalyzer(AnalysisSettings(analysis_mode='ecg')) ` | 把结果保存到 analyzer：调用 ECGQualityAnalyzer；参数：AnalysisSettings(analysis_mode='ecg')。 |
| 95 | `         result = analyzer.analyze_window(np.zeros(2500), 250) ` | 把结果保存到 result：调用 analyzer.analyze_window；参数：np.zeros(2500), 250。 |
| 96 | `         self.assertEqual(result['integrity'].color, 'red') ` | 断言两者相等，不相等则测试失败；参数：result['integrity'].color, 'red'。 |
| 97 | `         self.assertEqual(result['bsqi'].color, 'yellow') ` | 断言两者相等，不相等则测试失败；参数：result['bsqi'].color, 'yellow'。 |
| 98 | `         self.assertEqual(result['ecg_quality'].color, 'red') ` | 断言两者相等，不相等则测试失败；参数：result['ecg_quality'].color, 'red'。 |
| 99 | `         clipped = analyzer.analyze_window(np.full(2500, 100.), 250, [-100,100]) ` | 把结果保存到 clipped：调用 analyzer.analyze_window；参数：np.full(2500, 100.0), 250, [-100, 100]。 |
| 100 | `         self.assertEqual(clipped['integrity'].values['clipped_samples'],2500) ` | 断言两者相等，不相等则测试失败；参数：clipped['integrity'].values['clipped_samples'], 2500。 |
| 101 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 102 | `     def test_ecg_export_keeps_window_scope_and_project_mode(self): ` | 定义 test_ecg_export_keeps_window_scope_and_project_mode(self)。ECG 导出保留所选窗口、真实指标及模式。 定义到这里时不执行函数体。 |
| 103 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 104 | `             records = create_mode_demo(folder/'data',3,'ecg') ` | 把结果保存到 records：按模式选择正弦演示，或生成 30 秒脉冲/ECG 数据并注入特定故障。；参数：folder / 'data', 3, 'ecg'。 |
| 105 | `             result = AnalysisService(AnalysisSettings(analysis_mode='ecg')).analyze(records,['EXG1','EXG2','EXG3'],'') ` | 把结果保存到 result：调用 AnalysisService(AnalysisSettings(analysis_mode='ecg')).analyze；参数：records, ['EXG1', 'EXG2', 'EXG3'], ''。 |
| 106 | `             frame = result.frames[1] ` | 把结果保存到 frame：按索引/键 1 取 result.frames 的内容。 |
| 107 | `             displayed = [replace(e, extra=frame['metrics'][e.name]) for e in result.electrodes] ` | 把结果保存到 displayed：从 result.electrodes 逐个取 e，为每项生成 replace(e, extra=frame['metrics'][e.name])。 |
| 108 | `             ReportExporter().save(result,folder/'report','integrity',electrodes=displayed,scope='5-15 s') ` | 导出当前视图及完整实验结果、窗口表和事件表；HTML 中用户文本先转义。；参数：result, folder / 'report', 'integrity', electrodes=displayed, scope='5-15 s'。 |
| 109 | `             payload = json.loads((folder/'report/results.json').read_text(encoding='utf-8')) ` | 把结果保存到 payload：把 JSON 文本恢复为 Python 数据；参数：(folder / 'report/results.json').read_text(encoding='utf-8')。 |
| 110 | `             self.assertEqual(payload['export_view']['scope'],'5-15 s') ` | 断言两者相等，不相等则测试失败；参数：payload['export_view']['scope'], '5-15 s'。 |
| 111 | `             self.assertEqual(payload['export_view']['electrode_results'][2]['extra']['integrity']['color'],'red') ` | 断言两者相等，不相等则测试失败；参数：payload['export_view']['electrode_results'][2]['extra']['integrity']['color'], 'red'。 |
| 112 | `             _,settings,_,reference=load_project(folder/'report/project.json') ` | 把结果保存到 (_, settings, _, reference)：读取 JSON、兼容旧字段、解析相对路径、过滤允许的设置字段并校验。；参数：folder / 'report/project.json'。 |
| 113 | `             self.assertEqual(settings.analysis_mode,'ecg'); self.assertEqual(reference,'') ` | 断言两者相等，不相等则测试失败；参数：settings.analysis_mode, 'ecg'。 断言两者相等，不相等则测试失败；参数：reference, ''。 |
| 114 | `             self.assertIn('start_s,end_s', (folder/'report/ecg_windows.csv').read_text(encoding='utf-8-sig')) ` | 断言包含指定项；参数：'start_s,end_s', (folder / 'report/ecg_windows.csv').read_text(encoding='utf-8-sig')。 |
| 115 | `             self.assertNotRegex((folder/'report/report.html').read_text(encoding='utf-8'),r'[\u4e00-\u9fff]') ` | 断言文本不匹配给定正则；参数：(folder / 'report/report.html').read_text(encoding='utf-8'), '[\\u4e00-\\u9fff]'。 |
| 116 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 117 | `     def test_gui_switch_clears_result_and_english_controls(self): ` | 定义 test_gui_switch_clears_result_and_english_controls(self)。切换工作流时旧结果清除，并检查界面文本。 定义到这里时不执行函数体。 |
| 118 | `         import tkinter as tk ` | 导入模块 tkinter（别名 tk）。桌面窗口、控件、文件选择框和消息框 |
| 119 | `         from gui import ElectrodeQAApp ` | 从 gui 导入 ElectrodeQAApp。创建 Tkinter 窗口，收集用户输入，用后台线程启动分析，并把结果交给热图、时间轴及躯干窗口。这里不直接计算 SQI。 |
| 120 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 121 | `             root = tk.Tk() ` | 创建 Tkinter 的根窗口；按钮和其他控件都挂在这个窗口或其子容器里。 |
| 122 | `         except tk.TclError: ` | 捕获 tk.TclError 异常，执行错误处理。 |
| 123 | `             self.skipTest('No Tk display') ` | 环境不支持时明确跳过该测试；参数：'No Tk display'。 |
| 124 | `         root.withdraw() ` | 隐藏测试窗口。 |
| 125 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 126 | `             app = ElectrodeQAApp(root) ` | 把结果保存到 app：创建主应用对象，立即运行 __init__ 搭建控件并连接按钮回调；参数：root。 |
| 127 | `             app.result = object() ` | 把结果保存到 app.result：调用 object。 |
| 128 | `             app.profile.set('Stage 2 - ECG quality'); app.change_profile() ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Stage 2 - ECG quality'。 切换工作流后更新指标列表和提示；脉冲移除 SNR/SINAD/THD 选项，然后清空旧结果。。 |
| 129 | `             self.assertIsNone(app.result) ` | 断言结果是 None；参数：app.result。 |
| 130 | `             self.assertEqual(app.mode.get(),'ECG quality') ` | 断言两者相等，不相等则测试失败；参数：app.mode.get(), 'ECG quality'。 |
| 131 | `             self.assertEqual(str(app.ref_combo.cget('state')),'disabled') ` | 断言两者相等，不相等则测试失败；参数：str(app.ref_combo.cget('state')), 'disabled'。 |
| 132 | `             def check_widgets(widget): ` | 定义 check_widgets(widget)。递归遍历测试窗口控件，检查其显示文字。 定义到这里时不执行函数体。 |
| 133 | `                 if 'text' in widget.keys(): ` | 检查条件 'text' in widget.keys()；为真时执行下面缩进的一组语句。 |
| 134 | `                     self.assertNotRegex(str(widget.cget('text')),r'[\u4e00-\u9fff]') ` | 断言文本不匹配给定正则；参数：str(widget.cget('text')), '[\\u4e00-\\u9fff]'。 |
| 135 | `                 for child in widget.winfo_children(): check_widgets(child) ` | 遍历 widget.winfo_children()，每次把一项赋给 child，执行下面缩进的循环体。 调用 check_widgets；参数：child。 |
| 136 | `             check_widgets(root) ` | 调用 check_widgets；参数：root。 |
| 137 | `         finally: ` | 不管前面的操作成功还是抛异常，都执行这里的收尾/资源清理。 |
| 138 | `             root.destroy() ` | 销毁窗口及控件。 |
| 139 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 140 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 141 | ` if __name__ == '__main__': ` | 只有直接运行这个文件时才进入启动代码；被 import 时不自动打开窗口。 |
| 142 | `     unittest.main() ` | 调用 unittest.main。 |
