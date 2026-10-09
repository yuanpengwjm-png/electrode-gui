# utils/bdf_reader.py：BDF 读取入口

检查头信息、真实通道及长度，支持 ZIP 内部成员，并通过上下文管理大数组的生命周期。

源码：[utils/bdf_reader.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/bdf_reader.py>)。本说明对应 90 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [22–24](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/bdf_reader.py:22>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `_open` | [27–36](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/bdf_reader.py:27>) | 统一普通文件和 ZIP 内部成员的只读流；yield 后由 with 自动关闭。 |
| `inspect` | [38–62](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/bdf_reader.py:38>) | 只读头信息，核对格式/长度，返回通道名、采样率、时长，过滤 Status/Annotations。 |
| `read` | [64–68](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/bdf_reader.py:64>) | 简单的内存读取接口；大文件建议走 open_data。 |
| `open_data` | [71–78](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/bdf_reader.py:71>) | 创建可清理的数组存储，解码完成后 yield 数据，退出 with 时释放缓存。 |
| `choose_channels` | [81–90](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/bdf_reader.py:81>) | 从实际电压通道按 EXG/scalp/all 分组选择前 count 个，数量不合法就报错。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Header discovery and calibrated 24-bit BDF reading, including ZIP members.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from contextlib import contextmanager ` | 从 contextlib 导入 contextmanager。管理 with 的进入/退出和资源清理 |
| 3 | ` from dataclasses import dataclass ` | 从 dataclasses 导入 dataclass。自动生成数据类并在数据类/字典之间转换 |
| 4 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 5 | ` import re ` | 导入模块 re。从名称解析频率/幅度并筛选通道 |
| 6 | ` import zipfile ` | 导入模块 zipfile。只读原始 ZIP 成员或写测试 ZIP |
| 7 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 8 | ` from models import InputRecord ` | 从 models 导入 InputRecord。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 9 | ` from utils.numerics import read_bdf_stream ` | 从 utils.numerics 导入 read_bdf_stream。按 BDF 头解码 24 位样本并换算 µV；用共同频率及逐通道最小二乘计算正弦幅度、基线和拟合残差。 |
| 10 | ` from utils.array_store import ArrayStore ` | 从 utils.array_store 导入 ArrayStore。小数组放内存，大于阈值的数组用临时磁盘映射；正常退出或异常退出都尝试清理本次缓存。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 13 | ` @dataclass ` | @dataclass 自动补充初始化等数据对象方法；frozen=True 时字段不能通常地重新赋值。 |
| 14 | ` class BdfInfo: ` | 定义 BdfInfo 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 15 | `     labels: list[str] ` | 声明 labels 的类型为 list[str]，用于保存 labels。构造对象时需要提供。 |
| 16 | `     voltage_labels: list[str] ` | 声明 voltage_labels 的类型为 list[str]，用于保存 voltage_labels。构造对象时需要提供。 |
| 17 | `     sample_rates: dict[str, float] ` | 声明 sample_rates 的类型为 dict[str, float]，用于保存 sample_rates。构造对象时需要提供。 |
| 18 | `     duration_s: float ` | 声明 duration_s 的类型为 float，用于本次实际保留并分析的时长（秒），可能短于原始记录。构造对象时需要提供。 |
| 19 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 20 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 21 | ` class BdfReader: ` | 定义 BdfReader 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 22 | `     def __init__(self, cache_root=None, max_memory_bytes=64 * 1024**2): ` | 定义 __init__(self, cache_root=None, max_memory_bytes=64 * 1024 ** 2)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 23 | `         self.cache_root = cache_root ` | 把结果保存到 self.cache_root：cache_root。 |
| 24 | `         self.max_memory_bytes = max_memory_bytes ` | 把结果保存到 self.max_memory_bytes：max_memory_bytes。 |
| 25 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 26 | `     @contextmanager ` | @contextmanager 将含 yield 的函数变为 with 可用的资源管理器。 |
| 27 | `     def _open(self, record): ` | 定义 _open(self, record)。统一普通文件和 ZIP 内部成员的只读流；yield 后由 with 自动关闭。 定义到这里时不执行函数体。 |
| 28 | `         path = Path(record.path) ` | 把结果保存到 path：构造路径对象；参数：record.path。 |
| 29 | `         if record.member: ` | 检查条件 record.member；为真时执行下面缩进的一组语句。 |
| 30 | `             with zipfile.ZipFile(path) as z: ` | 进入资源上下文：调用 zipfile.ZipFile；参数：path，对象命名为 z。退出时执行对应清理。 |
| 31 | `                 info = z.getinfo(record.member) ` | 把结果保存到 info：调用 z.getinfo；参数：record.member。 |
| 32 | `                 with z.open(info) as stream: ` | 进入资源上下文：打开文件或归档成员；参数：info，对象命名为 stream。退出时执行对应清理。 |
| 33 | `                     yield stream, info.file_size ` | 把 组装元组：(stream, info.file_size) 暂时交给调用者；上下文退出后继续执行清理。 |
| 34 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 35 | `             with path.open("rb") as stream: ` | 进入资源上下文：打开文件或归档成员；参数：'rb'，对象命名为 stream。退出时执行对应清理。 |
| 36 | `                 yield stream, path.stat().st_size ` | 把 组装元组：(stream, path.stat().st_size) 暂时交给调用者；上下文退出后继续执行清理。 |
| 37 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 38 | `     def inspect(self, record: InputRecord) -> BdfInfo: ` | 定义 inspect(self, record: InputRecord)。只读头信息，核对格式/长度，返回通道名、采样率、时长，过滤 Status/Annotations。 定义到这里时不执行函数体。 |
| 39 | `         with self._open(record) as (stream, size): ` | 进入资源上下文：统一普通文件和 ZIP 内部成员的只读流；yield 后由 with 自动关闭。；参数：record，对象命名为 (stream, size)。退出时执行对应清理。 |
| 40 | `             h = stream.read(256) ` | 把结果保存到 h：从文件流读取字节；参数：256。 |
| 41 | `             if len(h) != 256 or h[0] != 255 or b"BDF+D" in h[192:236]: ` | 检查条件 len(h) != 256 or h[0] != 255 or b'BDF+D' in h[192:236]；为真时执行下面缩进的一组语句。 |
| 42 | `                 raise ValueError("A continuous 24-bit BDF file is required; BDF+D is unsupported") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'A continuous 24-bit BDF file is required; BDF+D is unsupported'；上层可捕获并显示原因。 |
| 43 | `             nc, hb = int(h[252:256]), int(h[184:192]) ` | 把结果保存到 (nc, hb)：组装元组：(int(h[252:256]), int(h[184:192]))。 |
| 44 | `             nr, duration = int(h[236:244]), float(h[244:252]) ` | 把结果保存到 (nr, duration)：组装元组：(int(h[236:244]), float(h[244:252]))。 |
| 45 | `             if nc < 1 or nc > 4096 or hb != 256*(nc+1) or duration <= 0: ` | 检查条件 nc < 1 or nc > 4096 or hb != 256 * (nc + 1) or (duration <= 0)；为真时执行下面缩进的一组语句。 |
| 46 | `                 raise ValueError("Invalid BDF header") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Invalid BDF header'；上层可捕获并显示原因。 |
| 47 | `             fields = [] ` | 把结果保存到 fields：组装列表：[]。 |
| 48 | `             for width in (16, 80, 8, 8, 8, 8, 8, 80, 8, 32): ` | 遍历 (16, 80, 8, 8, 8, 8, 8, 80, 8, 32)，每次把一项赋给 width，执行下面缩进的循环体。 |
| 49 | `                 b = stream.read(width*nc) ` | 把结果保存到 b：从文件流读取字节；参数：width * nc。 |
| 50 | `                 if len(b) != width*nc: ` | 检查条件 len(b) != width * nc；为真时执行下面缩进的一组语句。 |
| 51 | `                     raise ValueError("Incomplete BDF header") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Incomplete BDF header'；上层可捕获并显示原因。 |
| 52 | `                 fields.append([b[i*width:(i+1)*width].decode("latin1").strip() for i in range(nc)]) ` | 把一项加入列表末尾；参数：[b[i * width:(i + 1) * width].decode('latin1').strip() for i in range(nc)]。 |
| 53 | `             samples = [int(s) for s in fields[8]] ` | 把结果保存到 samples：从 fields[8] 逐个取 s，为每项生成 int(s)。 |
| 54 | `             if any(s <= 0 for s in samples): ` | 检查条件 any((s <= 0 for s in samples))；为真时执行下面缩进的一组语句。 |
| 55 | `                 raise ValueError("Invalid BDF samples per record") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Invalid BDF samples per record'；上层可捕获并显示原因。 |
| 56 | `             actual, remainder = divmod(size-hb, 3*sum(samples)) ` | 把结果保存到 (actual, remainder)：调用 divmod；参数：size - hb, 3 * sum(samples)。 |
| 57 | `             if actual <= 0 or remainder or nr not in (-1, actual): ` | 检查条件 actual <= 0 or remainder or nr not in (-1, actual)；为真时执行下面缩进的一组语句。 |
| 58 | `                 raise ValueError("Incomplete BDF or record count mismatch") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Incomplete BDF or record count mismatch'；上层可捕获并显示原因。 |
| 59 | `             labels = fields[0] ` | 把结果保存到 labels：按索引/键 0 取 fields 的内容。 |
| 60 | `             voltage = [label for label, unit in zip(labels, fields[2]) ` | 把结果保存到 voltage：从 zip(labels, fields[2]) 逐个取 (label, unit)，仅保留 unit in ('uV', 'µV', 'mV', 'V') and (not re.search('status&#124;annotation', label, re.I))，为每项生成 label。 |
| 61 | `                        if unit in ("uV", "µV", "mV", "V") and not re.search(r"status\|annotation", label, re.I)] ` | 接续第 60 行的同一条语句，不是另起一段算法。 调用 re.search；参数：'status&#124;annotation', label, re.I。 |
| 62 | `             return BdfInfo(labels, voltage, dict(zip(labels, [s/duration for s in samples])), actual*duration) ` | 结束当前函数并返回：打包从文件头读到的元数据；参数：labels, voltage, dict(zip(labels, [s / duration for s in samples])), actual * duration。 |
| 63 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 64 | `     def read(self, record: InputRecord, channels: list[str]): ` | 定义 read(self, record: InputRecord, channels: list[str])。简单的内存读取接口；大文件建议走 open_data。 定义到这里时不执行函数体。 |
| 65 | `         if not channels or len(set(channels)) != len(channels): ` | 检查条件 not channels or len(set(channels)) != len(channels)；为真时执行下面缩进的一组语句。 |
| 66 | `             raise ValueError("Select unique electrode channels") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Select unique electrode channels'；上层可捕获并显示原因。 |
| 67 | `         with self._open(record) as (stream, size): ` | 进入资源上下文：统一普通文件和 ZIP 内部成员的只读流；yield 后由 with 自动关闭。；参数：record，对象命名为 (stream, size)。退出时执行对应清理。 |
| 68 | `             return read_bdf_stream(stream, size, channels) ` | 结束当前函数并返回：调用 read_bdf_stream；参数：stream, size, channels。 |
| 69 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 70 | `     @contextmanager ` | @contextmanager 将含 yield 的函数变为 with 可用的资源管理器。 |
| 71 | `     def open_data(self, record: InputRecord, channels: list[str], progress=lambda _: None): ` | 定义 open_data(self, record: InputRecord, channels: list[str], progress=lambda _: None)。创建可清理的数组存储，解码完成后 yield 数据，退出 with 时释放缓存。 定义到这里时不执行函数体。 |
| 72 | `         """Decode record by record; release scratch data even if analysis fails.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 73 | `         if not channels or len(set(channels)) != len(channels): ` | 检查条件 not channels or len(set(channels)) != len(channels)；为真时执行下面缩进的一组语句。 |
| 74 | `             raise ValueError('Select unique electrode channels') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Select unique electrode channels'；上层可捕获并显示原因。 |
| 75 | `         with ArrayStore(self.cache_root, self.max_memory_bytes) as store: ` | 进入资源上下文：调用 ArrayStore；参数：self.cache_root, self.max_memory_bytes，对象命名为 store。退出时执行对应清理。 |
| 76 | `             with self._open(record) as (stream, size): ` | 进入资源上下文：统一普通文件和 ZIP 内部成员的只读流；yield 后由 with 自动关闭。；参数：record，对象命名为 (stream, size)。退出时执行对应清理。 |
| 77 | `                 data = read_bdf_stream(stream, size, channels, allocator=store.empty, progress=progress) ` | 把结果保存到 data：调用 read_bdf_stream；参数：stream, size, channels, allocator=store.empty, progress=progress。 |
| 78 | `             yield data ` | 把 data 暂时交给调用者；上下文退出后继续执行清理。 |
| 79 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 80 | `     @staticmethod ` | @staticmethod 表示该方法不依赖 self，可直接通过类调用。 |
| 81 | `     def choose_channels(info: BdfInfo, count: int, pool="EXG"): ` | 定义 choose_channels(info: BdfInfo, count: int, pool='EXG')。从实际电压通道按 EXG/scalp/all 分组选择前 count 个，数量不合法就报错。 定义到这里时不执行函数体。 |
| 82 | `         if pool == "EXG": ` | 检查条件 pool == 'EXG'；为真时执行下面缩进的一组语句。 |
| 83 | `             names = [s for s in info.voltage_labels if re.fullmatch(r"EXG\d+", s, re.I)] ` | 把结果保存到 names：从 info.voltage_labels 逐个取 s，仅保留 re.fullmatch('EXG\\d+', s, re.I)，为每项生成 s。 |
| 84 | `         elif pool == "scalp": ` | 检查条件 pool == 'scalp'；为真时执行下面缩进的一组语句。 |
| 85 | `             names = [s for s in info.voltage_labels if not re.fullmatch(r"EXG\d+", s, re.I)] ` | 把结果保存到 names：从 info.voltage_labels 逐个取 s，仅保留 not re.fullmatch('EXG\\d+', s, re.I)，为每项生成 s。 |
| 86 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 87 | `             names = info.voltage_labels ` | 把结果保存到 names：读取 info 的 voltage_labels 属性。 |
| 88 | `         if count < 1 or count > len(names): ` | 检查条件 count < 1 or count > len(names)；为真时执行下面缩进的一组语句。 |
| 89 | `             raise ValueError(f"This channel group has {len(names)} voltage channels; cannot select {count} electrodes") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'This channel group has {len(names)} voltage channels; cannot select {count} electrodes'；上层可捕获并显示原因。 |
| 90 | `         return names[:count] ` | 结束当前函数并返回：按索引/键 :count 取 names 的内容；切片包含起点、不包含终点。 |
