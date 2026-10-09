# utils/centered_channels.py：按需去基线

只在请求某个电极时构造去直流/线性漂移的波形，减少 128 通道大数组的复制。

源码：[utils/centered_channels.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/centered_channels.py>)。本说明对应 23 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [6–10](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/centered_channels.py:6>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `__len__` | [12–13](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/centered_channels.py:12>) | 使 len(该对象) 返回原信号的采样点数。 |
| `column` | [15–20](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/centered_channels.py:15>) | 取一个通道，减去其偏置；如果有斜率，再减去中心化时间×斜率。 |
| `as_array` | [22–23](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/centered_channels.py:22>) | 把各通道去基线结果并排组成完整数组；比逐列懒计算占更多内存。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Materialize a single detrended electrode only when its crossings are needed.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 3 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 4 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 5 | ` class CenteredChannels: ` | 定义 CenteredChannels 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 6 | `     def __init__(self, samples, offsets, slopes=None, fs=1.): ` | 定义 __init__(self, samples, offsets, slopes=None, fs=1.0)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 7 | `         self.samples = samples ` | 把结果保存到 self.samples：samples。 |
| 8 | `         self.offsets = offsets ` | 把结果保存到 self.offsets：offsets。 |
| 9 | `         self.slopes = slopes ` | 把结果保存到 self.slopes：slopes。 |
| 10 | `         self.fs = fs ` | 把结果保存到 self.fs：fs。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | `     def __len__(self): ` | 定义 __len__(self)。使 len(该对象) 返回原信号的采样点数。 定义到这里时不执行函数体。 |
| 13 | `         return len(self.samples) ` | 结束当前函数并返回：取得元素个数；参数：self.samples。 |
| 14 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 15 | `     def column(self, index): ` | 定义 column(self, index)。取一个通道，减去其偏置；如果有斜率，再减去中心化时间×斜率。 定义到这里时不执行函数体。 |
| 16 | `         result = np.asarray(self.samples[:, index]) - self.offsets[index] ` | 把结果保存到 result：np.asarray(self.samples[:, index]) 与 self.offsets[index] 相减。 |
| 17 | `         if self.slopes is not None: ` | 检查条件 self.slopes is not None；为真时执行下面缩进的一组语句。 |
| 18 | `             time = (np.arange(len(self.samples)) - (len(self.samples)-1)/2) / self.fs ` | 把结果保存到 time：np.arange(len(self.samples)) - (len(self.samples) - 1) / 2 与 self.fs 相除。 |
| 19 | `             result -= time * self.slopes[index] ` | 把 result 的原值减去 time * self.slopes[index]，再写回同一变量。 |
| 20 | `         return result ` | 结束当前函数并返回：result。 |
| 21 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 22 | `     def as_array(self): ` | 定义 as_array(self)。把各通道去基线结果并排组成完整数组；比逐列懒计算占更多内存。 定义到这里时不执行函数体。 |
| 23 | `         return np.column_stack([self.column(i) for i in range(self.samples.shape[1])]) ` | 结束当前函数并返回：把一维列并排组成二维矩阵；参数：[self.column(i) for i in range(self.samples.shape[1])]。 |
