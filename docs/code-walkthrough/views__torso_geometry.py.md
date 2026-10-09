# views/torso_geometry.py：躯干示意几何

生成示意躯干网格和 A1–D32 位置，再做三维到二维的投影；这些坐标不是 CT 重建或患者实测坐标。

源码：[views/torso_geometry.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_geometry.py>)。本说明对应 91 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__post_init__` | [13–17](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_geometry.py:13>) | 数据类初始化后检查映射名称和方向布尔值。 |
| `positions` | [19–43](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_geometry.py:19>) | 按四组通道、每组三列、上下编号方向，把 A1–D32 放到示意躯干表面。 |
| `torso_radius` | [46–49](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_geometry.py:46>) | 按高度线性插值躯干宽度与厚度。 |
| `torso_mesh` | [52–75](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_geometry.py:52>) | 用椭圆环连接躯干多边形，再补上简化上臂；不是读取 CT 网格。 |
| `project` | [78–84](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_geometry.py:78>) | 根据 yaw/pitch 旋转三维点，再返回正交相机的水平、垂直、深度。 |
| `visible` | [87–88](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_geometry.py:87>) | 把表面法向量投影到相机方向，判断电极当前是否朝向观察者。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Schematic 3-D torso from the user's six-column sketch, not a cap montage.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import dataclass ` | 从 dataclasses 导入 dataclass。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` import math ` | 导入模块 math。标量数学函数和有限值检查 |
| 4 | ` import numpy as np ` | 导入模块 numpy（别名 np）。数组、向量计算和线性代数 |
| 5 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 6 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 7 | ` @dataclass(frozen=True) ` | @dataclass 自动补充初始化等数据对象方法；frozen=True 时字段不能通常地重新赋值。 |
| 8 | ` class TorsoLayout: ` | 定义 TorsoLayout 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 9 | `     back_mapping: str = 'C behind A' ` | 声明 back_mapping 的类型为 str，用于后背 C/D 与前面 A/B 的示意对应关系。默认值：'C behind A'。 |
| 10 | `     top_to_bottom: bool = False  # Outer columns: low at bottom; middle reverses. ` | 声明 top_to_bottom 的类型为 bool，用于是否让外侧两列编号从上往下增加；中间 11–21 列方向相反。默认值：False（否）。 |
| 11 | `     front_b_on_right: bool = False  # B/D = person's right, front-screen left. ` | 声明 front_b_on_right 的类型为 bool，用于正面图是否把 B 组放在画面右边。默认值：False（否）。 |
| 12 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 13 | `     def __post_init__(self): ` | 定义 __post_init__(self)。数据类初始化后检查映射名称和方向布尔值。 定义到这里时不执行函数体。 |
| 14 | `         if self.back_mapping not in ('C behind A', 'C behind B'): ` | 检查条件 self.back_mapping not in ('C behind A', 'C behind B')；为真时执行下面缩进的一组语句。 |
| 15 | `             raise ValueError('Unknown back mapping') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Unknown back mapping'；上层可捕获并显示原因。 |
| 16 | `         if not isinstance(self.top_to_bottom, bool) or not isinstance(self.front_b_on_right, bool): ` | 检查条件 not isinstance(self.top_to_bottom, bool) or not isinstance(self.front_b_on_right, bool)；为真时执行下面缩进的一组语句。 |
| 17 | `             raise ValueError('Numbering direction must be boolean') ` | 抛出异常并停止当前正常流程：调用 ValueError；参数：'Numbering direction must be boolean'；上层可捕获并显示原因。 |
| 18 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 19 | `     def positions(self): ` | 定义 positions(self)。按四组通道、每组三列、上下编号方向，把 A1–D32 放到示意躯干表面。 定义到这里时不执行函数体。 |
| 20 | `         output = {} ` | 把结果保存到 output：组装字典，键用于给数值/设置命名：{}。 |
| 21 | `         for bank in 'ABCD': ` | 遍历 'ABCD'，每次把一项赋给 bank，执行下面缩进的循环体。 |
| 22 | `             side = 1 if bank == 'A' else -1 if bank == 'B' else ( ` | 把结果保存到 side：若 bank == 'A'，用 1；否则用 -1 if bank == 'B' else 1 if (bank == 'C') == (self.back_mapping == 'C behind A') else -1。 |
| 23 | `                 1 if (bank == 'C') == (self.back_mapping == 'C behind A') else -1) ` | 接续第 22 行的同一条语句，不是另起一段算法。 把结果保存到 side：若 bank == 'A'，用 1；否则用 -1 if bank == 'B' else 1 if (bank == 'C') == (self.back_mapping == 'C behind A') else -1。 |
| 24 | `             if self.front_b_on_right: ` | 检查条件 self.front_b_on_right；为真时执行下面缩进的一组语句。 |
| 25 | `                 side *= -1 ` | 把 side 的原值乘以 -1，再写回同一变量。 |
| 26 | `             face = -1 if bank in 'AB' else 1 ` | 把结果保存到 face：若 bank in 'AB'，用 -1；否则用 1。 |
| 27 | `             for first, last, fraction in ((1, 10, .20), (11, 21, .49), (22, 32, .78)): ` | 遍历 ((1, 10, 0.2), (11, 21, 0.49), (22, 32, 0.78))，每次把一项赋给 (first, last, fraction)，执行下面缩进的循环体。 |
| 28 | `                 for row, number in enumerate(range(first, last+1)): ` | 遍历 enumerate(range(first, last + 1))，每次把一项赋给 (row, number)，执行下面缩进的循环体。 |
| 29 | `                     amount = row/(last-first) ` | 把结果保存到 amount：row 与 last - first 相除。 |
| 30 | `                     # Serpentine wiring: the 11-21 strip runs opposite to its ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 31 | `                     # neighbouring 1-10 and 22-32 strips (the user's sketch). ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 32 | `                     if first == 11: ` | 检查条件 first == 11；为真时执行下面缩进的一组语句。 |
| 33 | `                         amount = 1-amount ` | 把结果保存到 amount：1 与 amount 相减。 |
| 34 | `                     if not self.top_to_bottom: ` | 检查条件 not self.top_to_bottom；为真时执行下面缩进的一组语句。 |
| 35 | `                         amount = 1-amount ` | 把结果保存到 amount：1 与 amount 相减。 |
| 36 | `                     z = 2.13-1.85*amount ` | 把结果保存到 z：2.13 与 1.85 * amount 相减。 |
| 37 | `                     width, depth = torso_radius(z) ` | 把结果保存到 (width, depth)：调用 torso_radius；参数：z。 |
| 38 | `                     x = side*fraction*width ` | 把结果保存到 x：side * fraction 与 width 相乘。 |
| 39 | `                     y = face*(depth*math.sqrt(1-fraction*fraction)+.028) ` | 把结果保存到 y：face 与 depth * math.sqrt(1 - fraction * fraction) + 0.028 相乘。 |
| 40 | `                     output[f'{bank}{number}'] = dict(point=(x, y, z), ` | 把结果保存到 output[f'{bank}{number}']：组装键值字典；参数：point=(x, y, z), normal=(side * fraction / width, face * math.sqrt(1 - fraction * fraction) / depth, 0), face='Front' if face < 0 else 'Back', ba…（完整表达式见左栏）。 |
| 41 | `                         normal=(side*fraction/width, face*math.sqrt(1-fraction*fraction)/depth, 0), ` | 接续第 40 行的同一条语句，不是另起一段算法。 调用 math.sqrt；参数：1 - fraction * fraction。 |
| 42 | `                         face='Front' if face < 0 else 'Back', bank=bank) ` | 接续第 40 行的同一条语句，不是另起一段算法。 把结果保存到 output[f'{bank}{number}']：组装键值字典；参数：point=(x, y, z), normal=(side * fraction / width, face * math.sqrt(1 - fraction * fraction) / depth, 0), face='Front' if face < 0 else 'Back', ba…（完整表达式见左栏）。 |
| 43 | `         return output ` | 结束当前函数并返回：output。 |
| 44 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 45 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 46 | ` def torso_radius(z): ` | 定义 torso_radius(z)。按高度线性插值躯干宽度与厚度。 定义到这里时不执行函数体。 |
| 47 | `     levels = (0, .45, 1.2, 2.12, 2.33, 2.55, 2.68) ` | 把结果保存到 levels：组装元组：(0, 0.45, 1.2, 2.12, 2.33, 2.55, 2.68)。 |
| 48 | `     return (float(np.interp(z, levels, (.83, .78, .91, 1.04, .95, .24, .24))), ` | 结束当前函数并返回：组装元组：(float(np.interp(z, levels, (0.83, 0.78, 0.91, 1.04, 0.95, 0.24, 0.24))), float(np.interp(z, levels, (0.36, 0.37, 0.42, 0.43, 0.33, 0.23, 0.23))))。 |
| 49 | `             float(np.interp(z, levels, (.36, .37, .42, .43, .33, .23, .23)))) ` | 接续第 48 行的同一条语句，不是另起一段算法。 转换为浮点数；参数：np.interp(z, levels, (0.36, 0.37, 0.42, 0.43, 0.33, 0.23, 0.23))。 |
| 50 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 51 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 52 | ` def torso_mesh(): ` | 定义 torso_mesh()。用椭圆环连接躯干多边形，再补上简化上臂；不是读取 CT 网格。 定义到这里时不执行函数体。 |
| 53 | `     """Low-poly trunk and short upper arms, returned as ordered vertices.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 54 | `     faces = [] ` | 把结果保存到 faces：组装列表：[]。 |
| 55 | `     zs = sorted(set(np.linspace(0, 2.68, 18)) \| {2.12, 2.33, 2.55}) ` | 把结果保存到 zs：排序；参数：set(np.linspace(0, 2.68, 18)) &#124; {2.12, 2.33, 2.55}。 |
| 56 | `     angles = np.linspace(0, 2*math.pi, 33) ` | 把结果保存到 angles：生成包含两端的等间隔数值；参数：0, 2 * math.pi, 33。 |
| 57 | `     rings = [[(torso_radius(z)[0]*math.cos(a), torso_radius(z)[1]*math.sin(a), z) ` | 把结果保存到 rings：从 zs 逐个取 z，为每项生成 [(torso_radius(z)[0] * math.cos(a), torso_radius(z)[1] * math.sin(a), z) for a in angles]。 |
| 58 | `               for a in angles] for z in zs] ` | 接续第 57 行的同一条语句，不是另起一段算法。 把结果保存到 rings：从 zs 逐个取 z，为每项生成 [(torso_radius(z)[0] * math.cos(a), torso_radius(z)[1] * math.sin(a), z) for a in angles]。 |
| 59 | `     for lower, upper in zip(rings, rings[1:]): ` | 遍历 zip(rings, rings[1:])，每次把一项赋给 (lower, upper)，执行下面缩进的循环体。 |
| 60 | `         faces.extend([[lower[i], lower[i+1], upper[i+1], upper[i]] for i in range(32)]) ` | 把多项逐个加入列表；参数：[[lower[i], lower[i + 1], upper[i + 1], upper[i]] for i in range(32)]。 |
| 61 | `     faces.append(list(reversed(rings[0][:-1]))) ` | 把一项加入列表末尾；参数：list(reversed(rings[0][:-1]))。 |
| 62 | `     faces.append(rings[-1][:-1]) ` | 把一项加入列表末尾；参数：rings[-1][:-1]。 |
| 63 | `     for side in (-1, 1): ` | 遍历 (-1, 1)，每次把一项赋给 side，执行下面缩进的循环体。 |
| 64 | `         start, end = np.array((side*.99, 0, 2.16)), np.array((side*1.29, 0, .78)) ` | 把结果保存到 (start, end)：组装元组：(np.array((side * 0.99, 0, 2.16)), np.array((side * 1.29, 0, 0.78)))。 |
| 65 | `         axis = end-start; axis /= np.linalg.norm(axis) ` | 把结果保存到 axis：end 与 start 相减。 把 axis 的原值除以 np.linalg.norm(axis)，再写回同一变量。 |
| 66 | `         first = np.array((0,1,0)); second = np.cross(axis,first) ` | 把结果保存到 first：构造 NumPy 数组；参数：(0, 1, 0)。 把结果保存到 second：计算三维叉积得到表面法向量；参数：axis, first。 |
| 67 | `         arm_rings = [] ` | 把结果保存到 arm_rings：组装列表：[]。 |
| 68 | `         for fraction, radius in ((0,.20),(.25,.21),(.7,.17),(1,.15)): ` | 遍历 ((0, 0.2), (0.25, 0.21), (0.7, 0.17), (1, 0.15))，每次把一项赋给 (fraction, radius)，执行下面缩进的循环体。 |
| 69 | `             centre = start+fraction*(end-start) ` | 把结果保存到 centre：start 与 fraction * (end - start) 相加。 |
| 70 | `             arm_rings.append([tuple(centre+radius*(math.cos(a)*first+math.sin(a)*second)) ` | 把一项加入列表末尾；参数：[tuple(centre + radius * (math.cos(a) * first + math.sin(a) * second)) for a in np.linspace(0, 2 * math.pi, 17)]。 |
| 71 | `                               for a in np.linspace(0,2*math.pi,17)]) ` | 接续第 70 行的同一条语句，不是另起一段算法。 生成包含两端的等间隔数值；参数：0, 2 * math.pi, 17。 |
| 72 | `         for a,b in zip(arm_rings,arm_rings[1:]): ` | 遍历 zip(arm_rings, arm_rings[1:])，每次把一项赋给 (a, b)，执行下面缩进的循环体。 |
| 73 | `             faces.extend([[a[i],a[i+1],b[i+1],b[i]] for i in range(16)]) ` | 把多项逐个加入列表；参数：[[a[i], a[i + 1], b[i + 1], b[i]] for i in range(16)]。 |
| 74 | `         faces.append(arm_rings[-1][:-1]) ` | 把一项加入列表末尾；参数：arm_rings[-1][:-1]。 |
| 75 | `     return faces ` | 结束当前函数并返回：faces。 |
| 76 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 77 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 78 | ` def project(point, yaw=0., pitch=6.): ` | 定义 project(point, yaw=0.0, pitch=6.0)。根据 yaw/pitch 旋转三维点，再返回正交相机的水平、垂直、深度。 定义到这里时不执行函数体。 |
| 79 | `     """Orthographic camera. Front x>0 is viewer-right; back reverses naturally.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 80 | `     x,y,z = point ` | 把结果保存到 (x, y, z)：point。 |
| 81 | `     a,b = math.radians(yaw), math.radians(pitch) ` | 把结果保存到 (a, b)：组装元组：(math.radians(yaw), math.radians(pitch))。 |
| 82 | `     horizontal = x*math.cos(a)+y*math.sin(a) ` | 把结果保存到 horizontal：x * math.cos(a) 与 y * math.sin(a) 相加。 |
| 83 | `     near = x*math.sin(a)-y*math.cos(a) ` | 把结果保存到 near：x * math.sin(a) 与 y * math.cos(a) 相减。 |
| 84 | `     return horizontal, z*math.cos(b)-near*math.sin(b), z*math.sin(b)+near*math.cos(b) ` | 结束当前函数并返回：组装元组：(horizontal, z * math.cos(b) - near * math.sin(b), z * math.sin(b) + near * math.cos(b))。 |
| 85 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 86 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 87 | ` def visible(normal, yaw, pitch): ` | 定义 visible(normal, yaw, pitch)。把表面法向量投影到相机方向，判断电极当前是否朝向观察者。 定义到这里时不执行函数体。 |
| 88 | `     return project(normal,yaw,pitch)[2] > .02 ` | 结束当前函数并返回：project(normal, yaw, pitch)[2] > 0.02。 |
| 89 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 90 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 91 | ` MESH = torso_mesh() ` | 把结果保存到 MESH：调用 torso_mesh。 |
