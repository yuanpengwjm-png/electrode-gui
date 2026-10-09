# utils/project_io.py：项目保存和载入

保存文件清单、参数、通道和参考；恢复时适配部分旧配置，并统一幅度单位。保存的是配置，不是复制原始 BDF。

源码：[utils/project_io.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/project_io.py>)。本说明对应 51 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `load_project` | [12–44](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/project_io.py:12>) | 读取 JSON、兼容旧字段、解析相对路径、过滤允许的设置字段并校验。 |
| `save_project` | [47–51](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/project_io.py:47>) | 把记录和设置的数据类转成 JSON，保留通道、参考与可选布局信息。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """JSON projects and migration of the earlier electrode experiment config.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import asdict, fields ` | 从 dataclasses 导入 asdict、fields。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 4 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 5 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 6 | ` from config import AnalysisSettings ` | 从 config 导入 AnalysisSettings。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 7 | ` from models import InputRecord ` | 从 models 导入 InputRecord。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 8 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 9 | ` UNIT_FACTORS = {"mVpp":1., "mVpeak":2., "mVrms":2*math.sqrt(2), "uVpp":.001, "Vpp":1000.} ` | 把结果保存到 UNIT_FACTORS：组装字典，键用于给数值/设置命名：{'mVpp': 1.0, 'mVpeak': 2.0, 'mVrms': 2 * math.sqrt(2), 'uVpp': 0.001, 'Vpp': 1000.0}。 |
| 10 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | ` def load_project(path): ` | 定义 load_project(path)。读取 JSON、兼容旧字段、解析相对路径、过滤允许的设置字段并校验。 定义到这里时不执行函数体。 |
| 13 | `     path = Path(path).resolve() ` | 把结果保存到 path：解析绝对路径。 |
| 14 | `     data = json.loads(path.read_text(encoding="utf-8-sig")) ` | 把结果保存到 data：把 JSON 文本恢复为 Python 数据；参数：path.read_text(encoding='utf-8-sig')。 |
| 15 | `     if len({entry.get("group", "default") for entry in data["records"]}) > 1: ` | 检查条件 len({entry.get('group', 'default') for entry in data['records']}) > 1；为真时执行下面缩进的一组语句。 |
| 16 | `         raise ValueError("Load different wiring/experiment groups separately; do not pool them for linearity or repetition") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Load different wiring/experiment groups separately; do not pool them for linearity or repetition'；上层可捕获并显示原因。 |
| 17 | `     records = [] ` | 把结果保存到 records：组装列表：[]。 |
| 18 | `     valid = {f.name for f in fields(InputRecord)} ` | 把结果保存到 valid：从 fields(InputRecord) 逐个取 f，为每项生成 f.name。 |
| 19 | `     for entry in data["records"]: ` | 遍历 data['records']，每次把一项赋给 entry，执行下面缩进的循环体。 |
| 20 | `         if "input_amplitude" in entry:  # previous tool's config, without importing it ` | 检查条件 'input_amplitude' in entry；为真时执行下面缩进的一组语句。 |
| 21 | `             if entry.get("montage", "monopolar") != "monopolar" or "signals" in entry: ` | 检查条件 entry.get('montage', 'monopolar') != 'monopolar' or 'signals' in entry；为真时执行下面缩进的一组语句。 |
| 22 | `                 raise ValueError("This project contains differential paths; load individual monopolar electrode channels") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'This project contains differential paths; load individual monopolar electrode channels'；上层可捕获并显示原因。 |
| 23 | `             unit = entry.get("input_unit", "mVpp") ` | 把结果保存到 unit：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：'input_unit', 'mVpp'。 |
| 24 | `             if unit not in UNIT_FACTORS: ` | 检查条件 unit not in UNIT_FACTORS；为真时执行下面缩进的一组语句。 |
| 25 | `                 raise ValueError(f"Convert {unit} to mVpp before loading this project") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：f'Convert {unit} to mVpp before loading this project'；上层可捕获并显示原因。 |
| 26 | `             value = entry.get("input_amplitude") ` | 把结果保存到 value：读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：'input_amplitude'。 |
| 27 | `             entry = dict(id=entry["id"], path=entry["path"], member=entry.get("member"), frequency_hz=entry["frequency_hz"], ` | 把结果保存到 entry：组装键值字典；参数：id=entry['id'], path=entry['path'], member=entry.get('member'), frequency_hz=entry['frequency_hz'], input_mVpp=None if value is None else value *…（完整表达式见左栏）。 |
| 28 | `                 input_mVpp=None if value is None else value*UNIT_FACTORS[unit], input_confirmed=entry.get("input_confirmed", False), ` | 接续第 27 行的同一条语句，不是另起一段算法。 读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：'input_confirmed', False。 |
| 29 | `                 sweep=entry.get("linearity_included", True), repeat_group=entry.get("repeat_group", ""), nominal_mV=entry.get("repeat_nominal_mV")) ` | 接续第 27 行的同一条语句，不是另起一段算法。 读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：'linearity_included', True。 |
| 30 | `         record = InputRecord(**{k:v for k,v in entry.items() if k in valid}) ` | 把结果保存到 record：创建一份文件及其输入条件记录；参数：None={k: v for k, v in entry.items() if k in valid}。 |
| 31 | `         record.path = str((path.parent/record.path).resolve()) ` | 把结果保存到 record.path：转换为文本；参数：(path.parent / record.path).resolve()。 |
| 32 | `         records.append(record) ` | 把一项加入列表末尾；参数：record。 |
| 33 | `     setting_keys = {f.name for f in fields(AnalysisSettings)} ` | 把结果保存到 setting_keys：从 fields(AnalysisSettings) 逐个取 f，为每项生成 f.name。 |
| 34 | `     values = {k:v for k,v in data.get("settings", {}).items() if k in setting_keys} ` | 把结果保存到 values：从 data.get('settings', {}).items() 逐个取 (k, v)，仅保留 k in setting_keys，为每项生成 k: v。 |
| 35 | `     if data.get('version', 1) < 3: ` | 检查条件 data.get('version', 1) < 3；为真时执行下面缩进的一组语句。 |
| 36 | `         # Old projects stored the former blank defaults as null. Adopt the ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 37 | `         # user's new defaults while preserving any explicit numeric limits. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 38 | `         defaults = AnalysisSettings() ` | 把结果保存到 defaults：创建一套分析设置。 |
| 39 | `         for key in ('thd_limit_pct', 'frequency_limit_pct'): ` | 遍历 ('thd_limit_pct', 'frequency_limit_pct')，每次把一项赋给 key，执行下面缩进的循环体。 |
| 40 | `             if values.get(key) is None: ` | 检查条件 values.get(key) is None；为真时执行下面缩进的一组语句。 |
| 41 | `                 values[key] = getattr(defaults, key) ` | 把结果保存到 values[key]：按字段名读取对象属性；参数：defaults, key。 |
| 42 | `     settings = AnalysisSettings(**values) ` | 把结果保存到 settings：创建一套分析设置；参数：None=values。 |
| 43 | `     settings.validate() ` | 调用 settings.validate。 |
| 44 | `     return records, settings, data.get("channels", []), data.get("reference", "") ` | 结束当前函数并返回：组装元组：(records, settings, data.get('channels', []), data.get('reference', ''))。 |
| 45 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 46 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 47 | ` def save_project(path, records, settings, channels, reference, display=None): ` | 定义 save_project(path, records, settings, channels, reference, display=None)。把记录和设置的数据类转成 JSON，保留通道、参考与可选布局信息。 定义到这里时不执行函数体。 |
| 48 | `     payload = dict(version=3, records=[asdict(r) for r in records], settings=asdict(settings), channels=channels, reference=reference) ` | 把结果保存到 payload：组装键值字典；参数：version=3, records=[asdict(r) for r in records], settings=asdict(settings), channels=channels, reference=reference。 |
| 49 | `     if display is not None: ` | 检查条件 display is not None；为真时执行下面缩进的一组语句。 |
| 50 | `         payload['display'] = display ` | 把结果保存到 payload['display']：display。 |
| 51 | `     Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8") ` | 写入文本文件；参数：json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8'。 |
