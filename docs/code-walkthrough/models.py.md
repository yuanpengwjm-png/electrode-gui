# models.py：模块间的数据格式

InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。

源码：[models.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/models.py>)。本说明对应 123 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `recorded_duration_s` | [38–39](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/models.py:38>) | 返回原始记录时长；旧结果没有 source_duration_s 时，兼容地退回 duration_s。它是属性，读取时不需要加括号。 |
| `metric` | [52–74](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/models.py:52>) | 按用户所选指标返回单项或最差项组合；参考通道的自同步不作为独立通过证据。 |
| `record_electrodes` | [86–98](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/models.py:86>) | 复制并替换为指定记录自己的结果；单记录视图不能评估跨记录线性/重复性。 |
| `window_electrodes` | [100–113](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/models.py:100>) | 复制并替换为指定窗口自己的指标，避免把其他时间的故障带入当前窗口。 |
| `combine` | [116–123](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/models.py:116>) | 按红>黄>绿合并结果，并保留该级别的去重原因；空输入为黄色而非绿色。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Data shared by the GUI, metrics and report exporter; no GUI imports here.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import dataclass, field, replace ` | 从 dataclasses 导入 dataclass、field、replace。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` from typing import Any ` | 从 typing 导入 Any。描述类型，便于阅读和编辑器提示 |
| 4 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 5 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 6 | ` @dataclass ` | @dataclass 自动补充初始化等数据对象方法；frozen=True 时字段不能通常地重新赋值。 |
| 7 | ` class MetricResult: ` | 定义 MetricResult 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 8 | `     color: str  # green / yellow / red ` | 声明 color 的类型为 str，用于单项状态：green/yellow/red。构造对象时需要提供。 |
| 9 | `     message: str ` | 声明 message 的类型为 str，用于状态的可读原因。构造对象时需要提供。 |
| 10 | `     values: dict[str, Any] = field(default_factory=dict) ` | 声明 values 的类型为 dict[str, Any]，用于可复核的数值明细字典。默认值：为数据类设置默认工厂；每个实例各有自己的空列表/字典；参数：default_factory=dict。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 13 | ` @dataclass ` | @dataclass 自动补充初始化等数据对象方法；frozen=True 时字段不能通常地重新赋值。 |
| 14 | ` class InputRecord: ` | 定义 InputRecord 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 15 | `     id: str ` | 声明 id 的类型为 str，用于记录标识，用于关联来源和结果。构造对象时需要提供。 |
| 16 | `     path: str ` | 声明 path 的类型为 str，用于原始 BDF 或 ZIP 的路径。构造对象时需要提供。 |
| 17 | `     frequency_hz: float = 5.0 ` | 声明 frequency_hz 的类型为 float，用于该记录的名义输入频率（Hz）。默认值：5.0。 |
| 18 | `     input_mVpp: float \| None = None ` | 声明 input_mVpp 的类型为 float &#124; None，用于实际输入峰峰值（mV）；未知时为 None。默认值：None（未知/未设置）。 |
| 19 | `     input_confirmed: bool = False ` | 声明 input_confirmed 的类型为 bool，用于是否已独立确认输入电压及单位。默认值：False（否）。 |
| 20 | `     sweep: bool = True ` | 声明 sweep 的类型为 bool，用于该记录是否参加多幅度线性扫描。默认值：True（是）。 |
| 21 | `     repeat_group: str = "" ` | 声明 repeat_group 的类型为 str，用于人工指定的独立重复实验组名。默认值：''。 |
| 22 | `     member: str \| None = None  # optional BDF member in a ZIP ` | 声明 member 的类型为 str &#124; None，用于ZIP 内部 BDF 文件名；普通 BDF 时为 None。默认值：None（未知/未设置）。 |
| 23 | `     nominal_mV: float \| None = None ` | 声明 nominal_mV 的类型为 float &#124; None，用于重复分组用的名义输入等级。默认值：None（未知/未设置）。 |
| 24 | `     waveform: str = "unknown" ` | 声明 waveform 的类型为 str，用于声明的波形类型。默认值：'unknown'。 |
| 25 | `     setup_group: str = "default" ` | 声明 setup_group 的类型为 str，用于声明的接线/物理配置组。默认值：'default'。 |
| 26 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 27 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 28 | ` @dataclass ` | @dataclass 自动补充初始化等数据对象方法；frozen=True 时字段不能通常地重新赋值。 |
| 29 | ` class RunResult: ` | 定义 RunResult 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 30 | `     record: InputRecord ` | 声明 record 的类型为 InputRecord，用于本次结果对应的 InputRecord。构造对象时需要提供。 |
| 31 | `     channels: dict[str, dict] ` | 声明 channels 的类型为 dict[str, dict]，用于真实通道名称列表，或按通道索引的结果字典（依所属对象而定）。构造对象时需要提供。 |
| 32 | `     sample_rate_hz: float ` | 声明 sample_rate_hz 的类型为 float，用于实际采样率（Hz）。构造对象时需要提供。 |
| 33 | `     duration_s: float ` | 声明 duration_s 的类型为 float，用于本次实际保留并分析的时长（秒），可能短于原始记录。构造对象时需要提供。 |
| 34 | `     source_duration_s: float \| None = None ` | 声明 source_duration_s 的类型为 float &#124; None，用于原始文件的记录时长（秒），用于与保留分析时长区分。默认值：None（未知/未设置）。 |
| 35 | `     excluded_tail_s: float = 0.0 ` | 声明 excluded_tail_s 的类型为 float，用于按样本取整后实际排除的末尾时长（秒）。默认值：0.0。 |
| 36 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 37 | `     @property ` | @property 把方法变为只读计算属性，读取 obj.属性名 时执行，不需要 obj.方法名()。 |
| 38 | `     def recorded_duration_s(self): ` | 定义 recorded_duration_s(self)。返回原始记录时长；旧结果没有 source_duration_s 时，兼容地退回 duration_s。它是属性，读取时不需要加括号。 定义到这里时不执行函数体。 |
| 39 | `         return self.duration_s if self.source_duration_s is None else self.source_duration_s ` | 结束当前函数并返回：若 self.source_duration_s is None，用 self.duration_s；否则用 self.source_duration_s。 |
| 40 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 41 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 42 | ` @dataclass ` | @dataclass 自动补充初始化等数据对象方法；frozen=True 时字段不能通常地重新赋值。 |
| 43 | ` class ElectrodeResult: ` | 定义 ElectrodeResult 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 44 | `     name: str ` | 声明 name 的类型为 str，用于电极/通道名称。构造对象时需要提供。 |
| 45 | `     gain: MetricResult ` | 声明 gain 的类型为 MetricResult，用于幅度增益结果。构造对象时需要提供。 |
| 46 | `     linearity: MetricResult ` | 声明 linearity 的类型为 MetricResult，用于多幅度线性度结果。构造对象时需要提供。 |
| 47 | `     synchronization: MetricResult ` | 声明 synchronization 的类型为 MetricResult，用于相对时序结果。构造对象时需要提供。 |
| 48 | `     repetition: MetricResult ` | 声明 repetition 的类型为 MetricResult，用于独立重复性结果。构造对象时需要提供。 |
| 49 | `     is_reference: bool = False ` | 声明 is_reference 的类型为 bool，用于是否为同步参考通道。默认值：False（否）。 |
| 50 | `     extra: dict[str, MetricResult] = field(default_factory=dict) ` | 声明 extra 的类型为 dict[str, MetricResult]，用于当前工作流额外指标，如频谱或 ECG SQI。默认值：为数据类设置默认工厂；每个实例各有自己的空列表/字典；参数：default_factory=dict。 |
| 51 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 52 | `     def metric(self, mode: str) -> MetricResult: ` | 定义 metric(self, mode: str)。按用户所选指标返回单项或最差项组合；参考通道的自同步不作为独立通过证据。 定义到这里时不执行函数体。 |
| 53 | `         if mode in self.extra: ` | 检查条件 mode in self.extra；为真时执行下面缩进的一组语句。 |
| 54 | `             return self.extra[mode] ` | 结束当前函数并返回：按索引/键 mode 取 self.extra 的内容。 |
| 55 | `         if mode == "bench_summary": ` | 检查条件 mode == 'bench_summary'；为真时执行下面缩进的一组语句。 |
| 56 | `             items = [self.gain] + [self.extra[k] for k in ("snr", "thd", "frequency") if k in self.extra] ` | 把结果保存到 items：拼接 [self.gain] 和 [self.extra[k] for k in ('snr', 'thd', 'frequency') if k in self.extra]。 |
| 57 | `             if not self.is_reference: ` | 检查条件 not self.is_reference；为真时执行下面缩进的一组语句。 |
| 58 | `                 items.append(self.synchronization) ` | 把一项加入列表末尾；参数：self.synchronization。 |
| 59 | `         elif mode == "current": ` | 检查条件 mode == 'current'；为真时执行下面缩进的一组语句。 |
| 60 | `             # Self-comparison is not an independent synchronization measurement. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 61 | `             items = [self.gain] if self.is_reference else [self.gain, self.synchronization] ` | 把结果保存到 items：若 self.is_reference，用 [self.gain]；否则用 [self.gain, self.synchronization]。 |
| 62 | `         elif mode == "overall": ` | 检查条件 mode == 'overall'；为真时执行下面缩进的一组语句。 |
| 63 | `             items = [self.metric("bench_summary"), self.linearity, self.repetition] ` | 把结果保存到 items：组装列表：[self.metric('bench_summary'), self.linearity, self.repetition]。 |
| 64 | `             if not self.is_reference: ` | 检查条件 not self.is_reference；为真时执行下面缩进的一组语句。 |
| 65 | `                 items.append(self.synchronization) ` | 把一项加入列表末尾；参数：self.synchronization。 |
| 66 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 67 | `             return getattr(self, mode, MetricResult("yellow", "Not applicable to this analysis mode")) ` | 结束当前函数并返回：按字段名读取对象属性；参数：self, mode, MetricResult('yellow', 'Not applicable to this analysis mode')。 |
| 68 | `         rank = {"green": 0, "yellow": 1, "red": 2} ` | 把结果保存到 rank：组装字典，键用于给数值/设置命名：{'green': 0, 'yellow': 1, 'red': 2}。 |
| 69 | `         color = max(items, key=lambda m: rank[m.color]).color ` | 把结果保存到 color：读取 max(items, key=lambda m: rank[m.color]) 的 color 属性。 |
| 70 | `         details = [m.message for m in items if m.color != "green"] ` | 把结果保存到 details：从 items 逐个取 m，仅保留 m.color != 'green'，为每项生成 m.message。 |
| 71 | `         message = "; ".join(dict.fromkeys(details)) if details else "Completed checks are within the current limits" ` | 把结果保存到 message：若 details，用 '; '.join(dict.fromkeys(details))；否则用 'Completed checks are within the current limits'。 |
| 72 | `         if self.is_reference: ` | 检查条件 self.is_reference；为真时执行下面缩进的一组语句。 |
| 73 | `             message += "; REF timing has not been independently verified" ` | 把 message 的原值加上 '; REF timing has not been independently verified'，再写回同一变量。 |
| 74 | `         return MetricResult(color, message) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：color, message。 |
| 75 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 76 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 77 | ` @dataclass ` | @dataclass 自动补充初始化等数据对象方法；frozen=True 时字段不能通常地重新赋值。 |
| 78 | ` class AnalysisResult: ` | 定义 AnalysisResult 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 79 | `     electrodes: list[ElectrodeResult] ` | 声明 electrodes 的类型为 list[ElectrodeResult]，用于逐电极汇总结果列表。构造对象时需要提供。 |
| 80 | `     runs: list[RunResult] ` | 声明 runs 的类型为 list[RunResult]，用于逐记录结果列表。构造对象时需要提供。 |
| 81 | `     reference: str ` | 声明 reference 的类型为 str，用于同步参考通道名称。构造对象时需要提供。 |
| 82 | `     elapsed_s: float ` | 声明 elapsed_s 的类型为 float，用于本次分析的计算耗时（秒）。构造对象时需要提供。 |
| 83 | `     settings: dict ` | 声明 settings 的类型为 dict，用于本次使用的参数。构造对象时需要提供。 |
| 84 | `     frames: list[dict] = field(default_factory=list) ` | 声明 frames 的类型为 list[dict]，用于逐窗口结果，含记录 ID 和起止时间。默认值：为数据类设置默认工厂；每个实例各有自己的空列表/字典；参数：default_factory=list。 |
| 85 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 86 | `     def record_electrodes(self, record_id: str) -> list[ElectrodeResult]: ` | 定义 record_electrodes(self, record_id: str)。复制并替换为指定记录自己的结果；单记录视图不能评估跨记录线性/重复性。 定义到这里时不执行函数体。 |
| 87 | `         """Project one analyzed record without borrowing another record's flags.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 88 | `         run = next(r for r in self.runs if r.record.id == record_id) ` | 把结果保存到 run：取迭代器的下一项或匹配到的第一项；参数：(r for r in self.runs if r.record.id == record_id)。 |
| 89 | `         unavailable = MetricResult("yellow", "Multi-record check: analyze All loaded records and select All analyzed records / worst case") ` | 把结果保存到 unavailable：打包颜色、原因和指标数值；参数：'yellow', 'Multi-record check: analyze All loaded records and select All analyzed records / worst case'。 |
| 90 | `         result = [] ` | 把结果保存到 result：组装列表：[]。 |
| 91 | `         for electrode in self.electrodes: ` | 遍历 self.electrodes，每次把一项赋给 electrode，执行下面缩进的循环体。 |
| 92 | `             data = run.channels[electrode.name] ` | 把结果保存到 data：按索引/键 electrode.name 取 run.channels 的内容。 |
| 93 | `             if "gain" in data: ` | 检查条件 'gain' in data；为真时执行下面缩进的一组语句。 |
| 94 | `                 result.append(replace(electrode, gain=data["gain"], synchronization=data["sync"], ` | 把一项加入列表末尾；参数：replace(electrode, gain=data['gain'], synchronization=data['sync'], linearity=unavailable, repetition=unavailable, extra=data['extra'])。 |
| 95 | `                                       linearity=unavailable, repetition=unavailable, extra=data["extra"])) ` | 接续第 94 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：replace(electrode, gain=data['gain'], synchronization=data['sync'], linearity=unavailable, repetition=unavailable, extra=data['extra'])。 |
| 96 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 97 | `                 result.append(replace(electrode, extra=data["extra"])) ` | 把一项加入列表末尾；参数：replace(electrode, extra=data['extra'])。 |
| 98 | `         return result ` | 结束当前函数并返回：result。 |
| 99 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 100 | `     def window_electrodes(self, index: int) -> list[ElectrodeResult]: ` | 定义 window_electrodes(self, index: int)。复制并替换为指定窗口自己的指标，避免把其他时间的故障带入当前窗口。 定义到这里时不执行函数体。 |
| 101 | `         """Return only this window's checks, never whole-record or batch metrics.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 102 | `         frame = self.frames[index] ` | 把结果保存到 frame：按索引/键 index 取 self.frames 的内容。 |
| 103 | `         unavailable = MetricResult("yellow", "Linearity and independent repetition cannot be assessed from one time window") ` | 把结果保存到 unavailable：打包颜色、原因和指标数值；参数：'yellow', 'Linearity and independent repetition cannot be assessed from one time window'。 |
| 104 | `         electrodes = [] ` | 把结果保存到 electrodes：组装列表：[]。 |
| 105 | `         for electrode in self.electrodes: ` | 遍历 self.electrodes，每次把一项赋给 electrode，执行下面缩进的循环体。 |
| 106 | `             metrics = frame["metrics"][electrode.name] ` | 把结果保存到 metrics：按索引/键 electrode.name 取 frame['metrics'] 的内容。 |
| 107 | `             if "gain" in metrics: ` | 检查条件 'gain' in metrics；为真时执行下面缩进的一组语句。 |
| 108 | `                 extra = {k: v for k, v in metrics.items() if k not in ("gain", "synchronization")} ` | 把结果保存到 extra：从 metrics.items() 逐个取 (k, v)，仅保留 k not in ('gain', 'synchronization')，为每项生成 k: v。 |
| 109 | `                 electrodes.append(replace(electrode, gain=metrics["gain"], synchronization=metrics["synchronization"], ` | 把一项加入列表末尾；参数：replace(electrode, gain=metrics['gain'], synchronization=metrics['synchronization'], linearity=unavailable, repetition=unavailable, extra=extra)。 |
| 110 | `                                           linearity=unavailable, repetition=unavailable, extra=extra)) ` | 接续第 109 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：replace(electrode, gain=metrics['gain'], synchronization=metrics['synchronization'], linearity=unavailable, repetition=unavailable, extra=extra)。 |
| 111 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 112 | `                 electrodes.append(replace(electrode, extra=metrics)) ` | 把一项加入列表末尾；参数：replace(electrode, extra=metrics)。 |
| 113 | `         return electrodes ` | 结束当前函数并返回：electrodes。 |
| 114 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 115 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 116 | ` def combine(results: list[MetricResult], empty="No evaluable data", labels=None) -> MetricResult: ` | 定义 combine(results: list[MetricResult], empty='No evaluable data', labels=None)。按红>黄>绿合并结果，并保留该级别的去重原因；空输入为黄色而非绿色。 定义到这里时不执行函数体。 |
| 117 | `     if not results: ` | 检查条件 not results；为真时执行下面缩进的一组语句。 |
| 118 | `         return MetricResult("yellow", empty) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：'yellow', empty。 |
| 119 | `     rank = {"green": 0, "yellow": 1, "red": 2} ` | 把结果保存到 rank：组装字典，键用于给数值/设置命名：{'green': 0, 'yellow': 1, 'red': 2}。 |
| 120 | `     color = max(results, key=lambda r: rank[r.color]).color ` | 把结果保存到 color：读取 max(results, key=lambda r: rank[r.color]) 的 color 属性。 |
| 121 | `     messages = [(f"{labels[i]}: " if labels and len(results) > 1 else "") + r.message ` | 把结果保存到 messages：从 enumerate(results) 逐个取 (i, r)，仅保留 r.color == color，为每项生成 (f'{labels[i]}: ' if labels and len(results) > 1 else '') + r.message。 |
| 122 | `                 for i, r in enumerate(results) if r.color == color] ` | 接续第 121 行的同一条语句，不是另起一段算法。 同时取序号和值；参数：results。 |
| 123 | `     return MetricResult(color, "; ".join(dict.fromkeys(messages))) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：color, '; '.join(dict.fromkeys(messages))。 |
