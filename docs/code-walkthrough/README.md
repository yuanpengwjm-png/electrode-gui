# electrode-gui 代码阅读入口

第一次读项目，先打开 [从一次点击读懂整个项目](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/START_HERE_ZH.md>)。再用下面的索引逐文件查看。

先从应用流程理解，再对照每行源码。所有讲解都基于当前代码，不把计划中的 TCP/CT 功能当成已经实现。
覆盖 45 个源码/配置文件、4344 行；逐行表包含注释和空行。没有修改应用源代码。

源码核对快照时间（本机）：2026-09-30T15:41:38。后续代码改变时，以 source_manifest.json 中的行数和 SHA256 区分版本。

## 先认清现在的程序

当前是 Python + Tkinter 的离线 BDF/ZIP 分析程序。已有：正弦台架、两平台脉冲、ECG SQI、窗口回放、二维网格、示意三维躯干和导出。
尚未实现：ActiView TCP 数据适配器、CT-on/off 配对噪声分析、LQMLib、ECGI 逆问题重建。躯干是示意图，不是 CT 解剖模型。

## 用一个用户操作串起全部模块

点击 Open BDF/ZIP → input_catalog 建记录 → BdfReader 检查头 → GUI 编辑参数/选通道 → prepare 固定本次请求 → run 启后台线程 → AnalysisService 按文件排除末尾并选择算法 → MetricResult/AnalysisResult 保存数值与状态 → poll 接收结果 → redraw 更新热图/时间轴/躯干 → ReportExporter 导出。

界面函数是回调：先定义并交给按钮，只有点击后才执行。导入/定义类并不等于运行分析。

## 推荐阅读顺序

1. main.py 和 gui.py 最后的启动语句：程序如何出现窗口。
2. models.py：认识 InputRecord、MetricResult、AnalysisResult。
3. gui.py 的 prepare、run、worker、poll、accept_result、redraw：一次点击怎么到结果。
4. services/analysis_service.py：三种模式如何分流。
5. gain_error、time_synchronization、bench_spectrum：先学你关心的幅度、同步、SNR/THD。
6. ecg_quality：逐个读检测器与 SQI，留意单位、频带和阈值。
7. BDF 底层、窗口、显示和测试：了解数据怎么来、结果为何可信到什么程度。

## Python 符号速查

| 写法 | 在本项目里的意思 |
|---|---|
| import / from ... import | 取得其他模块的工具，供后面使用 |
| class / def | 定义一组对象行为 / 定义函数，此时通常还不执行函数体 |
| self | 当前这个对象；self.settings 是它保存的参数 |
| __init__ | 创建对象时运行的初始化函数 |
| x[:, i] | 所有采样点、第 i 个通道；通道编号从 0 开始计索引 |
| x[left:right] | 取采样区间，含 left、不含 right |
| fs | 每秒采样数；n/fs 把采样点位置变成秒 |
| @ 运算符 | 矩阵乘法；行首 @dataclass 则是另一种语法：装饰器 |
| None | 没有值/未评估，不等于 0 |
| callback / command=self.run | 保存函数引用，点击按钮后才调用 |
| lambda | 一个短小的匿名回调；常把事件转发到另一个函数 |
| **dict | 将字典展开成命名参数；在数学表达式中 ** 是乘方 |
| with / yield / finally | 管理文件与缓存的使用和退出清理 |
| try / except | 执行可能失败的操作，捕获异常并解释错误 |
| field(default_factory=dict) | 每个结果对象各有自己的新字典，避免互相污染 |
| list comprehension | 在一行中遍历、筛选并生成列表 |
| StringVar / BooleanVar | 把表单控件与 Python 状态连接起来 |

## 几个最容易混淆的实现细节

- THD 在本代码中是百分比；SNR/SINAD 是 dB。谐波阶数和积分带宽会影响数值。
- 台架幅度使用有物理单位的波形，正弦是拟合基频 Vpp，脉冲是高低平台差。
- 同步是去基线后的真实双向事件差，正值表示待测通道较晚；参考自己对自己不算验证。
- bSQI 当前使用 matched/(A+B−matched)，而不是所有文献都会采用的同一种定义。
- flatline 当前输出最长近似平线时长及削顶计数，没有另返回一个统一的 fSQI 百分比分数。
- basSQI 在去常数 DC 后的频谱计算，公式 1−P[0,1)/P[0,40)；不先把低频漂移滤掉再声称它不存在。
- 绿色只代表通过当前所设规则；黄色既可能临界，也可能缺数据/未校准。当前实现没有独立灰色 MetricResult。
- 躯干的灰色表示通道没有当前分析结果/未选中，不等于质量正常。
- Linearity 要至少三个不同输入等级；Repetition 默认至少三次人工声明的独立运行。两个 Test 文件可作探索比较，但默认程序不会给三次重复要求的通过结论。
- ECG 默认 10 秒窗口、5 秒步长；台架 GUI 默认启用 10 秒/1 秒窗口。没有完整窗时不把不同文件拼接。
- 当前默认每份文件先排除最后 1 秒再分析；窗口对齐保留数据末端。duration_s 是保留时长，source_duration_s 是原始时长，excluded_tail_s 是实际排除秒数。排除不等于通过。
- 当前 THD 默认限值为 1%，频率误差默认限值为 0.1%；仍可留空表示没有验收阈值。它们是本项目设置，不是自动推导的标准。
- 播放只切换已算好的结果，并非实时接收；双向 filtfilt 及完整窗口处理目前都是离线实现。
- 二维圆点和三维躯干都只展示颜色；当前 GUI 没有用于检查原始 ECG 波形的专用曲线面板。

## 全部文件的入口

| 文件 | 职责 | 逐行说明 |
|---|---|---|
| [.vscode/extensions.json](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/.vscode/extensions.json>) | 扩展建议：推荐 Python 和 debugpy；只是推荐列表，不会在这里计算指标。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/.vscode__extensions.json.md>) |
| [.vscode/launch.json](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/.vscode/launch.json>) | F5 启动配置：定义普通 GUI 与演示 GUI 两个调试入口；不是信号处理算法。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/.vscode__launch.json.md>) |
| [.vscode/settings.json](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/.vscode/settings.json>) | 编辑器设置：启用 unittest、设置发现路径与 UTF-8 编码。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/.vscode__settings.json.md>) |
| [.vscode/tasks.json](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/.vscode/tasks.json>) | VS Code 测试任务：调用当前选择的 Python，运行 unittest 自动发现 tests 下的测试。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/.vscode__tasks.json.md>) |
| [Electrode-QA.code-workspace](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/Electrode-QA.code-workspace>) | 工作区入口：让 VS Code 把当前目录作为项目根，并设置窗口标题。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/Electrode-QA.code-workspace.md>) |
| [config.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/config.py>) | 参数与阈值：保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/config.py.md>) |
| [gui.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/gui.py>) | 界面与按钮：创建 Tkinter 窗口，收集用户输入，用后台线程启动分析，并把结果交给热图、时间轴及躯干窗口。这里不直接计算 SQI。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/gui.py.md>) |
| [main.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/main.py>) | 程序入口：同时提供有窗口运行和 --headless 无窗口分析两种入口；VS Code 默认 F5 配置直接运行 gui.py。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/main.py.md>) |
| [models.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/models.py>) | 模块间的数据格式：InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/models.py.md>) |
| [modules/__init__.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/__init__.py>) | 包入口：标识该目录为 Python 包，便于导入其中的模块。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules____init__.py.md>) |
| [modules/bench_spectrum.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/bench_spectrum.py>) | 正弦的噪声与谐波：独立估计每通道频率，拟合基频和指定谐波，把残差噪声与谐波功率分开，用于 SNR、THD、SINAD。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules__bench_spectrum.py.md>) |
| [modules/ecg_quality.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/ecg_quality.py>) | ECG SQI：两个不同的心搏检测器加一对一匹配，计算 bSQI；Welch 频谱计算 pSQI/basSQI；另算 Pearson 峰度和平线/削顶。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules__ecg_quality.py.md>) |
| [modules/gain_error.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/gain_error.py>) | 幅度准确性：用输出基频/平台 Vpp 与确认过的实际输入比较；没有可靠波形或输入校准时，不把结果判为幅度合格。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules__gain_error.py.md>) |
| [modules/linearity.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/linearity.py>) | 输入输出线性度：按频率分组，要求至少三个已确认的输入幅度等级，拟合直线并计算最大偏差占输入跨度的百分比。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules__linearity.py.md>) |
| [modules/pulse_analyzer.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/pulse_analyzer.py>) | 两平台脉冲：估计高低平台与中点；复用同步匹配器，但不套用正弦拟合或正弦 THD。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules__pulse_analyzer.py.md>) |
| [modules/repeatability.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/repeatability.py>) | 独立重复实验：按人工声明的 repeat_group 与频率比较独立记录；计算增益或输出幅度 CV，以及各次延迟中位数的 SD。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules__repeatability.py.md>) |
| [modules/sine_fitter.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/sine_fitter.py>) | 正弦拟合封装：调用底层正弦拟合，返回幅度等结果和按需去基线的通道对象，供过零检测使用。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules__sine_fitter.py.md>) |
| [modules/time_synchronization.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/time_synchronization.py>) | 通道相对时序：先找上升、下降过零事件，再分别匹配；不移动波形，不用后面的周期补漏检。输出事件表、延迟 P95 和 jitter。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules__time_synchronization.py.md>) |
| [modules/windowing.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/windowing.py>) | 窗口索引：把秒数转换成采样索引，给出完整窗口；不足长度不补零；必要时补一个贴齐传入数据末端的完整窗口（当前先按设置排除文件尾部）。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/modules__windowing.py.md>) |
| [requirements.txt](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/requirements.txt>) | 依赖清单：NumPy 做数组与线性代数，SciPy 做滤波/频谱/统计，Matplotlib 导出图片。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/requirements.txt.md>) |
| [services/__init__.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/__init__.py>) | 包入口：标识该目录为 Python 包，便于导入其中的模块。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/services____init__.py.md>) |
| [services/analysis_service.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/analysis_service.py>) | 分析调度：验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/services__analysis_service.py.md>) |
| [services/demo_data.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/services/demo_data.py>) | 演示数据：生成已知故障的合成 BDF：幅度偏差、延迟、非线性、重复变化、ECG 漂移、平线、噪声。演示标签不是实验验证结论。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/services__demo_data.py.md>) |
| [tests/test_analysis.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_analysis.py>) | 基础行为测试：用已知输入检查 BDF 单位、幅度/同步/线性/重复性、配置往返、GUI 状态及导出。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/tests__test_analysis.py.md>) |
| [tests/test_large_bdf.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_large_bdf.py>) | 大数据路径测试：检查磁盘缓存与内存读取得到相同结果、异常清理及磁盘不足处理。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/tests__test_large_bdf.py.md>) |
| [tests/test_record_scope.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_record_scope.py>) | 结果范围测试：检查输入确认只属于当前文件，以及单文件/窗口视图不会借用其他文件的颜色。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/tests__test_record_scope.py.md>) |
| [tests/test_stages.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_stages.py>) | 分析模式测试：检查正弦谐波分离、脉冲不走正弦拟合、ECG 窗口与 SQI、错误模式拒绝。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/tests__test_stages.py.md>) |
| [tests/test_tail_exclusion.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_tail_exclusion.py>) | 排除文件末尾的行为测试：用末尾带漂移和削顶的合成数据，核对台架/ECG、时间轴、躯干和导出都只使用保留区间，并验证原文件不变及旧配置兼容。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/tests__test_tail_exclusion.py.md>) |
| [tests/test_torso.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_torso.py>) | 躯干与主窗口联动测试：检查 A–D 组的身体左右和蛇形编号、选点与旋转、双窗口播放互斥、旧结果清除，以及导出/恢复时保持同一窗口和布局。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/tests__test_torso.py.md>) |
| [tests/test_windows.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_windows.py>) | 窗口和播放测试：检查局部故障只影响对应窗口、短文件不拼接、末尾覆盖、播放与导出范围一致。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/tests__test_windows.py.md>) |
| [utils/__init__.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/__init__.py>) | 包入口：标识该目录为 Python 包，便于导入其中的模块。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/utils____init__.py.md>) |
| [utils/array_store.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/array_store.py>) | 大文件内存管理：小数组放内存，大于阈值的数组用临时磁盘映射；正常退出或异常退出都尝试清理本次缓存。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/utils__array_store.py.md>) |
| [utils/bdf_reader.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/bdf_reader.py>) | BDF 读取入口：检查头信息、真实通道及长度，支持 ZIP 内部成员，并通过上下文管理大数组的生命周期。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/utils__bdf_reader.py.md>) |
| [utils/centered_channels.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/centered_channels.py>) | 按需去基线：只在请求某个电极时构造去直流/线性漂移的波形，减少 128 通道大数组的复制。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/utils__centered_channels.py.md>) |
| [utils/demo_bdf.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/demo_bdf.py>) | 测试文件写入：只为演示/测试生成简单的连续 BDF；将已知 µV 数组打包成 24 位字节。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/utils__demo_bdf.py.md>) |
| [utils/input_catalog.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/input_catalog.py>) | 建立文件清单：枚举 BDF 或 ZIP 中的 BDF；从名称猜测波形、频率、幅度，但默认 input_confirmed=False。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/utils__input_catalog.py.md>) |
| [utils/numerics.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/numerics.py>) | 底层数值计算：按 BDF 头解码 24 位样本并换算 µV；用共同频率及逐通道最小二乘计算正弦幅度、基线和拟合残差。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/utils__numerics.py.md>) |
| [utils/project_io.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/project_io.py>) | 项目保存和载入：保存文件清单、参数、通道和参考；恢复时适配部分旧配置，并统一幅度单位。保存的是配置，不是复制原始 BDF。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/utils__project_io.py.md>) |
| [utils/report_exporter.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/report_exporter.py>) | 导出：生成当前视图的 PNG/CSV，以及完整 JSON、项目配置、各窗口和过零事件表、HTML 报告。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/utils__report_exporter.py.md>) |
| [views/__init__.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/__init__.py>) | 包入口：标识该目录为 Python 包，便于导入其中的模块。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/views____init__.py.md>) |
| [views/heatmap_view.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/heatmap_view.py>) | 二维通道网格：读取计算完成的颜色，画可点击圆点；另有不依赖 Tk 窗口的 PNG 导出器。网格顺序不是身体坐标。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/views__heatmap_view.py.md>) |
| [views/timeline_view.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/timeline_view.py>) | 离线结果播放：管理已有窗口结果的滑块、播放/暂停、前后跳转、下一个提醒；不会在播放时重新分析样本。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/views__timeline_view.py.md>) |
| [views/torso_geometry.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_geometry.py>) | 躯干示意几何：生成示意躯干网格和 A1–D32 位置，再做三维到二维的投影；这些坐标不是 CT 重建或患者实测坐标。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/views__torso_geometry.py.md>) |
| [views/torso_view.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_view.py>) | 躯干绘制与交互：画示意躯干，按已有指标上色，处理旋转、缩放、选点、悬停和图片导出；不计算电极质量。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/views__torso_view.py.md>) |
| [views/torso_window.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/views/torso_window.py>) | 独立躯干窗口：把躯干、指标选择、提醒列表、详情及时间轴组合成第二窗口，与主窗口使用同一份结果。 | [打开](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/docs/code-walkthrough/views__torso_window.py.md>) |

## 文档和产物目录

- README.md：如何启动、操作、导出及当前限制，不是可执行代码。
- CODE_GUIDE_ZH.md：现有中文架构与算法说明；本目录补充真实源码逐行对照及新增躯干模块。
- output/：之前运行的演示、测试或报告文件，属于结果而非主程序；本次未重新运行这些实验。
- __pycache__/：Python 自动生成的字节码缓存，不需要逐行学习。
- source_manifest.json：讲解对应的源码哈希与行数，可检查以后代码是否已经改变。
- walkthrough_data.json：逐行说明的机器可读版本。

本次只做代码阅读与文档核对，没有重新运行硬件采集、GUI 全套测试或确认医学有效性。
