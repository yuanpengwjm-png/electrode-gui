# modules/bench_spectrum.py：正弦的噪声与谐波

独立估计每通道频率，拟合基频和指定谐波，把残差噪声与谐波功率分开，用于 SNR、THD、SINAD。

源码：[modules/bench_spectrum.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/bench_spectrum.py>)。本说明对应 87 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [14–15](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/bench_spectrum.py:14>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `frequency_result` | [17–25](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/bench_spectrum.py:17>) | 记录测得频率及相对名义输入的误差；没有校准容差时保留黄色。 |
| `analyze` | [27–87](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/bench_spectrum.py:27>) | 对单通道做带宽受控的降采样、频率搜索、谐波拟合、残差频谱，得到四个指标。 |
| `objective` | [45–47](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/bench_spectrum.py:45>) | 给定候选频率，最小二乘拟合正弦/余弦/DC/漂移，用残差均方衡量这个频率好不好。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Sine-only frequency, noise and harmonic measurements, independent of the GUI. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 3 | ` Noise is the band-limited residual AFTER the specified harmonics are removed. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 4 | ` SINAD adds those harmonics back to the denominator. No clinical limits are implied. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 5 | ` """ ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 6 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 7 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 8 | ` from scipy.optimize import minimize_scalar ` | 从 scipy.optimize 导入 minimize_scalar。在范围内寻找使拟合残差最小的频率 |
| 9 | ` from scipy.signal import resample_poly, welch ` | 从 scipy.signal 导入 resample_poly、welch。滤波、降采样、找峰和 Welch 功率谱 |
| 10 | ` from models import MetricResult ` | 从 models 导入 MetricResult。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 13 | ` class BenchSpectrumAnalyzer: ` | 定义 BenchSpectrumAnalyzer 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 14 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 15 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 16 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 17 | `     def frequency_result(self, measured, nominal, reliable=True): ` | 定义 frequency_result(self, measured, nominal, reliable=True)。记录测得频率及相对名义输入的误差；没有校准容差时保留黄色。 定义到这里时不执行函数体。 |
| 18 | `         error = 100 * (measured / nominal - 1) ` | 把结果保存到 error：100 与 measured / nominal - 1 相乘。 |
| 19 | `         values = dict(measured_hz=float(measured), nominal_hz=nominal, error_pct=float(error)) ` | 把结果保存到 values：组装键值字典；参数：measured_hz=float(measured), nominal_hz=nominal, error_pct=float(error)。 |
| 20 | `         if not reliable: ` | 检查条件 not reliable；为真时执行下面缩进的一组语句。 |
| 21 | `             return MetricResult("yellow", "Frequency estimate is unreliable or at the search boundary", values) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：'yellow', 'Frequency estimate is unreliable or at the search boundary', values。 |
| 22 | `         limit = self.settings.frequency_limit_pct ` | 把结果保存到 limit：读取 self.settings 的 frequency_limit_pct 属性。 |
| 23 | `         if limit is None: ` | 检查条件 limit is None；为真时执行下面缩进的一组语句。 |
| 24 | `             return MetricResult("yellow", f"Frequency {measured:.6f} Hz ({error:+.4f}%); set a calibrated tolerance", values) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：'yellow', f'Frequency {measured:.6f} Hz ({error:+.4f}%); set a calibrated tolerance', values。 |
| 25 | `         return MetricResult(self.settings.color(error, limit), f"Frequency error {error:+.4f}%", values) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：self.settings.color(error, limit), f'Frequency error {error:+.4f}%', values。 |
| 26 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 27 | `     def analyze(self, samples_uV, fs, nominal): ` | 定义 analyze(self, samples_uV, fs, nominal)。对单通道做带宽受控的降采样、频率搜索、谐波拟合、残差频谱，得到四个指标。 定义到这里时不执行函数体。 |
| 28 | `         s = self.settings ` | 把结果保存到 s：读取 self 的 settings 属性。 |
| 29 | `         if nominal * 2 >= min(s.bench_bandwidth_hz, fs / 2): ` | 检查条件 nominal * 2 >= min(s.bench_bandwidth_hz, fs / 2)；为真时执行下面缩进的一组语句。 |
| 30 | `             m = MetricResult("yellow", "Analysis bandwidth must include the fundamental and at least its second harmonic") ` | 把结果保存到 m：打包颜色、原因和指标数值；参数：'yellow', 'Analysis bandwidth must include the fundamental and at least its second harmonic'。 |
| 31 | `             return {key: m for key in ("snr", "sinad", "thd", "frequency")} ` | 结束当前函数并返回：从 ('snr', 'sinad', 'thd', 'frequency') 逐个取 key，为每项生成 key: m。 |
| 32 | `         # Anti-aliased reduction for fast tone fitting. The measurement band is ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 33 | `         # explicitly limited below both the original and reduced Nyquist limits. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 34 | `         factor = max(1, int(fs // max(512., s.bench_bandwidth_hz * 4))) ` | 把结果保存到 factor：取最大值；参数：1, int(fs // max(512.0, s.bench_bandwidth_hz * 4))。 |
| 35 | `         y = resample_poly(np.asarray(samples_uV, float), 1, factor) if factor > 1 else np.asarray(samples_uV, float) ` | 把结果保存到 y：若 factor > 1，用 resample_poly(np.asarray(samples_uV, float), 1, factor)；否则用 np.asarray(samples_uV, float)。 |
| 36 | `         rate = fs / factor ` | 把结果保存到 rate：fs 与 factor 相除。 |
| 37 | `         t = np.arange(len(y)) / rate ` | 把结果保存到 t：np.arange(len(y)) 与 rate 相除。 |
| 38 | `         t = t - t.mean() ` | 把结果保存到 t：t 与 t.mean() 相减。 |
| 39 | `         band = min(s.bench_bandwidth_hz, fs * .45, rate * .45) ` | 把结果保存到 band：取最小值；参数：s.bench_bandwidth_hz, fs * 0.45, rate * 0.45。 |
| 40 | `         margin = s.frequency_search_pct / 100 ` | 把结果保存到 margin：s.frequency_search_pct 与 100 相除。 |
| 41 | `         low, high = nominal * (1 - margin), nominal * (1 + margin) ` | 把结果保存到 (low, high)：组装元组：(nominal * (1 - margin), nominal * (1 + margin))。 |
| 42 | `         stride = max(1, len(y) // 4000) ` | 把结果保存到 stride：取最大值；参数：1, len(y) // 4000。 |
| 43 | `         ts, ys = t[::stride], y[::stride] ` | 把结果保存到 (ts, ys)：组装元组：(t[::stride], y[::stride])。 |
| 44 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 45 | `         def objective(f): ` | 定义 objective(f)。给定候选频率，最小二乘拟合正弦/余弦/DC/漂移，用残差均方衡量这个频率好不好。 定义到这里时不执行函数体。 |
| 46 | `             b = np.column_stack((np.sin(2*np.pi*f*ts), np.cos(2*np.pi*f*ts), np.ones(len(ts)), ts)) ` | 把结果保存到 b：把一维列并排组成二维矩阵；参数：(np.sin(2 * np.pi * f * ts), np.cos(2 * np.pi * f * ts), np.ones(len(ts)), ts)。 |
| 47 | `             return float(np.mean((ys - b @ np.linalg.lstsq(b, ys, rcond=None)[0]) ** 2)) ` | 结束当前函数并返回：转换为浮点数；参数：np.mean((ys - b @ np.linalg.lstsq(b, ys, rcond=None)[0]) ** 2)。 |
| 48 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 49 | `         grid = np.linspace(low, high, 25) ` | 把结果保存到 grid：生成包含两端的等间隔数值；参数：low, high, 25。 |
| 50 | `         index = int(np.argmin([objective(f) for f in grid])) ` | 把结果保存到 index：转换为整数；参数：np.argmin([objective(f) for f in grid])。 |
| 51 | `         f = float(minimize_scalar(objective, bounds=(grid[max(0,index-1)], grid[min(len(grid)-1,index+1)]), ` | 把结果保存到 f：转换为浮点数；参数：minimize_scalar(objective, bounds=(grid[max(0, index - 1)], grid[min(len(grid) - 1, index + 1)]), method='bounded', options={'xatol': 1e-09}).x。 |
| 52 | `                                   method="bounded", options={"xatol": 1e-9}).x) ` | 接续第 51 行的同一条语句，不是另起一段算法。 把结果保存到 f：转换为浮点数；参数：minimize_scalar(objective, bounds=(grid[max(0, index - 1)], grid[min(len(grid) - 1, index + 1)]), method='bounded', options={'xatol': 1e-09}).x。 |
| 53 | `         order = min(int(s.harmonic_count), int(band // f)) ` | 把结果保存到 order：取最小值；参数：int(s.harmonic_count), int(band // f)。 |
| 54 | `         columns = [np.ones(len(t)), t] ` | 把结果保存到 columns：组装列表：[np.ones(len(t)), t]。 |
| 55 | `         for h in range(1, order + 1): ` | 遍历 range(1, order + 1)，每次把一项赋给 h，执行下面缩进的循环体。 |
| 56 | `             columns.extend((np.sin(2*np.pi*h*f*t), np.cos(2*np.pi*h*f*t))) ` | 把多项逐个加入列表；参数：(np.sin(2 * np.pi * h * f * t), np.cos(2 * np.pi * h * f * t))。 |
| 57 | `         design = np.column_stack(columns) ` | 把结果保存到 design：把一维列并排组成二维矩阵；参数：columns。 |
| 58 | `         beta = np.linalg.lstsq(design, y, rcond=None)[0] ` | 把结果保存到 beta：按索引/键 0 取 np.linalg.lstsq(design, y, rcond=None) 的内容。 |
| 59 | `         tone_power = np.array([(beta[2*h]**2 + beta[2*h+1]**2) / 2 for h in range(1, order+1)]) ` | 每阶正余弦系数的平方和除以 2，得到对应正弦成分的均方功率（µV²）。 |
| 60 | `         fundamental = float(tone_power[0]) ` | 把结果保存到 fundamental：转换为浮点数；参数：tone_power[0]。 |
| 61 | `         residual = y - design @ beta ` | 把结果保存到 residual：y 与 design @ beta 相减。 |
| 62 | `         frequencies, psd = welch(residual, rate, nperseg=min(len(y), max(32, int(rate*2))), detrend="constant") ` | 把结果保存到 (frequencies, psd)：分段加窗平均估计功率谱密度；参数：residual, rate, nperseg=min(len(y), max(32, int(rate * 2))), detrend='constant'。 |
| 63 | `         df = frequencies[1] - frequencies[0] ` | 把结果保存到 df：frequencies[1] 与 frequencies[0] 相减。 |
| 64 | `         noise_power = float(np.sum(psd[(frequencies > 0) & (frequencies <= band)]) * df) ` | 对去除指定谐波后的残差 PSD 在大于 0 到 band Hz 内求和乘 Δf；未建模谐波也可能留在残差。 |
| 65 | `         harmonic_power = float(tone_power[1:].sum()) ` | 只加二阶到最高已拟合阶的功率；第零个数组元素是基频，不能算入谐波失真。 |
| 66 | `         valid = len(y)/rate*nominal >= s.min_cycles and fundamental > (s.min_response_uVpp/(2*np.sqrt(2)))**2 ` | 把结果保存到 valid：len(y) / rate * nominal >= s.min_cycles and fundamental > (s.min_response_uVpp / (2 * np.sqrt(2))) ** 2。 |
| 67 | `         valid &= min(f-low, high-f) > nominal*margin*.01 ` | 把 valid 的原值应用本行运算于 min(f - low, high - f) > nominal * margin * 0.01，再写回同一变量。 |
| 68 | `         floor = max(fundamental, 1e-24) * 1e-16  # finite 160 dB numerical reporting ceiling ` | 把结果保存到 floor：max(fundamental, 1e-24) 与 1e-16 相乘。 |
| 69 | `         snr = float(10*np.log10(max(fundamental, 1e-24)/max(noise_power, floor))) ` | 用基频功率/残差噪声功率计算 dB；下限保护避免除零，并使显示存在数值上限。 |
| 70 | `         sinad = float(10*np.log10(max(fundamental, 1e-24)/max(noise_power+harmonic_power, floor))) ` | SINAD 分母含残差噪声和已拟合谐波功率，因此和 SNR 分开。 |
| 71 | `         thd = float(100*np.sqrt(harmonic_power/max(fundamental, 1e-24))) ` | THD%=100×sqrt(谐波功率/基频功率)；当前程序返回百分比。分母下限只用于避免除零。 |
| 72 | `         values = dict(frequency_hz=f, bandwidth_hz=band, highest_harmonic=order, ` | 把结果保存到 values：组装键值字典；参数：frequency_hz=f, bandwidth_hz=band, highest_harmonic=order, noise_rms_uV=math.sqrt(noise_power), fundamental_rms_uV=math.sqrt(fundamental), snr_db…（完整表达式见左栏）。 |
| 73 | `                       noise_rms_uV=math.sqrt(noise_power), fundamental_rms_uV=math.sqrt(fundamental), ` | 接续第 72 行的同一条语句，不是另起一段算法。 调用 math.sqrt；参数：noise_power。 |
| 74 | `                       snr_db=snr, sinad_db=sinad, thd_pct=thd, ` | 接续第 72 行的同一条语句，不是另起一段算法。 把结果保存到 values：组装键值字典；参数：frequency_hz=f, bandwidth_hz=band, highest_harmonic=order, noise_rms_uV=math.sqrt(noise_power), fundamental_rms_uV=math.sqrt(fundamental), snr_db…（完整表达式见左栏）。 |
| 75 | `                       definition="SNR excludes fitted harmonics 2..N; SINAD includes them; DC/drift excluded") ` | 接续第 72 行的同一条语句，不是另起一段算法。 把结果保存到 values：组装键值字典；参数：frequency_hz=f, bandwidth_hz=band, highest_harmonic=order, noise_rms_uV=math.sqrt(noise_power), fundamental_rms_uV=math.sqrt(fundamental), snr_db…（完整表达式见左栏）。 |
| 76 | `         if not valid: ` | 检查条件 not valid；为真时执行下面缩进的一组语句。 |
| 77 | `             unavailable = MetricResult("yellow", "Insufficient cycles/response or frequency outside search range", values) ` | 把结果保存到 unavailable：打包颜色、原因和指标数值；参数：'yellow', 'Insufficient cycles/response or frequency outside search range', values。 |
| 78 | `             return dict(snr=unavailable, sinad=unavailable, thd=unavailable, ` | 结束当前函数并返回：组装键值字典；参数：snr=unavailable, sinad=unavailable, thd=unavailable, frequency=self.frequency_result(f, nominal, False)。 |
| 79 | `                         frequency=self.frequency_result(f, nominal, False)) ` | 接续第 78 行的同一条语句，不是另起一段算法。 记录测得频率及相对名义输入的误差；没有校准容差时保留黄色。；参数：f, nominal, False。 |
| 80 | `         color = "green" if snr >= s.snr_good_db else "yellow" if snr >= s.snr_bad_db else "red" ` | 把结果保存到 color：若 snr >= s.snr_good_db，用 'green'；否则用 'yellow' if snr >= s.snr_bad_db else 'red'。 |
| 81 | `         thd_color = "yellow" if s.thd_limit_pct is None else s.color(thd, s.thd_limit_pct) ` | 把结果保存到 thd_color：若 s.thd_limit_pct is None，用 'yellow'；否则用 s.color(thd, s.thd_limit_pct)。 |
| 82 | `         return dict( ` | 结束当前函数并返回：组装键值字典；参数：snr=MetricResult(color, f'SNR {snr:.2f} dB, 0–{band:g} Hz (specified harmonics excluded)', values), sinad=MetricResult('yellow', f'SINAD {sinad:.…（完整表达式见左栏）。 |
| 83 | `             snr=MetricResult(color, f"SNR {snr:.2f} dB, 0–{band:g} Hz (specified harmonics excluded)", values), ` | 接续第 82 行的同一条语句，不是另起一段算法。 打包颜色、原因和指标数值；参数：color, f'SNR {snr:.2f} dB, 0–{band:g} Hz (specified harmonics excluded)', values。 |
| 84 | `             sinad=MetricResult("yellow", f"SINAD {sinad:.2f} dB; descriptive measurement, no acceptance limit", values), ` | 接续第 82 行的同一条语句，不是另起一段算法。 打包颜色、原因和指标数值；参数：'yellow', f'SINAD {sinad:.2f} dB; descriptive measurement, no acceptance limit', values。 |
| 85 | `             thd=MetricResult(thd_color, f"THD {thd:.4f}% through harmonic {order}" + ` | 接续第 82 行的同一条语句，不是另起一段算法。 打包颜色、原因和指标数值；参数：thd_color, f'THD {thd:.4f}% through harmonic {order}' + ('; set a calibrated tolerance' if s.thd_limit_pct is None else ''), values。 |
| 86 | `                              ("; set a calibrated tolerance" if s.thd_limit_pct is None else ""), values), ` | 接续第 82 行的同一条语句，不是另起一段算法。 结束当前函数并返回：组装键值字典；参数：snr=MetricResult(color, f'SNR {snr:.2f} dB, 0–{band:g} Hz (specified harmonics excluded)', values), sinad=MetricResult('yellow', f'SINAD {sinad:.…（完整表达式见左栏）。 |
| 87 | `             frequency=self.frequency_result(f, nominal)) ` | 接续第 82 行的同一条语句，不是另起一段算法。 记录测得频率及相对名义输入的误差；没有校准容差时保留黄色。；参数：f, nominal。 |
