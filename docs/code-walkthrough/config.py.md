# config.py：参数与阈值

保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。

源码：[config.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/config.py>)。本说明对应 104 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `validate` | [60–97](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/config.py:60>) | 检查模式、正数、最少样本事件数、窗口步长和阈值顺序等约束。 |
| `color` | [99–104](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/config.py:99>) | 上限型指标先取绝对值；超过 limit 为红，到 warning_fraction×limit 为黄，其余为绿。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Editable project criteria. These are engineering starting points, not standards.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import dataclass, asdict ` | 从 dataclasses 导入 dataclass、asdict。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 4 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 5 | ` COLORS = {"green": "#21866A", "yellow": "#E7B647", "red": "#C84E58"} ` | 把结果保存到 COLORS：组装字典，键用于给数值/设置命名：{'green': '#21866A', 'yellow': '#E7B647', 'red': '#C84E58'}。 |
| 6 | ` COLOR_LABELS = {"green": "Within limits", "yellow": "Review / insufficient data", "red": "Check required"} ` | 把结果保存到 COLOR_LABELS：组装字典，键用于给数值/设置命名：{'green': 'Within limits', 'yellow': 'Review / insufficient data', 'red': 'Check required'}。 |
| 7 | ` BENCH_VIEWS = {"Bench summary": "bench_summary", "Gain + timing": "current", "Gain error": "gain", ` | 把结果保存到 BENCH_VIEWS：组装字典，键用于给数值/设置命名：{'Bench summary': 'bench_summary', 'Gain + timing': 'current', 'Gain error': 'gain', 'Linearity': 'linearity', 'Time synchronization': 'synchronization', 'Repet…（完整表达式见左栏）。 |
| 8 | `                "Linearity": "linearity", "Time synchronization": "synchronization", ` | 接续第 7 行的同一条语句，不是另起一段算法。 把结果保存到 BENCH_VIEWS：组装字典，键用于给数值/设置命名：{'Bench summary': 'bench_summary', 'Gain + timing': 'current', 'Gain error': 'gain', 'Linearity': 'linearity', 'Time synchronization': 'synchronization', 'Repet…（完整表达式见左栏）。 |
| 9 | `                "Repetition": "repetition", "SNR": "snr", "SINAD": "sinad", "THD": "thd", ` | 接续第 7 行的同一条语句，不是另起一段算法。 把结果保存到 BENCH_VIEWS：组装字典，键用于给数值/设置命名：{'Bench summary': 'bench_summary', 'Gain + timing': 'current', 'Gain error': 'gain', 'Linearity': 'linearity', 'Time synchronization': 'synchronization', 'Repet…（完整表达式见左栏）。 |
| 10 | `                "Frequency error": "frequency", "Full protocol (incl. repeats)": "overall"} ` | 接续第 7 行的同一条语句，不是另起一段算法。 把结果保存到 BENCH_VIEWS：组装字典，键用于给数值/设置命名：{'Bench summary': 'bench_summary', 'Gain + timing': 'current', 'Gain error': 'gain', 'Linearity': 'linearity', 'Time synchronization': 'synchronization', 'Repet…（完整表达式见左栏）。 |
| 11 | ` ECG_VIEWS = {"ECG quality": "ecg_quality", "Beat agreement (bSQI)": "bsqi", "QRS power (pSQI)": "psqi", ` | 把结果保存到 ECG_VIEWS：组装字典，键用于给数值/设置命名：{'ECG quality': 'ecg_quality', 'Beat agreement (bSQI)': 'bsqi', 'QRS power (pSQI)': 'psqi', 'Kurtosis (kSQI)': 'ksqi', 'Baseline (basSQI)': 'bassqi', 'Flatline …（完整表达式见左栏）。 |
| 12 | `              "Kurtosis (kSQI)": "ksqi", "Baseline (basSQI)": "bassqi", "Flatline / clipping": "integrity"} ` | 接续第 11 行的同一条语句，不是另起一段算法。 把结果保存到 ECG_VIEWS：组装字典，键用于给数值/设置命名：{'ECG quality': 'ecg_quality', 'Beat agreement (bSQI)': 'bsqi', 'QRS power (pSQI)': 'psqi', 'Kurtosis (kSQI)': 'ksqi', 'Baseline (basSQI)': 'bassqi', 'Flatline …（完整表达式见左栏）。 |
| 13 | ` VIEW_LABELS = BENCH_VIEWS ` | 把结果保存到 VIEW_LABELS：BENCH_VIEWS。 |
| 14 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 15 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 16 | ` @dataclass ` | @dataclass 自动补充初始化等数据对象方法；frozen=True 时字段不能通常地重新赋值。 |
| 17 | ` class AnalysisSettings: ` | 定义 AnalysisSettings 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 18 | `     analysis_mode: str = "bench_sine"  # bench_sine / bench_pulse / ecg ` | 声明 analysis_mode 的类型为 str，用于分析模式：正弦台架、脉冲台架或 ECG。默认值：'bench_sine'。 |
| 19 | `     gain_limit_pct: float = 5.0 ` | 声明 gain_limit_pct 的类型为 float，用于幅度/增益误差的上限（%）。默认值：5.0。 |
| 20 | `     linearity_limit_pct: float = 2.0 ` | 声明 linearity_limit_pct 的类型为 float，用于线性偏差占输入跨度的上限（%）。默认值：2.0。 |
| 21 | `     sync_delay_limit_ms: float = 1.0 ` | 声明 sync_delay_limit_ms 的类型为 float，用于双方向绝对延迟 P95 的限值（ms）。默认值：1.0。 |
| 22 | `     sync_jitter_limit_ms: float = 0.2 ` | 声明 sync_jitter_limit_ms 的类型为 float，用于事件延迟抖动 SD 的限值（ms）。默认值：0.2。 |
| 23 | `     repeat_cv_limit_pct: float = 2.0 ` | 声明 repeat_cv_limit_pct 的类型为 float，用于多次独立实验幅度/增益 CV 的限值（%）。默认值：2.0。 |
| 24 | `     repeat_delay_sd_limit_ms: float = 0.2 ` | 声明 repeat_delay_sd_limit_ms 的类型为 float，用于不同运行间延迟 SD 的限值（ms）。默认值：0.2。 |
| 25 | `     warning_fraction: float = 0.8 ` | 声明 warning_fraction 的类型为 float，用于接近上限时提前预警的比例。默认值：0.8。 |
| 26 | `     min_cycles: float = 3.0 ` | 声明 min_cycles 的类型为 float，用于可评估台架信号的最少周期数。默认值：3.0。 |
| 27 | `     max_residual_pct: float = 2.0 ` | 声明 max_residual_pct 的类型为 float，用于正弦拟合残差 RMS/基频 RMS 的门限（%）。默认值：2.0。 |
| 28 | `     max_residual_step_pct: float = 2.0 ` | 声明 max_residual_step_pct 的类型为 float，用于最大相邻残差跳变/Vpp 的门限（%）。默认值：2.0。 |
| 29 | `     frequency_search_pct: float = 5.0 ` | 声明 frequency_search_pct 的类型为 float，用于围绕名义频率搜索的相对范围（%）。默认值：5.0。 |
| 30 | `     min_response_uVpp: float = 1.0 ` | 声明 min_response_uVpp 的类型为 float，用于可可靠辨认响应的最低峰峰值（µV）。默认值：1.0。 |
| 31 | `     zero_hysteresis_peak_fraction: float = 0.02 ` | 声明 zero_hysteresis_peak_fraction 的类型为 float，用于过零滞回确认阈值占信号峰值的比例。默认值：0.02。 |
| 32 | `     min_zero_pairs: int = 3 ` | 声明 min_zero_pairs 的类型为 int，用于每个方向最少需要的成功事件对数。默认值：3。 |
| 33 | `     zero_match_period_fraction: float = 0.25 ` | 声明 zero_match_period_fraction 的类型为 float，用于单侧事件匹配范围占周期的比例。默认值：0.25。 |
| 34 | `     min_repeat_runs: int = 3 ` | 声明 min_repeat_runs 的类型为 int，用于同条件独立记录的最少次数。默认值：3。 |
| 35 | `     snr_good_db: float = 20.0 ` | 声明 snr_good_db 的类型为 float，用于SNR 绿色下边界（dB）。默认值：20.0。 |
| 36 | `     snr_bad_db: float = 10.0 ` | 声明 snr_bad_db 的类型为 float，用于SNR 红色/黄色边界（dB）。默认值：10.0。 |
| 37 | `     bench_bandwidth_hz: float = 100.0 ` | 声明 bench_bandwidth_hz 的类型为 float，用于台架残差噪声积分的最高频率（Hz）。默认值：100.0。 |
| 38 | `     harmonic_count: int = 5  # highest harmonic order, including the fundamental ` | 声明 harmonic_count 的类型为 int，用于最高拟合谐波阶数，1 代表基频。默认值：5。 |
| 39 | `     thd_limit_pct: float \| None = 1.0  # User-selected default; blank still means uncalibrated. ` | 声明 thd_limit_pct 的类型为 float &#124; None，用于THD 百分比限值；None 表示尚未设定。默认值：1.0。 |
| 40 | `     frequency_limit_pct: float \| None = 0.1 ` | 声明 frequency_limit_pct 的类型为 float &#124; None，用于频率误差百分比限值；None 表示尚未设定。默认值：0.1。 |
| 41 | `     exclude_last_s: float = 1.0  # Analysis-only tail exclusion; original BDF is unchanged. ` | 声明 exclude_last_s 的类型为 float，用于每个文件在所有分析和分窗之前排除的末尾秒数；0 表示不排除，不改原始文件。默认值：1.0。 |
| 42 | `     bench_windows: bool = False  # GUI enables this; legacy CLI keeps whole-record work. ` | 声明 bench_windows 的类型为 bool，用于是否额外计算台架时间窗口。默认值：False（否）。 |
| 43 | `     bench_window_s: float = 10.0 ` | 声明 bench_window_s 的类型为 float，用于台架窗口长度（秒）。默认值：10.0。 |
| 44 | `     bench_hop_s: float = 1.0 ` | 声明 bench_hop_s 的类型为 float，用于台架相邻窗口起点的步长（秒）。默认值：1.0。 |
| 45 | `     ecg_window_s: float = 10.0 ` | 声明 ecg_window_s 的类型为 float，用于ECG 完整窗口长度（秒）。默认值：10.0。 |
| 46 | `     ecg_hop_s: float = 5.0 ` | 声明 ecg_hop_s 的类型为 float，用于ECG 窗口步长（秒）。默认值：5.0。 |
| 47 | `     ecg_match_ms: float = 50.0 ` | 声明 ecg_match_ms 的类型为 float，用于两个心搏检测器的事件匹配容差（ms）。默认值：50.0。 |
| 48 | `     ecg_min_beats: int = 3 ` | 声明 ecg_min_beats 的类型为 int，用于每个检测器至少需要检测到的心搏数。默认值：3。 |
| 49 | `     bsqi_good: float = 0.90 ` | 声明 bsqi_good 的类型为 float，用于bSQI 绿色边界；当前实现使用严格大于。默认值：0.9。 |
| 50 | `     bsqi_bad: float = 0.60 ` | 声明 bsqi_bad 的类型为 float，用于bSQI 红色与黄色边界。默认值：0.6。 |
| 51 | `     psqi_low: float = 0.50 ` | 声明 psqi_low 的类型为 float，用于pSQI 绿色区间下界。默认值：0.5。 |
| 52 | `     psqi_high: float = 0.80 ` | 声明 psqi_high 的类型为 float，用于pSQI 绿色区间上界。默认值：0.8。 |
| 53 | `     psqi_bad: float = 0.40 ` | 声明 psqi_bad 的类型为 float，用于pSQI 最低候选边界。默认值：0.4。 |
| 54 | `     ksqi_min: float = 5.0 ` | 声明 ksqi_min 的类型为 float，用于Pearson 峰度绿色边界；当前实现使用严格大于。默认值：5.0。 |
| 55 | `     bassqi_good: float = 0.95 ` | 声明 bassqi_good 的类型为 float，用于basSQI 绿色下界。默认值：0.95。 |
| 56 | `     bassqi_bad: float = 0.90 ` | 声明 bassqi_bad 的类型为 float，用于basSQI 红色与黄色边界。默认值：0.9。 |
| 57 | `     flatline_s: float = 0.75 ` | 声明 flatline_s 的类型为 float，用于持续近似平线的时长阈值（秒）。默认值：0.75。 |
| 58 | `     flat_epsilon_uV: float = 0.10 ` | 声明 flat_epsilon_uV 的类型为 float，用于相邻样本差小于此值时视为近似不变化（µV）。默认值：0.1。 |
| 59 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 60 | `     def validate(self): ` | 定义 validate(self)。检查模式、正数、最少样本事件数、窗口步长和阈值顺序等约束。 定义到这里时不执行函数体。 |
| 61 | `         if not isinstance(self.bench_windows, bool): ` | 检查条件 not isinstance(self.bench_windows, bool)；为真时执行下面缩进的一组语句。 |
| 62 | `             raise ValueError("bench_windows must be boolean") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'bench_windows must be boolean'；上层可捕获并显示原因。 |
| 63 | `         for key, value in asdict(self).items(): ` | 遍历 asdict(self).items()，每次把一项赋给 (key, value)，执行下面缩进的循环体。 |
| 64 | `             if key in ("analysis_mode", "bench_windows") or (key in ("thd_limit_pct", "frequency_limit_pct") and value is None): ` | 检查条件 key in ('analysis_mode', 'bench_windows') or (key in ('thd_limit_pct', 'frequency_limit_pct') and value is None)；为真时执行下面缩进的一组语句。 |
| 65 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 66 | `             if key == "exclude_last_s": ` | 检查条件 key == 'exclude_last_s'；为真时执行下面缩进的一组语句。 |
| 67 | `                 if not math.isfinite(float(value)) or value < 0: ` | 检查条件 not math.isfinite(float(value)) or value < 0；为真时执行下面缩进的一组语句。 |
| 68 | `                     raise ValueError("exclude_last_s must be a non-negative finite number (0 disables exclusion)") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'exclude_last_s must be a non-negative finite number (0 disables exclusion)'；上层可捕获并显示原因。 |
| 69 | `                 continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 70 | `             if not math.isfinite(float(value)) or value <= 0: ` | 检查条件 not math.isfinite(float(value)) or value <= 0；为真时执行下面缩进的一组语句。 |
| 71 | `                 raise ValueError(f"{key} must be a positive finite number") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'{key} must be a positive finite number'；上层可捕获并显示原因。 |
| 72 | `         if self.analysis_mode not in ("bench_sine", "bench_pulse", "ecg"): ` | 检查条件 self.analysis_mode not in ('bench_sine', 'bench_pulse', 'ecg')；为真时执行下面缩进的一组语句。 |
| 73 | `             raise ValueError("Select Bench / Sine, Bench / Pulse, or ECG quality") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Select Bench / Sine, Bench / Pulse, or ECG quality'；上层可捕获并显示原因。 |
| 74 | `         for key in ("min_zero_pairs", "min_repeat_runs", "ecg_min_beats"): ` | 遍历 ('min_zero_pairs', 'min_repeat_runs', 'ecg_min_beats')，每次把一项赋给 key，执行下面缩进的循环体。 |
| 75 | `             if getattr(self, key) < 3 or int(getattr(self, key)) != getattr(self, key): ` | 检查条件 getattr(self, key) < 3 or int(getattr(self, key)) != getattr(self, key)；为真时执行下面缩进的一组语句。 |
| 76 | `                 raise ValueError(f"{key} must be an integer of at least 3") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'{key} must be an integer of at least 3'；上层可捕获并显示原因。 |
| 77 | `         if not 2 <= self.harmonic_count <= 20 or int(self.harmonic_count) != self.harmonic_count: ` | 检查条件 not 2 <= self.harmonic_count <= 20 or int(self.harmonic_count) != self.harmonic_count；为真时执行下面缩进的一组语句。 |
| 78 | `             raise ValueError("Harmonic order must be an integer from 2 to 20") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Harmonic order must be an integer from 2 to 20'；上层可捕获并显示原因。 |
| 79 | `         if self.snr_bad_db >= self.snr_good_db: ` | 检查条件 self.snr_bad_db >= self.snr_good_db；为真时执行下面缩进的一组语句。 |
| 80 | `             raise ValueError("SNR bad boundary must be below the good boundary") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'SNR bad boundary must be below the good boundary'；上层可捕获并显示原因。 |
| 81 | `         if self.bench_hop_s > self.bench_window_s: ` | 检查条件 self.bench_hop_s > self.bench_window_s；为真时执行下面缩进的一组语句。 |
| 82 | `             raise ValueError("Bench window step must not exceed window duration") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Bench window step must not exceed window duration'；上层可捕获并显示原因。 |
| 83 | `         if self.ecg_window_s < 4 or self.ecg_hop_s > self.ecg_window_s: ` | 检查条件 self.ecg_window_s < 4 or self.ecg_hop_s > self.ecg_window_s；为真时执行下面缩进的一组语句。 |
| 84 | `             raise ValueError("ECG window must be >= 4 s; hop must not exceed the window") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'ECG window must be >= 4 s; hop must not exceed the window'；上层可捕获并显示原因。 |
| 85 | `         if self.ecg_match_ms >= 125 or self.flatline_s > self.ecg_window_s: ` | 检查条件 self.ecg_match_ms >= 125 or self.flatline_s > self.ecg_window_s；为真时执行下面缩进的一组语句。 |
| 86 | `             raise ValueError("Beat match tolerance must be < 125 ms; flatline duration must fit the ECG window") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Beat match tolerance must be < 125 ms; flatline duration must fit the ECG window'；上层可捕获并显示原因。 |
| 87 | `         for low, high in ((self.bsqi_bad, self.bsqi_good), (self.bassqi_bad, self.bassqi_good)): ` | 遍历 ((self.bsqi_bad, self.bsqi_good), (self.bassqi_bad, self.bassqi_good))，每次把一项赋给 (low, high)，执行下面缩进的循环体。 |
| 88 | `             if not 0 < low < high <= 1: ` | 检查条件 not 0 < low < high <= 1；为真时执行下面缩进的一组语句。 |
| 89 | `                 raise ValueError("SQI boundaries must satisfy 0 < bad < good <= 1") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'SQI boundaries must satisfy 0 < bad < good <= 1'；上层可捕获并显示原因。 |
| 90 | `         if not 0 < self.psqi_bad < self.psqi_low < self.psqi_high <= 1: ` | 检查条件 not 0 < self.psqi_bad < self.psqi_low < self.psqi_high <= 1；为真时执行下面缩进的一组语句。 |
| 91 | `             raise ValueError("pSQI boundaries must satisfy 0 < bad < low < high <= 1") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'pSQI boundaries must satisfy 0 < bad < low < high <= 1'；上层可捕获并显示原因。 |
| 92 | `         if not 0 < self.warning_fraction < 1: ` | 检查条件 not 0 < self.warning_fraction < 1；为真时执行下面缩进的一组语句。 |
| 93 | `             raise ValueError("Warning fraction must be between 0 and 1") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Warning fraction must be between 0 and 1'；上层可捕获并显示原因。 |
| 94 | `         if not 0 < self.zero_match_period_fraction < .5: ` | 检查条件 not 0 < self.zero_match_period_fraction < 0.5；为真时执行下面缩进的一组语句。 |
| 95 | `             raise ValueError("Event matching window must be smaller than half a period") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Event matching window must be smaller than half a period'；上层可捕获并显示原因。 |
| 96 | `         if not 0 < self.zero_hysteresis_peak_fraction < .5 or self.frequency_search_pct >= 50: ` | 检查条件 not 0 < self.zero_hysteresis_peak_fraction < 0.5 or self.frequency_search_pct >= 50；为真时执行下面缩进的一组语句。 |
| 97 | `             raise ValueError("Invalid crossing hysteresis or frequency search range") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Invalid crossing hysteresis or frequency search range'；上层可捕获并显示原因。 |
| 98 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 99 | `     def color(self, value, limit): ` | 定义 color(self, value, limit)。上限型指标先取绝对值；超过 limit 为红，到 warning_fraction×limit 为黄，其余为绿。 定义到这里时不执行函数体。 |
| 100 | `         if abs(value) > limit: ` | 检查条件 abs(value) > limit；为真时执行下面缩进的一组语句。 |
| 101 | `             return "red" ` | 结束当前函数并返回：'red'。 |
| 102 | `         if abs(value) >= limit * self.warning_fraction: ` | 检查条件 abs(value) >= limit * self.warning_fraction；为真时执行下面缩进的一组语句。 |
| 103 | `             return "yellow" ` | 结束当前函数并返回：'yellow'。 |
| 104 | `         return "green" ` | 结束当前函数并返回：'green'。 |
