"""English two-stage desktop app. Algorithms are separate, GUI-independent classes."""
from dataclasses import asdict
from pathlib import Path
import copy
import json
import math
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import AnalysisSettings, COLORS, COLOR_LABELS, BENCH_VIEWS, ECG_VIEWS
from services.analysis_service import AnalysisService
from services.demo_data import create_mode_demo, create_timeline_demo
from utils.bdf_reader import BdfReader
from utils.input_catalog import records_from_paths
from utils.project_io import UNIT_FACTORS, load_project, save_project
from utils.report_exporter import ReportExporter
from views.heatmap_view import HeatmapView
from views.timeline_view import TimelineView
from views.torso_geometry import TorsoLayout
from views.torso_window import TorsoWindow
HERE = Path(__file__).resolve().parent
PROFILES = {'Stage 1 - Bench / Sine': 'bench_sine',
 'Stage 1 - Bench / Pulse': 'bench_pulse',
 'Stage 2 - ECG quality': 'ecg'}
CRITERIA = {'exclude_last_s': 'Exclude final seconds per file (0 = keep all)',
 'gain_limit_pct': 'Gain error limit (%)',
 'linearity_limit_pct': 'Linearity (% of input span)',
 'sync_delay_limit_ms': 'Event delay P95 (ms)',
 'sync_jitter_limit_ms': 'Event jitter (ms)',
 'repeat_cv_limit_pct': 'Repeat amplitude/gain CV (%)',
 'repeat_delay_sd_limit_ms': 'Between-run delay SD (ms)',
 'min_repeat_runs': 'Minimum independent repeat runs',
 'frequency_limit_pct': 'Frequency error (%) - blank: uncalibrated',
 'thd_limit_pct': 'THD (%) - blank: uncalibrated',
 'snr_good_db': 'SNR good boundary (dB)',
 'snr_bad_db': 'SNR bad boundary (dB)',
 'bench_bandwidth_hz': 'Noise measurement bandwidth (Hz)',
 'harmonic_count': 'Highest fitted harmonic order',
 'max_residual_pct': 'Sine residual gate (% of fundamental RMS)',
 'max_residual_step_pct': 'Residual step gate (% of Vpp)',
 'min_cycles': 'Minimum bench signal cycles',
 'frequency_search_pct': 'Frequency search range (+/- %)',
 'bench_window_s': 'Bench window duration (s)',
 'bench_hop_s': 'Bench window step (s)',
 'ecg_window_s': 'ECG window duration (s)',
 'ecg_hop_s': 'ECG window step (s)',
 'ecg_match_ms': 'Beat matching tolerance (ms)',
 'ecg_min_beats': 'Minimum beats per detector',
 'bsqi_good': 'bSQI good boundary (strictly greater)',
 'bsqi_bad': 'bSQI bad boundary',
 'psqi_low': 'pSQI good range - lower',
 'psqi_high': 'pSQI good range - upper',
 'psqi_bad': 'pSQI bad lower boundary',
 'ksqi_min': 'Pearson kurtosis good boundary (strictly greater)',
 'bassqi_good': 'basSQI good boundary',
 'bassqi_bad': 'basSQI bad boundary',
 'flatline_s': 'Sustained near-flat duration (s)',
 'flat_epsilon_uV': 'Near-flat sample difference (uV)',
 'warning_fraction': 'Warning fraction of upper limits (0 to 1)'}

class ElectrodeQAApp:

    def __init__(self, root):
        self.root = root
        self.records, self.channels = ([], [])
        self.settings = AnalysisSettings(bench_windows=True)
        self.info = self.selected = self.result = None
        self.busy = self.loading = False
        self.events = queue.Queue()
        self.controls, self.combos, self.bench_controls = ([], [], [])
        self.count = tk.StringVar(value='8')
        self.pool = tk.StringVar(value='scalp')
        self.reference = tk.StringVar()
        self.profile = tk.StringVar(value=next(iter(PROFILES)))
        self.mode = tk.StringVar(value='Bench summary')
        self.scope = tk.StringVar(value='Not analyzed')
        self.analysis_target = tk.StringVar(value='Selected record')
        self.windowed = tk.BooleanVar(value=self.settings.bench_windows)
        self.focused_electrode = None
        self.timeline_cache = {}
        self.torso_window = None
        self.live_window = None
        self.torso_layout = TorsoLayout()
        self.status = tk.StringVar(value='Open BDF or ZIP files. Verify the declared waveform and connected channels.')
        self.summary = tk.StringVar(value='Not analyzed')
        self.source_label = tk.StringVar(value='No BDF selected')
        self.hint = tk.StringVar()
        self.lab_choice = tk.StringVar(value='10 electrodes - Sine')
        self.record_vars = {k: tk.StringVar() for k in ('frequency', 'amplitude', 'unit', 'repeat', 'setup', 'waveform')}
        self.confirmed = tk.BooleanVar(value=False)
        self.sweep = tk.BooleanVar(value=True)
        self.limit_vars = {k: tk.StringVar(value='' if getattr(self.settings, k) is None else str(getattr(self.settings, k))) for k in CRITERIA}
        self.frame_labels = ['Not analyzed']
        self.result_scopes = {}
        self._build()
        for variable in (*self.record_vars.values(), self.confirmed, self.sweep, self.windowed, *self.limit_vars.values(), self.count, self.pool, self.reference):
            variable.trace_add('write', self.invalidate)
        self.change_profile()

    def analysis_mode(self):
        return PROFILES[self.profile.get()]

    def open_live(self):
        from views.live_window import LiveWindow
        if self.live_window is None or not self.live_window.winfo_exists():
            self.live_window = LiveWindow(self.root, self.settings, self.torso_layout)
        else:
            self.live_window.lift()

    def button(self, parent, text, callback):
        w = ttk.Button(parent, text=text, command=callback)
        self.controls.append(w)
        return w

    def combo(self, parent, variable, values, width=18):
        w = ttk.Combobox(parent, textvariable=variable, values=values, width=width, state='readonly')
        self.combos.append(w)
        return w

    def _build(self):
        self.root.title('Electrode QA | Bench validation + ECG quality')
        height = min(950, self.root.winfo_screenheight() - 90)
        self.root.geometry(f'1400x{height}')
        self.root.minsize(1180, 820)
        style = ttk.Style(self.root)
        style.theme_use('clam')
        for name in ('TFrame', 'TLabel', 'TLabelframe', 'TCheckbutton'):
            style.configure(name, background='#F4F7FA')
        style.configure('TLabel', foreground='#243243', font=('Segoe UI', 10))
        style.configure('TButton', padding=(8, 5), font=('Segoe UI', 10))
        style.configure('Treeview', rowheight=26, font=('Segoe UI', 9))
        header = tk.Frame(self.root, bg='#182B3A', padx=20, pady=12)
        header.pack(fill='x')
        tk.Label(header, text='Electrode QA', bg='#182B3A', fg='white', font=('Segoe UI', 22, 'bold')).pack(side='left')
        tk.Label(header, text='Known-input validation / ECG quality screening', bg='#182B3A', fg='#BECDD9', font=('Segoe UI', 12)).pack(side='left', padx=25)
        ttk.Button(header, text='Live LSL · Sine', command=self.open_live).pack(side='right')
        flow = ttk.Frame(self.root, padding=(18, 10))
        flow.pack(fill='x')
        ttk.Label(flow, text='Analysis workflow').pack(side='left')
        w = self.combo(flow, self.profile, list(PROFILES), 32)
        w.pack(side='left', padx=10)
        w.bind('<<ComboboxSelected>>', self.change_profile)
        ttk.Label(flow, textvariable=self.hint, wraplength=830, foreground='#526A7A').pack(side='left', padx=10)
        body = ttk.Frame(self.root, padding=(14, 0, 14, 8))
        body.pack(fill='both', expand=True)
        # Scroll the input column on smaller screens instead of clipping controls.
        left_shell = ttk.Frame(body, width=430)
        left_shell.pack(side='left', fill='y', padx=(0, 14))
        left_shell.pack_propagate(False)
        input_canvas = tk.Canvas(left_shell, width=410, bg='#F4F7FA', highlightthickness=0)
        input_scroll = ttk.Scrollbar(left_shell, orient='vertical', command=input_canvas.yview)
        input_canvas.configure(yscrollcommand=input_scroll.set)
        input_scroll.pack(side='right', fill='y')
        input_canvas.pack(side='left', fill='both', expand=True)
        left = ttk.Frame(input_canvas, width=410)
        input_window = input_canvas.create_window((0, 0), window=left, anchor='nw')
        left.bind('<Configure>', lambda _: input_canvas.configure(scrollregion=input_canvas.bbox('all')))
        input_canvas.bind('<Configure>', lambda e: input_canvas.itemconfigure(input_window, width=e.width))
        input_canvas.bind('<MouseWheel>', lambda e: input_canvas.yview_scroll(-int(e.delta/120), 'units'))
        right = ttk.Frame(body)
        right.pack(side='left', fill='both', expand=True)
        self._build_records(left)
        self._build_results(right)
        self.status_label = ttk.Label(self.root, textvariable=self.status, padding=(18, 8), wraplength=1100)
        self.status_label.pack(side='bottom', fill='x', before=body)

    def _build_records(self, parent):
        ttk.Label(parent, text='01  Records and input', font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        bar = ttk.Frame(parent)
        bar.pack(fill='x', pady=7)
        for title, fn in (('Open BDF / ZIP', self.add_files), ('Remove', self.remove_record), ('Clear', self.clear_records)):
            self.button(bar, title, fn).pack(side='left', padx=(0, 5))
        self.record_tree = ttk.Treeview(parent, columns=('file', 'input', 'verified'), show='headings', height=5, selectmode='browse')
        for key, title, width in (('file', 'Record', 245), ('input', 'mVpp', 60), ('verified', 'Verified', 65)):
            self.record_tree.heading(key, text=title)
            self.record_tree.column(key, width=width)
        self.record_tree.pack(fill='x')
        self.record_tree.bind('<<TreeviewSelect>>', self.select_record)
        ttk.Label(parent, textvariable=self.source_label, wraplength=395, foreground='#657588').pack(anchor='w', pady=5)
        form = ttk.LabelFrame(parent, text='Selected record - verify filename suggestions', padding=8)
        form.pack(fill='x', pady=5)
        fields = (('waveform', 'Declared waveform'), ('setup', 'Physical setup group'), ('frequency', 'Input frequency (Hz)'), ('amplitude', 'Actual input amplitude'), ('repeat', 'Independent repeat group'))
        for row, (key, title) in enumerate(fields):
            ttk.Label(form, text=title).grid(row=row, column=0, sticky='w', pady=4)
            if key == 'waveform':
                w = self.combo(form, self.record_vars[key], ('unknown', 'sine', 'pulse', 'ecg'), 13)
            else:
                w = ttk.Entry(form, textvariable=self.record_vars[key], width=16)
                self.controls.append(w)
            w.grid(row=row, column=1, sticky='ew', padx=5)
            if key in ('frequency', 'amplitude', 'repeat'):
                self.bench_controls.append(w)
        self.unit_combo = self.combo(form, self.record_vars['unit'], list(UNIT_FACTORS), 8)
        self.unit_combo.grid(row=3, column=2)
        self.bench_controls.append(self.unit_combo)
        for row, title, var in ((5, 'Input Vpp and units verified for THIS record', self.confirmed), (6, 'Include in linearity sweep', self.sweep)):
            w = ttk.Checkbutton(form, text=title, variable=var)
            w.grid(row=row, column=0, columnspan=3, sticky='w', pady=3)
            self.controls.append(w)
            self.bench_controls.append(w)
        self.button(form, 'Apply record', self.apply_record).grid(row=7, column=0, sticky='w', pady=4)
        bar = ttk.Frame(parent)
        bar.pack(fill='x', pady=8)
        for title, fn in (('Load project', self.load_dialog), ('Save project', self.save_dialog), ('Demo', self.load_demo)):
            self.button(bar, title, fn).pack(side='left', padx=(0, 5))
        lab = ttk.LabelFrame(parent, text='Latest lab presets', padding=8)
        lab.pack(fill='x', pady=5)
        self.combo(lab, self.lab_choice, ('10 electrodes - Sine', '128 electrodes - Sine', '128 electrodes - Pulse', '10 electrodes - ECG'), 24).pack(side='left')
        self.button(lab, 'Load', self.load_lab).pack(side='left', padx=8)
        ttk.Label(parent, text='Presets select A1-A10 or A1-D32. Verify the physical wiring.\n\nRepeated cycles are not independent runs. A generator setting or plot scale does not confirm actual input Vpp.', wraplength=395, foreground='#657588').pack(anchor='w', pady=8)

    def _build_results(self, parent):
        ttk.Label(parent, text='02  Channels and analysis', font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=7)
        ttk.Label(row, text='Group').pack(side='left')
        self.combo(row, self.pool, ('scalp', 'EXG', 'all'), 7).pack(side='left', padx=5)
        ttk.Label(row, text='Count').pack(side='left')
        w = ttk.Spinbox(row, from_=1, to=4096, textvariable=self.count, width=5)
        w.pack(side='left', padx=5)
        self.controls.append(w)
        self.button(row, 'Apply count', self.apply_count).pack(side='left')
        self.button(row, 'Choose channels', self.choose_channels).pack(side='left', padx=5)
        ttk.Label(row, text='Timing ref.').pack(side='left')
        self.ref_combo = self.combo(row, self.reference, (), 8)
        self.ref_combo.pack(side='left', padx=5)
        self.channel_label = ttk.Label(parent, text='No channels selected', wraplength=870, foreground='#657588')
        self.channel_label.pack(anchor='w', pady=4)
        target_row = ttk.Frame(parent)
        target_row.pack(fill='x', pady=3)
        ttk.Label(target_row, text='Analyze').pack(side='left')
        self.combo(target_row, self.analysis_target, ('Selected record', 'All loaded records'), 21).pack(side='left', padx=8)
        ttk.Label(target_row, text='Linearity and repetition require multiple records.', foreground='#657588').pack(side='left')
        window_row = ttk.Frame(parent)
        window_row.pack(fill='x', pady=3)
        self.window_check = ttk.Checkbutton(window_row, text='Build time windows', variable=self.windowed,
                                            command=self.context_states)
        self.window_check.pack(side='left')
        self.controls.append(self.window_check)
        ttk.Label(window_row, text='Window (s)').pack(side='left', padx=(10, 4))
        self.window_entry = ttk.Entry(window_row, width=6)
        self.window_entry.pack(side='left')
        ttk.Label(window_row, text='Step (s)').pack(side='left', padx=(10, 4))
        self.hop_entry = ttk.Entry(window_row, width=6)
        self.hop_entry.pack(side='left')
        self.controls.extend((self.window_entry, self.hop_entry))
        ttk.Label(window_row, text='Complete windows only; no padding.', foreground='#657588').pack(side='left', padx=10)
        crop_row = ttk.Frame(parent)
        crop_row.pack(fill='x', pady=3)
        ttk.Label(crop_row, text='Exclude final (s)').pack(side='left')
        self.crop_entry = ttk.Entry(crop_row, width=6, textvariable=self.limit_vars['exclude_last_s'])
        self.crop_entry.pack(side='left', padx=8)
        self.controls.append(self.crop_entry)
        ttk.Label(crop_row, text='Per file, before all checks and windows. Original BDF unchanged.', foreground='#657588').pack(side='left')
        bar = ttk.Frame(parent)
        bar.pack(fill='x', pady=7)
        self.run_button = self.button(bar, 'Run analysis', self.run)
        self.run_button.pack(side='left')
        self.button(bar, 'Export PNG / CSV / report', self.export).pack(side='left', padx=8)
        self.progress = ttk.Progressbar(bar, mode='indeterminate', length=90)
        self.progress.pack(side='left', padx=8)
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)
        tabs = [ttk.Frame(self.notebook, padding=10) for _ in range(4)]
        for tab, title in zip(tabs, ('Electrode heatmap', 'Results', 'Criteria', 'How it works')):
            self.notebook.add(tab, text=title)
        row = ttk.Frame(tabs[0])
        row.pack(fill='x')
        ttk.Label(row, text='Metric').pack(side='left')
        self.view_combo = self.combo(row, self.mode, list(BENCH_VIEWS), 29)
        self.view_combo.pack(side='left', padx=8)
        self.view_combo.bind('<<ComboboxSelected>>', lambda _: self.redraw())
        ttk.Label(row, textvariable=self.summary).pack(side='left')
        self.button(row, '3D torso', self.open_torso).pack(side='right', padx=4)
        row = ttk.Frame(tabs[0])
        row.pack(fill='x', pady=6)
        ttk.Label(row, text='Result scope').pack(side='left')
        self.window_combo = self.combo(row, self.scope, self.frame_labels, 60)
        self.window_combo.pack(side='left', padx=8, fill='x', expand=True)
        self.window_combo.bind('<<ComboboxSelected>>', self.change_scope)
        self.timeline = TimelineView(tabs[0], self.select_window)
        self.timeline.pack(fill='x', pady=(0, 5))
        ttk.Label(tabs[0], text='Timeline colors: worst channel for the selected metric. Drag to inspect a window.',
                  foreground='#657588').pack(anchor='w')
        row = ttk.Frame(tabs[0])
        row.pack(fill='x', pady=3)
        for key in COLORS:
            tk.Label(row, text='● ' + COLOR_LABELS[key], fg=COLORS[key], bg='#F4F7FA', font=('Segoe UI', 9, 'bold')).pack(side='left', padx=(0, 12))
        # Reserve the reason panel before letting the scrollable grid expand.
        # Otherwise the new timeline can push reasons off small screens.
        detail_shell = ttk.Frame(tabs[0])
        detail_shell.pack(side='bottom', fill='x')
        ttk.Label(detail_shell, text='Click an electrode for values and reasons. Grid order is not a physical cap layout.', foreground='#657588').pack(anchor='w', pady=4)
        detail_row = ttk.Frame(detail_shell)
        detail_row.pack(fill='x')
        self.detail = tk.Text(detail_row, height=4, wrap='word', font=('Segoe UI', 10), bg='white', relief='flat', padx=9, pady=6)
        detail_scroll = ttk.Scrollbar(detail_row, orient='vertical', command=self.detail.yview)
        self.detail.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.pack(side='right', fill='y')
        self.detail.pack(fill='x', expand=True)
        self.detail.configure(state='disabled')
        self.heatmap = HeatmapView(tabs[0], self.show_detail)
        self.heatmap.pack(fill='both', expand=True)
        self.results_tree = ttk.Treeview(tabs[1], show='headings')
        sx = ttk.Scrollbar(tabs[1], orient='horizontal', command=self.results_tree.xview)
        self.results_tree.configure(xscrollcommand=sx.set)
        sx.pack(side='bottom', fill='x')
        self.results_tree.pack(fill='both', expand=True)
        self.results_tree.bind('<<TreeviewSelect>>', self.select_result)
        self._build_criteria(tabs[2])
        self._build_help(tabs[3])

    def _build_criteria(self, parent):
        canvas = tk.Canvas(parent, bg='#F4F7FA', highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        canvas.pack(fill='both', expand=True)
        form = ttk.Frame(canvas, padding=10)
        canvas.create_window((0, 0), window=form, anchor='nw')
        form.bind('<Configure>', lambda _: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<MouseWheel>', lambda e: canvas.yview_scroll(-int(e.delta / 120), 'units'))
        ttk.Label(form, text='Defaults: frequency error 0.1%, THD 1%, exclude final 1 s per file.\nEngineering starting points; blank THD/frequency limits mean uncalibrated.').grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 12))
        for row, (key, title) in enumerate(CRITERIA.items(), 1):
            ttk.Label(form, text=title).grid(row=row, column=0, sticky='w', pady=6)
            w = ttk.Entry(form, textvariable=self.limit_vars[key], width=12)
            w.grid(row=row, column=1, padx=16)
            self.controls.append(w)

    def _build_help(self, parent):
        w = tk.Text(parent, wrap='word', font=('Segoe UI', 11), padx=12, pady=12, relief='flat')
        w.pack(fill='both', expand=True)
        w.insert('1.0', 'STAGE 1 - KNOWN INPUT\nSine: gain, multi-level linearity, both zero-crossing directions, repeatability, SNR, SINAD, THD and frequency.\nPulse: plateau amplitude, both midpoint edges, frequency and repeats. Sine distortion metrics are not applied to pulses.\n\nSTAGE 2 - ECG QUALITY\nComplete 10 s windows, every 5 s by default. bSQI compares two different QRS detector methods. pSQI, Pearson kSQI, basSQI and flatline/clipping checks describe other properties. Worst component wins: this is a prototype screen.\n\nCOLORS AND SCOPE\nGreen: evaluated criteria within limits. Yellow: warning, insufficient data, uncalibrated tolerance or descriptive-only metric. Red: check required. No color proves electrode damage.\nAnalyze defaults to Selected record. Input Vpp verification belongs to THIS record only; the list shows Verified Yes/No. Apply record or Run analysis saves edits. Result scope starts at the first complete window when available; otherwise it shows the whole record. For linearity/repetition, choose All loaded records, run, then select All analyzed records / worst case. Batch warnings name their source records. ECG record scope uses the worst complete window within that file; select a Window for its actual values. Only complete windows are used. Exclude final (s) defaults to 1 per file, before all checks. A final full window ends at the retained interval end; short records are not padded or joined.\n\nTIME SLIDER\nBench: enable Build time windows, set Window to 10 s and Step to 1 s (or 10 s for blocks), then Run analysis. ECG always uses windows. Drag the slider, click the colored strip, or Play/Pause. Playback uses cached results and stops at the retained interval end. The strip shows the worst channel for the selected metric; Next alert finds the next yellow/red interval. Selected electrodes stay selected. Short bench files retain whole-record analysis but cannot supply a full window. A colored window locates an interval, not an exact fault onset. Windows are not independent repetitions.\n\nTIMING\nRising/falling events are matched separately within +/-T/4 windows. Missing events keep their index. Periodic signals cannot resolve whole-cycle absolute delays. REF is not independently verified.\n\nDATA AND LIMITS\nOnly select electrodes connected in the test. Do not pool different physical setups. Defaults: frequency error 0.1%, THD 1%. Clearing either limit marks acceptance uncalibrated. SQI thresholds are provisional. The app reads files offline; it does not connect to ActiView TCP.\n\nCODE\ngui.py -> AnalysisService -> waveform-specific classes -> MetricResult -> heatmap/export.\nDetailed Chinese walkthrough: CODE_GUIDE_ZH.md.')
        w.configure(state='disabled')

    def change_profile(self, _=None):
        mode = self.analysis_mode()
        self.views = dict(ECG_VIEWS if mode == 'ecg' else BENCH_VIEWS)
        if mode == 'bench_pulse':
            for key in ('SNR', 'SINAD', 'THD'):
                self.views.pop(key)
        self.view_combo.configure(values=list(self.views))
        if self.mode.get() not in self.views:
            self.mode.set(next(iter(self.views)))
        self.hint.set({'bench_sine': 'Verify a known sine through the full acquisition chain. Actual input Vpp is required for absolute gain.', 'bench_pulse': 'Measure pulse plateaus and rising/falling midpoint edges. No sine-fit quality gate is applied.', 'ecg': 'Screen ECG channels in complete windows. Short files are marked insufficient; SQI does not prove electrode damage.'}[mode])
        self.context_states()
        self.invalidate()

    def context_states(self):
        ecg = self.analysis_mode() == 'ecg'
        self.window_check.configure(state='disabled' if ecg or self.busy else 'normal')
        self.window_check.configure(text='ECG time windows (always on)' if ecg else 'Build time windows')
        prefix = 'ecg' if ecg else 'bench'
        self.window_entry.configure(textvariable=self.limit_vars[prefix + '_window_s'])
        self.hop_entry.configure(textvariable=self.limit_vars[prefix + '_hop_s'])
        for w in (self.window_entry, self.hop_entry):
            w.configure(state='normal' if not self.busy and (ecg or self.windowed.get()) else 'disabled')
        self.ref_combo.configure(state='disabled' if ecg or self.busy else 'readonly')
        self.window_combo.configure(state='readonly' if self.result is not None and not self.busy else 'disabled')
        for w in self.bench_controls:
            w.configure(state='disabled' if ecg or self.busy else 'readonly' if isinstance(w, ttk.Combobox) else 'normal')
        self.unit_combo.configure(values=list(UNIT_FACTORS) if self.analysis_mode() == 'bench_sine' else ['mVpp', 'uVpp', 'Vpp'])

    def invalidate(self, *_):
        if self.loading or self.busy:
            return
        self.timeline.clear()
        self.timeline_cache.clear()
        self.focused_electrode = None
        self.result = None
        self.heatmap.show([], 'current')
        if self.torso_window is not None:
            self.torso_window.clear()
        self.results_tree.delete(*self.results_tree.get_children())
        self.detail_text('')
        self.summary.set('Not analyzed')
        self.frame_labels = ['Not analyzed']
        self.result_scopes = {}
        self.scope.set(self.frame_labels[0])
        self.window_combo.configure(values=self.frame_labels, state='disabled')
        if self.records:
            self.status.set('Inputs changed. Run analysis again to refresh the results.')

    def detail_text(self, text):
        self.detail.configure(state='normal')
        self.detail.delete('1.0', 'end')
        self.detail.insert('1.0', text)
        self.detail.configure(state='disabled')

    def suggest_mode(self, records):
        kinds = {r.waveform for r in records} - {'unknown'}
        if len(kinds) == 1:
            kind = next(iter(kinds))
            mode = {'ecg': 'ecg', 'pulse': 'bench_pulse', 'sine': 'bench_sine'}[kind]
            self.profile.set(next((k for k, v in PROFILES.items() if v == mode)))
            self.change_profile()

    def add_files(self):
        if not self.apply_record():
            return
        paths = filedialog.askopenfilenames(filetypes=[('BDF recordings / ZIP archives', '*.bdf *.zip')])
        if not paths:
            return
        try:
            additions = records_from_paths(paths)
            seen = {(r.path.lower(), r.member) for r in self.records}
            additions = [r for r in additions if (r.path.lower(), r.member) not in seen]
            if not self.records and additions:
                self.suggest_mode(additions)
            used = {r.id for r in self.records}
            for r in additions:
                while r.id in used:
                    r.id += '_new'
                used.add(r.id)
            self.records.extend(additions)
            self.refresh_records()
            if not self.channels:
                self.initialize_channels()
            self.invalidate()
        except (ValueError, OSError, KeyError) as exc:
            messagebox.showerror('Cannot read recording', str(exc))

    def refresh_records(self):
        self.selected = None
        self.record_tree.delete(*self.record_tree.get_children())
        for i, r in enumerate(self.records):
            self.record_tree.insert('', 'end', iid=str(i), values=self.record_row(r))
        if self.records:
            self.record_tree.selection_set('0')
            self.select_record()
        else:
            self.source_label.set('No BDF selected')

    def select_record(self, _=None):
        if self.busy or not self.record_tree.selection():
            return
        index = int(self.record_tree.selection()[0])
        if index == self.selected:
            return  # A duplicate selection event must not overwrite pending edits.
        self.timeline.pause()
        if self.torso_window is not None:
            self.torso_window.timeline.pause()
        if self.selected is not None and self.selected != index and (not self.apply_record()):
            self.record_tree.selection_set(str(self.selected))
            return
        self.selected = index
        r = self.records[index]
        self.loading = True
        for key, value in dict(frequency=str(r.frequency_hz), amplitude='' if r.input_mVpp is None else str(r.input_mVpp), unit='mVpp', repeat=r.repeat_group, setup=r.setup_group, waveform=r.waveform).items():
            self.record_vars[key].set(value)
        self.confirmed.set(r.input_confirmed)
        self.sweep.set(r.sweep)
        try:
            info = BdfReader().inspect(r)
            self.source_label.set(f'{Path(r.member or r.path).name}\n{info.duration_s:g} s | {next(iter(info.sample_rates.values())):g} Hz | {len(info.voltage_labels)} saved voltage channels')
        except (ValueError, OSError) as exc:
            self.source_label.set(str(exc))
        self.loading = False
        if self.result is not None:
            label = self.label_for_record(r.id)
            if label is None:
                self.invalidate()
                self.status.set('Selected record has not been analyzed. Click Run analysis.')
            else:
                self.scope.set(label)
                self.redraw()

    @staticmethod
    def record_row(record):
        return (record.id, record.input_mVpp if record.input_mVpp is not None else '?',
                'Yes' if record.input_confirmed else 'No')

    def apply_record(self):
        if self.selected is None:
            return True
        try:
            r = copy.deepcopy(self.records[self.selected])
            if self.analysis_mode() != 'ecg':
                r.frequency_hz = float(self.record_vars['frequency'].get())
                value = self.record_vars['amplitude'].get().strip()
                unit = self.record_vars['unit'].get()
                if self.analysis_mode() == 'bench_pulse' and unit not in ('mVpp', 'uVpp', 'Vpp'):
                    raise ValueError('Pulse input must be specified as peak-to-peak voltage')
                r.input_mVpp = float(value) * UNIT_FACTORS[unit] if value else None
                if not math.isfinite(r.frequency_hz) or r.frequency_hz <= 0:
                    raise ValueError('Frequency must be positive')
                if r.input_mVpp is not None and (not math.isfinite(r.input_mVpp) or r.input_mVpp <= 0):
                    raise ValueError('Input amplitude must be positive')
                r.input_confirmed = bool(self.confirmed.get())
                if r.input_confirmed and r.input_mVpp is None:
                    raise ValueError('A confirmed input needs a value')
                r.sweep = bool(self.sweep.get())
                r.repeat_group = self.record_vars['repeat'].get().strip()
            r.setup_group = self.record_vars['setup'].get().strip() or 'default'
            r.waveform = self.record_vars['waveform'].get() or 'unknown'
            self.records[self.selected] = r
            self.record_tree.item(str(self.selected), values=self.record_row(r))
            return True
        except (ValueError, KeyError) as exc:
            messagebox.showerror('Invalid record settings', str(exc))
            return False

    def initialize_channels(self, channels=None, reference=''):
        if not self.records:
            return
        self.info = BdfReader().inspect(self.records[0])
        scalp = [c for c in self.info.voltage_labels if not c.upper().startswith('EXG')]
        pool = 'scalp' if scalp else 'EXG'
        if channels and any((c not in self.info.voltage_labels for c in channels)):
            raise ValueError('Project channels are missing from the BDF')
        self.loading = True
        try:
            self.pool.set(pool)
            if channels:
                self.channels = list(channels)
                if all((c.upper().startswith('EXG') for c in channels)):
                    self.pool.set('EXG')
                elif any((c.upper().startswith('EXG') for c in channels)):
                    self.pool.set('all')
            else:
                size = len(scalp) if scalp else len(self.info.voltage_labels)
                self.channels = BdfReader.choose_channels(self.info, min(int(self.count.get()), size), pool)
            self.count.set(str(len(self.channels)))
            self.reference.set(reference if reference in self.channels else self.channels[0])
            self.update_channel_label()
        finally:
            self.loading = False

    def update_channel_label(self):
        self.ref_combo.configure(values=self.channels)
        text = ', '.join(self.channels[:12])
        if len(self.channels) > 12:
            text += f' ... ({len(self.channels)} selected)'
        self.channel_label.configure(text=text or 'No channels selected')

    def apply_count(self):
        try:
            if self.info is None:
                raise ValueError('Open a BDF first')
            self.channels = BdfReader.choose_channels(self.info, int(self.count.get()), self.pool.get())
            if self.reference.get() not in self.channels:
                self.reference.set(self.channels[0])
            self.update_channel_label()
            self.invalidate()
        except ValueError as exc:
            messagebox.showerror('Channel selection', str(exc))

    def choose_channels(self):
        if self.info is None:
            return
        dialog = tk.Toplevel(self.root)
        dialog.title('Select connected electrode channels')
        dialog.geometry('370x480')
        ttk.Label(dialog, text='Ctrl / Shift: multi-select. Status is excluded.', padding=10).pack()
        choices = tk.Listbox(dialog, selectmode='extended', exportselection=False)
        choices.pack(fill='both', expand=True, padx=12)
        for i, name in enumerate(self.info.voltage_labels):
            choices.insert('end', name)
            if name in self.channels:
                choices.selection_set(i)

        def commit():
            selected = [self.info.voltage_labels[i] for i in choices.curselection()]
            if not selected:
                return
            self.channels = selected
            self.count.set(str(len(selected)))
            if self.reference.get() not in selected:
                self.reference.set(selected[0])
            self.update_channel_label()
            self.invalidate()
            dialog.destroy()
        ttk.Button(dialog, text='Use selected channels', command=commit).pack(pady=12)
        dialog.transient(self.root)
        dialog.grab_set()

    def remove_record(self):
        if self.selected is not None:
            self.records.pop(self.selected)
            self.refresh_records()
            if not self.records:
                self.channels, self.info = ([], None)
                self.update_channel_label()
            self.invalidate()

    def clear_records(self):
        self.records, self.channels, self.info = ([], [], None)
        self.refresh_records()
        self.update_channel_label()
        self.invalidate()

    def prepare(self, all_records=False):
        if not self.apply_record():
            return None
        values = asdict(self.settings)
        for key, var in self.limit_vars.items():
            raw = var.get().strip()
            values[key] = None if raw == '' and key in ('thd_limit_pct', 'frequency_limit_pct') else float(raw)
        values['analysis_mode'] = self.analysis_mode()
        values['bench_windows'] = self.windowed.get()
        settings = AnalysisSettings(**values)
        settings.validate()
        if int(self.count.get()) != len(self.channels):
            raise ValueError('Count changed. Click Apply count to select actual BDF channels')
        reference = self.reference.get() if settings.analysis_mode != 'ecg' else ''
        records = self.records
        if not all_records and self.analysis_target.get() == 'Selected record':
            if self.selected is None:
                raise ValueError('Select a record in the left-hand list')
            records = [self.records[self.selected]]
        AnalysisService(settings)._validate(records, self.channels, reference)
        return (copy.deepcopy(records), settings, list(self.channels), reference)

    def load_path(self, path):
        try:
            records, settings, channels, reference = load_project(path)
            display = json.loads(Path(path).read_text(encoding='utf-8-sig')).get('display', {})
            layout = TorsoLayout(**display.get('torso', {}))
            if not records:
                raise ValueError('Project contains no BDF records')
            BdfReader().inspect(records[0])
            self.records, self.settings = (records, settings)
            self.torso_layout = layout
            if self.torso_window is not None:
                self.torso_window.set_layout(layout)
            self.loading = True
            self.windowed.set(settings.bench_windows)
            for key, var in self.limit_vars.items():
                var.set('' if getattr(settings, key) is None else str(getattr(settings, key)))
            self.profile.set(next((k for k, v in PROFILES.items() if v == settings.analysis_mode)))
            self.loading = False
            self.change_profile()
            self.refresh_records()
            self.initialize_channels(channels, reference)
            self.invalidate()
            self.status.set(f'Loaded {len(records)} records. Verify wiring and input calibration.')
        except (ValueError, OSError, KeyError, TypeError) as exc:
            self.loading = False
            messagebox.showerror('Project load failed', str(exc))

    def load_dialog(self):
        path = filedialog.askopenfilename(filetypes=[('JSON project', '*.json')])
        if path:
            self.load_path(path)

    def load_lab(self):
        try:
            label = self.lab_choice.get()
            patterns = {'10 electrodes - Sine': '*10 Active*Sine*.zip', '128 electrodes - Sine': '*All electrodes_Sine*.zip', '128 electrodes - Pulse': '*All electrodes_Pulse*.zip', '10 electrodes - ECG': '*10 Active*ECG*.zip'}
            paths = list((HERE.parent / 'latest lab check').glob(patterns[label]))
            if not paths:
                raise ValueError('Latest lab archive not found. Use Open BDF / ZIP instead')
            self.records = records_from_paths([sorted(paths)[-1]])
            self.count.set('128' if label.startswith('128') else '10')
            self.suggest_mode(self.records)
            self.refresh_records()
            self.initialize_channels()
            self.invalidate()
            self.status.set('Latest lab loaded. Input amplitudes are unconfirmed; no repeat groups were assigned automatically.')
        except (ValueError, OSError) as exc:
            messagebox.showerror('Lab preset', str(exc))

    def save_dialog(self):
        try:
            request = self.prepare(all_records=True)
            if request is None:
                return
            path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON project', '*.json')])
            if path:
                save_project(path, *request, display={'torso':asdict(self.torso_layout)})
        except (ValueError, OSError) as exc:
            messagebox.showerror('Save failed', str(exc))

    def load_demo(self):
        try:
            count = int(self.count.get())
            if not 1 <= count <= 256:
                raise ValueError('Demo supports 1 to 256 electrodes')
            if self.analysis_mode() == 'bench_sine' and self.windowed.get():
                self.records = create_timeline_demo(HERE / 'output/synthetic_inputs', count)
            else:
                self.records = create_mode_demo(HERE / 'output/synthetic_inputs', count, self.analysis_mode())
            self.refresh_records()
            self.initialize_channels()
            self.invalidate()
            self.run()
        except (ValueError, OSError) as exc:
            messagebox.showerror('Demo', str(exc))

    def set_busy(self, busy):
        self.busy = busy
        if busy:
            self.timeline.clear('Calculating windows in the background...')
        self.record_tree.configure(selectmode='none' if busy else 'browse')
        for w in self.controls:
            w.configure(state='disabled' if busy else 'normal')
        for w in self.combos:
            w.configure(state='disabled' if busy else 'readonly')
        self.context_states()
        if busy:
            self.progress.start(15)
        else:
            self.progress.stop()

    def run(self):
        try:
            request = self.prepare()
            if request is None:
                return
            records, settings, channels, reference = request
            self.invalidate()
            self.set_busy(True)

            def worker():
                try:
                    result = AnalysisService(settings).analyze(records, channels, reference, lambda text: self.events.put(('progress', text)))
                    self.events.put(('done', result))
                except Exception as exc:
                    self.events.put(('error', str(exc)))
            threading.Thread(target=worker, daemon=True).start()
            self.root.after(80, self.poll)
        except (ValueError, OSError, KeyError) as exc:
            messagebox.showerror('Cannot start analysis', str(exc))

    def poll(self):
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == 'progress':
                    self.status.set(payload)
                else:
                    self.set_busy(False)
                    if event == 'error':
                        self.status.set('Analysis failed. Check record, channel and mode settings.')
                        messagebox.showerror('Analysis failed', payload)
                    else:
                        self.accept_result(payload)
        except queue.Empty:
            pass
        if self.busy:
            self.root.after(80, self.poll)

    def accept_result(self, result):
        self.result = result
        self.settings = AnalysisSettings(**result.settings)
        self.result_scopes = {f'Record: {r.record.id}': ('record', r.record.id) for r in result.runs}
        for i, frame in enumerate(result.frames):
            self.result_scopes[f"Window: {frame['record_id']} | {frame['start_s']:g}-{frame['end_s']:g} s"] = ('frame', i)
        # Only an explicit choice displays the worst case across multiple files.
        if len(result.runs) > 1:
            self.result_scopes['All analyzed records / worst case'] = ('all', None)
        self.frame_labels = list(self.result_scopes)
        self.window_combo.configure(values=self.frame_labels, state='readonly')
        record_id = self.records[self.selected].id if self.selected is not None else result.runs[0].record.id
        self.scope.set(self.label_for_record(record_id) or self.frame_labels[0])
        first_window = next((label for label, (kind, value) in self.result_scopes.items()
                             if kind == 'frame' and result.frames[value]['record_id'] == record_id), None)
        if first_window:
            self.scope.set(first_window)
        demo = all((r.record.id.startswith('DEMO_') for r in result.runs))
        tail = sum((r.channels[result.electrodes[0].name].get('unassessed_tail_s', 0) for r in result.runs))
        excluded = sum(r.excluded_tail_s for r in result.runs)
        windowed = self.analysis_mode() == 'ecg' or result.settings.get('bench_windows', False)
        self.status.set(('SYNTHETIC DEMO | ' if demo else '') + f'{len(result.runs)} BDF | {len(result.electrodes)} electrodes | {result.elapsed_s:.2f} s analysis' + (f' | {len(result.frames)} complete windows | {tail:g} s without a complete window' if windowed else '') + f' | {excluded:g} s excluded in total')
        self.notebook.select(0)
        self.redraw()

    def label_for_record(self, record_id):
        return next((label for label, value in self.result_scopes.items() if value == ('record', record_id)), None)

    def change_scope(self, _=None):
        self.timeline.pause()
        if self.torso_window is not None:
            self.torso_window.timeline.pause()
        label = self.scope.get()
        kind, value = self.result_scopes.get(self.scope.get(), ('all', None))
        if kind in ('record', 'frame'):
            record_id = value if kind == 'record' else self.result.frames[value]['record_id']
            index = next((i for i, r in enumerate(self.records) if r.id == record_id), None)
            if index is not None:
                self.record_tree.selection_set(str(index))
                self.select_record()
            self.scope.set(label)
        self.redraw()

    def select_window(self, index, source='main'):
        if self.result is None:
            return
        if source == 'torso':
            self.timeline.pause()
        elif self.torso_window is not None:
            self.torso_window.timeline.pause()
        label = next(label for label, value in self.result_scopes.items() if value == ('frame', index))
        self.scope.set(label)
        self.redraw()

    def displayed_electrodes(self):
        if self.result is None:
            return []
        kind, value = self.result_scopes.get(self.scope.get(), ('all', None))
        if kind == 'record':
            return self.result.record_electrodes(value)
        if kind == 'frame':
            return self.result.window_electrodes(value)
        return self.result.electrodes

    def update_timeline(self, mode):
        kind, value = self.result_scopes.get(self.scope.get(), ('all', None))
        record_id = (self.result.frames[value]['record_id'] if kind == 'frame' else value if kind == 'record'
                     else self.records[self.selected].id if self.selected is not None else self.result.runs[0].record.id)
        key = (id(self.result), record_id, mode)
        if key not in self.timeline_cache:
            rank = {'green': 0, 'yellow': 1, 'red': 2}
            items = []
            for i, frame in enumerate(self.result.frames):
                if frame['record_id'] != record_id:
                    continue
                colors = [e.metric(mode).color for e in self.result.window_electrodes(i)
                          if not (mode == 'synchronization' and e.is_reference)]
                color = max(colors, key=rank.get) if colors else 'yellow'
                items.append((i, frame['start_s'], frame['end_s'], color))
            self.timeline_cache[key] = items
        ecg = self.analysis_mode() == 'ecg'
        run = next(r for r in self.result.runs if r.record.id == record_id)
        duration = self.result.settings['ecg_window_s' if ecg else 'bench_window_s']
        message = (f'Recorded {run.recorded_duration_s:g} s; retained {run.duration_s:g} s after excluding {run.excluded_tail_s:g} s; need {duration:g} s. No complete windows.'
                   if run.duration_s < duration else 'Enable Build time windows and run analysis.')
        self.timeline.show((id(self.result), record_id), self.timeline_cache[key],
                           current=value if kind == 'frame' else None, message=message)

    def redraw(self):
        if self.result is None:
            return
        electrodes = self.displayed_electrodes()
        mode = self.views[self.mode.get()]
        self.update_timeline(mode)
        self.heatmap.show(electrodes, mode)
        if self.torso_window is not None:
            kind,value = self.result_scopes.get(self.scope.get(), ('all',None))
            self.torso_window.show(electrodes,mode,self.scope.get(),list(self.views),self.timeline.key,
                                   self.timeline.items,value if kind=='frame' else None,self.timeline.caption.get())
        counts = {c: sum((e.metric(mode).color == c for e in electrodes)) for c in COLORS}
        self.summary.set(f"Green {counts['green']} | Yellow {counts['yellow']} | Red {counts['red']}")
        self.results_tree.delete(*self.results_tree.get_children())
        columns = ['name'] + list(dict.fromkeys(self.views.values()))
        self.results_tree.configure(columns=columns)
        for key in columns:
            self.results_tree.heading(key, text='Electrode' if key == 'name' else next((k for k, v in self.views.items() if v == key)))
            self.results_tree.column(key, width=145, minwidth=90)
        for i, e in enumerate(electrodes):
            self.results_tree.insert('', 'end', iid=str(i), values=(e.name, *[COLOR_LABELS[e.metric(k).color] for k in columns[1:]]))
        if electrodes:
            self.show_detail(next((e for e in electrodes if e.name == self.focused_electrode), electrodes[0]))

    def show_detail(self, electrode):
        self.focused_electrode = electrode.name
        mode = self.views[self.mode.get()]
        metric = electrode.metric(mode)
        lines = [electrode.name + (' | REF (not independently verified)' if electrode.is_reference else ''),
                 'Scope: ' + self.scope.get(), self.mode.get() + ' | ' + COLOR_LABELS[metric.color], metric.message]
        if self.result:
            kind, value = self.result_scopes.get(self.scope.get(), ('all', None))
            record_id = self.result.frames[value]['record_id'] if kind == 'frame' else value
            for run in self.result.runs:
                if kind != 'all' and run.record.id != record_id:
                    continue
                lines.append(f'{run.record.id}: analyzed 0-{run.duration_s:g} s of {run.recorded_duration_s:g} s recorded'
                             + (f'; excluded {run.duration_s:g}-{run.recorded_duration_s:g} s (final {run.excluded_tail_s:g} s)' if run.excluded_tail_s else '; no tail excluded'))
        if metric.values:
            lines.append(json.dumps(metric.values, indent=2, ensure_ascii=False, allow_nan=False))
        if self.result and self.analysis_mode() != 'ecg':
            kind, record_id = self.result_scopes.get(self.scope.get(), ('all', None))
            if kind == 'frame':
                frame = self.result.frames[record_id]
                value = frame['metrics'][electrode.name]['synchronization'].values
                lines.append(f"Window only: {frame['start_s']:g}-{frame['end_s']:g} s | rising {value['rising_count']} / falling {value['falling_count']}")
            for run in self.result.runs:
                if kind == 'frame':
                    continue
                if kind == 'record' and run.record.id != record_id:
                    continue
                value = run.channels[electrode.name]['sync'].values
                verified = 'Yes' if run.record.input_confirmed else 'No'
                lines.append(f"{run.record.id}: Vpp verified: {verified} | {run.duration_s:g} s, {run.sample_rate_hz:g} Hz | rising {value['rising_count']} / falling {value['falling_count']}")
        self.detail_text('\n'.join(lines))
        if self.torso_window is not None:
            self.torso_window.set_detail('\n'.join(lines),electrode.name)

    def open_torso(self):
        self.timeline.pause()
        if self.torso_window is None:
            self.torso_window = TorsoWindow(self.root,self.mode,list(self.views),self.redraw,self.show_detail,
                lambda index:self.select_window(index,source='torso'),self.torso_layout,
                self.set_torso_layout,lambda:setattr(self,'torso_window',None))
        else:
            self.torso_window.lift()
        if self.result is not None:
            self.redraw()

    def set_torso_layout(self,layout):
        self.torso_layout=layout

    def select_result(self, _=None):
        if self.result is not None and self.results_tree.selection():
            self.show_detail(self.displayed_electrodes()[int(self.results_tree.selection()[0])])
            self.notebook.select(0)

    def export(self):
        if self.result is None:
            messagebox.showinfo('Export', 'Run analysis for the current settings first')
            return
        self.timeline.pause()
        if self.torso_window is not None:
            self.torso_window.timeline.pause()
        folder = filedialog.askdirectory(title='Choose report folder')
        if folder:
            try:
                demo = all((r.record.id.startswith('DEMO_') for r in self.result.runs))
                title = ('SYNTHETIC DEMO | ' if demo else '') + self.profile.get()
                scope = self.scope.get()
                path = ReportExporter().save(self.result, folder, self.views[self.mode.get()], title, electrodes=self.displayed_electrodes(), scope=scope,
                                             display={'torso':asdict(self.torso_layout)})
                if self.torso_window is not None:
                    self.torso_window.save(folder)
                self.status.set(f'Exported: {path}')
            except (ValueError, OSError) as exc:
                messagebox.showerror('Export failed', str(exc))
if __name__ == '__main__':
    root = tk.Tk()
    ElectrodeQAApp(root)
    root.mainloop()
