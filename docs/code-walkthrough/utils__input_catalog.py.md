# utils/input_catalog.py：建立文件清单

枚举 BDF 或 ZIP 中的 BDF；从名称猜测波形、频率、幅度，但默认 input_confirmed=False。

源码：[utils/input_catalog.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/input_catalog.py>)。本说明对应 32 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `records_from_paths` | [9–32](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/input_catalog.py:9>) | 逐个路径枚举 BDF 成员，从名称提取候选设置，确认文件可读后组成 InputRecord 清单。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Read BDF/ZIP catalogs without extracting or modifying the original files.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 3 | ` import re ` | 导入模块 re。从名称解析频率/幅度并筛选通道 |
| 4 | ` import zipfile ` | 导入模块 zipfile。只读原始 ZIP 成员或写测试 ZIP |
| 5 | ` from models import InputRecord ` | 从 models 导入 InputRecord。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 6 | ` from utils.bdf_reader import BdfReader ` | 从 utils.bdf_reader 导入 BdfReader。检查头信息、真实通道及长度，支持 ZIP 内部成员，并通过上下文管理大数组的生命周期。 |
| 7 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 8 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 9 | ` def records_from_paths(paths): ` | 定义 records_from_paths(paths)。逐个路径枚举 BDF 成员，从名称提取候选设置，确认文件可读后组成 InputRecord 清单。 定义到这里时不执行函数体。 |
| 10 | `     records = [] ` | 把结果保存到 records：组装列表：[]。 |
| 11 | `     for path in map(Path, paths): ` | 遍历 map(Path, paths)，每次把一项赋给 path，执行下面缩进的循环体。 |
| 12 | `         if path.suffix.lower() == ".zip": ` | 检查条件 path.suffix.lower() == '.zip'；为真时执行下面缩进的一组语句。 |
| 13 | `             with zipfile.ZipFile(path) as archive: ` | 进入资源上下文：调用 zipfile.ZipFile；参数：path，对象命名为 archive。退出时执行对应清理。 |
| 14 | `                 members = sorted(n for n in archive.namelist() if n.lower().endswith(".bdf")) ` | 把结果保存到 members：排序；参数：(n for n in archive.namelist() if n.lower().endswith('.bdf'))。 |
| 15 | `             if not members: ` | 检查条件 not members；为真时执行下面缩进的一组语句。 |
| 16 | `                 raise ValueError(f"No BDF files in {path.name}") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'No BDF files in {path.name}'；上层可捕获并显示原因。 |
| 17 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 18 | `             members = [None] ` | 把结果保存到 members：组装列表：[None]。 |
| 19 | `         for member in members: ` | 遍历 members，每次把一项赋给 member，执行下面缩进的循环体。 |
| 20 | `             name = Path(member or path.name) ` | 把结果保存到 name：构造路径对象；参数：member or path.name。 |
| 21 | `             context = (str(path) + " " + str(member or "")).lower() ` | 把结果保存到 context：转为小写后比较。 |
| 22 | `             waveform = "ecg" if "ecg" in context else "pulse" if "pulse" in context else "sine" if "sine" in context else "unknown" ` | 把结果保存到 waveform：若 'ecg' in context，用 'ecg'；否则用 'pulse' if 'pulse' in context else 'sine' if 'sine' in context else 'unknown'。 |
| 23 | `             frequency = re.search(r"([\d.]+)hz", name.stem, re.I) ` | 把结果保存到 frequency：调用 re.search；参数：'([\\d.]+)hz', name.stem, re.I。 |
| 24 | `             amplitude = re.search(r"([\d.]+)mv", name.stem, re.I) ` | 把结果保存到 amplitude：调用 re.search；参数：'([\\d.]+)mv', name.stem, re.I。 |
| 25 | `             group = name.parent.name if member else path.parent.name ` | 把结果保存到 group：若 member，用 name.parent.name；否则用 path.parent.name。 |
| 26 | `             r = InputRecord(id=f"{name.stem}-{len(records)+1}", path=str(path.resolve()), member=member, ` | 把结果保存到 r：创建一份文件及其输入条件记录；参数：id=f'{name.stem}-{len(records) + 1}', path=str(path.resolve()), member=member, frequency_hz=float(frequency[1]) if frequency else 5.0, input_mVpp…（完整表达式见左栏）。 |
| 27 | `                 frequency_hz=float(frequency[1]) if frequency else 5., ` | 接续第 26 行的同一条语句，不是另起一段算法。 转换为浮点数；参数：frequency[1]。 |
| 28 | `                 input_mVpp=float(amplitude[1]) if amplitude else None, ` | 接续第 26 行的同一条语句，不是另起一段算法。 转换为浮点数；参数：amplitude[1]。 |
| 29 | `                 input_confirmed=False, waveform=waveform, setup_group=group or "default") ` | 接续第 26 行的同一条语句，不是另起一段算法。 把结果保存到 r：创建一份文件及其输入条件记录；参数：id=f'{name.stem}-{len(records) + 1}', path=str(path.resolve()), member=member, frequency_hz=float(frequency[1]) if frequency else 5.0, input_mVpp…（完整表达式见左栏）。 |
| 30 | `             BdfReader().inspect(r) ` | 只读头信息，核对格式/长度，返回通道名、采样率、时长，过滤 Status/Annotations。；参数：r。 |
| 31 | `             records.append(r) ` | 把一项加入列表末尾；参数：r。 |
| 32 | `     return records ` | 结束当前函数并返回：records。 |
