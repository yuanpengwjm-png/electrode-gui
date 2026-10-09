# modules/time_synchronization.py：通道相对时序

先找上升、下降过零事件，再分别匹配；不移动波形，不用后面的周期补漏检。输出事件表、延迟 P95 和 jitter。

源码：[modules/time_synchronization.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/time_synchronization.py>)。本说明对应 121 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [7–8](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/time_synchronization.py:7>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `detect` | [10–34](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/time_synchronization.py:10>) | 统一事件方向，用滞回确认过零，再线性插值；同方向相邻事件至少相隔半周期。 |
| `__init__` | [38–40](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/time_synchronization.py:38>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `match_direction` | [42–67](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/time_synchronization.py:42>) | 每个内部参考事件只在自己的 ±T/4 区域匹配；报告缺失、多个候选和多余事件。 |
| `evaluate_all` | [69–121](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/time_synchronization.py:69>) | 逐通道双方向检测和匹配，输出延迟/抖动；参考无效或周期不足时不作可靠同步结论。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Count and compare BOTH actual zero-crossing directions without re-indexing gaps.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 3 | ` from models import MetricResult ` | 从 models 导入 MetricResult。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 4 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 5 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 6 | ` class ZeroCrossingDetector: ` | 定义 ZeroCrossingDetector 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 7 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 8 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 9 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 10 | `     def detect(self, samples, fs, peak_uV, frequency, direction): ` | 定义 detect(self, samples, fs, peak_uV, frequency, direction)。统一事件方向，用滞回确认过零，再线性插值；同方向相邻事件至少相隔半周期。 定义到这里时不执行函数体。 |
| 11 | `         if direction not in ("rising", "falling"): ` | 检查条件 direction not in ('rising', 'falling')；为真时执行下面缩进的一组语句。 |
| 12 | `             raise ValueError("Detect rising and falling separately") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Detect rising and falling separately'；上层可捕获并显示原因。 |
| 13 | `         z = np.asarray(samples) * (1 if direction == "rising" else -1) ` | 把结果保存到 z：np.asarray(samples) 与 1 if direction == 'rising' else -1 相乘。 |
| 14 | `         if peak_uV <= 0 or len(z) < 2: ` | 检查条件 peak_uV <= 0 or len(z) < 2；为真时执行下面缩进的一组语句。 |
| 15 | `             return np.array([]) ` | 结束当前函数并返回：构造 NumPy 数组；参数：[]。 |
| 16 | `         h = peak_uV*self.settings.zero_hysteresis_peak_fraction ` | 把结果保存到 h：peak_uV 与 self.settings.zero_hysteresis_peak_fraction 相乘。 |
| 17 | `         crossings = np.flatnonzero((z[:-1] < 0) & (z[1:] >= 0)) ` | 把结果保存到 crossings：返回条件为真的扁平索引；参数：(z[:-1] < 0) & (z[1:] >= 0)。 |
| 18 | `         negative = np.flatnonzero(z <= -h) ` | 把结果保存到 negative：返回条件为真的扁平索引；参数：z <= -h。 |
| 19 | `         positive = np.flatnonzero(z >= h) ` | 把结果保存到 positive：返回条件为真的扁平索引；参数：z >= h。 |
| 20 | `         result, last_confirmation = [], -1 ` | 把结果保存到 (result, last_confirmation)：组装元组：([], -1)。 |
| 21 | `         # Iterate crossing candidates, not every 16,384-Hz sample. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 22 | `         for k, i in enumerate(crossings): ` | 遍历 enumerate(crossings)，每次把一项赋给 (k, i)，执行下面缩进的循环体。 |
| 23 | `             left = np.searchsorted(negative, i, side="right")-1 ` | 把结果保存到 left：np.searchsorted(negative, i, side='right') 与 1 相减。 |
| 24 | `             right = np.searchsorted(positive, i+1) ` | 把结果保存到 right：在已排序数组中找插入位置，用于定位匹配范围；参数：positive, i + 1。 |
| 25 | `             if left < 0 or right == len(positive) or negative[left] <= last_confirmation: ` | 检查条件 left < 0 or right == len(positive) or negative[left] <= last_confirmation；为真时执行下面缩进的一组语句。 |
| 26 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 27 | `             confirmation = positive[right] ` | 把结果保存到 confirmation：按索引/键 right 取 positive 的内容。 |
| 28 | `             if k+1 < len(crossings) and crossings[k+1] < confirmation: ` | 检查条件 k + 1 < len(crossings) and crossings[k + 1] < confirmation；为真时执行下面缩进的一组语句。 |
| 29 | `                 continue  # zero chatter: keep the last crossing before +h ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 30 | `             time = float((i-z[i]/(z[i+1]-z[i]))/fs) ` | 用包围零点的两个真实采样值做线性插值，先得到小数采样索引，再除 fs 换成秒。 |
| 31 | `             if not result or time-result[-1] >= .5/frequency: ` | 检查条件 not result or time - result[-1] >= 0.5 / frequency；为真时执行下面缩进的一组语句。 |
| 32 | `                 result.append(time) ` | 把一项加入列表末尾；参数：time。 |
| 33 | `                 last_confirmation = confirmation ` | 把结果保存到 last_confirmation：confirmation。 |
| 34 | `         return np.asarray(result) ` | 结束当前函数并返回：转换或视为 NumPy 数组；参数：result。 |
| 35 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 36 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 37 | ` class TimeSynchronizationAnalyzer: ` | 定义 TimeSynchronizationAnalyzer 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 38 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 39 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 40 | `         self.detector = ZeroCrossingDetector(settings) ` | 把结果保存到 self.detector：调用 ZeroCrossingDetector；参数：settings。 |
| 41 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 42 | `     def match_direction(self, reference, target, frequency, duration): ` | 定义 match_direction(self, reference, target, frequency, duration)。每个内部参考事件只在自己的 ±T/4 区域匹配；报告缺失、多个候选和多余事件。 定义到这里时不执行函数体。 |
| 43 | `         """Each interior reference event owns a disjoint +/-T/4 window. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 44 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 45 | `         Missing windows stay missing; target events are never shifted/re-numbered ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 46 | `         to hide a skipped period. A whole-cycle absolute offset is unidentifiable. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 47 | `         """ ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 48 | `         gap = self.settings.zero_match_period_fraction/frequency ` | 周期 T=1/f；默认单侧窗口 0.25T，因此每个参考事件只在 ±T/4 配对。 |
| 49 | `         pairs, missing, ambiguous = [], 0, 0 ` | 把结果保存到 (pairs, missing, ambiguous)：组装元组：([], 0, 0)。 |
| 50 | `         eligible = [(i, t) for i, t in enumerate(reference) if gap <= t <= duration-gap] ` | 把结果保存到 eligible：从 enumerate(reference) 逐个取 (i, t)，仅保留 gap <= t <= duration - gap，为每项生成 (i, t)。 |
| 51 | `         for index, t in eligible: ` | 遍历 eligible，每次把一项赋给 (index, t)，执行下面缩进的循环体。 |
| 52 | `             lo, hi = np.searchsorted(target, [t-gap, t+gap], side="left") ` | 把结果保存到 (lo, hi)：在已排序数组中找插入位置，用于定位匹配范围；参数：target, [t - gap, t + gap], side='left'。 |
| 53 | `             # Include a point exactly on the upper boundary. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 54 | `             hi = int(np.searchsorted(target, t+gap, side="right")) ` | 把结果保存到 hi：转换为整数；参数：np.searchsorted(target, t + gap, side='right')。 |
| 55 | `             if hi-lo == 0: ` | 检查条件 hi - lo == 0；为真时执行下面缩进的一组语句。 |
| 56 | `                 missing += 1 ` | 把 missing 的原值加上 1，再写回同一变量。 |
| 57 | `             elif hi-lo != 1: ` | 检查条件 hi - lo != 1；为真时执行下面缩进的一组语句。 |
| 58 | `                 ambiguous += 1 ` | 把 ambiguous 的原值加上 1，再写回同一变量。 |
| 59 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 60 | `                 pairs.append(dict(reference_event_index=index, reference_zero_s=float(t), ` | 把一项加入列表末尾；参数：dict(reference_event_index=index, reference_zero_s=float(t), electrode_zero_s=float(target[lo]), delay_ms=float((target[lo] - t) * 1000))。 |
| 61 | `                                   electrode_zero_s=float(target[lo]), delay_ms=float((target[lo]-t)*1000))) ` | 接续第 60 行的同一条语句，不是另起一段算法。 转换为浮点数；参数：target[lo]。 |
| 62 | `         # Extra target events in the interior must also be reported. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 63 | `         extra = 0 ` | 把结果保存到 extra：0。 |
| 64 | `         if eligible: ` | 检查条件 eligible；为真时执行下面缩进的一组语句。 |
| 65 | `             interior = target[(target >= eligible[0][1]-gap) & (target <= eligible[-1][1]+gap)] ` | 把结果保存到 interior：用 (target >= eligible[0][1] - gap) & (target <= eligible[-1][1] + gap) 生成的索引或布尔条件选取 target 中对应的元素。 |
| 66 | `             extra = max(0, len(interior)-len(pairs)) ` | 把结果保存到 extra：取最大值；参数：0, len(interior) - len(pairs)。 |
| 67 | `         return pairs, dict(reference_windows=len(eligible), missing=missing, ambiguous=ambiguous, extra=extra) ` | 结束当前函数并返回：组装元组：(pairs, dict(reference_windows=len(eligible), missing=missing, ambiguous=ambiguous, extra=extra))。 |
| 68 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 69 | `     def evaluate_all(self, centred, fits, names, reference, fs, frequency): ` | 定义 evaluate_all(self, centred, fits, names, reference, fs, frequency)。逐通道双方向检测和匹配，输出延迟/抖动；参考无效或周期不足时不作可靠同步结论。 定义到这里时不执行函数体。 |
| 70 | `         ref_index = names.index(reference) ` | 把结果保存到 ref_index：调用 names.index；参数：reference。 |
| 71 | `         duration = (len(centred)-1)/fs ` | 把结果保存到 duration：len(centred) - 1 与 fs 相除。 |
| 72 | `         events = {} ` | 把结果保存到 events：组装字典，键用于给数值/设置命名：{}。 |
| 73 | `         for i, name in enumerate(names): ` | 遍历 enumerate(names)，每次把一项赋给 (i, name)，执行下面缩进的循环体。 |
| 74 | `             column = centred.column(i) if hasattr(centred, 'column') else centred[:, i] ` | 把结果保存到 column：若 hasattr(centred, 'column')，用 centred.column(i)；否则用 centred[:, i]。 |
| 75 | `             events[name] = {d: self.detector.detect(column, fs, fits[i]["amplitude_pp_mV"]*500, ` | 把结果保存到 events[name]：从 ('rising', 'falling') 逐个取 d，为每项生成 d: self.detector.detect(column, fs, fits[i]['amplitude_pp_mV'] * 500, frequency, d)。 |
| 76 | `                                                   frequency, d) for d in ("rising", "falling")} ` | 接续第 75 行的同一条语句，不是另起一段算法。 把结果保存到 events[name]：从 ('rising', 'falling') 逐个取 d，为每项生成 d: self.detector.detect(column, fs, fits[i]['amplitude_pp_mV'] * 500, frequency, d)。 |
| 77 | `         result = {} ` | 把结果保存到 result：组装字典，键用于给数值/设置命名：{}。 |
| 78 | `         for i, name in enumerate(names): ` | 遍历 enumerate(names)，每次把一项赋给 (i, name)，执行下面缩进的循环体。 |
| 79 | `             values = dict(reference=reference, rising_count=len(events[name]["rising"]), ` | 把结果保存到 values：组装键值字典；参数：reference=reference, rising_count=len(events[name]['rising']), rising_events_s=events[name]['rising'].tolist(), falling_events_s=events[name]['fa…（完整表达式见左栏）。 |
| 80 | `                           rising_events_s=events[name]["rising"].tolist(), ` | 接续第 79 行的同一条语句，不是另起一段算法。 把数组转为普通列表以便 JSON 序列化。 |
| 81 | `                           falling_events_s=events[name]["falling"].tolist(), ` | 接续第 79 行的同一条语句，不是另起一段算法。 把数组转为普通列表以便 JSON 序列化。 |
| 82 | `                           falling_count=len(events[name]["falling"]), ` | 接续第 79 行的同一条语句，不是另起一段算法。 取得元素个数；参数：events[name]['falling']。 |
| 83 | `                           reference_rising_count=len(events[reference]["rising"]), ` | 接续第 79 行的同一条语句，不是另起一段算法。 取得元素个数；参数：events[reference]['rising']。 |
| 84 | `                           reference_falling_count=len(events[reference]["falling"]), directions={}, pairs=[]) ` | 接续第 79 行的同一条语句，不是另起一段算法。 取得元素个数；参数：events[reference]['falling']。 |
| 85 | `             all_delays, p95s, count_problems, too_short = [], [], [], False ` | 把结果保存到 (all_delays, p95s, count_problems, too_short)：组装元组：([], [], [], False)。 |
| 86 | `             for direction in ("rising", "falling"): ` | 遍历 ('rising', 'falling')，每次把一项赋给 direction，执行下面缩进的循环体。 |
| 87 | `                 pairs, counts = self.match_direction(events[reference][direction], events[name][direction], frequency, duration) ` | 把结果保存到 (pairs, counts)：每个内部参考事件只在自己的 ±T/4 区域匹配；报告缺失、多个候选和多余事件。；参数：events[reference][direction], events[name][direction], frequency, duration。 |
| 88 | `                 delays = np.array([p["delay_ms"] for p in pairs]) ` | 把结果保存到 delays：构造 NumPy 数组；参数：[p['delay_ms'] for p in pairs]。 |
| 89 | `                 values["directions"][direction] = dict(**counts, paired_count=len(pairs), ` | 把结果保存到 values['directions'][direction]：组装键值字典；参数：None=counts, paired_count=len(pairs), median_ms=float(np.median(delays)) if len(delays) and i != ref_index else None, abs_p95_ms=float(np.percent…（完整表达式见左栏）。 |
| 90 | `                     median_ms=float(np.median(delays)) if len(delays) and i != ref_index else None, ` | 接续第 89 行的同一条语句，不是另起一段算法。 转换为浮点数；参数：np.median(delays)。 |
| 91 | `                     abs_p95_ms=float(np.percentile(np.abs(delays), 95)) if len(delays) and i != ref_index else None) ` | 接续第 89 行的同一条语句，不是另起一段算法。 转换为浮点数；参数：np.percentile(np.abs(delays), 95)。 |
| 92 | `                 values["pairs"].extend([dict(**p, direction=direction) for p in pairs]) ` | 把多项逐个加入列表；参数：[dict(**p, direction=direction) for p in pairs]。 |
| 93 | `                 all_delays.extend(delays) ` | 把多项逐个加入列表；参数：delays。 |
| 94 | `                 if len(delays): ` | 检查条件 len(delays)；为真时执行下面缩进的一组语句。 |
| 95 | `                     p95s.append(float(np.percentile(np.abs(delays), 95))) ` | 把一项加入列表末尾；参数：float(np.percentile(np.abs(delays), 95))。 |
| 96 | `                 if any(counts[key] for key in ("missing", "ambiguous", "extra")): ` | 检查条件 any((counts[key] for key in ('missing', 'ambiguous', 'extra')))；为真时执行下面缩进的一组语句。 |
| 97 | `                     label = "Rising" if direction == "rising" else "Falling" ` | 把结果保存到 label：若 direction == 'rising'，用 'Rising'；否则用 'Falling'。 |
| 98 | `                     count_problems.append(f"{label} missing {counts['missing']} / ambiguous {counts['ambiguous']} / extra {counts['extra']}") ` | 把一项加入列表末尾；参数：f"{label} missing {counts['missing']} / ambiguous {counts['ambiguous']} / extra {counts['extra']}"。 |
| 99 | `                 too_short \|= len(pairs) < self.settings.min_zero_pairs ` | 把 too_short 的原值应用本行运算于 len(pairs) < self.settings.min_zero_pairs，再写回同一变量。 |
| 100 | `             values["max_direction_p95_ms"] = max(p95s) if p95s and i != ref_index else None ` | 把结果保存到 values['max_direction_p95_ms']：若 p95s and i != ref_index，用 max(p95s)；否则用 None。 |
| 101 | `             values["jitter_ms"] = float(np.std(all_delays, ddof=1)) if len(all_delays) >= 2 and i != ref_index else None ` | 把结果保存到 values['jitter_ms']：若 len(all_delays) >= 2 and i != ref_index，用 float(np.std(all_delays, ddof=1))；否则用 None。 |
| 102 | `             if i == ref_index: ` | 检查条件 i == ref_index；为真时执行下面缩进的一组语句。 |
| 103 | `                 values["pairs"] = [] ` | 把结果保存到 values['pairs']：组装列表：[]。 |
| 104 | `                 result[name] = MetricResult("yellow", "REF: self-comparison at 0 ms is not independent verification", values) ` | 把结果保存到 result[name]：打包颜色、原因和指标数值；参数：'yellow', 'REF: self-comparison at 0 ms is not independent verification', values。 |
| 105 | `             elif fits[i]["quality_reasons"] or fits[ref_index]["quality_reasons"]: ` | 检查条件 fits[i]['quality_reasons'] or fits[ref_index]['quality_reasons']；为真时执行下面缩进的一组语句。 |
| 106 | `                 reason = "Reference waveform" if fits[ref_index]["quality_reasons"] else "Electrode waveform" ` | 把结果保存到 reason：若 fits[ref_index]['quality_reasons']，用 'Reference waveform'；否则用 'Electrode waveform'。 |
| 107 | `                 result[name] = MetricResult("yellow", reason+" quality is insufficient; repeat the timing test", values) ` | 把结果保存到 result[name]：打包颜色、原因和指标数值；参数：'yellow', reason + ' quality is insufficient; repeat the timing test', values。 |
| 108 | `             elif count_problems: ` | 检查条件 count_problems；为真时执行下面缩进的一组语句。 |
| 109 | `                 result[name] = MetricResult("red", "Event count mismatch; check missing cycles, polarity or noise: "+"; ".join(count_problems), values) ` | 把结果保存到 result[name]：打包颜色、原因和指标数值；参数：'red', 'Event count mismatch; check missing cycles, polarity or noise: ' + '; '.join(count_problems), values。 |
| 110 | `             elif too_short: ` | 检查条件 too_short；为真时执行下面缩进的一组语句。 |
| 111 | `                 result[name] = MetricResult("yellow", "Insufficient complete event pairs; at least 3 per direction are required", values) ` | 把结果保存到 result[name]：打包颜色、原因和指标数值；参数：'yellow', 'Insufficient complete event pairs; at least 3 per direction are required', values。 |
| 112 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 113 | `                 p95, jitter = values["max_direction_p95_ms"], values["jitter_ms"] ` | 把结果保存到 (p95, jitter)：组装元组：(values['max_direction_p95_ms'], values['jitter_ms'])。 |
| 114 | `                 colors = [self.settings.color(p95, self.settings.sync_delay_limit_ms), ` | 把结果保存到 colors：组装列表：[self.settings.color(p95, self.settings.sync_delay_limit_ms), self.settings.color(jitter, self.settings.sync_jitter_limit_ms)]。 |
| 115 | `                           self.settings.color(jitter, self.settings.sync_jitter_limit_ms)] ` | 接续第 114 行的同一条语句，不是另起一段算法。 调用 self.settings.color；参数：jitter, self.settings.sync_jitter_limit_ms。 |
| 116 | `                 color = "red" if "red" in colors else "yellow" if "yellow" in colors else "green" ` | 把结果保存到 color：若 'red' in colors，用 'red'；否则用 'yellow' if 'yellow' in colors else 'green'。 |
| 117 | `                 up = values["directions"]["rising"]["median_ms"] ` | 把结果保存到 up：按索引/键 'median_ms' 取 values['directions']['rising'] 的内容。 |
| 118 | `                 down = values["directions"]["falling"]["median_ms"] ` | 把结果保存到 down：按索引/键 'median_ms' 取 values['directions']['falling'] 的内容。 |
| 119 | `                 message = f"Rising {up:+.3f} ms; Falling {down:+.3f} ms; P95 {p95:.3f} ms; jitter {jitter:.3f} ms" ` | 把结果保存到 message：将变量值插入 f-string 文本；格式如 .3f 表示显示三位小数。 |
| 120 | `                 result[name] = MetricResult(color, message+("; limit exceeded, check required" if color == "red" else ", near the limit" if color == "yellow" else ""), values) ` | 把结果保存到 result[name]：打包颜色、原因和指标数值；参数：color, message + ('; limit exceeded, check required' if color == 'red' else ', near the limit' if color == 'yellow' else ''), values。 |
| 121 | `         return result ` | 结束当前函数并返回：result。 |
