# modules/windowing.py：窗口索引

把秒数转换成采样索引，给出完整窗口；不足长度不补零；必要时补一个贴齐传入数据末端的完整窗口（当前先按设置排除文件尾部）。

源码：[modules/windowing.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/windowing.py>)。本说明对应 25 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `spans` | [11–25](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/windowing.py:11>) | 校验秒数和采样率，生成 [left,right) 索引；末尾必要时加一个完整窗，不补零。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Complete, sample-aligned windows. Never pad or join separate recordings.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import dataclass ` | 从 dataclasses 导入 dataclass。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 4 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 5 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 6 | ` @dataclass(frozen=True) ` | @dataclass 自动补充初始化等数据对象方法；frozen=True 时字段不能通常地重新赋值。 |
| 7 | ` class WindowPlan: ` | 定义 WindowPlan 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 8 | `     window_s: float = 10.0 ` | 声明 window_s 的类型为 float，用于窗口长度（秒）。默认值：10.0。 |
| 9 | `     hop_s: float = 1.0 ` | 声明 hop_s 的类型为 float，用于窗口起点步长（秒）。默认值：1.0。 |
| 10 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 11 | `     def spans(self, sample_count, fs): ` | 定义 spans(self, sample_count, fs)。校验秒数和采样率，生成 [left,right) 索引；末尾必要时加一个完整窗，不补零。 定义到这里时不执行函数体。 |
| 12 | `         if not all(math.isfinite(v) and v > 0 for v in (fs, self.window_s, self.hop_s)): ` | 检查条件 not all((math.isfinite(v) and v > 0 for v in (fs, self.window_s, self.hop_s)))；为真时执行下面缩进的一组语句。 |
| 13 | `             raise ValueError("Window duration, step and sample rate must be positive") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Window duration, step and sample rate must be positive'；上层可捕获并显示原因。 |
| 14 | `         if self.hop_s > self.window_s: ` | 检查条件 self.hop_s > self.window_s；为真时执行下面缩进的一组语句。 |
| 15 | `             raise ValueError("Window step must not exceed window duration") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Window step must not exceed window duration'；上层可捕获并显示原因。 |
| 16 | `         width, hop = round(self.window_s * fs), round(self.hop_s * fs) ` | 把结果保存到 (width, hop)：组装元组：(round(self.window_s * fs), round(self.hop_s * fs))。 |
| 17 | `         if width < 2 or hop < 1: ` | 检查条件 width < 2 or hop < 1；为真时执行下面缩进的一组语句。 |
| 18 | `             raise ValueError("Window or step is shorter than the sample resolution") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Window or step is shorter than the sample resolution'；上层可捕获并显示原因。 |
| 19 | `         if sample_count < width: ` | 检查条件 sample_count < width；为真时执行下面缩进的一组语句。 |
| 20 | `             return [] ` | 结束当前函数并返回：组装列表：[]。 |
| 21 | `         starts = list(range(0, sample_count - width + 1, hop)) ` | 把结果保存到 starts：构造列表；参数：range(0, sample_count - width + 1, hop)。 |
| 22 | `         # Cover the final samples with a full end-aligned window, without padding. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 23 | `         if starts[-1] != sample_count - width: ` | 检查条件 starts[-1] != sample_count - width；为真时执行下面缩进的一组语句。 |
| 24 | `             starts.append(sample_count - width) ` | 把一项加入列表末尾；参数：sample_count - width。 |
| 25 | `         return [(start, start + width) for start in starts] ` | 返回每窗 [起始采样索引,结束索引)；Python 切片不含右端，窗口长度恰为 width。 |
