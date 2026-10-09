# utils/numerics.py：底层数值计算

按 BDF 头解码 24 位样本并换算 µV；用共同频率及逐通道最小二乘计算正弦幅度、基线和拟合残差。

源码：[utils/numerics.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/numerics.py>)。本说明对应 142 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `read_bdf_stream` | [9–72](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/numerics.py:9>) | 先读取固定头和逐通道头；根据通道标签解码样本、符号扩展、标定至 µV，并计数数字削顶。 |
| `sine_design` | [75–77](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/numerics.py:75>) | 构造四列设计矩阵：sin、cos、常数 1、中心化时间；用来分开基频、DC 和线性漂移。 |
| `fit_record` | [80–142](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/numerics.py:80>) | 用各通道中位波形找共同频率，再保留原采样率逐通道拟合，返回物理幅度和质量门控理由。 |
| `objective` | [102–104](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/numerics.py:102>) | 计算给定频率的正弦拟合均方残差，供优化器最小化。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Tested BDF and sine kernels extracted from the existing bench-qa tool. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` No GUI imports and no runtime dependency on bench-qa. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 3 | ` """ ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 4 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 5 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 6 | ` from scipy.optimize import minimize_scalar ` | 从 scipy.optimize 导入 minimize_scalar。在范围内寻找使拟合残差最小的频率 |
| 7 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 8 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 9 | ` def read_bdf_stream(stream, size, selected, allocator=None, progress=lambda _: None): ` | 定义 read_bdf_stream(stream, size, selected, allocator=None, progress=lambda _: None)。先读取固定头和逐通道头；根据通道标签解码样本、符号扩展、标定至 µV，并计数数字削顶。 定义到这里时不执行函数体。 |
| 10 | `     """Read only selected channels from continuous 24-bit BDF, in microvolts.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 11 | `     h = stream.read(256) ` | 把结果保存到 h：从文件流读取字节；参数：256。 |
| 12 | `     if len(h) != 256 or h[0] != 255: ` | 检查条件 len(h) != 256 or h[0] != 255；为真时执行下面缩进的一组语句。 |
| 13 | `         raise ValueError("Expected a 24-bit BDF file") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Expected a 24-bit BDF file'；上层可捕获并显示原因。 |
| 14 | `     if b"BDF+D" in h[192:236]: ` | 检查条件 b'BDF+D' in h[192:236]；为真时执行下面缩进的一组语句。 |
| 15 | `         raise ValueError("Discontinuous BDF+D is unsupported; do not concatenate its segments") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Discontinuous BDF+D is unsupported; do not concatenate its segments'；上层可捕获并显示原因。 |
| 16 | `     nc, hb = int(h[252:256]), int(h[184:192]) ` | 把结果保存到 (nc, hb)：组装元组：(int(h[252:256]), int(h[184:192]))。 |
| 17 | `     nr, duration = int(h[236:244]), float(h[244:252]) ` | 把结果保存到 (nr, duration)：组装元组：(int(h[236:244]), float(h[244:252]))。 |
| 18 | `     if nc < 1 or hb != 256 * (nc + 1) or duration <= 0: ` | 检查条件 nc < 1 or hb != 256 * (nc + 1) or duration <= 0；为真时执行下面缩进的一组语句。 |
| 19 | `         raise ValueError("Invalid BDF header") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Invalid BDF header'；上层可捕获并显示原因。 |
| 20 | `     fields = [] ` | 把结果保存到 fields：组装列表：[]。 |
| 21 | `     for width in (16, 80, 8, 8, 8, 8, 8, 80, 8, 32): ` | 遍历 (16, 80, 8, 8, 8, 8, 8, 80, 8, 32)，每次把一项赋给 width，执行下面缩进的循环体。 |
| 22 | `         b = stream.read(width * nc) ` | 把结果保存到 b：从文件流读取字节；参数：width * nc。 |
| 23 | `         if len(b) != width * nc: ` | 检查条件 len(b) != width * nc；为真时执行下面缩进的一组语句。 |
| 24 | `             raise ValueError("Truncated BDF channel header") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Truncated BDF channel header'；上层可捕获并显示原因。 |
| 25 | `         fields.append([b[j*width:(j+1)*width].decode("latin1").strip() for j in range(nc)]) ` | 把一项加入列表末尾；参数：[b[j * width:(j + 1) * width].decode('latin1').strip() for j in range(nc)]。 |
| 26 | `     ns = np.array(fields[8], dtype=int) ` | 把结果保存到 ns：构造 NumPy 数组；参数：fields[8], dtype=int。 |
| 27 | `     if np.any(ns <= 0): ` | 检查条件 np.any(ns <= 0)；为真时执行下面缩进的一组语句。 |
| 28 | `         raise ValueError("Invalid samples per record") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Invalid samples per record'；上层可捕获并显示原因。 |
| 29 | `     indices = [] ` | 把结果保存到 indices：组装列表：[]。 |
| 30 | `     for label in selected: ` | 遍历 selected，每次把一项赋给 label，执行下面缩进的循环体。 |
| 31 | `         if fields[0].count(label) != 1: ` | 检查条件 fields[0].count(label) != 1；为真时执行下面缩进的一组语句。 |
| 32 | `             raise ValueError(f"Missing or ambiguous channel: {label}") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'Missing or ambiguous channel: {label}'；上层可捕获并显示原因。 |
| 33 | `         indices.append(fields[0].index(label)) ` | 把一项加入列表末尾；参数：fields[0].index(label)。 |
| 34 | `     if len(set(ns[indices])) != 1: ` | 检查条件 len(set(ns[indices])) != 1；为真时执行下面缩进的一组语句。 |
| 35 | `         raise ValueError("Selected channels have different sampling rates") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Selected channels have different sampling rates'；上层可捕获并显示原因。 |
| 36 | `     actual, remainder = divmod(size - hb, int(3 * ns.sum())) ` | 把结果保存到 (actual, remainder)：调用 divmod；参数：size - hb, int(3 * ns.sum())。 |
| 37 | `     if actual <= 0 or remainder or nr not in (-1, actual): ` | 检查条件 actual <= 0 or remainder or nr not in (-1, actual)；为真时执行下面缩进的一组语句。 |
| 38 | `         raise ValueError("Truncated file or BDF record count mismatch") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Truncated file or BDF record count mismatch'；上层可捕获并显示原因。 |
| 39 | `     n = int(actual * ns[indices[0]]) ` | 把结果保存到 n：转换为整数；参数：actual * ns[indices[0]]。 |
| 40 | `     if allocator is None and n * len(indices) > 80_000_000: ` | 检查条件 allocator is None and n * len(indices) > 80000000；为真时执行下面缩进的一组语句。 |
| 41 | `         raise ValueError("Selected data exceed in-memory read limit; use BdfReader.open_data for disk-backed analysis") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Selected data exceed in-memory read limit; use BdfReader.open_data for disk-backed analysis'；上层可捕获并显示原因。 |
| 42 | `     x = allocator((n, len(indices))) if allocator else np.empty((n, len(indices)), dtype=float, order='F') ` | 把结果保存到 x：若 allocator，用 allocator((n, len(indices)))；否则用 np.empty((n, len(indices)), dtype=float, order='F')。 |
| 43 | `     offsets = np.r_[0, np.cumsum(ns)] * 3 ` | 把结果保存到 offsets：np.r_[0, np.cumsum(ns)] 与 3 相乘。 |
| 44 | `     calibrations = [] ` | 把结果保存到 calibrations：组装列表：[]。 |
| 45 | `     for i in indices: ` | 遍历 indices，每次把一项赋给 i，执行下面缩进的循环体。 |
| 46 | `         unit = fields[2][i] ` | 把结果保存到 unit：按索引/键 i 取 fields[2] 的内容。 |
| 47 | `         factor = {"uV": 1., "µV": 1., "mV": 1000., "V": 1e6}.get(unit) ` | 把结果保存到 factor：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：unit。 |
| 48 | `         if factor is None: ` | 检查条件 factor is None；为真时执行下面缩进的一组语句。 |
| 49 | `             raise ValueError(f"Unsupported BDF physical unit: {unit!r}") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'Unsupported BDF physical unit: {unit!r}'；上层可捕获并显示原因。 |
| 50 | `         p0, p1, d0, d1 = (float(fields[k][i]) for k in (3, 4, 5, 6)) ` | 把结果保存到 (p0, p1, d0, d1)：从 (3, 4, 5, 6) 逐个取 k，为每项生成 float(fields[k][i])。 |
| 51 | `         if not all(math.isfinite(v) for v in (p0, p1, d0, d1)) or p1 <= p0 or d1 <= d0: ` | 检查条件 not all((math.isfinite(v) for v in (p0, p1, d0, d1))) or p1 <= p0 or d1 <= d0；为真时执行下面缩进的一组语句。 |
| 52 | `             raise ValueError("Invalid BDF calibration") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Invalid BDF calibration'；上层可捕获并显示原因。 |
| 53 | `         calibrations.append((p0, p1, d0, d1, factor)) ` | 把一项加入列表末尾；参数：(p0, p1, d0, d1, factor)。 |
| 54 | `     clipped = np.zeros(len(indices), dtype=int) ` | 把结果保存到 clipped：创建全零数组；参数：len(indices), dtype=int。 |
| 55 | `     for rec in range(actual): ` | 遍历 range(actual)，每次把一项赋给 rec，执行下面缩进的循环体。 |
| 56 | `         if rec % max(1, actual//20) == 0: ` | 检查条件 rec % max(1, actual // 20) == 0；为真时执行下面缩进的一组语句。 |
| 57 | `             progress(f"Decoding BDF record {rec+1}/{actual}" + (" using disk cache" if isinstance(x, np.memmap) else "")) ` | 调用 progress；参数：f'Decoding BDF record {rec + 1}/{actual}' + (' using disk cache' if isinstance(x, np.memmap) else '')。 |
| 58 | `         buf = stream.read(int(offsets[-1])) ` | 把结果保存到 buf：从文件流读取字节；参数：int(offsets[-1])。 |
| 59 | `         if len(buf) != offsets[-1]: ` | 检查条件 len(buf) != offsets[-1]；为真时执行下面缩进的一组语句。 |
| 60 | `             raise ValueError("Incomplete BDF data record") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Incomplete BDF data record'；上层可捕获并显示原因。 |
| 61 | `         for j, i in enumerate(indices): ` | 遍历 enumerate(indices)，每次把一项赋给 (j, i)，执行下面缩进的循环体。 |
| 62 | `             b = np.frombuffer(buf[int(offsets[i]):int(offsets[i+1])], dtype=np.uint8).reshape(-1, 3).astype(np.int32) ` | 把结果保存到 b：转换数组元素类型；参数：np.int32。 |
| 63 | `             d = b[:, 0] \| (b[:, 1] << 8) \| (b[:, 2] << 16) ` | 三个小端字节按 0、8、16 位移后按位或，拼出每个 24 位样本。 |
| 64 | `             d = np.where(d >= 2**23, d - 2**24, d) ` | 若 24 位最高位是 1，就减去 2²⁴，恢复二进制补码表示的负数。 |
| 65 | `             p0, p1, d0, d1, factor = calibrations[j] ` | 把结果保存到 (p0, p1, d0, d1, factor)：按索引/键 j 取 calibrations 的内容。 |
| 66 | `             x[rec*ns[i]:(rec+1)*ns[i], j] = ((d-d0)*(p1-p0)/(d1-d0)+p0)*factor ` | 把数字 ADC 编码按头内量程线性标定为物理电压，再统一转成 µV，放入对应记录和所选通道列。 |
| 67 | `             clipped[j] += np.count_nonzero((d <= d0) \| (d >= d1)) ` | 把 clipped[j] 的原值加上 np.count_nonzero((d <= d0) &#124; (d >= d1))，再写回同一变量。 |
| 68 | `     return x, float(ns[indices[0]] / duration), { ` | 结束当前函数并返回：组装元组：(x, float(ns[indices[0]] / duration), {'duration_s': actual * duration, 'clipped_samples_full_record': dict(zip(selected, clipped.tolist())), 'physical_limits_u…（完整表达式见左栏）。 |
| 69 | `         "duration_s": actual * duration, ` | 接续第 68 行的同一条语句，不是另起一段算法。 结束当前函数并返回：组装元组：(x, float(ns[indices[0]] / duration), {'duration_s': actual * duration, 'clipped_samples_full_record': dict(zip(selected, clipped.tolist())), 'physical_limits_u…（完整表达式见左栏）。 |
| 70 | `         "clipped_samples_full_record": dict(zip(selected, clipped.tolist())), ` | 接续第 68 行的同一条语句，不是另起一段算法。 组装键值字典；参数：zip(selected, clipped.tolist())。 |
| 71 | `         "physical_limits_uV": {label: [cal[0]*cal[4], cal[1]*cal[4]] for label, cal in zip(selected, calibrations)}, ` | 接续第 68 行的同一条语句，不是另起一段算法。 按位置配对多个序列；参数：selected, calibrations。 |
| 72 | `     } ` | 接续第 68 行的同一条语句，不是另起一段算法。 结束当前函数并返回：组装元组：(x, float(ns[indices[0]] / duration), {'duration_s': actual * duration, 'clipped_samples_full_record': dict(zip(selected, clipped.tolist())), 'physical_limits_u…（完整表达式见左栏）。 |
| 73 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 74 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 75 | ` def sine_design(t, f): ` | 定义 sine_design(t, f)。构造四列设计矩阵：sin、cos、常数 1、中心化时间；用来分开基频、DC 和线性漂移。 定义到这里时不执行函数体。 |
| 76 | `     return np.column_stack((np.sin(2*np.pi*f*t), np.cos(2*np.pi*f*t), ` | 结束当前函数并返回：把一维列并排组成二维矩阵；参数：(np.sin(2 * np.pi * f * t), np.cos(2 * np.pi * f * t), np.ones(len(t)), t - t.mean())。 |
| 77 | `                             np.ones(len(t)), t-t.mean())) ` | 接续第 76 行的同一条语句，不是另起一段算法。 创建全一数组；参数：len(t)。 |
| 78 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 79 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 80 | ` def fit_record(x, fs, frequency, settings, coefficients_out=None, progress=lambda _: None): ` | 定义 fit_record(x, fs, frequency, settings, coefficients_out=None, progress=lambda _: None)。用各通道中位波形找共同频率，再保留原采样率逐通道拟合，返回物理幅度和质量门控理由。 定义到这里时不执行函数体。 |
| 81 | `     """Common frequency, then native-rate fits one electrode at a time. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 82 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 83 | `     Frequency search uses the same median-channel trace and time samples as ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 84 | `     before, without materializing an N-sample by C-channel temporary matrix. ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 85 | `     """ ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 86 | `     if x.ndim != 2 or len(x) < 16: ` | 检查条件 x.ndim != 2 or len(x) < 16；为真时执行下面缩进的一组语句。 |
| 87 | `         raise ValueError("Too few samples or nonfinite data") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Too few samples or nonfinite data'；上层可捕获并显示原因。 |
| 88 | `     if not 0 < frequency < fs / 4: ` | 检查条件 not 0 < frequency < fs / 4；为真时执行下面缩进的一组语句。 |
| 89 | `         raise ValueError("Need at least four samples per nominal sine cycle") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Need at least four samples per nominal sine cycle'；上层可捕获并显示原因。 |
| 90 | `     t = np.arange(len(x)) / fs ` | 把结果保存到 t：np.arange(len(x)) 与 fs 相除。 |
| 91 | `     step = max(1, len(t) // 4000) ` | 把结果保存到 step：取最大值；参数：1, len(t) // 4000。 |
| 92 | `     ts = t[::step] ` | 把结果保存到 ts：按索引/键 ::step 取 t 的内容；切片包含起点、不包含终点。 |
| 93 | `     probe = np.empty((len(ts), x.shape[1])) ` | 把结果保存到 probe：分配尚未填值的数组；参数：(len(ts), x.shape[1])。 |
| 94 | `     for i in range(x.shape[1]): ` | 遍历 range(x.shape[1])，每次把一项赋给 i，执行下面缩进的循环体。 |
| 95 | `         y = np.asarray(x[:, i]) ` | 把结果保存到 y：转换或视为 NumPy 数组；参数：x[:, i]。 |
| 96 | `         if not np.isfinite(y).all(): ` | 检查条件 not np.isfinite(y).all()；为真时执行下面缩进的一组语句。 |
| 97 | `             raise ValueError("Too few samples or nonfinite data") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Too few samples or nonfinite data'；上层可捕获并显示原因。 |
| 98 | `         probe[:, i] = y[::step] - np.median(y) ` | 把结果保存到 probe[:, i]：y[::step] 与 np.median(y) 相减。 |
| 99 | `     ys = np.median(probe, axis=1) ` | 把结果保存到 ys：计算中位数；参数：probe, axis=1。 |
| 100 | `     del probe ` | 删除变量引用 probe，便于释放临时内存；不是删除原始数据文件。 |
| 101 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 102 | `     def objective(f): ` | 定义 objective(f)。计算给定频率的正弦拟合均方残差，供优化器最小化。 定义到这里时不执行函数体。 |
| 103 | `         b = sine_design(ts, f) ` | 把结果保存到 b：调用 sine_design；参数：ts, f。 |
| 104 | `         return float(np.mean((ys-b @ np.linalg.lstsq(b, ys, rcond=None)[0])**2)) ` | 结束当前函数并返回：转换为浮点数；参数：np.mean((ys - b @ np.linalg.lstsq(b, ys, rcond=None)[0]) ** 2)。 |
| 105 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 106 | `     margin = settings["frequency_search_pct"] / 100 ` | 把结果保存到 margin：settings['frequency_search_pct'] 与 100 相除。 |
| 107 | `     grid = np.linspace(frequency*(1-margin), frequency*(1+margin), 31) ` | 把结果保存到 grid：生成包含两端的等间隔数值；参数：frequency * (1 - margin), frequency * (1 + margin), 31。 |
| 108 | `     best = int(np.argmin([objective(f) for f in grid])) ` | 把结果保存到 best：转换为整数；参数：np.argmin([objective(f) for f in grid])。 |
| 109 | `     lo, hi = grid[max(0, best-1)], grid[min(len(grid)-1, best+1)] ` | 把结果保存到 (lo, hi)：组装元组：(grid[max(0, best - 1)], grid[min(len(grid) - 1, best + 1)])。 |
| 110 | `     f = float(minimize_scalar(objective, bounds=(lo, hi), method="bounded", ` | 把结果保存到 f：转换为浮点数；参数：minimize_scalar(objective, bounds=(lo, hi), method='bounded', options={'xatol': 1e-10}).x。 |
| 111 | `                               options={"xatol": 1e-10}).x) ` | 接续第 110 行的同一条语句，不是另起一段算法。 把结果保存到 f：转换为浮点数；参数：minimize_scalar(objective, bounds=(lo, hi), method='bounded', options={'xatol': 1e-10}).x。 |
| 112 | `     b = sine_design(t, f) ` | 把结果保存到 b：调用 sine_design；参数：t, f。 |
| 113 | `     inverse = np.linalg.pinv(b)  # One shared SVD, not one factorization per channel. ` | 对共用设计矩阵只算一次伪逆，随后每通道可复用，减少重复矩阵分解。 |
| 114 | `     result = [] ` | 把结果保存到 result：组装列表：[]。 |
| 115 | `     for i in range(x.shape[1]): ` | 遍历 range(x.shape[1])，每次把一项赋给 i，执行下面缩进的循环体。 |
| 116 | `         progress(f"Fitting native samples: channel {i+1}/{x.shape[1]}") ` | 调用 progress；参数：f'Fitting native samples: channel {i + 1}/{x.shape[1]}'。 |
| 117 | `         y = np.asarray(x[:, i]) ` | 把结果保存到 y：转换或视为 NumPy 数组；参数：x[:, i]。 |
| 118 | `         beta = inverse @ y ` | 矩阵乘法得到该通道的最小二乘系数：正弦、余弦、DC、线性漂移。 |
| 119 | `         if coefficients_out is not None: ` | 检查条件 coefficients_out is not None；为真时执行下面缩进的一组语句。 |
| 120 | `             coefficients_out.append(beta) ` | 把一项加入列表末尾；参数：beta。 |
| 121 | `         residual = y - b @ beta ` | 把结果保存到 residual：y 与 b @ beta 相减。 |
| 122 | `         amp = float(2*np.hypot(beta[0], beta[1])) ` | 正弦系数 a 与余弦系数 b 合成峰值 sqrt(a²+b²)，乘 2 得峰峰值；此时单位仍为 µV。 |
| 123 | `         rms = float(np.sqrt(np.mean(residual**2))) ` | 把结果保存到 rms：转换为浮点数；参数：np.sqrt(np.mean(residual ** 2))。 |
| 124 | `         reasons = [] ` | 把结果保存到 reasons：组装列表：[]。 |
| 125 | `         if len(x)/fs*frequency < settings["min_cycles"]: ` | 检查条件 len(x) / fs * frequency < settings['min_cycles']；为真时执行下面缩进的一组语句。 |
| 126 | `             reasons.append("too_few_cycles") ` | 把一项加入列表末尾；参数：'too_few_cycles'。 |
| 127 | `         if min(f-grid[0], grid[-1]-f) < frequency*margin*.01: ` | 检查条件 min(f - grid[0], grid[-1] - f) < frequency * margin * 0.01；为真时执行下面缩进的一组语句。 |
| 128 | `             reasons.append("frequency_at_search_boundary") ` | 把一项加入列表末尾；参数：'frequency_at_search_boundary'。 |
| 129 | `         ratio, jump = None, None ` | 把结果保存到 (ratio, jump)：组装元组：(None, None)。 |
| 130 | `         if amp < settings["min_response_uVpp"]: ` | 检查条件 amp < settings['min_response_uVpp']；为真时执行下面缩进的一组语句。 |
| 131 | `             reasons.append("no_reliable_sine_response") ` | 把一项加入列表末尾；参数：'no_reliable_sine_response'。 |
| 132 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 133 | `             ratio = float(100*rms/(amp/(2*np.sqrt(2)))) ` | 把拟合残差 RMS 除以基频 RMS；Vpp/(2√2) 是正弦 RMS。这个残差可能同时含噪声和谐波。 |
| 134 | `             jump = float(100*np.max(np.abs(np.diff(residual)))/amp) ` | 最大相邻残差差值除以峰峰值，检查正弦模型以外的突然跳变。 |
| 135 | `             if ratio > settings["max_residual_pct"]: ` | 检查条件 ratio > settings['max_residual_pct']；为真时执行下面缩进的一组语句。 |
| 136 | `                 reasons.append("large_sine_fit_residual") ` | 把一项加入列表末尾；参数：'large_sine_fit_residual'。 |
| 137 | `             if jump > settings["max_residual_step_pct"]: ` | 检查条件 jump > settings['max_residual_step_pct']；为真时执行下面缩进的一组语句。 |
| 138 | `                 reasons.append("abrupt_residual_step") ` | 把一项加入列表末尾；参数：'abrupt_residual_step'。 |
| 139 | `         result.append(dict(amplitude_pp_mV=amp/1000, fitted_frequency_hz=f, ` | 把一项加入列表末尾；参数：dict(amplitude_pp_mV=amp / 1000, fitted_frequency_hz=f, residual_rms_uV=rms, residual_pct=ratio, residual_step_pct=jump, quality_reasons=reasons)。 |
| 140 | `                            residual_rms_uV=rms, residual_pct=ratio, ` | 接续第 139 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(amplitude_pp_mV=amp / 1000, fitted_frequency_hz=f, residual_rms_uV=rms, residual_pct=ratio, residual_step_pct=jump, quality_reasons=reasons)。 |
| 141 | `                            residual_step_pct=jump, quality_reasons=reasons)) ` | 接续第 139 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(amplitude_pp_mV=amp / 1000, fitted_frequency_hz=f, residual_rms_uV=rms, residual_pct=ratio, residual_step_pct=jump, quality_reasons=reasons)。 |
| 142 | `     return result ` | 结束当前函数并返回：result。 |
