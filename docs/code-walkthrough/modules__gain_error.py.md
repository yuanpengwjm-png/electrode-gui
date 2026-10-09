# modules/gain_error.py：幅度准确性

用输出基频/平台 Vpp 与确认过的实际输入比较；没有可靠波形或输入校准时，不把结果判为幅度合格。

源码：[modules/gain_error.py](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/gain_error.py>)。本说明对应 23 行源码；按真实行号逐行列出。
连续多行组成一条语句时，续行会指向起始行。空行、注释和说明字符串也列出，以便逐行对齐。
这份说明解释本次读取到的实现；代码后续修改后，行号和阈值可能变化。

## 函数地图

| 函数 | 源码行号 | 为什么有这个函数 |
|---|---|---|
| `__init__` | [6–7](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/gain_error.py:6>) | 初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 |
| `evaluate` | [9–23](<C:/Users/yuanp/OneDrive/Desktop/BMET/BMET3921/electrode-gui/modules/gain_error.py:9>) | 先算输出/输入的百分比误差，再按响应可靠性、波形质量、输入确认和阈值依次给结论。 |

## 逐行对照

| 原行号 | 原始代码 | 中文说明 |
|---:|---|---|
| 1 | ` """AmplitudePeakGainError: calibrated sine peak-to-peak amplitude versus input.""" ` | 文档字符串的说明文字，属于模块/函数文档，不执行其中的句子。 |
| 2 | ` from models import MetricResult ` | 从 models 导入 MetricResult。InputRecord 描述文件与输入条件；RunResult 描述一次记录；MetricResult 保存颜色、原因、数值；AnalysisResult 保存整批和窗口结果。 |
| 3 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 4 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 5 | ` class AmplitudePeakGainError: ` | 定义 AmplitudePeakGainError 类；把相关数据和操作放在一起，实例通过 self 保存自己的状态。 |
| 6 | `     def __init__(self, settings): ` | 定义 __init__(self, settings)。初始化该类的一个实例，把设置/回调等保存到 self，供后续方法使用。 定义到这里时不执行函数体。 |
| 7 | `         self.settings = settings ` | 把结果保存到 self.settings：settings。 |
| 8 | ` （空行） ` | 空行：分隔代码段，便于阅读，没有运行操作。 |
| 9 | `     def evaluate(self, fit, record): ` | 定义 evaluate(self, fit, record)。先算输出/输入的百分比误差，再按响应可靠性、波形质量、输入确认和阈值依次给结论。 定义到这里时不执行函数体。 |
| 10 | `         measured = fit["amplitude_pp_mV"] ` | 把结果保存到 measured：按索引/键 'amplitude_pp_mV' 取 fit 的内容。 |
| 11 | `         error = None if measured is None or record.input_mVpp is None else 100*(measured/record.input_mVpp-1) ` | 输入或测量未知时返回 None；否则计算增益误差%=100×(输出Vpp/实际输入Vpp−1)。正值是偏大，负值是偏小。 |
| 12 | `         values = dict(output_mVpp=measured, input_mVpp=record.input_mVpp, gain_error_pct=error, ` | 把结果保存到 values：组装键值字典；参数：output_mVpp=measured, input_mVpp=record.input_mVpp, gain_error_pct=error, input_confirmed=record.input_confirmed, quality_reasons=fit['quality_re…（完整表达式见左栏）。 |
| 13 | `                       input_confirmed=record.input_confirmed, quality_reasons=fit["quality_reasons"]) ` | 接续第 12 行的同一条语句，不是另起一段算法。 把结果保存到 values：组装键值字典；参数：output_mVpp=measured, input_mVpp=record.input_mVpp, gain_error_pct=error, input_confirmed=record.input_confirmed, quality_reasons=fit['quality_re…（完整表达式见左栏）。 |
| 14 | `         if any(reason in fit["quality_reasons"] for reason in ("no_reliable_sine_response", "no_reliable_pulse_response")): ` | 检查条件 any((reason in fit['quality_reasons'] for reason in ('no_reliable_sine_response', 'no_reliable_pulse_response')))；为真时执行下面缩进的一组语句。 |
| 15 | `             return MetricResult("red", "No reliable response; check the electrode path and input", values) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：'red', 'No reliable response; check the electrode path and input', values。 |
| 16 | `         if fit["quality_reasons"]: ` | 检查条件 fit['quality_reasons']；为真时执行下面缩进的一组语句。 |
| 17 | `             return MetricResult("yellow", "Waveform quality is insufficient; repeat the gain test: "+", ".join(fit["quality_reasons"]), values) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：'yellow', 'Waveform quality is insufficient; repeat the gain test: ' + ', '.join(fit['quality_reasons']), values。 |
| 18 | `         if record.input_mVpp is None or not record.input_confirmed: ` | 检查条件 record.input_mVpp is None or not record.input_confirmed；为真时执行下面缩进的一组语句。 |
| 19 | `             return MetricResult("yellow", "Actual input Vpp is unconfirmed; absolute gain cannot be assessed", values) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：'yellow', 'Actual input Vpp is unconfirmed; absolute gain cannot be assessed', values。 |
| 20 | `         color = self.settings.color(error, self.settings.gain_limit_pct) ` | 把结果保存到 color：调用 self.settings.color；参数：error, self.settings.gain_limit_pct。 |
| 21 | `         kind = "low" if error < 0 else "high" ` | 把结果保存到 kind：若 error < 0，用 'low'；否则用 'high'。 |
| 22 | `         label = "within limits" if color == "green" else ("near the limit" if color == "yellow" else kind+"; check required") ` | 把结果保存到 label：若 color == 'green'，用 'within limits'；否则用 'near the limit' if color == 'yellow' else kind + '; check required'。 |
| 23 | `         return MetricResult(color, f"Gain {error:+.3f}%: {label}", values) ` | 结束当前函数并返回：打包颜色、原因和指标数值；参数：color, f'Gain {error:+.3f}%: {label}', values。 |
