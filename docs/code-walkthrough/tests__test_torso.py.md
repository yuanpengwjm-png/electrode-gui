# tests/test_torso.py：躯干与主窗口联动测试

检查 A–D 组的身体左右和蛇形编号、选点与旋转、双窗口播放互斥、旧结果清除，以及导出/恢复时保持同一窗口和布局。

源码：[tests/test_torso.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_torso.py>)。本说明对应 167 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `torso_record` | [19–25](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_torso.py:19>) | 生成一个两通道合成 BDF，再只修改这份测试文件的标签为 A1 和 D32，使信号故障可映射到躯干前后。 |
| `test_person_sides_back_pairs_and_serpentine_numbering` | [29–54](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_torso.py:29>) | 检查 128 个位置唯一、身体左右、前后配对和中间列反向编号，并检查正面/背面各显示 64 点。 |
| `test_3d_scrubbing_clicks_camera_playback_and_invalidation` | [56–99](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_torso.py:56>) | 检查拖时间轴、选择异常点、相机保留、两个播放器互斥，以及修改参数后清空旧结果。 |
| `test_unmapped_channels_stay_unmapped_and_pick_matches_label` | [101–125](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_torso.py:101>) | 检查 EXG1 不被伪装成 A–D 位置；点击返回正确通道，而拖动只旋转相机。 |
| `test_layout_project_roundtrip_and_export_keep_exact_window` | [127–163](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/tests/test_torso.py:127>) | 检查导出图片/JSON 的窗口一致；布局更改不改变分析值；新旧项目都能恢复合理布局。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """Physical-side mapping and linked 3D GUI/window behavior with synthetic BDFs.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import asdict ` | 从 dataclasses 导入 asdict。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 4 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 5 | ` from types import SimpleNamespace ` | 从 types 导入 SimpleNamespace。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 6 | ` import unittest ` | 导入模块 unittest。自动验证已知输入的程序行为 |
| 7 | ` from unittest.mock import patch ` | 从 unittest.mock 导入 patch。临时替换对象模拟异常或禁止某条路径 |
| 8 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 9 | ` from config import COLORS ` | 从 config 导入 COLORS。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 10 | ` from models import ElectrodeResult, MetricResult ` | 从 models 导入 ElectrodeResult、MetricResult。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 11 | ` from services.analysis_service import AnalysisService ` | 从 services.analysis_service 导入 AnalysisService。验证输入，按每个文件排除设置的末尾时段，再把保留数据送到正弦、脉冲或 ECG 分支，逐通道、逐窗口计算并汇总。 |
| 12 | ` from utils.project_io import save_project ` | 从 utils.project_io 导入 save_project。保存文件清单、参数、通道和参考；恢复时适配部分旧配置，并统一幅度单位。保存的是配置，不是复制原始 BDF。 |
| 13 | ` from views.torso_geometry import TorsoLayout, project, visible ` | 从 views.torso_geometry 导入 TorsoLayout、project、visible。生成示意躯干网格和 A1–D32 位置，再做三维到二维的投影；这些坐标不是 CT 重建或患者实测坐标。 |
| 14 | ` from test_analysis import fixture_folder ` | 从 test_analysis 导入 fixture_folder。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 15 | ` from test_record_scope import app_for ` | 从 test_record_scope 导入 app_for。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 16 | ` from test_windows import sine_record, settings ` | 从 test_windows 导入 sine_record、settings。供本模块后面的函数调用；导入本身不是进行信号分析。 |
| 17 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 18 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 19 | ` def torso_record(folder): ` | 定义 torso_record(folder)。生成一个两通道合成 BDF，再只修改这份测试文件的标签为 A1 和 D32，使信号故障可映射到躯干前后。 定义到这里时不执行函数体。 |
| 20 | `     record = sine_record(folder) ` | 把结果保存到 record：调用 sine_record；参数：folder。 |
| 21 | `     # Relabel only this generated fixture, never a laboratory source. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 22 | `     with Path(record.path).open('r+b') as stream: ` | 进入资源上下文：打开文件或归档成员；参数：'r+b'，对象命名为 stream。退出时执行对应清理。 |
| 23 | `         stream.seek(256) ` | 调用 stream.seek；参数：256。 |
| 24 | `         stream.write(b'A1'.ljust(16) + b'D32'.ljust(16)) ` | 向输出流写入字节；参数：b'A1'.ljust(16) + b'D32'.ljust(16)。 |
| 25 | `     return record ` | 结束当前函数并返回：record。 |
| 26 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 27 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 28 | ` class TorsoTests(unittest.TestCase): ` | 定义 TorsoTests 类，继承 unittest.TestCase；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 29 | `     def test_person_sides_back_pairs_and_serpentine_numbering(self): ` | 定义 test_person_sides_back_pairs_and_serpentine_numbering(self)。检查 128 个位置唯一、身体左右、前后配对和中间列反向编号，并检查正面/背面各显示 64 点。 定义到这里时不执行函数体。 |
| 30 | `         positions = TorsoLayout().positions() ` | 把结果保存到 positions：调用 TorsoLayout().positions。 |
| 31 | `         self.assertEqual(set(positions), {f'{b}{n}' for b in 'ABCD' for n in range(1,33)}) ` | 断言两者相等，不相等则测试失败；参数：set(positions), {f'{b}{n}' for b in 'ABCD' for n in range(1, 33)}。 |
| 32 | `         self.assertEqual(len({p['point'] for p in positions.values()}), 128) ` | 断言两者相等，不相等则测试失败；参数：len({p['point'] for p in positions.values()}), 128。 |
| 33 | `         for bank in 'AC': ` | 遍历 'AC'，每次把一项赋给 bank，执行下面缩进的循环体。 |
| 34 | `             self.assertTrue(all(positions[f'{bank}{n}']['point'][0] > 0 for n in range(1,33))) ` | 断言条件为真；参数：all((positions[f'{bank}{n}']['point'][0] > 0 for n in range(1, 33)))。 |
| 35 | `         for bank in 'BD': ` | 遍历 'BD'，每次把一项赋给 bank，执行下面缩进的循环体。 |
| 36 | `             self.assertTrue(all(positions[f'{bank}{n}']['point'][0] < 0 for n in range(1,33))) ` | 断言条件为真；参数：all((positions[f'{bank}{n}']['point'][0] < 0 for n in range(1, 33)))。 |
| 37 | `         for front,back in (('A','C'),('B','D')): ` | 遍历 (('A', 'C'), ('B', 'D'))，每次把一项赋给 (front, back)，执行下面缩进的循环体。 |
| 38 | `             for n in range(1,33): ` | 遍历 range(1, 33)，每次把一项赋给 n，执行下面缩进的循环体。 |
| 39 | `                 a,b = (positions[f'{name}{n}']['point'] for name in (front,back)) ` | 把结果保存到 (a, b)：从 (front, back) 逐个取 name，为每项生成 positions[f'{name}{n}']['point']。 |
| 40 | `                 self.assertEqual(a, (b[0],-b[1],b[2])) ` | 断言两者相等，不相等则测试失败；参数：a, (b[0], -b[1], b[2])。 |
| 41 | `         for bank in 'ABCD': ` | 遍历 'ABCD'，每次把一项赋给 bank，执行下面缩进的循环体。 |
| 42 | `             for lo,hi in ((1,10),(11,21),(22,32)): ` | 遍历 ((1, 10), (11, 21), (22, 32))，每次把一项赋给 (lo, hi)，执行下面缩进的循环体。 |
| 43 | `                 zs = [positions[f'{bank}{n}']['point'][2] for n in range(lo,hi+1)] ` | 把结果保存到 zs：从 range(lo, hi + 1) 逐个取 n，为每项生成 positions[f'{bank}{n}']['point'][2]。 |
| 44 | `                 self.assertEqual(zs, sorted(zs,reverse=lo==11)) ` | 断言两者相等，不相等则测试失败；参数：zs, sorted(zs, reverse=lo == 11)。 |
| 45 | `         front_names = ('B32','B11','B10','A10','A11','A32') ` | 把结果保存到 front_names：组装元组：('B32', 'B11', 'B10', 'A10', 'A11', 'A32')。 |
| 46 | `         front_x = [project(positions[n]['point'],0)[0] for n in front_names] ` | 把结果保存到 front_x：从 front_names 逐个取 n，为每项生成 project(positions[n]['point'], 0)[0]。 |
| 47 | `         self.assertEqual(front_x, sorted(front_x)) ` | 断言两者相等，不相等则测试失败；参数：front_x, sorted(front_x)。 |
| 48 | `         back_names = ('C32','C11','C10','D10','D11','D32') ` | 把结果保存到 back_names：组装元组：('C32', 'C11', 'C10', 'D10', 'D11', 'D32')。 |
| 49 | `         back_x = [project(positions[n]['point'],180)[0] for n in back_names] ` | 把结果保存到 back_x：从 back_names 逐个取 n，为每项生成 project(positions[n]['point'], 180)[0]。 |
| 50 | `         self.assertEqual(back_x, sorted(back_x)) ` | 断言两者相等，不相等则测试失败；参数：back_x, sorted(back_x)。 |
| 51 | `         for yaw,face in ((0,'Front'),(180,'Back')): ` | 遍历 ((0, 'Front'), (180, 'Back'))，每次把一项赋给 (yaw, face)，执行下面缩进的循环体。 |
| 52 | `             seen = [p for p in positions.values() if visible(p['normal'],yaw,6)] ` | 把结果保存到 seen：从 positions.values() 逐个取 p，仅保留 visible(p['normal'], yaw, 6)，为每项生成 p。 |
| 53 | `             self.assertEqual(len(seen),64) ` | 断言两者相等，不相等则测试失败；参数：len(seen), 64。 |
| 54 | `             self.assertTrue(all(p['face']==face for p in seen)) ` | 断言条件为真；参数：all((p['face'] == face for p in seen))。 |
| 55 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 56 | `     def test_3d_scrubbing_clicks_camera_playback_and_invalidation(self): ` | 定义 test_3d_scrubbing_clicks_camera_playback_and_invalidation(self)。检查拖时间轴、选择异常点、相机保留、两个播放器互斥，以及修改参数后清空旧结果。 定义到这里时不执行函数体。 |
| 57 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 58 | `             record = torso_record(folder) ` | 把结果保存到 record：调用 torso_record；参数：folder。 |
| 59 | `             result = AnalysisService(settings()).analyze([record], ['A1','D32'], 'A1') ` | 把结果保存到 result：调用 AnalysisService(settings()).analyze；参数：[record], ['A1', 'D32'], 'A1'。 |
| 60 | `             with app_for([record]) as app: ` | 进入资源上下文：调用 app_for；参数：[record]，对象命名为 app。退出时执行对应清理。 |
| 61 | `                 app.mode.set('Gain error'); app.accept_result(result); app.open_torso() ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Gain error'。 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 打开或抬起躯干窗口，连接选择回调，与主窗口共享指标和窗口结果。。 |
| 62 | `                 popup = app.torso_window ` | 把结果保存到 popup：读取 app 的 torso_window 属性。 |
| 63 | `                 popup.timeline._scrub('1') ` | 调用 popup.timeline._scrub；参数：'1'。 |
| 64 | `                 self.assertEqual(app.result_scopes[app.scope.get()], ('frame',1)) ` | 断言两者相等，不相等则测试失败；参数：app.result_scopes[app.scope.get()], ('frame', 1)。 |
| 65 | `                 self.assertEqual(popup.view.electrodes['D32'].gain.color,'red') ` | 断言两者相等，不相等则测试失败；参数：popup.view.electrodes['D32'].gain.color, 'red'。 |
| 66 | `                 self.assertIn('D32',popup.alerts.get_children()) ` | 断言包含指定项；参数：'D32', popup.alerts.get_children()。 |
| 67 | `                 popup.alerts.selection_set('D32'); popup.pick_alert() ` | 设置选中行；参数：'D32'。 调用 popup.pick_alert。 |
| 68 | `                 self.assertEqual(popup.view.yaw,180) ` | 断言两者相等，不相等则测试失败；参数：popup.view.yaw, 180。 |
| 69 | `                 self.assertEqual(app.focused_electrode,'D32') ` | 断言两者相等，不相等则测试失败；参数：app.focused_electrode, 'D32'。 |
| 70 | `                 self.assertIn('10-20 s',popup.detail.get('1.0','end')) ` | 断言包含指定项；参数：'10-20 s', popup.detail.get('1.0', 'end')。 |
| 71 | `                 markers = popup.view.scene(800,1000)[1] ` | 把结果保存到 markers：按索引/键 1 取 popup.view.scene(800, 1000) 的内容。 |
| 72 | `                 active = [m for m in markers if m['active']] ` | 把结果保存到 active：从 markers 逐个取 m，仅保留 m['active']，为每项生成 m。 |
| 73 | `                 self.assertEqual([m['name'] for m in active],['D32']) ` | 断言两者相等，不相等则测试失败；参数：[m['name'] for m in active], ['D32']。 |
| 74 | `                 self.assertEqual(active[0]['color'],COLORS['red']) ` | 断言两者相等，不相等则测试失败；参数：active[0]['color'], COLORS['red']。 |
| 75 | `                 self.assertEqual(sum(not m['active'] for m in markers),63) ` | 断言两者相等，不相等则测试失败；参数：sum((not m['active'] for m in markers)), 63。 |
| 76 | `                 # A second window changes data while preserving camera and focus. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 77 | `                 app.select_window(0) ` | 将时间轴提供的全局窗口索引映射到显示范围，并同步主窗口和躯干窗口。；参数：0。 |
| 78 | `                 self.assertEqual(popup.view.yaw,180) ` | 断言两者相等，不相等则测试失败；参数：popup.view.yaw, 180。 |
| 79 | `                 self.assertEqual(popup.view.selected,'D32') ` | 断言两者相等，不相等则测试失败；参数：popup.view.selected, 'D32'。 |
| 80 | `                 self.assertEqual(popup.view.electrodes['D32'].gain.color,'green') ` | 断言两者相等，不相等则测试失败；参数：popup.view.electrodes['D32'].gain.color, 'green'。 |
| 81 | `                 self.assertIn('0-10 s',popup.detail.get('1.0','end')) ` | 断言包含指定项；参数：'0-10 s', popup.detail.get('1.0', 'end')。 |
| 82 | `                 self.assertNotIn('D32',popup.alerts.get_children()) ` | 断言不包含指定项；参数：'D32', popup.alerts.get_children()。 |
| 83 | `                 popup.timeline.toggle() ` | 调用 popup.timeline.toggle。 |
| 84 | `                 self.assertTrue(popup.timeline.playing) ` | 断言条件为真；参数：popup.timeline.playing。 |
| 85 | `                 self.assertFalse(app.timeline.playing) ` | 断言条件为假；参数：app.timeline.playing。 |
| 86 | `                 app.timeline.toggle() ` | 调用 app.timeline.toggle。 |
| 87 | `                 self.assertTrue(app.timeline.playing) ` | 断言条件为真；参数：app.timeline.playing。 |
| 88 | `                 self.assertFalse(popup.timeline.playing) ` | 断言条件为假；参数：popup.timeline.playing。 |
| 89 | `                 self.assertIsNone(popup.timeline.timer) ` | 断言结果是 None；参数：popup.timeline.timer。 |
| 90 | `                 popup.timeline.toggle() ` | 调用 popup.timeline.toggle。 |
| 91 | `                 self.assertFalse(app.timeline.playing) ` | 断言条件为假；参数：app.timeline.playing。 |
| 92 | `                 self.assertIsNone(app.timeline.timer) ` | 断言结果是 None；参数：app.timeline.timer。 |
| 93 | `                 app.limit_vars['bench_window_s'].set('8') ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'8'。 |
| 94 | `                 self.assertIsNone(app.result) ` | 断言结果是 None；参数：app.result。 |
| 95 | `                 self.assertFalse(popup.timeline.playing) ` | 断言条件为假；参数：popup.timeline.playing。 |
| 96 | `                 self.assertIsNone(popup.timeline.timer) ` | 断言结果是 None；参数：popup.timeline.timer。 |
| 97 | `                 self.assertEqual(popup.view.electrodes,{}) ` | 断言两者相等，不相等则测试失败；参数：popup.view.electrodes, {}。 |
| 98 | `                 self.assertEqual(popup.alerts.get_children(),()) ` | 断言两者相等，不相等则测试失败；参数：popup.alerts.get_children(), ()。 |
| 99 | `                 popup.close(); self.assertIsNone(app.torso_window) ` | 关闭资源或窗口。 断言结果是 None；参数：app.torso_window。 |
| 100 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 101 | `     def test_unmapped_channels_stay_unmapped_and_pick_matches_label(self): ` | 定义 test_unmapped_channels_stay_unmapped_and_pick_matches_label(self)。检查 EXG1 不被伪装成 A–D 位置；点击返回正确通道，而拖动只旋转相机。 定义到这里时不执行函数体。 |
| 102 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 103 | `             with app_for([torso_record(folder)]) as app: ` | 进入资源上下文：调用 app_for；参数：[torso_record(folder)]，对象命名为 app。退出时执行对应清理。 |
| 104 | `                 app.open_torso(); popup=app.torso_window ` | 打开或抬起躯干窗口，连接选择回调，与主窗口共享指标和窗口结果。。 把结果保存到 popup：读取 app 的 torso_window 属性。 |
| 105 | `                 green=MetricResult('green','Synthetic pass') ` | 把结果保存到 green：打包颜色、原因和指标数值；参数：'green', 'Synthetic pass'。 |
| 106 | `                 red=MetricResult('red','Synthetic fault') ` | 把结果保存到 red：打包颜色、原因和指标数值；参数：'red', 'Synthetic fault'。 |
| 107 | `                 a=ElectrodeResult('A17',red,green,green,green) ` | 把结果保存到 a：打包一个电极的各项指标；参数：'A17', red, green, green, green。 |
| 108 | `                 exg=ElectrodeResult('EXG1',red,green,green,green) ` | 把结果保存到 exg：打包一个电极的各项指标；参数：'EXG1', red, green, green, green。 |
| 109 | `                 popup.show([a,exg],'gain','SYNTHETIC TEST',['Gain error'],None,[],None,'') ` | 调用 popup.show；参数：[a, exg], 'gain', 'SYNTHETIC TEST', ['Gain error'], None, [], None, ''。 |
| 110 | `                 self.assertIn('Unmapped: EXG1',popup.mapping_notice.get()) ` | 断言包含指定项；参数：'Unmapped: EXG1', popup.mapping_notice.get()。 |
| 111 | `                 self.assertEqual(popup.alerts.item('EXG1')['values'][1],'Unmapped') ` | 断言两者相等，不相等则测试失败；参数：popup.alerts.item('EXG1')['values'][1], 'Unmapped'。 |
| 112 | `                 popup.update_idletasks() ` | 调用 popup.update_idletasks。 |
| 113 | `                 marker=next(m for m in popup.view.hits if m['name']=='A17') ` | 把结果保存到 marker：取迭代器的下一项或匹配到的第一项；参数：(m for m in popup.view.hits if m['name'] == 'A17')。 |
| 114 | `                 event=SimpleNamespace(x=marker['x'],y=marker['y']) ` | 把结果保存到 event：调用 SimpleNamespace；参数：x=marker['x'], y=marker['y']。 |
| 115 | `                 with patch.object(popup.view,'on_select') as picked: ` | 进入资源上下文：调用 patch.object；参数：popup.view, 'on_select'，对象命名为 picked。退出时执行对应清理。 |
| 116 | `                     popup.view.press(event); popup.view.release(event) ` | 调用 popup.view.press；参数：event。 调用 popup.view.release；参数：event。 |
| 117 | `                     picked.assert_called_once_with(a) ` | 调用 picked.assert_called_once_with；参数：a。 |
| 118 | `                 # A drag rotates the model instead of opening the wrong channel. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 119 | `                 with patch.object(popup.view,'on_select') as picked: ` | 进入资源上下文：调用 patch.object；参数：popup.view, 'on_select'，对象命名为 picked。退出时执行对应清理。 |
| 120 | `                     popup.view.press(event) ` | 调用 popup.view.press；参数：event。 |
| 121 | `                     moved=SimpleNamespace(x=event.x+100,y=event.y+5) ` | 把结果保存到 moved：调用 SimpleNamespace；参数：x=event.x + 100, y=event.y + 5。 |
| 122 | `                     popup.view.motion(moved); popup.view.release(moved) ` | 调用 popup.view.motion；参数：moved。 调用 popup.view.release；参数：moved。 |
| 123 | `                     picked.assert_not_called() ` | 调用 picked.assert_not_called。 |
| 124 | `                 self.assertEqual(popup.view.yaw,50) ` | 断言两者相等，不相等则测试失败；参数：popup.view.yaw, 50。 |
| 125 | `                 popup.close() ` | 关闭资源或窗口。 |
| 126 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 127 | `     def test_layout_project_roundtrip_and_export_keep_exact_window(self): ` | 定义 test_layout_project_roundtrip_and_export_keep_exact_window(self)。检查导出图片/JSON 的窗口一致；布局更改不改变分析值；新旧项目都能恢复合理布局。 定义到这里时不执行函数体。 |
| 128 | `         with fixture_folder() as folder: ` | 进入资源上下文：调用 fixture_folder，对象命名为 folder。退出时执行对应清理。 |
| 129 | `             record=torso_record(folder) ` | 把结果保存到 record：调用 torso_record；参数：folder。 |
| 130 | `             result=AnalysisService(settings()).analyze([record],['A1','D32'],'A1') ` | 把结果保存到 result：调用 AnalysisService(settings()).analyze；参数：[record], ['A1', 'D32'], 'A1'。 |
| 131 | `             with app_for([record]) as app: ` | 进入资源上下文：调用 app_for；参数：[record]，对象命名为 app。退出时执行对应清理。 |
| 132 | `                 app.mode.set('Gain error');app.accept_result(result);app.open_torso() ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Gain error'。 保存完整结果，建立文件/窗口/整批显示范围，优先选择第一完整窗口，再刷新视图。；参数：result。 打开或抬起躯干窗口，连接选择回调，与主窗口共享指标和窗口结果。。 |
| 133 | `                 popup=app.torso_window ` | 把结果保存到 popup：读取 app 的 torso_window 属性。 |
| 134 | `                 popup.timeline._scrub('1');popup.view.face('Back') ` | 调用 popup.timeline._scrub；参数：'1'。 调用 popup.view.face；参数：'Back'。 |
| 135 | `                 # Changing the display layout never changes measured values. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 136 | `                 popup.order.set('Outer low at top');popup.change_layout() ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Outer low at top'。 调用 popup.change_layout。 |
| 137 | `                 self.assertIs(app.result,result) ` | 断言两者是同一个对象；参数：app.result, result。 |
| 138 | `                 self.assertTrue(app.torso_layout.top_to_bottom) ` | 断言条件为真；参数：app.torso_layout.top_to_bottom。 |
| 139 | `                 export=folder/'export';export.mkdir() ` | 把结果保存到 export：在 Path 路径 folder 后拼接 'export'；这里的 / 是路径拼接。 创建目录。 |
| 140 | `                 with patch('gui.filedialog.askdirectory',return_value=str(export)): ` | 进入资源上下文：调用 patch；参数：'gui.filedialog.askdirectory', return_value=str(export)。退出时执行对应清理。 |
| 141 | `                     app.export() ` | 暂停回放，选择输出文件夹，导出当前视图及完整结果；躯干窗口打开时同时保存其图片和布局。。 |
| 142 | `                 self.assertTrue((export/'torso_view.png').is_file()) ` | 断言条件为真；参数：(export / 'torso_view.png').is_file()。 |
| 143 | `                 layout=json.loads((export/'torso_layout.json').read_text()) ` | 把结果保存到 layout：把 JSON 文本恢复为 Python 数据；参数：(export / 'torso_layout.json').read_text()。 |
| 144 | `                 self.assertTrue(layout['schematic']) ` | 断言条件为真；参数：layout['schematic']。 |
| 145 | `                 self.assertEqual(layout['camera']['yaw'],180) ` | 断言两者相等，不相等则测试失败；参数：layout['camera']['yaw'], 180。 |
| 146 | `                 self.assertIn('10-20 s',layout['scope']) ` | 断言包含指定项；参数：'10-20 s', layout['scope']。 |
| 147 | `                 self.assertEqual(layout['metric'],'gain') ` | 断言两者相等，不相等则测试失败；参数：layout['metric'], 'gain'。 |
| 148 | `                 self.assertEqual(len(layout['positions']),128) ` | 断言两者相等，不相等则测试失败；参数：len(layout['positions']), 128。 |
| 149 | `                 data=json.loads((export/'results.json').read_text()) ` | 把结果保存到 data：把 JSON 文本恢复为 Python 数据；参数：(export / 'results.json').read_text()。 |
| 150 | `                 self.assertEqual(data['export_view']['scope'],layout['scope']) ` | 断言两者相等，不相等则测试失败；参数：data['export_view']['scope'], layout['scope']。 |
| 151 | `                 project=json.loads((export/'project.json').read_text()) ` | 把结果保存到 project：把 JSON 文本恢复为 Python 数据；参数：(export / 'project.json').read_text()。 |
| 152 | `                 self.assertEqual(project['display']['torso'],asdict(app.torso_layout)) ` | 断言两者相等，不相等则测试失败；参数：project['display']['torso'], asdict(app.torso_layout)。 |
| 153 | `                 popup.order.set('Outer low at bottom');popup.change_layout() ` | 给界面变量/控件设置新值；可能触发已注册的变化回调；参数：'Outer low at bottom'。 调用 popup.change_layout。 |
| 154 | `                 app.load_path(export/'project.json') ` | 恢复 JSON 项目与躯干显示设置，读取文件头核对，再更新 GUI。；参数：export / 'project.json'。 |
| 155 | `                 self.assertTrue(app.torso_layout.top_to_bottom) ` | 断言条件为真；参数：app.torso_layout.top_to_bottom。 |
| 156 | `                 self.assertTrue(popup.layout.top_to_bottom) ` | 断言条件为真；参数：popup.layout.top_to_bottom。 |
| 157 | `                 self.assertIsNone(app.result) ` | 断言结果是 None；参数：app.result。 |
| 158 | `                 # Older projects without a display block load the user's defaults. ` | 注释：给阅读者说明设计意图，不会作为 Python 指令执行。 |
| 159 | `                 old=folder/'old-project.json' ` | 把结果保存到 old：在 Path 路径 folder 后拼接 'old-project.json'；这里的 / 是路径拼接。 |
| 160 | `                 save_project(old,[record],settings(),['A1','D32'],'A1') ` | 把记录和设置的数据类转成 JSON，保留通道、参考与可选布局信息。；参数：old, [record], settings(), ['A1', 'D32'], 'A1'。 |
| 161 | `                 app.load_path(old) ` | 恢复 JSON 项目与躯干显示设置，读取文件头核对，再更新 GUI。；参数：old。 |
| 162 | `                 self.assertEqual(app.torso_layout,TorsoLayout()) ` | 断言两者相等，不相等则测试失败；参数：app.torso_layout, TorsoLayout()。 |
| 163 | `                 popup.close() ` | 关闭资源或窗口。 |
| 164 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 165 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 166 | ` if __name__ == '__main__': ` | 只有直接运行这个文件时才进入启动代码；被 import 时不自动打开窗口。 |
| 167 | `     unittest.main() ` | 调用 unittest.main。 |
