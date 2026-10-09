# services/demo_data.py：演示数据

生成已知故障的合成 BDF：幅度偏差、延迟、非线性、重复变化、ECG 漂移、平线、噪声。演示标签不是实验验证结论。

源码：[services/demo_data.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/demo_data.py>)。本说明对应 77 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `create_demo` | [8–32](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/demo_data.py:8>) | 生成五次已知正弦实验，包含三个幅度等级和三次 100 mV 独立合成记录。 |
| `create_mode_demo` | [35–61](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/demo_data.py:35>) | 按模式选择正弦演示，或生成 30 秒脉冲/ECG 数据并注入特定故障。 |
| `create_timeline_demo` | [64–77](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/demo_data.py:64>) | 生成 30 秒正弦，在第二通道 10–20 秒把振荡幅度减半，便于观察窗口颜色变化。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Known synthetic faults, clearly separated from real laboratory data.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 3 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 4 | ` from models import InputRecord ` | 从 models 导入 InputRecord。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 5 | ` from utils.demo_bdf import write_demo_bdf ` | 从 utils.demo_bdf 导入 write_demo_bdf。只为演示/测试生成简单的连续 BDF；将已知 µV 数组打包成 24 位字节。 |
| 6 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 7 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 8 | ` def create_demo(folder, count=8): ` | 定义 create_demo(folder, count=8)。生成五次已知正弦实验，包含三个幅度等级和三次 100 mV 独立合成记录。 定义到这里时不执行函数体。 |
| 9 | `     folder = Path(folder).resolve() ` | 把结果保存到 folder：解析绝对路径。 |
| 10 | `     folder.mkdir(parents=True, exist_ok=True) ` | 创建目录；参数：parents=True, exist_ok=True。 |
| 11 | `     fs = 2048 ` | 把结果保存到 fs：2048。 |
| 12 | `     t = np.arange(fs*4)/fs ` | 把结果保存到 t：np.arange(fs * 4) 与 fs 相除。 |
| 13 | `     rng = np.random.default_rng(31123921) ` | 把结果保存到 rng：创建固定种子随机发生器，让演示可重复；参数：31123921。 |
| 14 | `     records = [] ` | 把结果保存到 records：组装列表：[]。 |
| 15 | `     for index, level in enumerate((50, 100, 150, 100, 100)): ` | 遍历 enumerate((50, 100, 150, 100, 100))，每次把一项赋给 (index, level)，执行下面缩进的循环体。 |
| 16 | `         amplitude = np.full(count, float(level)) ` | 把结果保存到 amplitude：创建指定常数数组；参数：count, float(level)。 |
| 17 | `         delay = np.zeros(count) ` | 把结果保存到 delay：创建全零数组；参数：count。 |
| 18 | `         if count > 1: amplitude[1] *= .85 ` | 检查条件 count > 1；为真时执行下面缩进的一组语句。 把 amplitude[1] 的原值乘以 0.85，再写回同一变量。 |
| 19 | `         if count > 2: amplitude[2] *= .955 ` | 检查条件 count > 2；为真时执行下面缩进的一组语句。 把 amplitude[2] 的原值乘以 0.955，再写回同一变量。 |
| 20 | `         if count > 3: delay[3] = .003 ` | 检查条件 count > 3；为真时执行下面缩进的一组语句。 把结果保存到 delay[3]：0.003。 |
| 21 | `         if count > 4: delay[4] = .00085 ` | 检查条件 count > 4；为真时执行下面缩进的一组语句。 把结果保存到 delay[4]：0.00085。 |
| 22 | `         if count > 5 and level == 150: amplitude[5] = 115 ` | 检查条件 count > 5 and level == 150；为真时执行下面缩进的一组语句。 把结果保存到 amplitude[5]：115。 |
| 23 | `         if count > 7 and index == 3: amplitude[7] *= .96 ` | 检查条件 count > 7 and index == 3；为真时执行下面缩进的一组语句。 把 amplitude[7] 的原值乘以 0.96，再写回同一变量。 |
| 24 | `         if count > 7 and index == 4: amplitude[7] *= 1.04 ` | 检查条件 count > 7 and index == 4；为真时执行下面缩进的一组语句。 把 amplitude[7] 的原值乘以 1.04，再写回同一变量。 |
| 25 | `         x = 500*amplitude*np.sin(2*np.pi*5*(t[:, None]-delay)) ` | 把结果保存到 x：500 * amplitude 与 np.sin(2 * np.pi * 5 * (t[:, None] - delay)) 相乘。 |
| 26 | `         x += 2200+150*t[:, None]+rng.normal(0, .2, x.shape) ` | 把 x 的原值加上 2200 + 150 * t[:, None] + rng.normal(0, 0.2, x.shape)，再写回同一变量。 |
| 27 | `         if count > 6: x[(t > 1.5) & (t < 1.6), 6] += 20000 ` | 检查条件 count > 6；为真时执行下面缩进的一组语句。 把 x[(t > 1.5) & (t < 1.6), 6] 的原值加上 20000，再写回同一变量。 |
| 28 | `         path = folder/f"DEMO_{count}ch_run{index+1}_{level}mVpp.bdf" ` | 把结果保存到 path：在 Path 路径 folder 后拼接 f'DEMO_{count}ch_run{index + 1}_{level}mVpp.bdf'；这里的 / 是路径拼接。 |
| 29 | `         write_demo_bdf(path, x, fs) ` | 调用 write_demo_bdf；参数：path, x, fs。 |
| 30 | `         records.append(InputRecord(path.stem, str(path), 5., level, True, index < 3, ` | 把一项加入列表末尾；参数：InputRecord(path.stem, str(path), 5.0, level, True, index < 3, '100mV-repeat' if level == 100 else '', nominal_mV=level)。 |
| 31 | `                                    "100mV-repeat" if level == 100 else "", nominal_mV=level)) ` | 接续第 30 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：InputRecord(path.stem, str(path), 5.0, level, True, index < 3, '100mV-repeat' if level == 100 else '', nominal_mV=level)。 |
| 32 | `     return records ` | 结束当前函数并返回：records。 |
| 33 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 34 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 35 | ` def create_mode_demo(folder, count, mode): ` | 定义 create_mode_demo(folder, count, mode)。按模式选择正弦演示，或生成 30 秒脉冲/ECG 数据并注入特定故障。 定义到这里时不执行函数体。 |
| 36 | `     if mode == "bench_sine": ` | 检查条件 mode == 'bench_sine'；为真时执行下面缩进的一组语句。 |
| 37 | `         return create_demo(folder, count) ` | 结束当前函数并返回：调用 create_demo；参数：folder, count。 |
| 38 | `     folder = Path(folder).resolve() ` | 把结果保存到 folder：解析绝对路径。 |
| 39 | `     folder.mkdir(parents=True, exist_ok=True) ` | 创建目录；参数：parents=True, exist_ok=True。 |
| 40 | `     fs = 1024 ` | 把结果保存到 fs：1024。 |
| 41 | `     t = np.arange(fs*30)/fs ` | 把结果保存到 t：np.arange(fs * 30) 与 fs 相除。 |
| 42 | `     rng = np.random.default_rng(3921) ` | 把结果保存到 rng：创建固定种子随机发生器，让演示可重复；参数：3921。 |
| 43 | `     x = np.zeros((len(t), count)) ` | 把结果保存到 x：创建全零数组；参数：(len(t), count)。 |
| 44 | `     for ch in range(count): ` | 遍历 range(count)，每次把一项赋给 ch，执行下面缩进的循环体。 |
| 45 | `         if mode == "bench_pulse": ` | 检查条件 mode == 'bench_pulse'；为真时执行下面缩进的一组语句。 |
| 46 | `             delay = .004 if ch == 2 else 0. ` | 把结果保存到 delay：若 ch == 2，用 0.004；否则用 0.0。 |
| 47 | `             level = 85000 if ch == 1 else 100000 ` | 把结果保存到 level：若 ch == 1，用 85000；否则用 100000。 |
| 48 | `             x[:, ch] = level * (((t-delay)*2 % 1) < .15) + rng.normal(0, 2, len(t)) ` | 把结果保存到 x[:, ch]：level * ((t - delay) * 2 % 1 < 0.15) 与 rng.normal(0, 2, len(t)) 相加。 |
| 49 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 50 | `             for centre in np.arange(.6, 30, 1.): ` | 遍历 np.arange(0.6, 30, 1.0)，每次把一项赋给 centre，执行下面缩进的循环体。 |
| 51 | `                 z = t-centre ` | 把结果保存到 z：t 与 centre 相减。 |
| 52 | `                 x[:, ch] += (1000*np.exp(-.5*(z/.010)**2) - 220*np.exp(-.5*((z-.03)/.008)**2) ` | 把 x[:, ch] 的原值加上 1000 * np.exp(-0.5 * (z / 0.01) ** 2) - 220 * np.exp(-0.5 * ((z - 0.03) / 0.008) ** 2) + 180 * np.exp(-0.5 * ((z - 0.26) / 0.06) *…（完整表达式见左栏），再写回同一变量。 |
| 53 | `                              + 180*np.exp(-.5*((z-.26)/.06)**2)) ` | 接续第 52 行的同一条语句，不是另起一段算法。 调用 np.exp；参数：-0.5 * ((z - 0.26) / 0.06) ** 2。 |
| 54 | `             x[:, ch] += rng.normal(0, 2, len(t)) ` | 把 x[:, ch] 的原值加上 rng.normal(0, 2, len(t))，再写回同一变量。 |
| 55 | `             if ch == 1: x[:, ch] += 1500*np.sin(2*np.pi*.3*t) ` | 检查条件 ch == 1；为真时执行下面缩进的一组语句。 把 x[:, ch] 的原值加上 1500 * np.sin(2 * np.pi * 0.3 * t)，再写回同一变量。 |
| 56 | `             if ch == 2: x[(t >= 12) & (t < 18), ch] = 0 ` | 检查条件 ch == 2；为真时执行下面缩进的一组语句。 把结果保存到 x[(t >= 12) & (t < 18), ch]：0。 |
| 57 | `             if ch == 3: x[:, ch] += rng.normal(0, 650, len(t)) ` | 检查条件 ch == 3；为真时执行下面缩进的一组语句。 把 x[:, ch] 的原值加上 rng.normal(0, 650, len(t))，再写回同一变量。 |
| 58 | `     path = folder/f"DEMO_{mode}_{count}ch.bdf" ` | 把结果保存到 path：在 Path 路径 folder 后拼接 f'DEMO_{mode}_{count}ch.bdf'；这里的 / 是路径拼接。 |
| 59 | `     write_demo_bdf(path, x, fs) ` | 调用 write_demo_bdf；参数：path, x, fs。 |
| 60 | `     return [InputRecord(path.stem, str(path), 2., 100. if mode == "bench_pulse" else None, ` | 结束当前函数并返回：组装列表：[InputRecord(path.stem, str(path), 2.0, 100.0 if mode == 'bench_pulse' else None, mode == 'bench_pulse', False, waveform='pulse' if mode == 'bench_pulse' else '…（完整表达式见左栏）。 |
| 61 | `                         mode == "bench_pulse", False, waveform="pulse" if mode == "bench_pulse" else "ecg")] ` | 接续第 60 行的同一条语句，不是另起一段算法。 结束当前函数并返回：组装列表：[InputRecord(path.stem, str(path), 2.0, 100.0 if mode == 'bench_pulse' else None, mode == 'bench_pulse', False, waveform='pulse' if mode == 'bench_pulse' else '…（完整表达式见左栏）。 |
| 62 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 63 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 64 | ` def create_timeline_demo(folder, count): ` | 定义 create_timeline_demo(folder, count)。生成 30 秒正弦，在第二通道 10–20 秒把振荡幅度减半，便于观察窗口颜色变化。 定义到这里时不执行函数体。 |
| 65 | `     """30 s sine: channel 2 loses half its amplitude during 10-20 s only.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 66 | `     folder = Path(folder).resolve() ` | 把结果保存到 folder：解析绝对路径。 |
| 67 | `     folder.mkdir(parents=True, exist_ok=True) ` | 创建目录；参数：parents=True, exist_ok=True。 |
| 68 | `     fs = 8192 ` | 把结果保存到 fs：8192。 |
| 69 | `     t = np.arange(30*fs)/fs ` | 把结果保存到 t：np.arange(30 * fs) 与 fs 相除。 |
| 70 | `     x = np.repeat((50000*np.sin(2*np.pi*5*t)+2200)[:, None], count, axis=1) ` | 把结果保存到 x：重复数组元素/列；参数：(50000 * np.sin(2 * np.pi * 5 * t) + 2200)[:, None], count, axis=1。 |
| 71 | `     if count > 1: ` | 检查条件 count > 1；为真时执行下面缩进的一组语句。 |
| 72 | `         fault = (t >= 10) & (t < 20) ` | 把结果保存到 fault：t >= 10 与 t < 20 按位与。 |
| 73 | `         x[fault, 1] = 25000*np.sin(2*np.pi*5*t[fault])+2200 ` | 把结果保存到 x[fault, 1]：25000 * np.sin(2 * np.pi * 5 * t[fault]) 与 2200 相加。 |
| 74 | `     x += np.random.default_rng(3921).normal(0, 2, x.shape) ` | 把 x 的原值加上 np.random.default_rng(3921).normal(0, 2, x.shape)，再写回同一变量。 |
| 75 | `     path = folder/f'DEMO_timeline_sine_{count}ch.bdf' ` | 把结果保存到 path：在 Path 路径 folder 后拼接 f'DEMO_timeline_sine_{count}ch.bdf'；这里的 / 是路径拼接。 |
| 76 | `     write_demo_bdf(path, x, fs) ` | 调用 write_demo_bdf；参数：path, x, fs。 |
| 77 | `     return [InputRecord(path.stem, str(path), 5., 100., True, False, waveform='sine')] ` | 结束当前函数并返回：组装列表：[InputRecord(path.stem, str(path), 5.0, 100.0, True, False, waveform='sine')]。 |
