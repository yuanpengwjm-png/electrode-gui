# tests/test_large_bdf.py：大数据路径测试

检查磁盘缓存与内存读取得到相同结果、异常清理及磁盘不足处理。

源码：[tests/test_large_bdf.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_large_bdf.py>)。本说明对应 112 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `test_disk_and_ram_reads_identical_for_bdf_and_zip_and_cleanup` | [20–41](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_large_bdf.py:20>) | 验证普通/ZIP 文件在磁盘与内存模式逐样本相同，并在异常后清缓存。 |
| `test_native_channel_fit_matches_original_vectorized_formula` | [43–70](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_large_bdf.py:43>) | 新逐列拟合与原矩阵公式的频率、幅度和去基线样本应相符。 |
| `objective` | [55–57](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_large_bdf.py:55>) | 测试用的拟合残差目标函数，用于比较数组存储路径和数值结果。 |
| `test_all_modes_use_disk_context_and_match_ram_results` | [72–88](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_large_bdf.py:72>) | 三条分析路径均支持磁盘映射，数值结果与内存一致。 |
| `test_low_disk_space_fails_clearly_without_leaking_cache` | [90–97](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_large_bdf.py:90>) | 模拟磁盘不足，应该明确报错且不遗留缓存。 |
| `test_directory_cleanup_lock_does_not_discard_completed_work` | [99–108](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_large_bdf.py:99>) | 模拟清理锁定，只给警告而不丢弃已完成计算。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Disk-backed reads and channel-wise fits retain native-rate measurements.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import asdict ` | 从 dataclasses 导入 asdict。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 4 | ` from unittest.mock import patch ` | 从 unittest.mock 导入 patch。临时替换对象模拟异常或禁止某条路径 |
| 5 | ` import unittest ` | 导入模块 unittest。自动验证已知输入的程序行为 |
| 6 | ` import zipfile ` | 导入模块 zipfile。只读原始 ZIP 成员或写测试 ZIP |
| 7 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 8 | ` from scipy.optimize import minimize_scalar ` | 从 scipy.optimize 导入 minimize_scalar。在范围内寻找使拟合残差最小的频率 |
| 9 | ` from config import AnalysisSettings ` | 从 config 导入 AnalysisSettings。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 10 | ` from services.analysis_service import AnalysisService ` | 从 services.analysis_service 导入 AnalysisService。验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 |
| 11 | ` from services.demo_data import create_demo, create_mode_demo ` | 从 services.demo_data 导入 create_demo、create_mode_demo。生成已知故障的合成 BDF：幅度偏差、延迟、非线性、重复变化、ECG 漂移、平线、噪声。演示标签不是实验验证结论。 |
| 12 | ` from modules.sine_fitter import SineFitter ` | 从 modules.sine_fitter 导入 SineFitter。调用底层正弦拟合，返回幅度等结果和按需去基线的通道对象，供过零检测使用。 |
| 13 | ` from utils.array_store import ArrayStore ` | 从 utils.array_store 导入 ArrayStore。小数组放内存，大于阈值的数组用临时磁盘映射；正常退出或异常退出都尝试清理本次缓存。 |
| 14 | ` from utils.bdf_reader import BdfReader ` | 从 utils.bdf_reader 导入 BdfReader。检查头信息、真实通道及长度，支持 ZIP 内部成员，并通过上下文管理大数组的生命周期。 |
| 15 | ` from utils.numerics import sine_design ` | 从 utils.numerics 导入 sine_design。按 BDF 头解码 24 位样本并换算 µV；用共同频率及逐通道最小二乘计算正弦幅度、基线和拟合残差。 |
| 16 | ` from test_analysis import fixture_folder ` | 从 test_analysis 导入 fixture_folder。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 17 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 18 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 19 | ` class LargeBdfTests(unittest.TestCase): ` | 定义 LargeBdfTests 类，继承 unittest.TestCase；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 20 | `     def test_disk_and_ram_reads_identical_for_bdf_and_zip_and_cleanup(self): ` | 定义 test_disk_and_ram_reads_identical_for_bdf_and_zip_and_cleanup(self)。验证普通/ZIP 文件在磁盘与内存模式逐样本相同，并在异常后清缓存。 定义到这里时不执行函数体。 |
| 21 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 22 | `             record = create_demo(folder/'inputs', 3)[0] ` | 把结果保存到 record：按索引/键 0 取 create_demo(folder / 'inputs', 3) 的内容。 |
| 23 | `             names = ['EXG3', 'EXG1'] ` | 把结果保存到 names：组装列表：['EXG3', 'EXG1']。 |
| 24 | `             expected, fs, metadata = BdfReader().read(record, names) ` | 把结果保存到 (expected, fs, metadata)：从文件流读取字节；参数：record, names。 |
| 25 | `             archive = folder/'input.zip' ` | 把结果保存到 archive：在 Path 路径 folder 后拼接 'input.zip'；这里的 / 是路径拼接。 |
| 26 | `             with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z: ` | 进入资源上下文：调用 zipfile.ZipFile；参数：archive, 'w', zipfile.ZIP_DEFLATED，对象命名为 z。退出时执行对应清理。 |
| 27 | `                 z.write(record.path, 'test.bdf') ` | 向输出流写入字节；参数：record.path, 'test.bdf'。 |
| 28 | `             for zipped in (False, True): ` | 遍历 (False, True)，每次把一项赋给 zipped，执行下面缩进的循环体。 |
| 29 | `                 if zipped: ` | 检查条件 zipped；为真时执行下面缩进的一组语句。 |
| 30 | `                     record.path, record.member = str(archive), 'test.bdf' ` | 把结果保存到 (record.path, record.member)：组装元组：(str(archive), 'test.bdf')。 |
| 31 | `                 reader = BdfReader(folder/'cache', max_memory_bytes=1) ` | 把结果保存到 reader：调用 BdfReader；参数：folder / 'cache', max_memory_bytes=1。 |
| 32 | `                 with reader.open_data(record, names) as (actual, rate, header): ` | 进入资源上下文：调用 reader.open_data；参数：record, names，对象命名为 (actual, rate, header)。退出时执行对应清理。 |
| 33 | `                     self.assertIsInstance(actual, np.memmap) ` | 断言数据类型符合预期；参数：actual, np.memmap。 |
| 34 | `                     self.assertTrue(actual.flags.f_contiguous) ` | 断言条件为真；参数：actual.flags.f_contiguous。 |
| 35 | `                     np.testing.assert_array_equal(actual, expected) ` | 检查数组逐元素完全一致；参数：actual, expected。 |
| 36 | `                     self.assertEqual((rate, header), (fs, metadata)) ` | 断言两者相等，不相等则测试失败；参数：(rate, header), (fs, metadata)。 |
| 37 | `                 self.assertEqual(list((folder/'cache').iterdir()), []) ` | 断言两者相等，不相等则测试失败；参数：list((folder / 'cache').iterdir()), []。 |
| 38 | `             with self.assertRaisesRegex(RuntimeError, 'intentional'): ` | 进入资源上下文：要求指定异常且消息匹配给定正则；参数：RuntimeError, 'intentional'。退出时执行对应清理。 |
| 39 | `                 with reader.open_data(record, names): ` | 进入资源上下文：调用 reader.open_data；参数：record, names。退出时执行对应清理。 |
| 40 | `                     raise RuntimeError('intentional analysis failure') ` | 抛出异常并停止当前正常流程：调用 RuntimeError；参数：'intentional analysis failure'；上层可捕获并显示原因。 |
| 41 | `             self.assertEqual(list((folder/'cache').iterdir()), []) ` | 断言两者相等，不相等则测试失败；参数：list((folder / 'cache').iterdir()), []。 |
| 42 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 43 | `     def test_native_channel_fit_matches_original_vectorized_formula(self): ` | 定义 test_native_channel_fit_matches_original_vectorized_formula(self)。新逐列拟合与原矩阵公式的频率、幅度和去基线样本应相符。 定义到这里时不执行函数体。 |
| 44 | `         s = AnalysisSettings() ` | 把结果保存到 s：创建一套分析设置。 |
| 45 | `         fs = 2048 ` | 把结果保存到 fs：2048。 |
| 46 | `         t = np.arange(fs*4)/fs ` | 把结果保存到 t：np.arange(fs * 4) 与 fs 相除。 |
| 47 | `         rng = np.random.default_rng(23) ` | 把结果保存到 rng：创建固定种子随机发生器，让演示可重复；参数：23。 |
| 48 | `         x = 50000*np.sin(2*np.pi*5.013*(t[:, None]-np.array([0., .002, -.001]))) ` | 把结果保存到 x：50000 与 np.sin(2 * np.pi * 5.013 * (t[:, None] - np.array([0.0, 0.002, -0.001]))) 相乘。 |
| 49 | `         x += np.array([250., -800., 310.]) + t[:, None]*np.array([140., -25., 13.]) ` | 把 x 的原值加上 np.array([250.0, -800.0, 310.0]) + t[:, None] * np.array([140.0, -25.0, 13.0])，再写回同一变量。 |
| 50 | `         x += rng.normal(0, 3, x.shape) ` | 把 x 的原值加上 rng.normal(0, 3, x.shape)，再写回同一变量。 |
| 51 | `         # Independent reproduction of the pre-refactor vectorized computation. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 52 | `         trace = np.median(x-np.median(x, axis=0), axis=1) ` | 把结果保存到 trace：计算中位数；参数：x - np.median(x, axis=0), axis=1。 |
| 53 | `         step = max(1, len(t)//4000) ` | 把结果保存到 step：取最大值；参数：1, len(t) // 4000。 |
| 54 | `         ts, ys = t[::step], trace[::step] ` | 把结果保存到 (ts, ys)：组装元组：(t[::step], trace[::step])。 |
| 55 | `         def objective(f): ` | 定义 objective(f)。测试用的拟合残差目标函数，用于比较数组存储路径和数值结果。 定义到这里时不执行函数体。 |
| 56 | `             b = sine_design(ts, f) ` | 把结果保存到 b：调用 sine_design；参数：ts, f。 |
| 57 | `             return float(np.mean((ys-b @ np.linalg.lstsq(b, ys, rcond=None)[0])**2)) ` | 结束当前函数并返回：转换为浮点数；参数：np.mean((ys - b @ np.linalg.lstsq(b, ys, rcond=None)[0]) ** 2)。 |
| 58 | `         grid = np.linspace(4.75, 5.25, 31) ` | 把结果保存到 grid：生成包含两端的等间隔数值；参数：4.75, 5.25, 31。 |
| 59 | `         best = int(np.argmin([objective(f) for f in grid])) ` | 把结果保存到 best：转换为整数；参数：np.argmin([objective(f) for f in grid])。 |
| 60 | `         frequency = minimize_scalar(objective, bounds=(grid[max(0,best-1)], grid[min(30,best+1)]), ` | 把结果保存到 frequency：读取 minimize_scalar(objective, bounds=(grid[max(0, best - 1)], grid[min(30…（完整表达式见左栏） 的 x 属性。 |
| 61 | `                                     method='bounded', options={'xatol':1e-10}).x ` | 接续第 60 行的同一条语句，不是另起一段算法。 把结果保存到 frequency：读取 minimize_scalar(objective, bounds=(grid[max(0, best - 1)], grid[min(30…（完整表达式见左栏） 的 x 属性。 |
| 62 | `         basis = sine_design(t, frequency) ` | 把结果保存到 basis：调用 sine_design；参数：t, frequency。 |
| 63 | `         beta = np.linalg.lstsq(basis, x, rcond=None)[0] ` | 把结果保存到 beta：按索引/键 0 取 np.linalg.lstsq(basis, x, rcond=None) 的内容。 |
| 64 | `         expected = x-(beta[2]+(t-t.mean())[:, None]*beta[3]) ` | 把结果保存到 expected：x 与 beta[2] + (t - t.mean())[:, None] * beta[3] 相减。 |
| 65 | `         fits, lazy = SineFitter(s).fit(x, fs, 5., lazy=True) ` | 把结果保存到 (fits, lazy)：调用 SineFitter(s).fit；参数：x, fs, 5.0, lazy=True。 |
| 66 | `         for i, fit in enumerate(fits): ` | 遍历 enumerate(fits)，每次把一项赋给 (i, fit)，执行下面缩进的循环体。 |
| 67 | `             self.assertAlmostEqual(fit['fitted_frequency_hz'], frequency, places=10) ` | 在指定小数位或容差内比较数值；参数：fit['fitted_frequency_hz'], frequency, places=10。 |
| 68 | `             self.assertAlmostEqual(fit['amplitude_pp_mV'], 2*np.hypot(beta[0,i],beta[1,i])/1000, places=9) ` | 在指定小数位或容差内比较数值；参数：fit['amplitude_pp_mV'], 2 * np.hypot(beta[0, i], beta[1, i]) / 1000, places=9。 |
| 69 | `             self.assertAlmostEqual(fit['residual_rms_uV'], np.sqrt(np.mean((x[:,i]-basis@beta[:,i])**2)), places=7) ` | 在指定小数位或容差内比较数值；参数：fit['residual_rms_uV'], np.sqrt(np.mean((x[:, i] - basis @ beta[:, i]) ** 2)), places=7。 |
| 70 | `             np.testing.assert_allclose(lazy.column(i), expected[:,i], atol=1e-7, rtol=0) ` | 按数值容差逐元素检查数组一致；参数：lazy.column(i), expected[:, i], atol=1e-07, rtol=0。 |
| 71 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 72 | `     def test_all_modes_use_disk_context_and_match_ram_results(self): ` | 定义 test_all_modes_use_disk_context_and_match_ram_results(self)。三条分析路径均支持磁盘映射，数值结果与内存一致。 定义到这里时不执行函数体。 |
| 73 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 74 | `             for mode in ('bench_sine', 'bench_pulse', 'ecg'): ` | 遍历 ('bench_sine', 'bench_pulse', 'ecg')，每次把一项赋给 mode，执行下面缩进的循环体。 |
| 75 | `                 records = create_mode_demo(folder/mode, 3, mode)[:1] ` | 把结果保存到 records：按索引/键 :1 取 create_mode_demo(folder / mode, 3, mode) 的内容；切片包含起点、不包含终点。 |
| 76 | `                 settings = AnalysisSettings(analysis_mode=mode, bench_windows=True, ` | 把结果保存到 settings：创建一套分析设置；参数：analysis_mode=mode, bench_windows=True, bench_window_s=1, bench_hop_s=1。 |
| 77 | `                                             bench_window_s=1, bench_hop_s=1) ` | 接续第 76 行的同一条语句，不是另起一段算法。 把结果保存到 settings：创建一套分析设置；参数：analysis_mode=mode, bench_windows=True, bench_window_s=1, bench_hop_s=1。 |
| 78 | `                 names = ['EXG1', 'EXG2', 'EXG3'] ` | 把结果保存到 names：组装列表：['EXG1', 'EXG2', 'EXG3']。 |
| 79 | `                 ram = AnalysisService(settings) ` | 把结果保存到 ram：创建分析调度器，检查设置并准备各个分析模块；参数：settings。 |
| 80 | `                 expected = ram.analyze(records, names, 'EXG1') ` | 把结果保存到 expected：调用 ram.analyze；参数：records, names, 'EXG1'。 |
| 81 | `                 disk = AnalysisService(settings) ` | 把结果保存到 disk：创建分析调度器，检查设置并准备各个分析模块；参数：settings。 |
| 82 | `                 disk.reader = BdfReader(folder/'cache', max_memory_bytes=1) ` | 把结果保存到 disk.reader：调用 BdfReader；参数：folder / 'cache', max_memory_bytes=1。 |
| 83 | `                 with patch.object(disk.reader, 'read', side_effect=AssertionError('Full in-memory read must not be used')): ` | 进入资源上下文：调用 patch.object；参数：disk.reader, 'read', side_effect=AssertionError('Full in-memory read must not be used')。退出时执行对应清理。 |
| 84 | `                     actual = disk.analyze(records, names, 'EXG1') ` | 把结果保存到 actual：调用 disk.analyze；参数：records, names, 'EXG1'。 |
| 85 | `                 a, b = asdict(actual), asdict(expected) ` | 把结果保存到 (a, b)：组装元组：(asdict(actual), asdict(expected))。 |
| 86 | `                 a.pop('elapsed_s'); b.pop('elapsed_s') ` | 取出并移除指定项；参数：'elapsed_s'。 取出并移除指定项；参数：'elapsed_s'。 |
| 87 | `                 self.assertEqual(a, b) ` | 断言两者相等，不相等则测试失败；参数：a, b。 |
| 88 | `                 self.assertEqual(list((folder/'cache').iterdir()), []) ` | 断言两者相等，不相等则测试失败；参数：list((folder / 'cache').iterdir()), []。 |
| 89 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 90 | `     def test_low_disk_space_fails_clearly_without_leaking_cache(self): ` | 定义 test_low_disk_space_fails_clearly_without_leaking_cache(self)。模拟磁盘不足，应该明确报错且不遗留缓存。 定义到这里时不执行函数体。 |
| 91 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 92 | `             with patch('utils.array_store.shutil.disk_usage') as usage: ` | 进入资源上下文：调用 patch；参数：'utils.array_store.shutil.disk_usage'，对象命名为 usage。退出时执行对应清理。 |
| 93 | `                 usage.return_value.free = 0 ` | 把结果保存到 usage.return_value.free：0。 |
| 94 | `                 with self.assertRaisesRegex(ValueError, 'Insufficient disk space'): ` | 进入资源上下文：要求指定异常且消息匹配给定正则；参数：ValueError, 'Insufficient disk space'。退出时执行对应清理。 |
| 95 | `                     with ArrayStore(folder/'cache', max_memory_bytes=1) as store: ` | 进入资源上下文：调用 ArrayStore；参数：folder / 'cache', max_memory_bytes=1，对象命名为 store。退出时执行对应清理。 |
| 96 | `                         store.empty((100, 3)) ` | 调用 store.empty；参数：(100, 3)。 |
| 97 | `             self.assertEqual(list((folder/'cache').iterdir()), []) ` | 断言两者相等，不相等则测试失败；参数：list((folder / 'cache').iterdir()), []。 |
| 98 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 99 | `     def test_directory_cleanup_lock_does_not_discard_completed_work(self): ` | 定义 test_directory_cleanup_lock_does_not_discard_completed_work(self)。模拟清理锁定，只给警告而不丢弃已完成计算。 定义到这里时不执行函数体。 |
| 100 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 101 | `             with self.assertWarnsRegex(RuntimeWarning, 'cleanup incomplete'): ` | 进入资源上下文：调用 self.assertWarnsRegex；参数：RuntimeWarning, 'cleanup incomplete'。退出时执行对应清理。 |
| 102 | `                 with patch.object(Path, 'rmdir', side_effect=PermissionError('simulated sync lock')): ` | 进入资源上下文：调用 patch.object；参数：Path, 'rmdir', side_effect=PermissionError('simulated sync lock')。退出时执行对应清理。 |
| 103 | `                     with ArrayStore(folder/'cache', max_memory_bytes=1) as store: ` | 进入资源上下文：调用 ArrayStore；参数：folder / 'cache', max_memory_bytes=1，对象命名为 store。退出时执行对应清理。 |
| 104 | `                         array = store.empty((100, 3)) ` | 把结果保存到 array：调用 store.empty；参数：(100, 3)。 |
| 105 | `                         array[:] = 2 ` | 把结果保存到 array[:]：2。 |
| 106 | `                         measured = float(array[:, 1].mean()) ` | 把结果保存到 measured：转换为浮点数；参数：array[:, 1].mean()。 |
| 107 | `             self.assertEqual(measured, 2) ` | 断言两者相等，不相等则测试失败；参数：measured, 2。 |
| 108 | `             self.assertEqual(list((folder/'cache').rglob('*.float64')), []) ` | 断言两者相等，不相等则测试失败；参数：list((folder / 'cache').rglob('*.float64')), []。 |
| 109 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 110 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 111 | ` if __name__ == '__main__': ` | 只有直接运行这个文件时才进入启动代码；被 import 时不自动打开窗口。 |
| 112 | `     unittest.main() ` | 调用 unittest.main。 |
