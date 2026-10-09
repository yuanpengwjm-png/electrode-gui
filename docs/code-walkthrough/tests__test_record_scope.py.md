# tests/test_record_scope.py：结果范围测试

检查输入确认只属于当前文件，以及单文件/窗口视图不会借用其他文件的颜色。

源码：[tests/test_record_scope.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_record_scope.py>)。本说明对应 130 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `app_for` | [18–28](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_record_scope.py:18>) | 创建隐藏的 GUI 测试实例，加载测试记录，退出 with 时销毁窗口。 |
| `test_checkbox_applies_to_selected_file_and_run_applies_pending_edit` | [32–61](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_record_scope.py:32>) | 逐文件校准确认、保存待编辑内容与未分析文件隔离。 |
| `test_batch_confirmation_reasons_are_attributed_and_single_view_is_isolated` | [63–98](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_record_scope.py:63>) | 整批警告注明来源，单文件不继承另一文件的黄色。 |
| `test_single_record_never_borrows_batch_failure_or_protocol_metrics` | [100–110](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_record_scope.py:100>) | 单文件不能继承整批故障、线性度或重复性结论。 |
| `test_ecg_window_selection_is_preserved` | [112–126](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_record_scope.py:112>) | 整段最差颜色和当前 ECG 窗口颜色应可分别显示。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Regressions for per-file Vpp confirmation, analysis and displayed scope.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from contextlib import contextmanager ` | 从 contextlib 导入 contextmanager。管理 with 的进入/退出和资源清理 |
| 3 | ` from dataclasses import replace ` | 从 dataclasses 导入 replace。自动生成数据类并在数据类/字典之间转换 |
| 4 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 5 | ` import tkinter as tk ` | 导入模块 tkinter（别名 tk）。桌面窗口、控件、文件选择框和消息框 |
| 6 | ` import unittest ` | 导入模块 unittest。自动验证已知输入的程序行为 |
| 7 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 8 | ` from config import AnalysisSettings ` | 从 config 导入 AnalysisSettings。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 9 | ` from gui import ElectrodeQAApp ` | 从 gui 导入 ElectrodeQAApp。创建 Tkinter 窗口，收集用户输入，用后台线程启动分析，并把结果交给热图、时间轴及躯干窗口。这里不直接计算 SQI。 |
| 10 | ` from models import MetricResult ` | 从 models 导入 MetricResult。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 11 | ` from services.analysis_service import AnalysisService ` | 从 services.analysis_service 导入 AnalysisService。验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 |
| 12 | ` from services.demo_data import create_demo, create_mode_demo ` | 从 services.demo_data 导入 create_demo、create_mode_demo。生成已知故障的合成 BDF：幅度偏差、延迟、非线性、重复变化、ECG 漂移、平线、噪声。演示标签不是实验验证结论。 |
| 13 | ` from utils.report_exporter import ReportExporter ` | 从 utils.report_exporter 导入 ReportExporter。生成当前视图的 PNG/CSV，以及完整 JSON、项目配置、各窗口和过零事件表、HTML 报告。 |
| 14 | ` from test_analysis import fixture_folder ` | 从 test_analysis 导入 fixture_folder。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 15 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 16 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 17 | ` @contextmanager ` | @contextmanager 将含 yield 的函数变为 with 可用的资源管理器。 |
| 18 | ` def app_for(records): ` | 定义 app_for(records)。创建隐藏的 GUI 测试实例，加载测试记录，退出 with 时销毁窗口。 定义到这里时不执行函数体。 |
| 19 | `     root = tk.Tk() ` | 创建 Tkinter 的根窗口；按钮和其他控件都挂在这个窗口或其子容器里。 |
| 20 | `     root.withdraw() ` | 隐藏测试窗口。 |
| 21 | `     try: ` | 开始受保护的操作；异常由下面 except 处理，finally 无论成功失败都会执行。 |
| 22 | `         app = ElectrodeQAApp(root) ` | 把结果保存到 app：创建主应用对象，立即运行 __init__ 搭建控件并连接按钮回调；参数：root。 |
| 23 | `         app.records = records ` | 把结果保存到 app.records：records。 |
| 24 | `         app.refresh_records() ` | 重新填充文件列表，默认选择第一条，或在空列表时显示无文件。。 |
| 25 | `         app.initialize_channels() ` | 读取第一份文件头，选择实际存在的电压通道，并设置参考和数量。。 |
| 26 | `         yield app ` | 把 app 暂时交给调用者；上下文退出后继续执行清理。 |
| 27 | `     finally: ` | 不管前面的操作成功还是抛异常，都执行这里的收尾/资源清理。 |
| 28 | `         root.destroy() ` | 销毁窗口及控件。 |
| 29 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 30 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 31 | ` class RecordScopeTests(unittest.TestCase): ` | 定义 RecordScopeTests 类，继承 unittest.TestCase；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 32 | `     def test_checkbox_applies_to_selected_file_and_run_applies_pending_edit(self): ` | 定义 test_checkbox_applies_to_selected_file_and_run_applies_pending_edit(self)。逐文件校准确认、保存待编辑内容与未分析文件隔离。 定义到这里时不执行函数体。 |
| 33 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 34 | `             records = [replace(r, input_confirmed=False) for r in create_demo(folder, 2)[:2]] ` | 把结果保存到 records：从 create_demo(folder, 2)[:2] 逐个取 r，为每项生成 replace(r, input_confirmed=False)。 |
| 35 | `             with app_for(records) as app: ` | 进入资源上下文：调用 app_for；参数：records，对象命名为 app。退出时执行对应清理。 |
| 36 | `                 app.confirmed.set(True) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：True。 |
| 37 | `                 # A duplicate Tk selection event must not reset the user's edit. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 38 | `                 app.select_record() ` | 切换记录时保存上一份编辑，再加载新记录的参数；若它已被分析，切换到该文件自己的结果。。 |
| 39 | `                 self.assertTrue(app.confirmed.get()) ` | 断言条件为真；参数：app.confirmed.get()。 |
| 40 | `                 request = app.prepare() ` | 把结果保存到 request：保存待确认的表单编辑，检查参数，选择本次分析范围，并复制输入防止计算期间被修改。。 |
| 41 | `                 chosen, settings, channels, reference = request ` | 把结果保存到 (chosen, settings, channels, reference)：request。 |
| 42 | `                 self.assertEqual(len(chosen), 1) ` | 断言两者相等，不相等则测试失败；参数：len(chosen), 1。 |
| 43 | `                 self.assertTrue(chosen[0].input_confirmed) ` | 断言条件为真；参数：chosen[0].input_confirmed。 |
| 44 | `                 self.assertFalse(app.records[1].input_confirmed) ` | 断言条件为假；参数：app.records[1].input_confirmed。 |
| 45 | `                 self.assertEqual(app.record_tree.item('0')['values'][-1], 'Yes') ` | 断言两者相等，不相等则测试失败；参数：app.record_tree.item('0')['values'][-1], 'Yes'。 |
| 46 | `                 self.assertEqual(app.record_tree.item('1')['values'][-1], 'No') ` | 断言两者相等，不相等则测试失败；参数：app.record_tree.item('1')['values'][-1], 'No'。 |
| 47 | `                 self.assertEqual(len(app.prepare(all_records=True)[0]), 2)  # Save project retains all files. ` | 断言两者相等，不相等则测试失败；参数：len(app.prepare(all_records=True)[0]), 2。 |
| 48 | `                 result = AnalysisService(settings).analyze(chosen, channels, reference) ` | 把结果保存到 result：台架分支先测整段，再按需逐窗口重复同样的测量，最后做跨记录线性/重复性；ECG 走独立分支。；参数：chosen, channels, reference。 |
| 49 | `                 app.mode.set('Gain error') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Gain error'。 |
| 50 | `                 app.accept_result(result) ` | 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 |
| 51 | `                 self.assertEqual(app.displayed_electrodes()[0].gain.color, 'green') ` | 断言两者相等，不相等则测试失败；参数：app.displayed_electrodes()[0].gain.color, 'green'。 |
| 52 | `                 self.assertNotIn('unconfirmed', app.detail.get('1.0', 'end')) ` | 断言不包含指定项；参数：'unconfirmed', app.detail.get('1.0', 'end')。 |
| 53 | `                 # The second, unprocessed file must not inherit file 1's result or checkbox. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 54 | `                 app.record_tree.selection_set('1') ` | 设置选中行；参数：'1'。 |
| 55 | `                 app.select_record() ` | 切换记录时保存上一份编辑，再加载新记录的参数；若它已被分析，切换到该文件自己的结果。。 |
| 56 | `                 self.assertFalse(app.confirmed.get()) ` | 断言条件为假；参数：app.confirmed.get()。 |
| 57 | `                 self.assertIsNone(app.result) ` | 断言结果是 None；参数：app.result。 |
| 58 | `                 chosen, settings, channels, reference = app.prepare() ` | 把结果保存到 (chosen, settings, channels, reference)：保存待确认的表单编辑，检查参数，选择本次分析范围，并复制输入防止计算期间被修改。。 |
| 59 | `                 result = AnalysisService(settings).analyze(chosen, channels, reference) ` | 把结果保存到 result：台架分支先测整段，再按需逐窗口重复同样的测量，最后做跨记录线性/重复性；ECG 走独立分支。；参数：chosen, channels, reference。 |
| 60 | `                 app.accept_result(result) ` | 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 |
| 61 | `                 self.assertIn('unconfirmed', app.detail.get('1.0', 'end')) ` | 断言包含指定项；参数：'unconfirmed', app.detail.get('1.0', 'end')。 |
| 62 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 63 | `     def test_batch_confirmation_reasons_are_attributed_and_single_view_is_isolated(self): ` | 定义 test_batch_confirmation_reasons_are_attributed_and_single_view_is_isolated(self)。整批警告注明来源，单文件不继承另一文件的黄色。 定义到这里时不执行函数体。 |
| 64 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 65 | `             records = create_demo(folder, 2)[:2] ` | 把结果保存到 records：按索引/键 :2 取 create_demo(folder, 2) 的内容；切片包含起点、不包含终点。 |
| 66 | `             records[1].input_confirmed = False ` | 把结果保存到 records[1].input_confirmed：False（否）。 |
| 67 | `             with app_for(records) as app: ` | 进入资源上下文：调用 app_for；参数：records，对象命名为 app。退出时执行对应清理。 |
| 68 | `                 app.analysis_target.set('All loaded records') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'All loaded records'。 |
| 69 | `                 selected, settings, channels, reference = app.prepare() ` | 把结果保存到 (selected, settings, channels, reference)：保存待确认的表单编辑，检查参数，选择本次分析范围，并复制输入防止计算期间被修改。。 |
| 70 | `                 result = AnalysisService(settings).analyze(selected, channels, reference) ` | 把结果保存到 result：台架分支先测整段，再按需逐窗口重复同样的测量，最后做跨记录线性/重复性；ECG 走独立分支。；参数：selected, channels, reference。 |
| 71 | `                 aggregate = result.electrodes[0].gain ` | 把结果保存到 aggregate：读取 result.electrodes[0] 的 gain 属性。 |
| 72 | `                 self.assertEqual(aggregate.color, 'yellow') ` | 断言两者相等，不相等则测试失败；参数：aggregate.color, 'yellow'。 |
| 73 | `                 self.assertIn(records[1].id + ': Actual input Vpp is unconfirmed', aggregate.message) ` | 断言包含指定项；参数：records[1].id + ': Actual input Vpp is unconfirmed', aggregate.message。 |
| 74 | `                 self.assertNotIn(records[0].id + ':', aggregate.message) ` | 断言不包含指定项；参数：records[0].id + ':', aggregate.message。 |
| 75 | `                 app.accept_result(result) ` | 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 |
| 76 | `                 self.assertEqual(app.scope.get(), 'Record: ' + records[0].id) ` | 断言两者相等，不相等则测试失败；参数：app.scope.get(), 'Record: ' + records[0].id。 |
| 77 | `                 self.assertEqual(app.displayed_electrodes()[0].gain.color, 'green') ` | 断言两者相等，不相等则测试失败；参数：app.displayed_electrodes()[0].gain.color, 'green'。 |
| 78 | `                 # Result selection also selects the corresponding editable record. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 79 | `                 app.scope.set('Record: ' + records[1].id) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Record: ' + records[1].id。 |
| 80 | `                 app.change_scope() ` | 用户选择整段/窗口/整批时暂停播放，同步文件选择，再刷新显示。。 |
| 81 | `                 self.assertEqual(app.selected, 1) ` | 断言两者相等，不相等则测试失败；参数：app.selected, 1。 |
| 82 | `                 self.assertFalse(app.confirmed.get()) ` | 断言条件为假；参数：app.confirmed.get()。 |
| 83 | `                 self.assertEqual(app.displayed_electrodes()[0].gain.color, 'yellow') ` | 断言两者相等，不相等则测试失败；参数：app.displayed_electrodes()[0].gain.color, 'yellow'。 |
| 84 | `                 app.scope.set('All analyzed records / worst case') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'All analyzed records / worst case'。 |
| 85 | `                 app.change_scope() ` | 用户选择整段/窗口/整批时暂停播放，同步文件选择，再刷新显示。。 |
| 86 | `                 self.assertIs(app.displayed_electrodes(), result.electrodes) ` | 断言两者是同一个对象；参数：app.displayed_electrodes(), result.electrodes。 |
| 87 | `                 # Returning to file 1 excludes file 2's warning in details and export. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 88 | `                 app.record_tree.selection_set('0') ` | 设置选中行；参数：'0'。 |
| 89 | `                 app.select_record() ` | 切换记录时保存上一份编辑，再加载新记录的参数；若它已被分析，切换到该文件自己的结果。。 |
| 90 | `                 app.mode.set('Gain error') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Gain error'。 |
| 91 | `                 app.redraw() ` | 从已有结果更新热图、躯干、颜色计数、结果表和详情。。 |
| 92 | `                 self.assertNotIn(records[1].id, app.detail.get('1.0', 'end')) ` | 断言不包含指定项；参数：records[1].id, app.detail.get('1.0', 'end')。 |
| 93 | `                 ReportExporter().save(result, folder/'export', 'gain', ` | 导出当前视图及完整实验结果、窗口表和事件表；HTML 中用户文本先转义。；参数：result, folder / 'export', 'gain', electrodes=app.displayed_electrodes(), scope=app.scope.get()。 |
| 94 | `                                       electrodes=app.displayed_electrodes(), scope=app.scope.get()) ` | 接续第 93 行的同一条语句，不是另起一段算法。 只取当前整段、窗口或整批范围的电极结果；这个函数不重新算指标。。 |
| 95 | `                 data = json.loads((folder/'export/results.json').read_text(encoding='utf-8')) ` | 把结果保存到 data：把 JSON 文本恢复为 Python 数据；参数：(folder / 'export/results.json').read_text(encoding='utf-8')。 |
| 96 | `                 self.assertEqual(data['export_view']['scope'], 'Record: ' + records[0].id) ` | 断言两者相等，不相等则测试失败；参数：data['export_view']['scope'], 'Record: ' + records[0].id。 |
| 97 | `                 self.assertEqual(data['export_view']['electrode_results'][0]['gain']['color'], 'green') ` | 断言两者相等，不相等则测试失败；参数：data['export_view']['electrode_results'][0]['gain']['color'], 'green'。 |
| 98 | `                 self.assertEqual(len(data['runs']), 2) ` | 断言两者相等，不相等则测试失败；参数：len(data['runs']), 2。 |
| 99 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 100 | `     def test_single_record_never_borrows_batch_failure_or_protocol_metrics(self): ` | 定义 test_single_record_never_borrows_batch_failure_or_protocol_metrics(self)。单文件不能继承整批故障、线性度或重复性结论。 定义到这里时不执行函数体。 |
| 101 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 102 | `             records = create_demo(folder, 1) ` | 把结果保存到 records：调用 create_demo；参数：folder, 1。 |
| 103 | `             result = AnalysisService(AnalysisSettings()).analyze(records, ['EXG1'], 'EXG1') ` | 把结果保存到 result：调用 AnalysisService(AnalysisSettings()).analyze；参数：records, ['EXG1'], 'EXG1'。 |
| 104 | `             result.electrodes[0].extra['snr'] = MetricResult('red', 'Failure in another record') ` | 把结果保存到 result.electrodes[0].extra['snr']：打包颜色、原因和指标数值；参数：'red', 'Failure in another record'。 |
| 105 | `             single = result.record_electrodes(records[0].id)[0] ` | 把结果保存到 single：按索引/键 0 取 result.record_electrodes(records[0].id) 的内容。 |
| 106 | `             self.assertEqual(single.extra['snr'].color, 'green') ` | 断言两者相等，不相等则测试失败；参数：single.extra['snr'].color, 'green'。 |
| 107 | `             self.assertEqual(single.linearity.color, 'yellow') ` | 断言两者相等，不相等则测试失败；参数：single.linearity.color, 'yellow'。 |
| 108 | `             self.assertIn('Multi-record', single.linearity.message) ` | 断言包含指定项；参数：'Multi-record', single.linearity.message。 |
| 109 | `             self.assertEqual(result.electrodes[0].linearity.color, 'green') ` | 断言两者相等，不相等则测试失败；参数：result.electrodes[0].linearity.color, 'green'。 |
| 110 | `             self.assertEqual(result.electrodes[0].repetition.color, 'green') ` | 断言两者相等，不相等则测试失败；参数：result.electrodes[0].repetition.color, 'green'。 |
| 111 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 112 | `     def test_ecg_window_selection_is_preserved(self): ` | 定义 test_ecg_window_selection_is_preserved(self)。整段最差颜色和当前 ECG 窗口颜色应可分别显示。 定义到这里时不执行函数体。 |
| 113 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 114 | `             records = create_mode_demo(folder, 3, 'ecg') ` | 把结果保存到 records：按模式选择正弦演示，或生成 30 秒脉冲/ECG 数据并注入特定故障。；参数：folder, 3, 'ecg'。 |
| 115 | `             with app_for(records) as app: ` | 进入资源上下文：调用 app_for；参数：records，对象命名为 app。退出时执行对应清理。 |
| 116 | `                 app.profile.set('Stage 2 - ECG quality') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Stage 2 - ECG quality'。 |
| 117 | `                 app.change_profile() ` | 切换工作流后更新指标列表和提示；脉冲移除 SNR/SINAD/THD 选项，然后清空旧结果。。 |
| 118 | `                 selected, settings, channels, reference = app.prepare() ` | 把结果保存到 (selected, settings, channels, reference)：保存待确认的表单编辑，检查参数，选择本次分析范围，并复制输入防止计算期间被修改。。 |
| 119 | `                 result = AnalysisService(settings).analyze(selected, channels, reference) ` | 把结果保存到 result：台架分支先测整段，再按需逐窗口重复同样的测量，最后做跨记录线性/重复性；ECG 走独立分支。；参数：selected, channels, reference。 |
| 120 | `                 app.accept_result(result) ` | 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 |
| 121 | `                 app.scope.set('Record: ' + records[0].id) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Record: ' + records[0].id。 |
| 122 | `                 self.assertEqual(app.displayed_electrodes()[2].extra['integrity'].color, 'red') ` | 断言两者相等，不相等则测试失败；参数：app.displayed_electrodes()[2].extra['integrity'].color, 'red'。 |
| 123 | `                 label = next(k for k, v in app.result_scopes.items() if v == ('frame', 0)) ` | 把结果保存到 label：取迭代器的下一项或匹配到的第一项；参数：(k for k, v in app.result_scopes.items() if v == ('frame', 0))。 |
| 124 | `                 app.scope.set(label) ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：label。 |
| 125 | `                 app.change_scope() ` | 用户选择整段/窗口/整批时暂停播放，同步文件选择，再刷新显示。。 |
| 126 | `                 self.assertEqual(app.displayed_electrodes()[2].extra['integrity'].color, 'green') ` | 断言两者相等，不相等则测试失败；参数：app.displayed_electrodes()[2].extra['integrity'].color, 'green'。 |
| 127 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 128 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 129 | ` if __name__ == '__main__': ` | 只有直接运行这个文件时才进入启动代码；被 import 时不自动打开窗口。 |
| 130 | `     unittest.main() ` | 调用 unittest.main。 |
