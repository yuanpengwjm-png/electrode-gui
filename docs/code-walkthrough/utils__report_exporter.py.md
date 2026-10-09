# utils/report_exporter.py：导出

生成当前视图的 PNG/CSV，以及完整 JSON、项目配置、各窗口和过零事件表、HTML 报告。

源码：[utils/report_exporter.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/report_exporter.py>)。本说明对应 100 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `_csv` | [14–18](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/report_exporter.py:14>) | 按统一表头写入 UTF-8 BOM 的 CSV，newline='' 避免 Windows 空白行。 |
| `save` | [20–99](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/utils/report_exporter.py:20>) | 导出当前视图及完整实验结果、窗口表和事件表；HTML 中用户文本先转义。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """English, mode-aware exports. Numerical details and exact display scope are retained.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from dataclasses import asdict ` | 从 dataclasses 导入 asdict。自动生成数据类并在数据类/字典之间转换 |
| 3 | ` from pathlib import Path ` | 从 pathlib 导入 Path。用 Path 处理文件和目录 |
| 4 | ` import csv ` | 导入模块 csv。读写表格 CSV |
| 5 | ` import html ` | 导入模块 html。转义 HTML 文本，防止文件名被当成标签 |
| 6 | ` import json ` | 导入模块 json。读写结构化 JSON |
| 7 | ` from config import COLOR_LABELS, AnalysisSettings, BENCH_VIEWS, ECG_VIEWS ` | 从 config 导入 COLOR_LABELS、AnalysisSettings、BENCH_VIEWS、ECG_VIEWS。保存模式、窗口长度、指标限值和显示名称；validate 拦截非法设置，color 处理上限型指标。这里的默认值是项目设置，不是普适标准。 |
| 8 | ` from views.heatmap_view import HeatmapRenderer ` | 从 views.heatmap_view 导入 HeatmapRenderer。读取计算完成的颜色，画可点击圆点；另有不依赖 Tk 窗口的 PNG 导出器。网格顺序不是身体坐标。 |
| 9 | ` from utils.project_io import save_project ` | 从 utils.project_io 导入 save_project。保存文件清单、参数、通道和参考；恢复时适配部分旧配置，并统一幅度单位。保存的是配置，不是复制原始 BDF。 |
| 10 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 11 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 12 | ` class ReportExporter: ` | 定义 ReportExporter 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 13 | `     @staticmethod ` | @staticmethod 表示该方法不依赖 self，可直接通过类调用。 |
| 14 | `     def _csv(path, rows, headers): ` | 定义 _csv(path, rows, headers)。按统一表头写入 UTF-8 BOM 的 CSV，newline='' 避免 Windows 空白行。 定义到这里时不执行函数体。 |
| 15 | `         with path.open("w", newline="", encoding="utf-8-sig") as stream: ` | 进入资源上下文：打开文件或归档成员；参数：'w', newline='', encoding='utf-8-sig'，对象命名为 stream。退出时执行对应清理。 |
| 16 | `             writer = csv.DictWriter(stream, fieldnames=headers) ` | 把结果保存到 writer：调用 csv.DictWriter；参数：stream, fieldnames=headers。 |
| 17 | `             writer.writeheader() ` | 调用 writer.writeheader。 |
| 18 | `             writer.writerows(rows) ` | 调用 writer.writerows；参数：rows。 |
| 19 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 20 | `     def save(self, result, folder, mode="current", title="Electrode QA", electrodes=None, scope="All records", display=None): ` | 定义 save(self, result, folder, mode='current', title='Electrode QA', electrodes=None, scope='All records', display=None)。导出当前视图及完整实验结果、窗口表和事件表；HTML 中用户文本先转义。 定义到这里时不执行函数体。 |
| 21 | `         folder = Path(folder) ` | 把结果保存到 folder：构造路径对象；参数：folder。 |
| 22 | `         folder.mkdir(parents=True, exist_ok=True) ` | 创建目录；参数：parents=True, exist_ok=True。 |
| 23 | `         electrodes = result.electrodes if electrodes is None else electrodes ` | 把结果保存到 electrodes：若 electrodes is None，用 result.electrodes；否则用 electrodes。 |
| 24 | `         ecg = result.settings["analysis_mode"] == "ecg" ` | 把结果保存到 ecg：result.settings['analysis_mode'] == 'ecg'。 |
| 25 | `         columns = dict(ECG_VIEWS if ecg else BENCH_VIEWS) ` | 把结果保存到 columns：组装键值字典；参数：ECG_VIEWS if ecg else BENCH_VIEWS。 |
| 26 | `         if result.settings["analysis_mode"] == "bench_pulse": ` | 检查条件 result.settings['analysis_mode'] == 'bench_pulse'；为真时执行下面缩进的一组语句。 |
| 27 | `             for label in ("SNR", "SINAD", "THD"): ` | 遍历 ('SNR', 'SINAD', 'THD')，每次把一项赋给 label，执行下面缩进的循环体。 |
| 28 | `                 columns.pop(label) ` | 取出并移除指定项；参数：label。 |
| 29 | `         HeatmapRenderer().save(electrodes, mode, folder/"heatmap.png", title+"\n"+scope) ` | 调用 HeatmapRenderer().save；参数：electrodes, mode, folder / 'heatmap.png', title + '\n' + scope。 |
| 30 | `         payload = asdict(result) ` | 把结果保存到 payload：把数据类递归转换成字典；参数：result。 |
| 31 | `         payload["export_view"] = dict(metric=mode, scope=scope, electrode_results=[asdict(e) for e in electrodes]) ` | 把结果保存到 payload['export_view']：组装键值字典；参数：metric=mode, scope=scope, electrode_results=[asdict(e) for e in electrodes]。 |
| 32 | `         (folder/"results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8") ` | 写入文本文件；参数：json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8'。 |
| 33 | `         save_project(folder/"project.json", [r.record for r in result.runs], AnalysisSettings(**result.settings), ` | 把记录和设置的数据类转成 JSON，保留通道、参考与可选布局信息。；参数：folder / 'project.json', [r.record for r in result.runs], AnalysisSettings(**result.settings), [r.name for r in result.electrodes], result.refere…（完整表达式见左栏）。 |
| 34 | `                      [r.name for r in result.electrodes], result.reference, display=display) ` | 接续第 33 行的同一条语句，不是另起一段算法。 把记录和设置的数据类转成 JSON，保留通道、参考与可选布局信息。；参数：folder / 'project.json', [r.record for r in result.runs], AnalysisSettings(**result.settings), [r.name for r in result.electrodes], result.refere…（完整表达式见左栏）。 |
| 35 | `         rows = [] ` | 把结果保存到 rows：组装列表：[]。 |
| 36 | `         for electrode in electrodes: ` | 遍历 electrodes，每次把一项赋给 electrode，执行下面缩进的循环体。 |
| 37 | `             metric = electrode.metric(mode) ` | 把结果保存到 metric：调用 electrode.metric；参数：mode。 |
| 38 | `             row = dict(electrode=electrode.name, color=metric.color, explanation=metric.message, scope=scope) ` | 把结果保存到 row：组装键值字典；参数：electrode=electrode.name, color=metric.color, explanation=metric.message, scope=scope。 |
| 39 | `             for key in columns.values(): ` | 遍历 columns.values()，每次把一项赋给 key，执行下面缩进的循环体。 |
| 40 | `                 row[key] = electrode.metric(key).color ` | 把结果保存到 row[key]：读取 electrode.metric(key) 的 color 属性。 |
| 41 | `                 row[key+"_reason"] = electrode.metric(key).message ` | 把结果保存到 row[key + '_reason']：读取 electrode.metric(key) 的 message 属性。 |
| 42 | `             rows.append(row) ` | 把一项加入列表末尾；参数：row。 |
| 43 | `         self._csv(folder/"electrodes.csv", rows, list(rows[0])) ` | 按统一表头写入 UTF-8 BOM 的 CSV，newline='' 避免 Windows 空白行。；参数：folder / 'electrodes.csv', rows, list(rows[0])。 |
| 44 | `         pairs, counts, spectral = [], [], [] ` | 把结果保存到 (pairs, counts, spectral)：组装元组：([], [], [])。 |
| 45 | `         count_headers = ["record","electrode","reference","event_definition","sample_period_ms","rising_count","falling_count", ` | 把结果保存到 count_headers：组装列表：['record', 'electrode', 'reference', 'event_definition', 'sample_period_ms', 'rising_count', 'falling_count', 'rising_paired', 'falling_paired', 'rising_median_…（完整表达式见左栏）。 |
| 46 | `                          "rising_paired","falling_paired","rising_median_ms","falling_median_ms","max_direction_p95_ms","jitter_ms"] ` | 接续第 45 行的同一条语句，不是另起一段算法。 把结果保存到 count_headers：组装列表：['record', 'electrode', 'reference', 'event_definition', 'sample_period_ms', 'rising_count', 'falling_count', 'rising_paired', 'falling_paired', 'rising_median_…（完整表达式见左栏）。 |
| 47 | `         for run in result.runs: ` | 遍历 result.runs，每次把一项赋给 run，执行下面缩进的循环体。 |
| 48 | `             for channel, data in run.channels.items(): ` | 遍历 run.channels.items()，每次把一项赋给 (channel, data)，执行下面缩进的循环体。 |
| 49 | `                 if "sync" not in data: ` | 检查条件 'sync' not in data；为真时执行下面缩进的一组语句。 |
| 50 | `                     continue ` | 跳过本轮后续操作，进入下一轮；避免把不满足条件的数据继续用于计算。 |
| 51 | `                 v = data["sync"].values ` | 把结果保存到 v：读取 data['sync'] 的 values 属性。 |
| 52 | `                 counts.append(dict(record=run.record.id, electrode=channel, reference=result.reference, ` | 把一项加入列表末尾；参数：dict(record=run.record.id, electrode=channel, reference=result.reference, event_definition=v.get('event_definition'), sample_period_ms=v.get('sam…（完整表达式见左栏）。 |
| 53 | `                     event_definition=v.get("event_definition"), sample_period_ms=v.get("sample_period_ms"), ` | 接续第 52 行的同一条语句，不是另起一段算法。 读取当前值；若是 dict.get，缺少键时可返回指定默认值；参数：'event_definition'。 |
| 54 | `                     rising_count=v["rising_count"], falling_count=v["falling_count"], ` | 接续第 52 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(record=run.record.id, electrode=channel, reference=result.reference, event_definition=v.get('event_definition'), sample_period_ms=v.get('sam…（完整表达式见左栏）。 |
| 55 | `                     rising_paired=v["directions"]["rising"]["paired_count"], falling_paired=v["directions"]["falling"]["paired_count"], ` | 接续第 52 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(record=run.record.id, electrode=channel, reference=result.reference, event_definition=v.get('event_definition'), sample_period_ms=v.get('sam…（完整表达式见左栏）。 |
| 56 | `                     rising_median_ms=v["directions"]["rising"]["median_ms"], falling_median_ms=v["directions"]["falling"]["median_ms"], ` | 接续第 52 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(record=run.record.id, electrode=channel, reference=result.reference, event_definition=v.get('event_definition'), sample_period_ms=v.get('sam…（完整表达式见左栏）。 |
| 57 | `                     max_direction_p95_ms=v["max_direction_p95_ms"], jitter_ms=v["jitter_ms"])) ` | 接续第 52 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(record=run.record.id, electrode=channel, reference=result.reference, event_definition=v.get('event_definition'), sample_period_ms=v.get('sam…（完整表达式见左栏）。 |
| 58 | `                 pairs.extend([dict(record=run.record.id,electrode=channel,reference=result.reference,**p) for p in v["pairs"]]) ` | 把多项逐个加入列表；参数：[dict(record=run.record.id, electrode=channel, reference=result.reference, **p) for p in v['pairs']]。 |
| 59 | `                 for key, metric in data.get("extra",{}).items(): ` | 遍历 data.get('extra', {}).items()，每次把一项赋给 (key, metric)，执行下面缩进的循环体。 |
| 60 | `                     spectral.append(dict(record=run.record.id,electrode=channel,metric=key,color=metric.color, ` | 把一项加入列表末尾；参数：dict(record=run.record.id, electrode=channel, metric=key, color=metric.color, reason=metric.message, values_json=json.dumps(metric.values, allow_…（完整表达式见左栏）。 |
| 61 | `                                          reason=metric.message,values_json=json.dumps(metric.values,allow_nan=False))) ` | 接续第 60 行的同一条语句，不是另起一段算法。 把数据编码为 JSON 文本；参数：metric.values, allow_nan=False。 |
| 62 | `         self._csv(folder/"zero_counts_and_time.csv", counts, count_headers) ` | 按统一表头写入 UTF-8 BOM 的 CSV，newline='' 避免 Windows 空白行。；参数：folder / 'zero_counts_and_time.csv', counts, count_headers。 |
| 63 | `         self._csv(folder/"zero_pairs.csv", pairs, ["record","electrode","reference","reference_event_index","reference_zero_s","electrode_zero_s","delay_ms","direction"]) ` | 按统一表头写入 UTF-8 BOM 的 CSV，newline='' 避免 Windows 空白行。；参数：folder / 'zero_pairs.csv', pairs, ['record', 'electrode', 'reference', 'reference_event_index', 'reference_zero_s', 'electrode_zero_s', 'delay_ms…（完整表达式见左栏）。 |
| 64 | `         self._csv(folder/"bench_metrics.csv", spectral, ["record","electrode","metric","color","reason","values_json"]) ` | 按统一表头写入 UTF-8 BOM 的 CSV，newline='' 避免 Windows 空白行。；参数：folder / 'bench_metrics.csv', spectral, ['record', 'electrode', 'metric', 'color', 'reason', 'values_json']。 |
| 65 | `         windows, window_summary = [], [] ` | 把结果保存到 (windows, window_summary)：组装元组：([], [])。 |
| 66 | `         for index, frame in enumerate(result.frames): ` | 遍历 enumerate(result.frames)，每次把一项赋给 (index, frame)，执行下面缩进的循环体。 |
| 67 | `             for name, metrics in frame["metrics"].items(): ` | 遍历 frame['metrics'].items()，每次把一项赋给 (name, metrics)，执行下面缩进的循环体。 |
| 68 | `                 for key, metric in metrics.items(): ` | 遍历 metrics.items()，每次把一项赋给 (key, metric)，执行下面缩进的循环体。 |
| 69 | `                     windows.append(dict(record=frame["record_id"],start_s=frame["start_s"],end_s=frame["end_s"], ` | 把一项加入列表末尾；参数：dict(record=frame['record_id'], start_s=frame['start_s'], end_s=frame['end_s'], electrode=name, metric=key, color=metric.color, reason=metric.mes…（完整表达式见左栏）。 |
| 70 | `                                         electrode=name,metric=key,color=metric.color,reason=metric.message, ` | 接续第 69 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(record=frame['record_id'], start_s=frame['start_s'], end_s=frame['end_s'], electrode=name, metric=key, color=metric.color, reason=metric.mes…（完整表达式见左栏）。 |
| 71 | `                                         values_json=json.dumps(metric.values,allow_nan=False))) ` | 接续第 69 行的同一条语句，不是另起一段算法。 把数据编码为 JSON 文本；参数：metric.values, allow_nan=False。 |
| 72 | `             for electrode in result.window_electrodes(index): ` | 遍历 result.window_electrodes(index)，每次把一项赋给 electrode，执行下面缩进的循环体。 |
| 73 | `                 metric = electrode.metric(mode) ` | 把结果保存到 metric：调用 electrode.metric；参数：mode。 |
| 74 | `                 window_summary.append(dict(record=frame["record_id"], start_s=frame["start_s"], end_s=frame["end_s"], ` | 把一项加入列表末尾；参数：dict(record=frame['record_id'], start_s=frame['start_s'], end_s=frame['end_s'], electrode=electrode.name, metric=mode, color=metric.color, reason…（完整表达式见左栏）。 |
| 75 | `                                            electrode=electrode.name, metric=mode, color=metric.color, reason=metric.message)) ` | 接续第 74 行的同一条语句，不是另起一段算法。 把一项加入列表末尾；参数：dict(record=frame['record_id'], start_s=frame['start_s'], end_s=frame['end_s'], electrode=electrode.name, metric=mode, color=metric.color, reason…（完整表达式见左栏）。 |
| 76 | `         window_headers = ["record","start_s","end_s","electrode","metric","color","reason","values_json"] ` | 把结果保存到 window_headers：组装列表：['record', 'start_s', 'end_s', 'electrode', 'metric', 'color', 'reason', 'values_json']。 |
| 77 | `         self._csv(folder/"window_metrics.csv", windows, window_headers) ` | 按统一表头写入 UTF-8 BOM 的 CSV，newline='' 避免 Windows 空白行。；参数：folder / 'window_metrics.csv', windows, window_headers。 |
| 78 | `         self._csv(folder/"ecg_windows.csv", windows if ecg else [], window_headers) ` | 按统一表头写入 UTF-8 BOM 的 CSV，newline='' 避免 Windows 空白行。；参数：folder / 'ecg_windows.csv', windows if ecg else [], window_headers。 |
| 79 | `         self._csv(folder/"window_summary.csv", window_summary, window_headers[:-1]) ` | 按统一表头写入 UTF-8 BOM 的 CSV，newline='' 避免 Windows 空白行。；参数：folder / 'window_summary.csv', window_summary, window_headers[:-1]。 |
| 80 | `         esc = html.escape ` | 把结果保存到 esc：读取 html 的 escape 属性。 |
| 81 | `         body = [] ` | 把结果保存到 body：组装列表：[]。 |
| 82 | `         for electrode in electrodes: ` | 遍历 electrodes，每次把一项赋给 electrode，执行下面缩进的循环体。 |
| 83 | `             cells = "".join(f'<td class="{electrode.metric(k).color}">{esc(COLOR_LABELS[electrode.metric(k).color])}<small>{esc(electrode.metric(k).message)}</small></td>' for k in columns.values()) ` | 把结果保存到 cells：调用 ''.join；参数：(f'<td class="{electrode.metric(k).color}">{esc(COLOR_LABELS[electrode.metric(k).color])}<small>{esc(electrode.metric(k).message)}</small></td>' …（完整表达式见左栏）。 |
| 84 | `             body.append(f'<tr><th>{esc(electrode.name)}{" / REF" if electrode.is_reference else ""}</th>{cells}</tr>') ` | 把一项加入列表末尾；参数：f"<tr><th>{esc(electrode.name)}{(' / REF' if electrode.is_reference else '')}</th>{cells}</tr>"。 |
| 85 | `         settings_table = "".join(f"<tr><td>{esc(k)}</td><td>{esc(str(v))}</td></tr>" for k,v in result.settings.items()) ` | 把结果保存到 settings_table：调用 ''.join；参数：(f'<tr><td>{esc(k)}</td><td>{esc(str(v))}</td></tr>' for k, v in result.settings.items())。 |
| 86 | `         source_rows = "".join(f'<tr><td>{esc(r.record.id)}</td><td>{r.sample_rate_hz:g} Hz</td><td>{r.recorded_duration_s:g} s</td><td>0-{r.duration_s:g} s</td><td>{r.excluded_tail_s:g} s</td><td>{r.channels[result.electrodes[0].name].get("unassessed_tail_s",0):g} s</td></tr>' for r in result.runs) ` | 把结果保存到 source_rows：调用 ''.join；参数：(f"<tr><td>{esc(r.record.id)}</td><td>{r.sample_rate_hz:g} Hz</td><td>{r.recorded_duration_s:g} s</td><td>0-{r.duration_s:g} s</td><td>{r.exclude…（完整表达式见左栏）。 |
| 87 | `         page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Electrode QA</title> ` | 把结果保存到 page：将变量值插入 f-string 文本；格式如 .3f 表示显示三位小数。 |
| 88 | ` <style>body{{font:15px/1.6 Arial,sans-serif;color:#243243;margin:28px}}table{{border-collapse:collapse}}td,th{{border:1px solid #dce2e8;padding:9px;text-align:left;min-width:100px}}small{{display:block}}.green{{background:#e1f1e9}}.yellow{{background:#fff0c6}}.red{{background:#f8dddd}}img{{max-width:100%}}.scroll{{overflow:auto}}</style> ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 89 | ` <h1>{esc(title)}</h1><p>Mode: {esc(result.settings['analysis_mode'])} \| Display: {esc(mode)} \| Scope: {esc(scope)}</p> ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 90 | ` <p>{len(electrodes)} electrodes \| {len(result.runs)} BDF records \| {result.elapsed_s:.3f} s computation</p> ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 91 | ` <p>Green: evaluated criteria within limits. Yellow: review, missing calibration, insufficient data or descriptive-only metric. Red: check required. These engineering criteria do not diagnose damaged electrodes.</p> ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 92 | ` <img src="heatmap.png" alt="electrode heatmap"><div class="scroll"><table><tr><th>Electrode</th>{''.join('<th>'+esc(k)+'</th>' for k in columns)}</tr>{''.join(body)}</table></div> ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 93 | ` <p>Bench summary includes applicable single-record checks. Full protocol additionally requires multi-level linearity and independent repeats. REF timing is not independently verified. Periodic signals cannot resolve whole-cycle absolute delays. SNR excludes the fitted harmonics; SINAD includes them, using the stated bandwidth.</p> ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 94 | ` <p>Window views contain only the named time interval. Tail exclusion is applied per file before every measurement and before building windows, without modifying the source BDF. The final complete window is aligned to the retained interval's end when needed. Excluded time is not assessed as passing. Short files are not padded or joined. Whole-record bench results use the retained interval. Overlapping windows are not independent repetitions. ECG record aggregate is the worst complete window; SQI rules and detectors require validation on labeled recordings.</p> ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 95 | ` <table><tr><th>Record</th><th>Sample rate</th><th>Recorded duration</th><th>Analyzed interval</th><th>Excluded tail</th><th>Retained duration without a complete window</th></tr>{source_rows}</table> ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 96 | ` <details><summary>Analysis settings</summary><table>{settings_table}</table></details> ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 97 | ` <p>results.json includes all metrics and the exported view; window_metrics.csv contains all window measurements; window_summary.csv lists status by time and electrode for the exported metric; ecg_windows.csv contains ECG windows; bench_metrics.csv contains whole-record spectral/frequency results; zero_pairs.csv contains whole-record event times; project.json reloads the configuration.</p></html>''' ` | 接续第 87 行的同一条语句，不是另起一段算法。 此行是多行模板内容；花括号字段在格式化时替换为数据。 |
| 98 | `         (folder/"report.html").write_text(page,encoding="utf-8") ` | 写入文本文件；参数：page, encoding='utf-8'。 |
| 99 | `         return folder/"report.html" ` | 结束当前函数并返回：在 Path 路径 folder 后拼接 'report.html'；这里的 / 是路径拼接。 |
| 100 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
