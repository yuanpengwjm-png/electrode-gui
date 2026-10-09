# main.py：程序入口

同时提供有窗口运行和 --headless 无窗口分析两种入口；VS Code 默认 F5 配置直接运行 gui.py。

源码：[main.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/main.py>)。本说明对应 62 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `main` | [11–58](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/main.py:11>) | 读取命令行参数；无窗口模式直接调用分析和导出，有窗口模式创建 Tk 根窗口并进入事件循环。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Run the desktop app, or analyze/export without a GUI for repeatable tests.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 3 | ` import argparse ` | 导入模块 argparse。解析命令行选项 |
| 4 | ` from config import AnalysisSettings ` | 从 config 导入 AnalysisSettings。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 5 | ` from services.analysis_service import AnalysisService ` | 从 services.analysis_service 导入 AnalysisService。验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 |
| 6 | ` from services.demo_data import create_mode_demo ` | 从 services.demo_data 导入 create_mode_demo。生成已知故障的合成 BDF：幅度偏差、延迟、非线性、重复变化、ECG 漂移、平线、噪声。演示标签不是实验验证结论。 |
| 7 | ` from utils.project_io import load_project ` | 从 utils.project_io 导入 load_project。保存文件清单、参数、通道和参考；恢复时适配部分旧配置，并统一幅度单位。保存的是配置，不是复制原始 BDF。 |
| 8 | ` from utils.report_exporter import ReportExporter ` | 从 utils.report_exporter 导入 ReportExporter。生成当前视图的 PNG/CSV，以及完整 JSON、项目配置、各窗口和过零事件表、HTML 报告。 |
| 9 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 10 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 11 | ` def main(): ` | 定义 main()。读取命令行参数；无窗口模式直接调用分析和导出，有窗口模式创建 Tk 根窗口并进入事件循环。 定义到这里时不执行函数体。 |
| 12 | `     parser = argparse.ArgumentParser(description=__doc__) ` | 把结果保存到 parser：创建命令行参数解析器；__doc__ 使用文件开头的说明作为帮助文字；参数：description=__doc__。 |
| 13 | `     parser.add_argument("--headless", action="store_true") ` | 注册无窗口开关；写上此选项时为 True，直接分析并导出，不创建 Tk 窗口；参数：'--headless', action='store_true'。 |
| 14 | `     parser.add_argument("--demo", action="store_true") ` | 注册演示开关；启用时生成合成 BDF；参数：'--demo', action='store_true'。 |
| 15 | `     parser.add_argument("--mode", choices=("bench_sine", "bench_pulse", "ecg"), default=None) ` | 注册分析模式选项，只允许正弦台架、脉冲台架或 ECG；不指定时为 None；参数：'--mode', choices=('bench_sine', 'bench_pulse', 'ecg'), default=None。 |
| 16 | `     parser.add_argument("--config", type=Path) ` | 注册项目 JSON 路径选项，并把输入转换为 Path 对象；参数：'--config', type=Path。 |
| 17 | `     parser.add_argument("--electrodes", type=int, default=8) ` | 注册通道数量选项，转换为整数，默认 8；用于演示或项目未指定通道时的自动选择；参数：'--electrodes', type=int, default=8。 |
| 18 | `     parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent/"output/demo") ` | 注册无窗口分析的输出目录；未指定时使用脚本旁的 output/demo；参数：'--out', type=Path, default=Path(__file__).resolve().parent / 'output/demo'。 |
| 19 | `     args = parser.parse_args() ` | 把结果保存到 args：读取本次启动命令中的选项，并整理为 args 对象；后面用 args.headless 等属性读取。 |
| 20 | `     if args.headless: ` | 检查条件 args.headless；为真时执行下面缩进的一组语句。 |
| 21 | `         if args.demo: ` | 检查条件 args.demo；为真时执行下面缩进的一组语句。 |
| 22 | `             if not 1 <= args.electrodes <= 256: ` | 检查条件 not 1 <= args.electrodes <= 256；为真时执行下面缩进的一组语句。 |
| 23 | `                 parser.error("Demo electrode count must be between 1 and 256") ` | 报告参数错误并终止该入口；参数：'Demo electrode count must be between 1 and 256'。 |
| 24 | `             mode = args.mode or "bench_sine" ` | 把结果保存到 mode：args.mode or 'bench_sine'。 |
| 25 | `             records = create_mode_demo(args.out/"synthetic_inputs", args.electrodes, mode) ` | 把结果保存到 records：按模式选择正弦演示，或生成 30 秒脉冲/ECG 数据并注入特定故障。；参数：args.out / 'synthetic_inputs', args.electrodes, mode。 |
| 26 | `             settings, channels, reference = AnalysisSettings(analysis_mode=mode), [f"EXG{i+1}" for i in range(args.electrodes)], "EXG1" ` | 把结果保存到 (settings, channels, reference)：组装元组：(AnalysisSettings(analysis_mode=mode), [f'EXG{i + 1}' for i in range(args.electrodes)], 'EXG1')。 |
| 27 | `             title = "SYNTHETIC DEMO - not laboratory evidence" ` | 把结果保存到 title：'SYNTHETIC DEMO - not laboratory evidence'。 |
| 28 | `         elif args.config: ` | 检查条件 args.config；为真时执行下面缩进的一组语句。 |
| 29 | `             records, settings, channels, reference = load_project(args.config) ` | 把结果保存到 (records, settings, channels, reference)：读取 JSON、兼容旧字段、解析相对路径、过滤允许的设置字段并校验。；参数：args.config。 |
| 30 | `             if not channels: ` | 检查条件 not channels；为真时执行下面缩进的一组语句。 |
| 31 | `                 from utils.bdf_reader import BdfReader ` | 从 utils.bdf_reader 导入 BdfReader。检查头信息、真实通道及长度，支持 ZIP 内部成员，并通过上下文管理大数组的生命周期。 |
| 32 | `                 info = BdfReader().inspect(records[0]) ` | 把结果保存到 info：只读头信息，核对格式/长度，返回通道名、采样率、时长，过滤 Status/Annotations。；参数：records[0]。 |
| 33 | `                 pool = "scalp" if any(not c.upper().startswith("EXG") for c in info.voltage_labels) else "EXG" ` | 把结果保存到 pool：若 any((not c.upper().startswith('EXG') for c in info.voltage_labels))，用 'scalp'；否则用 'EXG'。 |
| 34 | `                 channels = BdfReader.choose_channels(info, args.electrodes, pool) ` | 把结果保存到 channels：从实际电压通道按 EXG/scalp/all 分组选择前 count 个，数量不合法就报错。；参数：info, args.electrodes, pool。 |
| 35 | `             reference = reference or channels[0] ` | 把结果保存到 reference：reference or channels[0]。 |
| 36 | `             title = "Electrode QA laboratory results" ` | 把结果保存到 title：'Electrode QA laboratory results'。 |
| 37 | `         else: ` | 前面对应条件不成立时，进入此分支。 |
| 38 | `             parser.error("--headless requires --demo or --config") ` | 报告参数错误并终止该入口；参数：'--headless requires --demo or --config'。 |
| 39 | `         if args.mode: ` | 检查条件 args.mode；为真时执行下面缩进的一组语句。 |
| 40 | `             settings.analysis_mode = args.mode ` | 把结果保存到 settings.analysis_mode：读取 args 的 mode 属性。 |
| 41 | `         result = AnalysisService(settings).analyze(records, channels, reference, print) ` | 把结果保存到 result：台架分支先测整段，再按需逐窗口重复同样的测量，最后做跨记录线性/重复性；ECG 走独立分支。；参数：records, channels, reference, print。 |
| 42 | `         report = ReportExporter().save(result, args.out, "ecg_quality" if settings.analysis_mode == "ecg" else "bench_summary", title) ` | 把结果保存到 report：导出当前视图及完整实验结果、窗口表和事件表；HTML 中用户文本先转义。；参数：result, args.out, 'ecg_quality' if settings.analysis_mode == 'ecg' else 'bench_summary', title。 |
| 43 | `         print(f"{len(result.electrodes)} electrodes, {result.elapsed_s:.3f} s. Report: {report.resolve()}") ` | 把信息输出到终端；参数：f'{len(result.electrodes)} electrodes, {result.elapsed_s:.3f} s. Report: {report.resolve()}'。 |
| 44 | `     else: ` | 前面对应条件不成立时，进入此分支。 |
| 45 | `         import tkinter as tk ` | 导入模块 tkinter（别名 tk）。桌面窗口、控件、文件选择框和消息框 |
| 46 | `         from gui import ElectrodeQAApp ` | 从 gui 导入 ElectrodeQAApp。创建 Tkinter 窗口，收集用户输入，用后台线程启动分析，并把结果交给热图、时间轴及躯干窗口。这里不直接计算 SQI。 |
| 47 | `         root = tk.Tk() ` | 创建 Tkinter 的根窗口；按钮和其他控件都挂在这个窗口或其子容器里。 |
| 48 | `         app = ElectrodeQAApp(root) ` | 把结果保存到 app：创建主应用对象，立即运行 __init__ 搭建控件并连接按钮回调；参数：root。 |
| 49 | `         if args.config: ` | 检查条件 args.config；为真时执行下面缩进的一组语句。 |
| 50 | `             app.load_path(args.config) ` | 恢复 JSON 项目与躯干显示设置，读取文件头核对，再更新 GUI。；参数：args.config。 |
| 51 | `         if args.demo: ` | 检查条件 args.demo；为真时执行下面缩进的一组语句。 |
| 52 | `             app.count.set(str(args.electrodes)) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：str(args.electrodes)。 |
| 53 | `             root.after(150, app.load_demo) ` | 安排稍后执行回调，当前立即返回；参数：150, app.load_demo。 |
| 54 | `         if args.mode: ` | 检查条件 args.mode；为真时执行下面缩进的一组语句。 |
| 55 | `             from gui import PROFILES ` | 从 gui 导入 PROFILES。创建 Tkinter 窗口，收集用户输入，用后台线程启动分析，并把结果交给热图、时间轴及躯干窗口。这里不直接计算 SQI。 |
| 56 | `             app.profile.set(next(k for k,v in PROFILES.items() if v == args.mode)) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：next((k for k, v in PROFILES.items() if v == args.mode))。 |
| 57 | `             app.change_profile() ` | 切换工作流后更新指标列表和提示；脉冲移除 SNR/SINAD/THD 选项，然后清空旧结果。。 |
| 58 | `         root.mainloop() ` | 进入 GUI 事件循环，持续响应点击、重画和定时回调；不是再次运行信号分析。 |
| 59 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 60 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 61 | ` if __name__ == "__main__": ` | 只有直接运行这个文件时才执行下方入口；导入模块只定义类和函数。 |
| 62 | `     main() ` | 调用 main。 |
