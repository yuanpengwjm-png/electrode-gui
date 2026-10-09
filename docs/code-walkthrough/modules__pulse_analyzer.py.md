# modules/pulse_analyzer.py：两平台脉冲

估计高低平台与中点；复用同步匹配器，但不套用正弦拟合或正弦 THD。

源码：[modules/pulse_analyzer.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/pulse_analyzer.py>)。本说明对应 55 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [8–9](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/pulse_analyzer.py:8>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `fit` | [11–40](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/pulse_analyzer.py:11>) | 用两个平台中位数迭代分组，计算平台差 Vpp 和平台中点，检查响应/周期/稳定性。 |
| `frequencies` | [42–55](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/pulse_analyzer.py:42>) | 从原始时间轴上的上升事件间隔取中位周期，其倒数为频率；至少四个上升事件。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Two-level pulse measurements; no sine fit is used for pulse recordings.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 3 | ` from modules.bench_spectrum import BenchSpectrumAnalyzer ` | 从 modules.bench_spectrum 导入 BenchSpectrumAnalyzer。独立估计每通道频率，拟合基频和指定谐波，把残差噪声与谐波功率分开，用于 SNR、THD、SINAD。 |
| 4 | ` from utils.centered_channels import CenteredChannels ` | 从 utils.centered_channels 导入 CenteredChannels。只在请求某个电极时构造去直流/线性漂移的波形，减少 128 通道大数组的复制。 |
| 5 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 6 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 7 | ` class PulseAnalyzer: ` | 定义 PulseAnalyzer 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 8 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 9 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 10 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 11 | `     def fit(self, x, fs, frequency, lazy=False, progress=lambda _: None): ` | 定义 fit(self, x, fs, frequency, lazy=False, progress=lambda _: None)。用两个平台中位数迭代分组，计算平台差 Vpp 和平台中点，检查响应/周期/稳定性。 定义到这里时不执行函数体。 |
| 12 | `         if not 0 < frequency < fs/4: ` | 检查条件 not 0 < frequency < fs / 4；为真时执行下面缩进的一组语句。 |
| 13 | `             raise ValueError("At least four samples per nominal pulse period are required") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'At least four samples per nominal pulse period are required'；上层可捕获并显示原因。 |
| 14 | `         fits, offsets = [], [] ` | 把结果保存到 (fits, offsets)：组装元组：([], [])。 |
| 15 | `         for i in range(x.shape[1]): ` | 遍历 range(x.shape[1])，每次把一项赋给 i，执行下面缩进的循环体。 |
| 16 | `             progress(f"Fitting pulse plateaus: channel {i+1}/{x.shape[1]}") ` | 调用 progress；参数：f'Fitting pulse plateaus: channel {i + 1}/{x.shape[1]}'。 |
| 17 | `             y = x[:, i] ` | 把结果保存到 y：按索引/键 (:, i) 取 x 的内容；切片包含起点、不包含终点。 |
| 18 | `             low, high = np.percentile(y, [.5, 99.5]) ` | 把结果保存到 (low, high)：计算指定百分位数；参数：y, [0.5, 99.5]。 |
| 19 | `             # Two robust plateau centres. Requires both levels to be represented; ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 20 | `             # extremely narrow pulses (<~0.5% duty cycle) are outside this model. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 21 | `             for _ in range(5): ` | 遍历 range(5)，每次把一项赋给 _，执行下面缩进的循环体。 |
| 22 | `                 split = (low+high)/2 ` | 把结果保存到 split：low + high 与 2 相除。 |
| 23 | `                 a, b = y[y <= split], y[y > split] ` | 把结果保存到 (a, b)：组装元组：(y[y <= split], y[y > split])。 |
| 24 | `                 if not len(a) or not len(b): ` | 检查条件 not len(a) or not len(b)；为真时执行下面缩进的一组语句。 |
| 25 | `                     break ` | 立即退出当前循环，继续执行循环后面的代码。 |
| 26 | `                 low, high = float(np.median(a)), float(np.median(b)) ` | 把结果保存到 (low, high)：组装元组：(float(np.median(a)), float(np.median(b)))。 |
| 27 | `             amplitude = float(high-low) ` | 脉冲高平台减低平台就是峰峰值，不用正弦波的峰值/RMS 换算。 |
| 28 | `             reasons = [] ` | 把结果保存到 reasons：组装列表：[]。 |
| 29 | `             if amplitude < self.settings.min_response_uVpp: ` | 检查条件 amplitude < self.settings.min_response_uVpp；为真时执行下面缩进的一组语句。 |
| 30 | `                 reasons.append("no_reliable_pulse_response") ` | 把一项加入列表末尾；参数：'no_reliable_pulse_response'。 |
| 31 | `             if len(y)/fs*frequency < self.settings.min_cycles: ` | 检查条件 len(y) / fs * frequency < self.settings.min_cycles；为真时执行下面缩进的一组语句。 |
| 32 | `                 reasons.append("too_few_cycles") ` | 把一项加入列表末尾；参数：'too_few_cycles'。 |
| 33 | `             offsets.append((high+low)/2) ` | 把一项加入列表末尾；参数：(high + low) / 2。 |
| 34 | `             residual = np.minimum(np.abs(y-low), np.abs(y-high)) ` | 把结果保存到 residual：调用 np.minimum；参数：np.abs(y - low), np.abs(y - high)。 |
| 35 | `             if amplitude and float(np.median(residual))/amplitude > .10: ` | 检查条件 amplitude and float(np.median(residual)) / amplitude > 0.1；为真时执行下面缩进的一组语句。 |
| 36 | `                 reasons.append("unstable_pulse_plateaus") ` | 把一项加入列表末尾；参数：'unstable_pulse_plateaus'。 |
| 37 | `             fits.append(dict(amplitude_pp_mV=amplitude/1000, low_uV=float(low), high_uV=float(high), ` | 把一项加入列表末尾；参数：dict(amplitude_pp_mV=amplitude / 1000, low_uV=float(low), high_uV=float(high), quality_reasons=reasons, measurement='two plateau medians; midpoin…（完整表达式见左栏）。 |
| 38 | `                              quality_reasons=reasons, measurement="two plateau medians; midpoint edge timing")) ` | 接续第 37 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(amplitude_pp_mV=amplitude / 1000, low_uV=float(low), high_uV=float(high), quality_reasons=reasons, measurement='two plateau medians; midpoin…（完整表达式见左栏）。 |
| 39 | `         centred = CenteredChannels(x, offsets) ` | 把结果保存到 centred：创建按需去基线的波形对象；参数：x, offsets。 |
| 40 | `         return fits, centred if lazy else centred.as_array() ` | 结束当前函数并返回：组装元组：(fits, centred if lazy else centred.as_array())。 |
| 41 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 42 | `     def frequencies(self, timings, nominal): ` | 定义 frequencies(self, timings, nominal)。从原始时间轴上的上升事件间隔取中位周期，其倒数为频率；至少四个上升事件。 定义到这里时不执行函数体。 |
| 43 | `         output = {} ` | 把结果保存到 output：组装字典，键用于给数值/设置命名：{}。 |
| 44 | `         helper = BenchSpectrumAnalyzer(self.settings) ` | 把结果保存到 helper：调用 BenchSpectrumAnalyzer；参数：self.settings。 |
| 45 | `         for channel, metric in timings.items(): ` | 遍历 timings.items()，每次把一项赋给 (channel, metric)，执行下面缩进的循环体。 |
| 46 | `             # Reference event series and target series remain on original time axes. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 47 | `             events = metric.values.get("rising_events_s", []) ` | 把结果保存到 events：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：'rising_events_s', []。 |
| 48 | `             if len(events) < 4: ` | 检查条件 len(events) < 4；为真时执行下面缩进的一组语句。 |
| 49 | `                 from models import MetricResult ` | 从 models 导入 MetricResult。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 50 | `                 output[channel] = MetricResult("yellow", "At least 4 rising edges are needed for pulse frequency") ` | 把结果保存到 output[channel]：打包颜色、原因和指标数值；参数：'yellow', 'At least 4 rising edges are needed for pulse frequency'。 |
| 51 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 52 | `             periods = np.diff(events) ` | 把结果保存到 periods：计算相邻值之差；参数：events。 |
| 53 | `             measured = float(1/np.median(periods)) ` | 对上升边沿间隔取中位周期，再求倒数得到 Hz。 |
| 54 | `             output[channel] = helper.frequency_result(measured, nominal, bool(np.all(periods > 0))) ` | 把结果保存到 output[channel]：调用 helper.frequency_result；参数：measured, nominal, bool(np.all(periods > 0))。 |
| 55 | `         return output ` | 结束当前函数并返回：output。 |
