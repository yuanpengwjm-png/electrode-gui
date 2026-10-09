# modules/ecg_quality.py：ECG SQI

两个不同的心搏检测器加一对一匹配，计算 bSQI；Welch 频谱计算 pSQI/basSQI；另算 Pearson 峰度和平线/削顶。

源码：[modules/ecg_quality.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py>)。本说明对应 143 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `longest_true` | [12–15](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py:12>) | 给布尔序列两端补 False，通过差分找到每段 True 的起止，返回最长连续长度。 |
| `bandpass` | [18–19](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py:18>) | 构建三阶 Butterworth 二阶节带通滤波器，再对当前数组正反向滤波。它使用完整数组，并非流式因果滤波。 |
| `detect` | [24–41](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py:24>) | 按所属检测器的路径定位候选心搏，返回以秒表示的时间，而不是采样点编号。 |
| `detect` | [46–54](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py:46>) | 按所属检测器的路径定位候选心搏，返回以秒表示的时间，而不是采样点编号。 |
| `score` | [60–71](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py:60>) | 排序两个时间列表，用双指针一对一匹配，得分为匹配数/并集数；没有事件时返回 None。 |
| `__init__` | [77–80](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py:77>) | 保存参数并创建能量法与突出度法两个检测器。 |
| `unavailable` | [82–83](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py:82>) | 给所有 SQI 返回黄色和无法评估原因，不伪造一个零分。 |
| `analyze_window` | [85–143](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py:85>) | 检查完整性，在合适采样率下检测心搏、估计频谱和峰度，分别判定后按最差分项汇总。 |
| `power` | [124–125](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py:124>) | 选取左闭右开的频段，PSD 求和乘频率间隔得到功率。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Transparent ECG SQI prototype. Two different beat detectors, complete windows. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 3 | ` The fusion rule is conservative: worst component wins. It is an engineering ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 4 | ` screen, not a validated diagnosis of electrode damage or ECG interpretability. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 5 | ` """ ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 6 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 7 | ` from scipy.signal import butter, sosfiltfilt, find_peaks, resample_poly, welch ` | 从 scipy.signal 导入 butter、sosfiltfilt、find_peaks、resample_poly、welch。滤波、降采样、找峰和 Welch 功率谱 |
| 8 | ` from scipy.stats import kurtosis ` | 从 scipy.stats 导入 kurtosis。统计量，例如峰度 |
| 9 | ` from models import MetricResult, combine ` | 从 models 导入 MetricResult、combine。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 10 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | ` def longest_true(mask): ` | 定义 longest_true(mask)。给布尔序列两端补 False，通过差分找到每段 True 的起止，返回最长连续长度。 定义到这里时不执行函数体。 |
| 13 | `     edges = np.diff(np.r_[False, np.asarray(mask, bool), False].astype(int)) ` | 把结果保存到 edges：计算相邻值之差；参数：np.r_[False, np.asarray(mask, bool), False].astype(int)。 |
| 14 | `     starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1) ` | 把结果保存到 (starts, ends)：组装元组：(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1))。 |
| 15 | `     return int(np.max(ends-starts)) if len(starts) else 0 ` | 结束当前函数并返回：若 len(starts)，用 int(np.max(ends - starts))；否则用 0。 |
| 16 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 17 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 18 | ` def bandpass(x, fs, low, high): ` | 定义 bandpass(x, fs, low, high)。构建三阶 Butterworth 二阶节带通滤波器，再对当前数组正反向滤波。它使用完整数组，并非流式因果滤波。 定义到这里时不执行函数体。 |
| 19 | `     return sosfiltfilt(butter(3, (low, high), btype="bandpass", fs=fs, output="sos"), x) ` | 结束当前函数并返回：用二阶节做正反向滤波；参数：butter(3, (low, high), btype='bandpass', fs=fs, output='sos'), x。 |
| 20 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 21 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 22 | ` class EnergyQRSDetector: ` | 定义 EnergyQRSDetector 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 23 | `     """Derivative energy + 100 ms integration, then local peak refinement.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 24 | `     def detect(self, x, fs): ` | 定义 detect(self, x, fs)。按所属检测器的路径定位候选心搏，返回以秒表示的时间，而不是采样点编号。 定义到这里时不执行函数体。 |
| 25 | `         filtered = bandpass(x, fs, 5, 18) ` | 把结果保存到 filtered：调用 bandpass；参数：x, fs, 5, 18。 |
| 26 | `         energy = np.diff(filtered, prepend=filtered[0])**2 ` | 把结果保存到 energy：np.diff(filtered, prepend=filtered[0]) 与 2 乘方。 |
| 27 | `         width = max(1, round(.10*fs)) ` | 把结果保存到 width：取最大值；参数：1, round(0.1 * fs)。 |
| 28 | `         integrated = np.convolve(energy, np.ones(width)/width, mode="same") ` | 把结果保存到 integrated：做离散卷积；此处用于滑动积分；参数：energy, np.ones(width) / width, mode='same'。 |
| 29 | `         span = float(np.percentile(integrated, 99)-np.median(integrated)) ` | 把结果保存到 span：转换为浮点数；参数：np.percentile(integrated, 99) - np.median(integrated)。 |
| 30 | `         if span <= 1e-20: ` | 检查条件 span <= 1e-20；为真时执行下面缩进的一组语句。 |
| 31 | `             return np.array([]) ` | 结束当前函数并返回：构造 NumPy 数组；参数：[]。 |
| 32 | `         peaks, _ = find_peaks(integrated, distance=max(1, round(.25*fs)), ` | 把结果保存到 (peaks, _)：按高度、突出度和间距找局部峰；参数：integrated, distance=max(1, round(0.25 * fs)), height=np.median(integrated) + 0.2 * span, prominence=0.12 * span。 |
| 33 | `                              height=np.median(integrated)+.20*span, prominence=.12*span) ` | 接续第 32 行的同一条语句，不是另起一段算法。 计算中位数；参数：integrated。 |
| 34 | `         refined = [] ` | 把结果保存到 refined：组装列表：[]。 |
| 35 | `         half = max(1, round(.09*fs)) ` | 把结果保存到 half：取最大值；参数：1, round(0.09 * fs)。 |
| 36 | `         for peak in peaks: ` | 遍历 peaks，每次把一项赋给 peak，执行下面缩进的循环体。 |
| 37 | `             lo, hi = max(0, peak-half), min(len(x), peak+half+1) ` | 把结果保存到 (lo, hi)：组装元组：(max(0, peak - half), min(len(x), peak + half + 1))。 |
| 38 | `             k = lo + int(np.argmax(np.abs(filtered[lo:hi]))) ` | 把结果保存到 k：lo 与 int(np.argmax(np.abs(filtered[lo:hi]))) 相加。 |
| 39 | `             if not refined or k-refined[-1] >= .25*fs: ` | 检查条件 not refined or k - refined[-1] >= 0.25 * fs；为真时执行下面缩进的一组语句。 |
| 40 | `                 refined.append(k) ` | 把一项加入列表末尾；参数：k。 |
| 41 | `         return np.asarray(refined, float)/fs ` | 结束当前函数并返回：np.asarray(refined, float) 与 fs 相除。 |
| 42 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 43 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 44 | ` class ProminenceQRSDetector: ` | 定义 ProminenceQRSDetector 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 45 | `     """Independent amplitude/prominence path; no derivative-energy candidates.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 46 | `     def detect(self, x, fs): ` | 定义 detect(self, x, fs)。按所属检测器的路径定位候选心搏，返回以秒表示的时间，而不是采样点编号。 定义到这里时不执行函数体。 |
| 47 | `         filtered = np.abs(bandpass(x, fs, 5, 25)) ` | 把结果保存到 filtered：逐元素取绝对值；参数：bandpass(x, fs, 5, 25)。 |
| 48 | `         baseline = float(np.median(filtered)) ` | 把结果保存到 baseline：转换为浮点数；参数：np.median(filtered)。 |
| 49 | `         span = float(np.percentile(filtered, 99)-baseline) ` | 把结果保存到 span：转换为浮点数；参数：np.percentile(filtered, 99) - baseline。 |
| 50 | `         if span <= 1e-12: ` | 检查条件 span <= 1e-12；为真时执行下面缩进的一组语句。 |
| 51 | `             return np.array([]) ` | 结束当前函数并返回：构造 NumPy 数组；参数：[]。 |
| 52 | `         peaks, _ = find_peaks(filtered, distance=max(1, round(.25*fs)), ` | 把结果保存到 (peaks, _)：按高度、突出度和间距找局部峰；参数：filtered, distance=max(1, round(0.25 * fs)), height=baseline + 0.35 * span, prominence=0.3 * span。 |
| 53 | `                              height=baseline+.35*span, prominence=.30*span) ` | 接续第 52 行的同一条语句，不是另起一段算法。 把结果保存到 (peaks, _)：按高度、突出度和间距找局部峰；参数：filtered, distance=max(1, round(0.25 * fs)), height=baseline + 0.35 * span, prominence=0.3 * span。 |
| 54 | `         return peaks.astype(float)/fs ` | 结束当前函数并返回：peaks.astype(float) 与 fs 相除。 |
| 55 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 56 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 57 | ` class BeatAgreement: ` | 定义 BeatAgreement 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 58 | `     """One-to-one matching; one detected beat cannot satisfy two matches.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 59 | `     @staticmethod ` | @staticmethod 表示该方法不依赖 self，可直接通过类调用。 |
| 60 | `     def score(a, b, tolerance): ` | 定义 score(a, b, tolerance)。排序两个时间列表，用双指针一对一匹配，得分为匹配数/并集数；没有事件时返回 None。 定义到这里时不执行函数体。 |
| 61 | `         a, b = np.sort(a), np.sort(b) ` | 把结果保存到 (a, b)：组装元组：(np.sort(a), np.sort(b))。 |
| 62 | `         i = j = matched = 0 ` | 把结果保存到 i、j、matched：0。 |
| 63 | `         while i < len(a) and j < len(b): ` | 只要 i < len(a) and j < len(b) 为真就重复循环；退出依靠条件改变、break 或异常。 |
| 64 | `             if abs(a[i]-b[j]) <= tolerance: ` | 检查条件 abs(a[i] - b[j]) <= tolerance；为真时执行下面缩进的一组语句。 |
| 65 | `                 matched += 1; i += 1; j += 1 ` | 把 matched 的原值加上 1，再写回同一变量。 把 i 的原值加上 1，再写回同一变量。 把 j 的原值加上 1，再写回同一变量。 |
| 66 | `             elif a[i] < b[j]: ` | 检查条件 a[i] < b[j]；为真时执行下面缩进的一组语句。 |
| 67 | `                 i += 1 ` | 把 i 的原值加上 1，再写回同一变量。 |
| 68 | `             else: ` | 前面对应条件不成立时，进入此分支。 |
| 69 | `                 j += 1 ` | 把 j 的原值加上 1，再写回同一变量。 |
| 70 | `         union = len(a)+len(b)-matched ` | 并集计数：两组事件数相加减去共同匹配数；当前 bSQI 使用这个分母，不是 F1 的分母。 |
| 71 | `         return (float(matched/union) if union else None), matched ` | 返回 bSQI=匹配数/并集数以及匹配数；双方无峰时 bSQI 为 None，不能视为完全一致。 |
| 72 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 73 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 74 | ` class ECGQualityAnalyzer: ` | 定义 ECGQualityAnalyzer 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 75 | `     metric_keys = ("bsqi", "psqi", "ksqi", "bassqi", "integrity") ` | 把结果保存到 metric_keys：组装元组：('bsqi', 'psqi', 'ksqi', 'bassqi', 'integrity')。 |
| 76 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 77 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。保存参数并创建能量法与突出度法两个检测器。 定义到这里时不执行函数体。 |
| 78 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 79 | `         self.detector_a = EnergyQRSDetector() ` | 把结果保存到 self.detector_a：调用 EnergyQRSDetector。 |
| 80 | `         self.detector_b = ProminenceQRSDetector() ` | 把结果保存到 self.detector_b：调用 ProminenceQRSDetector。 |
| 81 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 82 | `     def unavailable(self, message): ` | 定义 unavailable(self, message)。给所有 SQI 返回黄色和无法评估原因，不伪造一个零分。 定义到这里时不执行函数体。 |
| 83 | `         return {key: MetricResult("yellow", message) for key in (*self.metric_keys, "ecg_quality")} ` | 结束当前函数并返回：从 (*self.metric_keys, 'ecg_quality') 逐个取 key，为每项生成 key: MetricResult('yellow', message)。 |
| 84 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 85 | `     def analyze_window(self, raw_uV, fs, limits=None): ` | 定义 analyze_window(self, raw_uV, fs, limits=None)。检查完整性，在合适采样率下检测心搏、估计频谱和峰度，分别判定后按最差分项汇总。 定义到这里时不执行函数体。 |
| 86 | `         s = self.settings ` | 把结果保存到 s：读取 self 的 settings 属性。 |
| 87 | `         raw = np.asarray(raw_uV, float) ` | 把结果保存到 raw：转换或视为 NumPy 数组；参数：raw_uV, float。 |
| 88 | `         if not np.isfinite(raw).all(): ` | 检查条件 not np.isfinite(raw).all()；为真时执行下面缩进的一组语句。 |
| 89 | `             return self.unavailable("Missing or non-finite samples; window unavailable") ` | 结束当前函数并返回：给所有 SQI 返回黄色和无法评估原因，不伪造一个零分。；参数：'Missing or non-finite samples; window unavailable'。 |
| 90 | `         if fs < 100: ` | 检查条件 fs < 100；为真时执行下面缩进的一组语句。 |
| 91 | `             return self.unavailable("ECG SQI requires a sample rate of at least 100 Hz") ` | 结束当前函数并返回：给所有 SQI 返回黄色和无法评估原因，不伪造一个零分。；参数：'ECG SQI requires a sample rate of at least 100 Hz'。 |
| 92 | `         if len(raw) < round(s.ecg_window_s*fs): ` | 检查条件 len(raw) < round(s.ecg_window_s * fs)；为真时执行下面缩进的一组语句。 |
| 93 | `             return self.unavailable(f"Insufficient data: need a complete {s.ecg_window_s:g} s ECG window") ` | 结束当前函数并返回：给所有 SQI 返回黄色和无法评估原因，不伪造一个零分。；参数：f'Insufficient data: need a complete {s.ecg_window_s:g} s ECG window'。 |
| 94 | `         flat_samples = longest_true(np.abs(np.diff(raw)) <= s.flat_epsilon_uV) ` | 在原始 µV 样本中找连续相邻差很小的最长段；它是持续时间检查，并非这里另算一个标准化 fSQI 分数。 |
| 95 | `         flat_s = (flat_samples+1)/fs if flat_samples else 0. ` | 连续 k 个小差值跨越 k+1 个采样点；按本实现换成近似平线秒数。 |
| 96 | `         clipped = 0 if limits is None else int(np.count_nonzero((raw <= limits[0]) \| (raw >= limits[1]))) ` | 把结果保存到 clipped：若 limits is None，用 0；否则用 int(np.count_nonzero((raw <= limits[0]) &#124; (raw >= limits[1])))。 |
| 97 | `         integrity_bad = flat_s >= s.flatline_s or clipped > 0 ` | 把结果保存到 integrity_bad：flat_s >= s.flatline_s or clipped > 0。 |
| 98 | `         integrity = MetricResult("red" if integrity_bad else "green", ` | 把结果保存到 integrity：打包颜色、原因和指标数值；参数：'red' if integrity_bad else 'green', f'Longest near-flat segment {flat_s:.3f} s; digital rail samples {clipped}', dict(flatline_s=flat_s, clipped…（完整表达式见左栏）。 |
| 99 | `             f"Longest near-flat segment {flat_s:.3f} s; digital rail samples {clipped}", ` | 接续第 98 行的同一条语句，不是另起一段算法。 把结果保存到 integrity：打包颜色、原因和指标数值；参数：'red' if integrity_bad else 'green', f'Longest near-flat segment {flat_s:.3f} s; digital rail samples {clipped}', dict(flatline_s=flat_s, clipped…（完整表达式见左栏）。 |
| 100 | `             dict(flatline_s=flat_s, clipped_samples=clipped, epsilon_uV=s.flat_epsilon_uV)) ` | 接续第 98 行的同一条语句，不是另起一段算法。 组装键值字典；参数：flatline_s=flat_s, clipped_samples=clipped, epsilon_uV=s.flat_epsilon_uV。 |
| 101 | `         if np.ptp(raw) <= s.flat_epsilon_uV: ` | 检查条件 np.ptp(raw) <= s.flat_epsilon_uV；为真时执行下面缩进的一组语句。 |
| 102 | `             metrics = self.unavailable("No measurable ECG variation; spectral ratios and beat agreement are undefined") ` | 把结果保存到 metrics：给所有 SQI 返回黄色和无法评估原因，不伪造一个零分。；参数：'No measurable ECG variation; spectral ratios and beat agreement are undefined'。 |
| 103 | `             metrics["integrity"] = integrity ` | 把结果保存到 metrics['integrity']：integrity。 |
| 104 | `             metrics["ecg_quality"] = combine([integrity]) ` | 把结果保存到 metrics['ecg_quality']：调用 combine；参数：[integrity]。 |
| 105 | `             return metrics ` | 结束当前函数并返回：metrics。 |
| 106 | `         factor = max(1, int(fs // 250)) ` | 选整数降采样因子；目标是降低 ECG 计算量，最终采样率为 fs/factor，并不保证恰好 250 Hz。 |
| 107 | `         x = resample_poly(raw-raw.mean(), 1, factor) if factor > 1 else raw-raw.mean() ` | 把结果保存到 x：若 factor > 1，用 resample_poly(raw - raw.mean(), 1, factor)；否则用 raw - raw.mean()。 |
| 108 | `         rate = fs/factor ` | 把结果保存到 rate：fs 与 factor 相除。 |
| 109 | `         a, b = self.detector_a.detect(x, rate), self.detector_b.detect(x, rate) ` | 把结果保存到 (a, b)：组装元组：(self.detector_a.detect(x, rate), self.detector_b.detect(x, rate))。 |
| 110 | `         # Both detectors see identical input; avoid edge effects in both equally. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 111 | `         duration = len(x)/rate ` | 把结果保存到 duration：len(x) 与 rate 相除。 |
| 112 | `         a = a[(a >= .2) & (a < duration-.2)] ` | 把结果保存到 a：用 (a >= 0.2) & (a < duration - 0.2) 生成的索引或布尔条件选取 a 中对应的元素。 |
| 113 | `         b = b[(b >= .2) & (b < duration-.2)] ` | 把结果保存到 b：用 (b >= 0.2) & (b < duration - 0.2) 生成的索引或布尔条件选取 b 中对应的元素。 |
| 114 | `         agreement, matched = BeatAgreement.score(a, b, s.ecg_match_ms/1000) ` | 将匹配容差由 ms 换成秒，对同一通道的两组心搏时间一对一匹配，返回一致率和匹配数。 |
| 115 | `         counts = dict(value=agreement, detector_a_count=len(a), detector_b_count=len(b), matched=matched, ` | 把结果保存到 counts：组装键值字典；参数：value=agreement, detector_a_count=len(a), detector_b_count=len(b), matched=matched, detector_a_s=a.tolist(), detector_b_s=b.tolist(), tolerance_m…（完整表达式见左栏）。 |
| 116 | `                       detector_a_s=a.tolist(), detector_b_s=b.tolist(), tolerance_ms=s.ecg_match_ms) ` | 接续第 115 行的同一条语句，不是另起一段算法。 把数组转为普通列表以便 JSON 序列化。 |
| 117 | `         if agreement is None or min(len(a), len(b)) < s.ecg_min_beats: ` | 检查条件 agreement is None or min(len(a), len(b)) < s.ecg_min_beats；为真时执行下面缩进的一组语句。 |
| 118 | `             bsqi = MetricResult("yellow", "Insufficient detected beats for reliable bSQI", counts) ` | 把结果保存到 bsqi：打包颜色、原因和指标数值；参数：'yellow', 'Insufficient detected beats for reliable bSQI', counts。 |
| 119 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 120 | `             color = "green" if agreement > s.bsqi_good else "yellow" if agreement >= s.bsqi_bad else "red" ` | 把结果保存到 color：若 agreement > s.bsqi_good，用 'green'；否则用 'yellow' if agreement >= s.bsqi_bad else 'red'。 |
| 121 | `             bsqi = MetricResult(color, f"bSQI {agreement:.3f}; A={len(a)}, B={len(b)}, matched={matched}", counts) ` | 把结果保存到 bsqi：打包颜色、原因和指标数值；参数：color, f'bSQI {agreement:.3f}; A={len(a)}, B={len(b)}, matched={matched}', counts。 |
| 122 | `         f, p = welch(x, rate, nperseg=min(len(x), round(rate*4)), detrend="constant") ` | 把结果保存到 (f, p)：分段加窗平均估计功率谱密度；参数：x, rate, nperseg=min(len(x), round(rate * 4)), detrend='constant'。 |
| 123 | `         df = float(f[1]-f[0]) ` | 把结果保存到 df：转换为浮点数；参数：f[1] - f[0]。 |
| 124 | `         def power(low, high): ` | 定义 power(low, high)。选取左闭右开的频段，PSD 求和乘频率间隔得到功率。 定义到这里时不执行函数体。 |
| 125 | `             return float(np.sum(p[(f >= low) & (f < high)])*df) ` | 结束当前函数并返回：转换为浮点数；参数：np.sum(p[(f >= low) & (f < high)]) * df。 |
| 126 | `         denominator = power(5, 40) ` | 把结果保存到 denominator：调用 power；参数：5, 40。 |
| 127 | `         total = power(0, 40) ` | 把结果保存到 total：调用 power；参数：0, 40。 |
| 128 | `         psqi = None if denominator <= 1e-20 else power(5, 15)/denominator ` | 分母足够大时计算 pSQI=P[5,15)/P[5,40)；近乎无能量时返回 None。 |
| 129 | `         bas = None if total <= 1e-20 else float(np.clip(1-power(0, 1)/total, 0, 1)) ` | 计算 basSQI=1−P[0,1)/P[0,40)，把数值舍入误差限制在 [0,1]；分母太小则未知。 |
| 130 | `         k = float(kurtosis(x, fisher=False, bias=False)) ` | 计算经当前预处理后的波形 Pearson 峰度，并使用偏差修正；fisher=False 表示不减 3。 |
| 131 | `         if psqi is None: ` | 检查条件 psqi is None；为真时执行下面缩进的一组语句。 |
| 132 | `             pmetric = MetricResult("yellow", "pSQI denominator is too small") ` | 把结果保存到 pmetric：打包颜色、原因和指标数值；参数：'yellow', 'pSQI denominator is too small'。 |
| 133 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 134 | `             color = "green" if s.psqi_low <= psqi <= s.psqi_high else "yellow" if s.psqi_bad <= psqi < s.psqi_low else "red" ` | 把结果保存到 color：若 s.psqi_low <= psqi <= s.psqi_high，用 'green'；否则用 'yellow' if s.psqi_bad <= psqi < s.psqi_low else 'red'。 |
| 135 | `             pmetric = MetricResult(color, f"pSQI {psqi:.3f} = P[5,15) / P[5,40)", dict(value=float(psqi))) ` | 把结果保存到 pmetric：打包颜色、原因和指标数值；参数：color, f'pSQI {psqi:.3f} = P[5,15) / P[5,40)', dict(value=float(psqi))。 |
| 136 | `         bmetric = MetricResult("yellow", "basSQI denominator is too small") if bas is None else MetricResult( ` | 把结果保存到 bmetric：若 bas is None，用 MetricResult('yellow', 'basSQI denominator is too small')；否则用 MetricResult('green' if bas >= s.bassqi_good else 'yellow' if bas >= s.bassqi_bad else 're…（完整表达式见左栏）。 |
| 137 | `             "green" if bas >= s.bassqi_good else "yellow" if bas >= s.bassqi_bad else "red", ` | 接续第 136 行的同一条语句，不是另起一段算法。 把结果保存到 bmetric：若 bas is None，用 MetricResult('yellow', 'basSQI denominator is too small')；否则用 MetricResult('green' if bas >= s.bassqi_good else 'yellow' if bas >= s.bassqi_bad else 're…（完整表达式见左栏）。 |
| 138 | `             f"basSQI {bas:.3f} = 1 - P[0,1) / P[0,40)", dict(value=bas)) ` | 接续第 136 行的同一条语句，不是另起一段算法。 组装键值字典；参数：value=bas。 |
| 139 | `         kmetric = MetricResult("green" if k > s.ksqi_min else "red", f"Pearson kurtosis {k:.3f}", dict(value=k)) if np.isfinite(k) else MetricResult("yellow", "Kurtosis is undefined") ` | 把结果保存到 kmetric：若 np.isfinite(k)，用 MetricResult('green' if k > s.ksqi_min else 'red', f'Pearson kurtosis {k:.3f}', dict(value…（完整表达式见左栏）；否则用 MetricResult('yellow', 'Kurtosis is undefined')。 |
| 140 | `         result = dict(bsqi=bsqi, psqi=pmetric, ksqi=kmetric, bassqi=bmetric, integrity=integrity) ` | 把结果保存到 result：组装键值字典；参数：bsqi=bsqi, psqi=pmetric, ksqi=kmetric, bassqi=bmetric, integrity=integrity。 |
| 141 | `         result["ecg_quality"] = combine(list(result.values())) ` | 把结果保存到 result['ecg_quality']：调用 combine；参数：list(result.values())。 |
| 142 | `         result["ecg_quality"].message = "Prototype ECG screen: " + result["ecg_quality"].message ` | 把结果保存到 result['ecg_quality'].message：拼接 'Prototype ECG screen: ' 和 result['ecg_quality'].message。 |
| 143 | `         return result ` | 结束当前函数并返回：result。 |
