# modules/repeatability.py：独立重复实验

按人工声明的 repeat_group 与频率比较独立记录；计算增益或输出幅度 CV，以及各次延迟中位数的 SD。

源码：[modules/repeatability.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/repeatability.py>)。本说明对应 55 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [7–8](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/repeatability.py:7>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `evaluate` | [10–55](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/repeatability.py:10>) | 分组检查独立运行数量和同名义输入；输入全部校准则比较 gain，否则比较输出幅度，最后检查运行间时序稳定性。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Independent repetitions at the same frequency, nominal input and wiring.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 3 | ` from models import MetricResult, combine ` | 从 models 导入 MetricResult、combine。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 4 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 5 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 6 | ` class RepeatabilityAnalyzer: ` | 定义 RepeatabilityAnalyzer 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 7 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 8 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 9 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 10 | `     def evaluate(self, runs, channel, reference): ` | 定义 evaluate(self, runs, channel, reference)。分组检查独立运行数量和同名义输入；输入全部校准则比较 gain，否则比较输出幅度，最后检查运行间时序稳定性。 定义到这里时不执行函数体。 |
| 11 | `         groups = sorted({(r.record.repeat_group, r.record.frequency_hz) for r in runs if r.record.repeat_group}) ` | 把结果保存到 groups：排序；参数：{(r.record.repeat_group, r.record.frequency_hz) for r in runs if r.record.repeat_group}。 |
| 12 | `         results = [] ` | 把结果保存到 results：组装列表：[]。 |
| 13 | `         for label, frequency in groups: ` | 遍历 groups，每次把一项赋给 (label, frequency)，执行下面缩进的循环体。 |
| 14 | `             group = [r for r in runs if r.record.repeat_group == label and r.record.frequency_hz == frequency] ` | 把结果保存到 group：从 runs 逐个取 r，仅保留 r.record.repeat_group == label and r.record.frequency_hz == frequency，为每项生成 r。 |
| 15 | `             if len(group) < self.settings.min_repeat_runs: ` | 检查条件 len(group) < self.settings.min_repeat_runs；为真时执行下面缩进的一组语句。 |
| 16 | `                 results.append(MetricResult("yellow", f"{label} has {len(group)} runs; at least {self.settings.min_repeat_runs} independent runs are required")) ` | 把一项加入列表末尾；参数：MetricResult('yellow', f'{label} has {len(group)} runs; at least {self.settings.min_repeat_runs} independent runs are required')。 |
| 17 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 18 | `             known = all(r.record.input_confirmed and r.record.input_mVpp is not None for r in group) ` | 把结果保存到 known：要求所有条件为真；参数：(r.record.input_confirmed and r.record.input_mVpp is not None for r in group)。 |
| 19 | `             levels = {r.record.nominal_mV if r.record.nominal_mV is not None else r.record.input_mVpp for r in group} ` | 把结果保存到 levels：从 group 逐个取 r，为每项生成 r.record.nominal_mV if r.record.nominal_mV is not None else r.record.input_mVpp。 |
| 20 | `             if len(levels) != 1 or None in levels: ` | 检查条件 len(levels) != 1 or None in levels；为真时执行下面缩进的一组语句。 |
| 21 | `                 results.append(MetricResult("yellow", "Repeat group input settings are inconsistent or missing")) ` | 把一项加入列表末尾；参数：MetricResult('yellow', 'Repeat group input settings are inconsistent or missing')。 |
| 22 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 23 | `             if any(r.channels[channel]["fit"]["quality_reasons"] for r in group): ` | 检查条件 any((r.channels[channel]['fit']['quality_reasons'] for r in group))；为真时执行下面缩进的一组语句。 |
| 24 | `                 results.append(MetricResult("yellow", "Repeat group contains invalid waveforms; repeat the measurements")) ` | 把一项加入列表末尾；参数：MetricResult('yellow', 'Repeat group contains invalid waveforms; repeat the measurements')。 |
| 25 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 26 | `             amplitudes = [r.channels[channel]["fit"]["amplitude_pp_mV"] / ` | 把结果保存到 amplitudes：从 group 逐个取 r，为每项生成 r.channels[channel]['fit']['amplitude_pp_mV'] / (r.record.input_mVpp if known else 1)。 |
| 27 | `                           (r.record.input_mVpp if known else 1) for r in group] ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 amplitudes：从 group 逐个取 r，为每项生成 r.channels[channel]['fit']['amplitude_pp_mV'] / (r.record.input_mVpp if known else 1)。 |
| 28 | `             cv = float(100*np.std(amplitudes, ddof=1)/np.mean(amplitudes)) ` | 用样本标准差（n−1 分母）/均值×100% 算 CV；这里列表装的是 gain 或输出幅度，取决于是否全已校准。 |
| 29 | `             values = dict(group=label, independent_runs=len(group), amplitude_cv_pct=cv, ` | 把结果保存到 values：组装键值字典；参数：group=label, independent_runs=len(group), amplitude_cv_pct=cv, basis='gain' if known else 'recorded_amplitude', direction_sd_ms={}。 |
| 30 | `                           basis="gain" if known else "recorded_amplitude", direction_sd_ms={}) ` | 接续第 29 行的同一条语句，不是另起一段算法。 把结果保存到 values：组装键值字典；参数：group=label, independent_runs=len(group), amplitude_cv_pct=cv, basis='gain' if known else 'recorded_amplitude', direction_sd_ms={}。 |
| 31 | `             color = self.settings.color(cv, self.settings.repeat_cv_limit_pct) ` | 把结果保存到 color：调用 self.settings.color；参数：cv, self.settings.repeat_cv_limit_pct。 |
| 32 | `             message = f"Repeat {'gain' if known else 'output amplitude'} CV {cv:.3f}%" ` | 把结果保存到 message：将变量值插入 f-string 文本；格式如 .3f 表示显示三位小数。 |
| 33 | `             if channel != reference: ` | 检查条件 channel != reference；为真时执行下面缩进的一组语句。 |
| 34 | `                 timing_valid = all(not r.channels[channel]["fit"]["quality_reasons"] and ` | 把结果保存到 timing_valid：要求所有条件为真；参数：(not r.channels[channel]['fit']['quality_reasons'] and all((not d['missing'] and (not d['ambiguous']) and (not d['extra']) and (d['paired_count']…（完整表达式见左栏）。 |
| 35 | `                     all(not d["missing"] and not d["ambiguous"] and not d["extra"] and d["paired_count"] >= self.settings.min_zero_pairs ` | 接续第 34 行的同一条语句，不是另起一段算法。 要求所有条件为真；参数：(not d['missing'] and (not d['ambiguous']) and (not d['extra']) and (d['paired_count'] >= self.settings.min_zero_pairs) for d in r.channels[chann…（完整表达式见左栏）。 |
| 36 | `                         for d in r.channels[channel]["sync"].values["directions"].values()) and ` | 接续第 34 行的同一条语句，不是另起一段算法。 取字典值。 |
| 37 | `                     not r.channels[reference]["fit"]["quality_reasons"] for r in group) ` | 接续第 34 行的同一条语句，不是另起一段算法。 把结果保存到 timing_valid：要求所有条件为真；参数：(not r.channels[channel]['fit']['quality_reasons'] and all((not d['missing'] and (not d['ambiguous']) and (not d['extra']) and (d['paired_count']…（完整表达式见左栏）。 |
| 38 | `                 if not timing_valid: ` | 检查条件 not timing_valid；为真时执行下面缩进的一组语句。 |
| 39 | `                     results.append(MetricResult("red" if color == "red" else "yellow", message+"; repeat timing data are insufficient", values)) ` | 把一项加入列表末尾；参数：MetricResult('red' if color == 'red' else 'yellow', message + '; repeat timing data are insufficient', values)。 |
| 40 | `                     continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 41 | `                 for direction in ("rising", "falling"): ` | 遍历 ('rising', 'falling')，每次把一项赋给 direction，执行下面缩进的循环体。 |
| 42 | `                     medians = [r.channels[channel]["sync"].values["directions"][direction]["median_ms"] for r in group] ` | 把结果保存到 medians：从 group 逐个取 r，为每项生成 r.channels[channel]['sync'].values['directions'][direction]['median_ms']。 |
| 43 | `                     values["direction_sd_ms"][direction] = float(np.std(medians, ddof=1)) ` | 把结果保存到 values['direction_sd_ms'][direction]：转换为浮点数；参数：np.std(medians, ddof=1)。 |
| 44 | `                 sd = max(values["direction_sd_ms"].values()) ` | 把结果保存到 sd：取最大值；参数：values['direction_sd_ms'].values()。 |
| 45 | `                 timing_color = self.settings.color(sd, self.settings.repeat_delay_sd_limit_ms) ` | 把结果保存到 timing_color：调用 self.settings.color；参数：sd, self.settings.repeat_delay_sd_limit_ms。 |
| 46 | `                 color = "red" if "red" in (color, timing_color) else "yellow" if "yellow" in (color, timing_color) else "green" ` | 把结果保存到 color：若 'red' in (color, timing_color)，用 'red'；否则用 'yellow' if 'yellow' in (color, timing_color) else 'green'。 |
| 47 | `                 message += f"; repeat delay SD {sd:.3f} ms" ` | 把 message 的原值加上 f'; repeat delay SD {sd:.3f} ms'，再写回同一变量。 |
| 48 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 49 | `                 message += "; REF: amplitude repeatability only" ` | 把 message 的原值加上 '; REF: amplitude repeatability only'，再写回同一变量。 |
| 50 | `             if not known: ` | 检查条件 not known；为真时执行下面缩进的一组语句。 |
| 51 | `                 message += " (includes generator and fixture variation)" ` | 把 message 的原值加上 ' (includes generator and fixture variation)'，再写回同一变量。 |
| 52 | `             results.append(MetricResult(color, message, values)) ` | 把一项加入列表末尾；参数：MetricResult(color, message, values)。 |
| 53 | `         result = combine(results, "No independent repeat group; cycles within one BDF are not separate experiments") ` | 把结果保存到 result：调用 combine；参数：results, 'No independent repeat group; cycles within one BDF are not separate experiments'。 |
| 54 | `         result.values = {"groups": [r.values for r in results]} ` | 把结果保存到 result.values：组装字典，键用于给数值/设置命名：{'groups': [r.values for r in results]}。 |
| 55 | `         return result ` | 结束当前函数并返回：result。 |
