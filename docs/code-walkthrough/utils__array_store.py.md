# utils/array_store.py：大文件内存管理

小数组放内存，大于阈值的数组用临时磁盘映射；正常退出或异常退出都尝试清理本次缓存。

源码：[utils/array_store.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/array_store.py>)。本说明对应 59 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [11–15](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/array_store.py:11>) | 保存缓存根路径和内存阈值，尚不创建数据文件。 |
| `__enter__` | [17–18](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/array_store.py:17>) | 进入 with 时把存储器自身交给 as 后的变量。 |
| `empty` | [20–39](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/array_store.py:20>) | 按数组大小选择内存或磁盘映射，先检查空间，再使用独立 UUID 目录保存缓存。 |
| `__exit__` | [41–59](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/array_store.py:41>) | 关闭磁盘映射并删除本次缓存；清理失败只警告，不覆盖分析本身的结果或异常。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Per-analysis scratch arrays: small arrays in RAM, large arrays on disk.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 3 | ` import shutil ` | 导入模块 shutil。磁盘空间检查和测试缓存清理 |
| 4 | ` import tempfile ` | 导入模块 tempfile。取得系统临时目录 |
| 5 | ` import uuid ` | 导入模块 uuid。生成本次缓存/测试目录的唯一名称 |
| 6 | ` import warnings ` | 导入模块 warnings。发出不终止结果交付的清理提醒 |
| 7 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 8 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 9 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 10 | ` class ArrayStore: ` | 定义 ArrayStore 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 11 | `     def __init__(self, root=None, max_memory_bytes=64 * 1024**2): ` | 定义 __init__(self, root=None, max_memory_bytes=64 * 1024 ** 2)。保存缓存根路径和内存阈值，尚不创建数据文件。 定义到这里时不执行函数体。 |
| 12 | `         self.root = Path(root) if root else Path(tempfile.gettempdir())/'electrode-qa-cache' ` | 把结果保存到 self.root：若 root，用 Path(root)；否则用 Path(tempfile.gettempdir()) / 'electrode-qa-cache'。 |
| 13 | `         self.max_memory_bytes = max_memory_bytes ` | 把结果保存到 self.max_memory_bytes：max_memory_bytes。 |
| 14 | `         self.folder = None ` | 把结果保存到 self.folder：None（未知/未设置）。 |
| 15 | `         self.arrays = [] ` | 把结果保存到 self.arrays：组装列表：[]。 |
| 16 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 17 | `     def __enter__(self): ` | 定义 __enter__(self)。进入 with 时把存储器自身交给 as 后的变量。 定义到这里时不执行函数体。 |
| 18 | `         return self ` | 结束当前函数并返回：self。 |
| 19 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 20 | `     def empty(self, shape): ` | 定义 empty(self, shape)。按数组大小选择内存或磁盘映射，先检查空间，再使用独立 UUID 目录保存缓存。 定义到这里时不执行函数体。 |
| 21 | `         size = int(np.prod(shape)) * np.dtype('float64').itemsize ` | 把结果保存到 size：int(np.prod(shape)) 与 np.dtype('float64').itemsize 相乘。 |
| 22 | `         if size <= self.max_memory_bytes: ` | 检查条件 size <= self.max_memory_bytes；为真时执行下面缩进的一组语句。 |
| 23 | `             return np.empty(shape, dtype='float64', order='F') ` | 结束当前函数并返回：分配尚未填值的数组；参数：shape, dtype='float64', order='F'。 |
| 24 | `         self.root.mkdir(parents=True, exist_ok=True) ` | 创建目录；参数：parents=True, exist_ok=True。 |
| 25 | `         if shutil.disk_usage(self.root).free < size + 256 * 1024**2: ` | 检查条件 shutil.disk_usage(self.root).free < size + 256 * 1024 ** 2；为真时执行下面缩进的一组语句。 |
| 26 | `             raise ValueError(f'Insufficient disk space for temporary BDF cache: need about {size/1024**3:.2f} GiB plus 256 MiB free') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'Insufficient disk space for temporary BDF cache: need about {size / 1024 ** 3:.2f} GiB plus 256 MiB free'；上层可捕获并显示原因。 |
| 27 | `         if self.folder is None: ` | 检查条件 self.folder is None；为真时执行下面缩进的一组语句。 |
| 28 | `             self.folder = self.root/uuid.uuid4().hex ` | 把结果保存到 self.folder：self.root 与 uuid.uuid4().hex 相除。 |
| 29 | `             self.folder.mkdir() ` | 创建目录。 |
| 30 | `         path = self.folder/f'{len(self.arrays)}.float64' ` | 把结果保存到 path：self.folder 与 f'{len(self.arrays)}.float64' 相除。 |
| 31 | `         # Columns are contiguous: each electrode can be fitted without reading ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 32 | `         # every other channel's disk pages again. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 33 | `         try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 34 | `             array = np.memmap(path, mode='w+', dtype='float64', shape=shape, order='F') ` | 把结果保存到 array：创建磁盘映射数组；参数：path, mode='w+', dtype='float64', shape=shape, order='F'。 |
| 35 | `         except Exception: ` | 捕获 Exception 异常，执行错误处理。 |
| 36 | `             path.unlink(missing_ok=True) ` | 删除指定临时/输出文件；参数：missing_ok=True。 |
| 37 | `             raise ` | 抛出异常并停止当前正常流程：None（没有值）；上层可捕获并显示原因。 |
| 38 | `         self.arrays.append((array, path)) ` | 把一项加入列表末尾；参数：(array, path)。 |
| 39 | `         return array ` | 结束当前函数并返回：array。 |
| 40 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 41 | `     def __exit__(self, exc_type, exc, traceback): ` | 定义 __exit__(self, exc_type, exc, traceback)。关闭磁盘映射并删除本次缓存；清理失败只警告，不覆盖分析本身的结果或异常。 定义到这里时不执行函数体。 |
| 42 | `         notices = [] ` | 把结果保存到 notices：组装列表：[]。 |
| 43 | `         for array, path in self.arrays: ` | 遍历 self.arrays，每次把一项赋给 (array, path)，执行下面缩进的循环体。 |
| 44 | `             array._mmap.close() ` | 关闭资源或窗口。 |
| 45 | `             try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 46 | `                 path.unlink() ` | 删除指定临时/输出文件。 |
| 47 | `             except OSError as error: ` | 捕获 OSError 异常，保存到 error，执行错误处理。 |
| 48 | `                 notices.append(f'{path}: {error}') ` | 把一项加入列表末尾；参数：f'{path}: {error}'。 |
| 49 | `         self.arrays.clear() ` | 清空容器，或调用该视图定义的清除方法。 |
| 50 | `         if self.folder is not None: ` | 检查条件 self.folder is not None；为真时执行下面缩进的一组语句。 |
| 51 | `             try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 52 | `                 self.folder.rmdir()  # Only our own now-empty UUID directory. ` | 只删除本次分析创建且已经清空的 UUID 临时目录；不是删除原始记录或整个缓存根目录。 |
| 53 | `             except OSError as error: ` | 捕获 OSError 异常，保存到 error，执行错误处理。 |
| 54 | `                 notices.append(f'{self.folder}: {error}') ` | 把一项加入列表末尾；参数：f'{self.folder}: {error}'。 |
| 55 | `         # A sync service / antivirus lock must not discard completed metrics or ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 56 | `         # replace the original analysis exception with a cleanup exception. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 57 | `         if notices: ` | 检查条件 notices；为真时执行下面缩进的一组语句。 |
| 58 | `             warnings.warn('Temporary BDF cache cleanup incomplete: ' + '; '.join(notices), RuntimeWarning) ` | 调用 warnings.warn；参数：'Temporary BDF cache cleanup incomplete: ' + '; '.join(notices), RuntimeWarning。 |
| 59 | `         return False ` | 在普通函数中返回布尔 False；若属于 __exit__，表示不吞掉原有异常，清理后让其继续向上传递。 |
