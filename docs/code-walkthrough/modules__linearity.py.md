# modules/linearity.py：输入输出线性度

按频率分组，要求至少三个已确认的输入幅度等级，拟合直线并计算最大偏差占输入跨度的百分比。

源码：[modules/linearity.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/linearity.py>)。本说明对应 34 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [7–8](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/linearity.py:7>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `evaluate` | [10–34](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/linearity.py:10>) | 按频率收集扫描记录，校验至少三个真实输入等级，再拟合斜率/截距与归一化最大偏差。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """LinearityAnalyzer: output versus three or more known input levels.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 3 | ` from models import MetricResult, combine ` | 从 models 导入 MetricResult、combine。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 4 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 5 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 6 | ` class LinearityAnalyzer: ` | 定义 LinearityAnalyzer 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 7 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 8 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 9 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 10 | `     def evaluate(self, runs, channel): ` | 定义 evaluate(self, runs, channel)。按频率收集扫描记录，校验至少三个真实输入等级，再拟合斜率/截距与归一化最大偏差。 定义到这里时不执行函数体。 |
| 11 | `         frequencies = sorted({r.record.frequency_hz for r in runs if r.record.sweep}) ` | 把结果保存到 frequencies：排序；参数：{r.record.frequency_hz for r in runs if r.record.sweep}。 |
| 12 | `         results = [] ` | 把结果保存到 results：组装列表：[]。 |
| 13 | `         for frequency in frequencies: ` | 遍历 frequencies，每次把一项赋给 frequency，执行下面缩进的循环体。 |
| 14 | `             group = [r for r in runs if r.record.sweep and r.record.frequency_hz == frequency] ` | 把结果保存到 group：从 runs 逐个取 r，仅保留 r.record.sweep and r.record.frequency_hz == frequency，为每项生成 r。 |
| 15 | `             if any(r.channels[channel]["fit"]["quality_reasons"] for r in group): ` | 检查条件 any((r.channels[channel]['fit']['quality_reasons'] for r in group))；为真时执行下面缩进的一组语句。 |
| 16 | `                 results.append(MetricResult("yellow", f"{frequency:g} Hz sweep contains invalid waveforms; repeat the measurement")) ` | 把一项加入列表末尾；参数：MetricResult('yellow', f'{frequency:g} Hz sweep contains invalid waveforms; repeat the measurement')。 |
| 17 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 18 | `             if any(r.record.input_mVpp is None or not r.record.input_confirmed for r in group): ` | 检查条件 any((r.record.input_mVpp is None or not r.record.input_confirmed for r in group))；为真时执行下面缩进的一组语句。 |
| 19 | `                 results.append(MetricResult("yellow", "Actual inputs for linearity are unconfirmed")) ` | 把一项加入列表末尾；参数：MetricResult('yellow', 'Actual inputs for linearity are unconfirmed')。 |
| 20 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 21 | `             x = np.array([r.record.input_mVpp for r in group]) ` | 把结果保存到 x：构造 NumPy 数组；参数：[r.record.input_mVpp for r in group]。 |
| 22 | `             if len(set(x)) < 3: ` | 检查条件 len(set(x)) < 3；为真时执行下面缩进的一组语句。 |
| 23 | `                 results.append(MetricResult("yellow", "Linearity needs at least 3 input levels at the same frequency")) ` | 把一项加入列表末尾；参数：MetricResult('yellow', 'Linearity needs at least 3 input levels at the same frequency')。 |
| 24 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 25 | `             y = np.array([r.channels[channel]["fit"]["amplitude_pp_mV"] for r in group]) ` | 把结果保存到 y：构造 NumPy 数组；参数：[r.channels[channel]['fit']['amplitude_pp_mV'] for r in group]。 |
| 26 | `             k, b = np.linalg.lstsq(np.column_stack((x, np.ones(len(x)))), y, rcond=None)[0] ` | 把结果保存到 (k, b)：按索引/键 0 取 np.linalg.lstsq(np.column_stack((x, np.ones(len(x)))), y, rcond=None) 的内容。 |
| 27 | `             deviation = float(100*np.max(np.abs(y-(k*x+b)))/np.ptp(x)) ` | 取实际输出到拟合直线的最大绝对差，除输入最大值−最小值，再乘 100%。 |
| 28 | `             color = self.settings.color(deviation, self.settings.linearity_limit_pct) ` | 把结果保存到 color：调用 self.settings.color；参数：deviation, self.settings.linearity_limit_pct。 |
| 29 | `             results.append(MetricResult(color, f"Linearity deviation {deviation:.3f}% of input span" + ` | 把一项加入列表末尾；参数：MetricResult(color, f'Linearity deviation {deviation:.3f}% of input span' + ('; nonlinearity exceeds the limit' if color == 'red' else ', near th…（完整表达式见左栏）。 |
| 30 | `                                         ("; nonlinearity exceeds the limit" if color == "red" else ", near the limit" if color == "yellow" else ", within limits"), ` | 接续第 29 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：MetricResult(color, f'Linearity deviation {deviation:.3f}% of input span' + ('; nonlinearity exceeds the limit' if color == 'red' else ', near th…（完整表达式见左栏）。 |
| 31 | `                                         dict(frequency_hz=frequency, deviation_pct=deviation, slope=float(k), intercept_mVpp=float(b)))) ` | 接续第 29 行的同一条语句，不是另起一段算法。 组装键值字典；参数：frequency_hz=frequency, deviation_pct=deviation, slope=float(k), intercept_mVpp=float(b)。 |
| 32 | `         result = combine(results, "No linearity sweep; multiple input levels at one frequency are required") ` | 把结果保存到 result：调用 combine；参数：results, 'No linearity sweep; multiple input levels at one frequency are required'。 |
| 33 | `         result.values = {"sweeps": [r.values for r in results]} ` | 把结果保存到 result.values：组装字典，键用于给数值/设置命名：{'sweeps': [r.values for r in results]}。 |
| 34 | `         return result ` | 结束当前函数并返回：result。 |
