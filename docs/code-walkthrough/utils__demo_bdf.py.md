# utils/demo_bdf.py：测试文件写入

只为演示/测试生成简单的连续 BDF；将已知 µV 数组打包成 24 位字节。

源码：[utils/demo_bdf.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/demo_bdf.py>)。本说明对应 30 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `write_demo_bdf` | [4–30](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/demo_bdf.py:4>) | 把合成的采样点×通道 µV 数组写成简单 BDF 测试文件；只接受整秒。 |
| `fixed` | [6–10](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/demo_bdf.py:6>) | 把字段编码为 ASCII 并补到固定宽度，超长时拒绝写入以免头错位。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Synthetic BDF writer used only by demo generation and tests.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 3 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 4 | ` def write_demo_bdf(path, x, fs): ` | 定义 write_demo_bdf(path, x, fs)。把合成的采样点×通道 µV 数组写成简单 BDF 测试文件；只接受整秒。 定义到这里时不执行函数体。 |
| 5 | `     """Minimal continuous BDF fixture writer; x is in microvolts.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 6 | `     def fixed(value, width): ` | 定义 fixed(value, width)。把字段编码为 ASCII 并补到固定宽度，超长时拒绝写入以免头错位。 定义到这里时不执行函数体。 |
| 7 | `         b = str(value).encode("ascii") ` | 把结果保存到 b：调用 str(value).encode；参数：'ascii'。 |
| 8 | `         if len(b) > width: ` | 检查条件 len(b) > width；为真时执行下面缩进的一组语句。 |
| 9 | `             raise ValueError("Demo header field too long") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Demo header field too long'；上层可捕获并显示原因。 |
| 10 | `         return b.ljust(width) ` | 结束当前函数并返回：调用 b.ljust；参数：width。 |
| 11 | `     n, nc = x.shape ` | 把结果保存到 (n, nc)：读取 x 的 shape 属性。 |
| 12 | `     if n % fs: ` | 检查条件 n % fs；为真时执行下面缩进的一组语句。 |
| 13 | `         raise ValueError("Demo length must contain whole one-second records") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Demo length must contain whole one-second records'；上层可捕获并显示原因。 |
| 14 | `     header = (b"\xffBIOSEMI" + fixed("Synthetic QA", 80) + fixed("Sine sweep", 80) ` | 把结果保存到 header：b'\xffBIOSEMI' + fixed('Synthetic QA', 80) + fixed('Sine sweep', 80) + b'01.01.2600.00.00'…（完整表达式见左栏） 与 fixed(nc, 4) 相加。 |
| 15 | `               + b"01.01.2600.00.00" + fixed(256*(nc+1), 8) + fixed("24BIT", 44) ` | 接续第 14 行的同一条语句，不是另起一段算法。 调用 fixed；参数：'24BIT', 44。 |
| 16 | `               + fixed(n//fs, 8) + fixed(1, 8) + fixed(nc, 4)) ` | 接续第 14 行的同一条语句，不是另起一段算法。 调用 fixed；参数：nc, 4。 |
| 17 | `     fields = [([f"EXG{i+1}" for i in range(nc)], 16), ([""]*nc, 80), (["uV"]*nc, 8), ` | 把结果保存到 fields：组装列表：[([f'EXG{i + 1}' for i in range(nc)], 16), ([''] * nc, 80), (['uV'] * nc, 8), ([-262144] * nc, 8), ([262143] * nc, 8), ([-8388608] * nc, 8), ([8388607] * nc, 8)…（完整表达式见左栏）。 |
| 18 | `               ([-262144]*nc, 8), ([262143]*nc, 8), ([-8388608]*nc, 8), ([8388607]*nc, 8), ` | 接续第 17 行的同一条语句，不是另起一段算法。 把结果保存到 fields：组装列表：[([f'EXG{i + 1}' for i in range(nc)], 16), ([''] * nc, 80), (['uV'] * nc, 8), ([-262144] * nc, 8), ([262143] * nc, 8), ([-8388608] * nc, 8), ([8388607] * nc, 8)…（完整表达式见左栏）。 |
| 19 | `               (["Synthetic no filter"]*nc, 80), ([fs]*nc, 8), ([""]*nc, 32)] ` | 接续第 17 行的同一条语句，不是另起一段算法。 把结果保存到 fields：组装列表：[([f'EXG{i + 1}' for i in range(nc)], 16), ([''] * nc, 80), (['uV'] * nc, 8), ([-262144] * nc, 8), ([262143] * nc, 8), ([-8388608] * nc, 8), ([8388607] * nc, 8)…（完整表达式见左栏）。 |
| 20 | `     for values, width in fields: ` | 遍历 fields，每次把一项赋给 (values, width)，执行下面缩进的循环体。 |
| 21 | `         header += b"".join(fixed(v, width) for v in values) ` | 把 header 的原值加上 b''.join((fixed(v, width) for v in values))，再写回同一变量。 |
| 22 | `     d = np.rint((x+262144)*16777215/524287-8388608).astype(np.int64) ` | 把结果保存到 d：转换数组元素类型；参数：np.int64。 |
| 23 | `     if np.any((d < -8388608) \| (d > 8388607)): ` | 检查条件 np.any((d < -8388608) &#124; (d > 8388607))；为真时执行下面缩进的一组语句。 |
| 24 | `         raise ValueError("Synthetic fixture exceeds the BDF range") ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Synthetic fixture exceeds the BDF range'；上层可捕获并显示原因。 |
| 25 | `     with path.open("wb") as f: ` | 进入资源上下文：打开文件或归档成员；参数：'wb'，对象命名为 f。退出时执行对应清理。 |
| 26 | `         f.write(header) ` | 向输出流写入字节；参数：header。 |
| 27 | `         for rec in range(n//fs): ` | 遍历 range(n // fs)，每次把一项赋给 rec，执行下面缩进的循环体。 |
| 28 | `             values = (d[rec*fs:(rec+1)*fs].T.reshape(-1) & 0xffffff).astype(np.uint32) ` | 把结果保存到 values：转换数组元素类型；参数：np.uint32。 |
| 29 | `             packed = np.column_stack((values & 255, (values >> 8) & 255, (values >> 16) & 255)).astype(np.uint8) ` | 把结果保存到 packed：转换数组元素类型；参数：np.uint8。 |
| 30 | `             f.write(packed.tobytes()) ` | 向输出流写入字节；参数：packed.tobytes()。 |
