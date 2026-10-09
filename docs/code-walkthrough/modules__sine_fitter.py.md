# modules/sine_fitter.py：正弦拟合封装

调用底层正弦拟合，返回幅度等结果和按需去基线的通道对象，供过零检测使用。

源码：[modules/sine_fitter.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/sine_fitter.py>)。本说明对应 17 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [9–10](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/sine_fitter.py:9>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `fit` | [12–17](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/sine_fitter.py:12>) | 取正弦拟合结果及系数，构造去 DC/漂移的懒计算对象；lazy=False 才一次生成完整去基线数组。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Fit the common test frequency and each electrode's sine amplitude/baseline.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import asdict ` | 从 dataclasses 导入 asdict。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 4 | ` from utils.numerics import fit_record ` | 从 utils.numerics 导入 fit_record。按 BDF 头解码 24 位样本并换算 µV；用共同频率及逐通道最小二乘计算正弦幅度、基线和拟合残差。 |
| 5 | ` from utils.centered_channels import CenteredChannels ` | 从 utils.centered_channels 导入 CenteredChannels。只在请求某个电极时构造去直流/线性漂移的波形，减少 128 通道大数组的复制。 |
| 6 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 7 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 8 | ` class SineFitter: ` | 定义 SineFitter 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 9 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 10 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | `     def fit(self, x_uV, fs, frequency, lazy=False, progress=lambda _: None): ` | 定义 fit(self, x_uV, fs, frequency, lazy=False, progress=lambda _: None)。取正弦拟合结果及系数，构造去 DC/漂移的懒计算对象；lazy=False 才一次生成完整去基线数组。 定义到这里时不执行函数体。 |
| 13 | `         coefficients = [] ` | 把结果保存到 coefficients：组装列表：[]。 |
| 14 | `         fits = fit_record(x_uV, fs, frequency, asdict(self.settings), coefficients, progress) ` | 把结果保存到 fits：调用 fit_record；参数：x_uV, fs, frequency, asdict(self.settings), coefficients, progress。 |
| 15 | `         beta = np.asarray(coefficients) ` | 把结果保存到 beta：转换或视为 NumPy 数组；参数：coefficients。 |
| 16 | `         centred = CenteredChannels(x_uV, beta[:, 2], beta[:, 3], fs) ` | 把结果保存到 centred：创建按需去基线的波形对象；参数：x_uV, beta[:, 2], beta[:, 3], fs。 |
| 17 | `         return fits, centred if lazy else centred.as_array() ` | 结束当前函数并返回：组装元组：(fits, centred if lazy else centred.as_array())。 |
