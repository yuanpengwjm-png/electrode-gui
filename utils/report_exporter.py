"""English, mode-aware exports. Numerical details and exact display scope are retained."""
from dataclasses import asdict
from pathlib import Path
import csv
import html
import json
from config import COLOR_LABELS, AnalysisSettings, BENCH_VIEWS, ECG_VIEWS
from views.heatmap_view import HeatmapRenderer
from utils.project_io import save_project


class ReportExporter:
    @staticmethod
    def _csv(path, rows, headers):
        with path.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def save(self, result, folder, mode="current", title="Electrode QA", electrodes=None, scope="All records", display=None):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        electrodes = result.electrodes if electrodes is None else electrodes
        ecg = result.settings["analysis_mode"] == "ecg"
        columns = dict(ECG_VIEWS if ecg else BENCH_VIEWS)
        if result.settings["analysis_mode"] == "bench_pulse":
            for label in ("SNR", "SINAD", "THD"):
                columns.pop(label)
        HeatmapRenderer().save(electrodes, mode, folder/"heatmap.png", title+"\n"+scope)
        payload = asdict(result)
        payload["export_view"] = dict(metric=mode, scope=scope, electrode_results=[asdict(e) for e in electrodes])
        (folder/"results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        save_project(folder/"project.json", [r.record for r in result.runs], AnalysisSettings(**result.settings),
                     [r.name for r in result.electrodes], result.reference, display=display)
        rows = []
        for electrode in electrodes:
            metric = electrode.metric(mode)
            row = dict(electrode=electrode.name, color=metric.color, explanation=metric.message, scope=scope)
            for key in columns.values():
                row[key] = electrode.metric(key).color
                row[key+"_reason"] = electrode.metric(key).message
            rows.append(row)
        self._csv(folder/"electrodes.csv", rows, list(rows[0]))
        pairs, counts, spectral = [], [], []
        count_headers = ["record","electrode","reference","event_definition","sample_period_ms","rising_count","falling_count",
                         "rising_paired","falling_paired","rising_median_ms","falling_median_ms","max_direction_p95_ms","jitter_ms"]
        for run in result.runs:
            for channel, data in run.channels.items():
                if "sync" not in data:
                    continue
                v = data["sync"].values
                counts.append(dict(record=run.record.id, electrode=channel, reference=result.reference,
                    event_definition=v.get("event_definition"), sample_period_ms=v.get("sample_period_ms"),
                    rising_count=v["rising_count"], falling_count=v["falling_count"],
                    rising_paired=v["directions"]["rising"]["paired_count"], falling_paired=v["directions"]["falling"]["paired_count"],
                    rising_median_ms=v["directions"]["rising"]["median_ms"], falling_median_ms=v["directions"]["falling"]["median_ms"],
                    max_direction_p95_ms=v["max_direction_p95_ms"], jitter_ms=v["jitter_ms"]))
                pairs.extend([dict(record=run.record.id,electrode=channel,reference=result.reference,**p) for p in v["pairs"]])
                for key, metric in data.get("extra",{}).items():
                    spectral.append(dict(record=run.record.id,electrode=channel,metric=key,color=metric.color,
                                         reason=metric.message,values_json=json.dumps(metric.values,allow_nan=False)))
        self._csv(folder/"zero_counts_and_time.csv", counts, count_headers)
        self._csv(folder/"zero_pairs.csv", pairs, ["record","electrode","reference","reference_event_index","reference_zero_s","electrode_zero_s","delay_ms","direction"])
        self._csv(folder/"bench_metrics.csv", spectral, ["record","electrode","metric","color","reason","values_json"])
        windows, window_summary = [], []
        for index, frame in enumerate(result.frames):
            for name, metrics in frame["metrics"].items():
                for key, metric in metrics.items():
                    windows.append(dict(record=frame["record_id"],start_s=frame["start_s"],end_s=frame["end_s"],
                                        electrode=name,metric=key,color=metric.color,reason=metric.message,
                                        values_json=json.dumps(metric.values,allow_nan=False)))
            for electrode in result.window_electrodes(index):
                metric = electrode.metric(mode)
                window_summary.append(dict(record=frame["record_id"], start_s=frame["start_s"], end_s=frame["end_s"],
                                           electrode=electrode.name, metric=mode, color=metric.color, reason=metric.message))
        window_headers = ["record","start_s","end_s","electrode","metric","color","reason","values_json"]
        self._csv(folder/"window_metrics.csv", windows, window_headers)
        self._csv(folder/"ecg_windows.csv", windows if ecg else [], window_headers)
        self._csv(folder/"window_summary.csv", window_summary, window_headers[:-1])
        esc = html.escape
        body = []
        for electrode in electrodes:
            cells = "".join(f'<td class="{electrode.metric(k).color}">{esc(COLOR_LABELS[electrode.metric(k).color])}<small>{esc(electrode.metric(k).message)}</small></td>' for k in columns.values())
            body.append(f'<tr><th>{esc(electrode.name)}{" / REF" if electrode.is_reference else ""}</th>{cells}</tr>')
        settings_table = "".join(f"<tr><td>{esc(k)}</td><td>{esc(str(v))}</td></tr>" for k,v in result.settings.items())
        source_rows = "".join(f'<tr><td>{esc(r.record.id)}</td><td>{r.sample_rate_hz:g} Hz</td><td>{r.recorded_duration_s:g} s</td><td>0-{r.duration_s:g} s</td><td>{r.excluded_tail_s:g} s</td><td>{r.channels[result.electrodes[0].name].get("unassessed_tail_s",0):g} s</td></tr>' for r in result.runs)
        page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Electrode QA</title>
<style>body{{font:15px/1.6 Arial,sans-serif;color:#243243;margin:28px}}table{{border-collapse:collapse}}td,th{{border:1px solid #dce2e8;padding:9px;text-align:left;min-width:100px}}small{{display:block}}.green{{background:#e1f1e9}}.yellow{{background:#fff0c6}}.red{{background:#f8dddd}}img{{max-width:100%}}.scroll{{overflow:auto}}</style>
<h1>{esc(title)}</h1><p>Mode: {esc(result.settings['analysis_mode'])} | Display: {esc(mode)} | Scope: {esc(scope)}</p>
<p>{len(electrodes)} electrodes | {len(result.runs)} BDF records | {result.elapsed_s:.3f} s computation</p>
<p>Green: evaluated criteria within limits. Yellow: review, missing calibration, insufficient data or descriptive-only metric. Red: check required. These engineering criteria do not diagnose damaged electrodes.</p>
<img src="heatmap.png" alt="electrode heatmap"><div class="scroll"><table><tr><th>Electrode</th>{''.join('<th>'+esc(k)+'</th>' for k in columns)}</tr>{''.join(body)}</table></div>
<p>Bench summary includes applicable single-record checks. Full protocol additionally requires multi-level linearity and independent repeats. REF timing is not independently verified. Periodic signals cannot resolve whole-cycle absolute delays. SNR excludes the fitted harmonics; SINAD includes them, using the stated bandwidth.</p>
<p>Window views contain only the named time interval. Tail exclusion is applied per file before every measurement and before building windows, without modifying the source BDF. The final complete window is aligned to the retained interval's end when needed. Excluded time is not assessed as passing. Short files are not padded or joined. Whole-record bench results use the retained interval. Overlapping windows are not independent repetitions. ECG record aggregate is the worst complete window; SQI rules and detectors require validation on labeled recordings.</p>
<table><tr><th>Record</th><th>Sample rate</th><th>Recorded duration</th><th>Analyzed interval</th><th>Excluded tail</th><th>Retained duration without a complete window</th></tr>{source_rows}</table>
<details><summary>Analysis settings</summary><table>{settings_table}</table></details>
<p>results.json includes all metrics and the exported view; window_metrics.csv contains all window measurements; window_summary.csv lists status by time and electrode for the exported metric; ecg_windows.csv contains ECG windows; bench_metrics.csv contains whole-record spectral/frequency results; zero_pairs.csv contains whole-record event times; project.json reloads the configuration.</p></html>'''
        (folder/"report.html").write_text(page,encoding="utf-8")
        return folder/"report.html"

