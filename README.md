# Electrode QA - Real-time / Post analysis

English Tkinter GUI with peer Real-time and Post analysis entry points. Real-time defaults to ECG quality screening, with an optional known-sine mode. CT noise analysis is a separate application in `../noise-analysis`; launch its `Start_Noise_Analysis.cmd`.
See [current workflow](REALTIME_POST_GUIDE.md), [Git / setup guide](GIT_SETUP_CN.md), and [deployment findings for review](DEPLOYMENT_REVIEW_CN.md).
For a complete Chinese explanation of the architecture, formulas, callbacks and classes, read [CODE_GUIDE_ZH.md](CODE_GUIDE_ZH.md).

## Run in VS Code

Open this repository folder or `Electrode-QA.code-workspace`. On a new Windows checkout, install Python 3.10+ (3.12 recommended), then run `Setup_Environment.cmd` once. This creates the ignored local `.venv` and installs `requirements_live.txt`, including pylsl. Select `.venv/Scripts/python.exe` in VS Code and press F5 with **Electrode QA - Real-time / Post** selected. Equivalent commands:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements_live.txt
.\.venv\Scripts\python.exe live_main.py
```

`Start_Electrode_QA.cmd` also starts the mode selector; `Start_Live.cmd` opens Real-time directly. Tkinter normally ships with Python on Windows. Post analysis needs no live ActiView connection. Real-time requires an LSL outlet and verified channel/unit mapping. Existing `dist/` executables have not been rebuilt with these source changes.

Running `gui.py` with VS Code's **Run Python File** also opens the Real-time / Post selector, just like `main.py` without arguments. If this existing lab checkout has no `.venv`, use **Python: Select Interpreter → Enter interpreter path** and select `../.venv-lsl/Scripts/python.exe`. A fresh clone should use `Setup_Environment.cmd` to create its own `.venv`.

## Three analysis paths

| Workflow | Measurements |
|---|---|
| Stage 1 - Bench / Sine | Gain, multi-level linearity, rising/falling zero crossings, independent repeatability, SNR, SINAD, THD, frequency error |
| Stage 1 - Bench / Pulse | Two-platform amplitude, rising/falling midpoint edges, frequency, linearity and independent repeatability |
| Stage 2 - ECG quality | Complete-window bSQI, pSQI, Pearson kSQI, basSQI, near-flat and digital clipping checks |

ECG and pulse signals are never passed through the sine-fit path. Declared waveform mismatches and mixed physical setup groups are rejected. Filename hints remain editable and are not proof of the physical waveform or calibration.

## Typical workflow

1. Choose the analysis workflow.
2. Open BDF or ZIP files, or choose a Latest lab preset and click Load.
3. Verify the declared waveform and physical setup group.
4. For bench data, enter actual input frequency and amplitude. The GUI uses the entered amplitude and units automatically; no confirmation checkbox is required. Pulse inputs must be peak-to-peak; peak/RMS conversions are sine-specific.
5. Use Choose channels to select the actual connected BDF channels, or enter Count and click Select first N to select voltage channels in file order. There is no scalp/EXG grouping. Verify the displayed names against your wiring.
6. Select a timing reference for Stage 1. Stage 2 does not require one.
7. Criteria now default to Frequency error = 0.1% and THD = 1%. Exclude final (s) defaults to 1 per file; set 0 to retain every sample. Analyze defaults to Selected record: Run analysis processes only the highlighted BDF. Choose All loaded records explicitly for linearity/repetition or batch analysis.
8. Enable Build time windows for bench data (on by default). Set Window (s) = 10 and Step (s) = 1 for overlapping windows, or Step (s) = 10 for consecutive blocks. ECG always uses windows; its existing default step is 5 s. Run analysis calculates the windows in a background worker.
9. Result scope initially selects the first complete window, or the whole record when no complete window exists. Drag the time slider, click the colored strip, or use Previous / Next / Play / Pause. Click an electrode for its values; it stays selected as playback advances. Selecting another analyzed file pauses playback and switches to that file's whole-record result; its windows are available on the slider. An unprocessed file requires Run analysis.
10. Result scope also offers Record and, after a multi-file run, All analyzed records / worst case. Select the latter for multi-record Linearity, Repetition or Full protocol.
11. Click **3D torso** beside Metric for the physical front/back view. Select Front / Back, drag to rotate, or use the wheel to zoom. Its timeline selects the same window as the main grid.
12. Export the current view and full underlying results.

Changing any analysis input invalidates the old heatmap. The original BDF/ZIP files are never modified.

Input amplitudes and units are used automatically for each record, including loaded projects. Apply record or Run analysis saves edits; no Vpp confirmation checkbox or Verified column is shown. Missing amplitudes remain unavailable for absolute gain. Batch warnings name their source files. Save project preserves all loaded records even when Analyze is set to Selected record.

## Meaning of the colors and scope

- Green: evaluated criteria are within the selected limits.
- Yellow: near a limit, insufficient data, unverified input, uncalibrated acceptance, or descriptive-only measurement.
- Red: a signal check needs attention. It does not prove that an electrode is physically damaged.

Bench summary combines the applicable gain, timing, SNR, THD and frequency checks for the displayed window or record. Only the explicit All analyzed records / worst case scope combines files. Full protocol also requires linearity and independent repeats in that multi-record scope. Single-record and window views mark those multi-record metrics unavailable. Gain + timing preserves the original narrower view. Reference self-comparison is not counted as independent synchronization verification.

ECG record view uses the worst complete window within the retained interval. Bench record view recalculates the entire retained interval; it is separate from its window results. All analyzed records / worst case aggregates the analyzed files; the window view reports one specific interval. Overlapping windows are not independent runs. A final complete window ending at the retained interval's end covers the tail when the regular step does not land there. Intervals shorter than the window are never padded or joined; bench whole-record analysis remains available, while ECG reports insufficient data.

## Final-second exclusion

By user request, every workflow excludes the last 1 s of each file before sine/pulse fitting, gain, spectral metrics, crossing detection, linearity/repetition inputs, ECG checks and window generation. Samples at and after `recorded duration - 1 s` are excluded. A fractional exclusion is rounded up to a whole sample. This is an analysis-only crop, not deletion from the BDF. It applies to the record summary, grid, 3D view, timeline and exports alike. It does not remove any disturbance earlier in the retained data.

For an 85 s file, the retained interval is 0-84 s; 10 s windows with 1 s steps give 75 windows, ending at 74-84 s. Details/report/JSON distinguish recorded duration, analyzed duration and excluded tail. Excluded data have no pass/fail result. An exclusion that leaves no samples produces an explicit error; reduce Exclude final (s) or set it to 0. Short retained recordings still undergo the usual minimum-cycle/full-window checks.

Settings persist in project version 3. Older projects with blank THD/frequency defaults adopt 1% and 0.1%; explicit numeric limits are preserved. Version 3 also preserves deliberately cleared limits or a disabled crop. New and old projects without an exclusion setting default to 1 s.

Verified on actual Lab 5 Test 4 (85 s, 16384 Hz), selecting A1, A2 and D32: 75 windows, final 74-84 s, no sine waveform-quality flags in that final window. Original input calibration remains unconfirmed. Evidence: `output/tail_exclusion_validation/lab5_test4.json`.

## Time slider and animation

The colored strip shows the worst selected channel for the current metric in each window. Next alert moves to the next yellow or red window. Synchronization colors exclude reference self-comparison. Playback speeds are 0.5x, 1x, 2x and 4x, relative to the recorded time between window starts. Playback ends at the last window; manual scrubbing pauses it. It never crosses into another BDF automatically.

Windows are computed once after Run analysis. Scrubbing reuses cached results and snaps to the available starts; it does not re-read the BDF. Changing duration, step, channels or criteria clears the cache and requires a new run. This is offline playback, not an ActiView live stream. A red 10-second window identifies an interval requiring inspection, not the exact onset or cause of a fault.

For a 12 s record with the default 1 s exclusion and a 10 s window / 1 s step, the windows are 0-10 and 1-11 s. Setting exclusion to 0 also includes 2-12 s. The actual 3 s Test 6 retains 2 s and cannot provide a 10 s window. The approximately 90 s pulse records support longer playback. A crossing at a window boundary may be omitted if samples on both sides are unavailable; complete periods and event matching are evaluated within each window.

For a quick example, choose Bench / Sine, enable Build time windows, set Count to 8 and click Demo. The synthetic 31 s recording retains 30 s with the default crop and has a 50% amplitude loss on EXG2 during 10-20 s. Choose Gain error and drag between 0-10, 10-20 and 20-30 s. Windows that overlap a transition can report poor waveform quality. Disable Build time windows before Demo to use the original multi-level/repeat demonstration.

## Measurement definitions

Sine gain uses fundamental Vpp from a sine/cosine/DC/linear-drift fit. Linearity needs at least three distinct confirmed input levels at a common frequency and setup. Repeatability needs at least three genuinely independent runs at the same nominal input and frequency.

Timing uses actual interpolated crossings, separately for both directions. Each reference event owns a disjoint +/-T/4 window. Missing events keep their original indices. Periodic signals cannot resolve whole-cycle absolute delays. Subsample interpolation requires calibration when the sampling interval exceeds the timing tolerance.

SNR excludes the explicitly fitted harmonics; residual noise power is integrated over the stated band (default 0-100 Hz, constrained by Nyquist). THD includes fitted harmonic orders 2-5 by default. Higher unmodeled harmonics inside the band remain in the residual. SINAD includes fitted harmonic power in the denominator. SNR and SINAD have a finite 160 dB numerical reporting ceiling. Measurement bandwidth/order are retained in exports.

THD defaults to 1% and frequency error to 0.1%, as requested by the user. These are configured engineering limits, not universal electrode standards. Clearing a limit still marks acceptance uncalibrated/yellow. SINAD is descriptive-only and excluded from Bench summary.

ECG defaults: 10 s window, 5 s step. EnergyQRSDetector uses integrated derivative energy; ProminenceQRSDetector uses bandpassed amplitude/prominence. Both operate on the same channel. A one-to-one 50 ms match gives bSQI. Other ratios use Welch power, with left-closed/right-open frequency intervals. kSQI uses Pearson, not excess, kurtosis. Worst-component fusion and thresholds are provisional; this is not a clinically validated classifier.

## Classes and data flow

```text
gui.py / ElectrodeQAApp
    -> InputRecord + AnalysisSettings
    -> AnalysisService
        -> BdfReader + WindowPlan
        -> SineFitter + BenchSpectrumAnalyzer, or PulseAnalyzer
        -> gain / linearity / timing / repeatability
        -> or ECGQualityAnalyzer + two QRS detectors + BeatAgreement
    -> MetricResult / ElectrodeResult / AnalysisResult
    -> TimelineView + HeatmapView + TorsoWindow / ReportExporter
```

The calculation classes do not import Tkinter. `gui.py` handles form state, callbacks, the worker queue and result selection; it does not calculate SQIs in widget callbacks.

## 3D torso layout

The default follows the user's body-side convention: **A/C on the person's left; B/D on the person's right**. C is behind A; D is behind B. R/L labels refer to the person, not the viewer.

| Camera | Screen left | Screen right |
|---|---|---|
| Front | B / person's right | A / person's left |
| Back | C / person's left | D / person's right |

Each bank has three vertical columns, centre to outside: 1-10, 11-21, 22-32. Numbering is serpentine: small numbers are at the bottom of the outer columns, and the middle column runs in the reverse direction. Front-screen columns from left to right, listed top-to-bottom, are B32-B22, B11-B21, B10-B1, A10-A1, A11-A21, A32-A22. B/D follow the user's alternating-direction instruction; A/C use the same mirrored pattern as a working assumption. DRL is an unscored orientation marker on the person's right.

The 3D popup uses the exact selected metric and record/window results from the main GUI. Green/yellow/red retain the grid's meanings. Unselected positions are gray. EXG or other labels without known torso positions remain in the grid and are explicitly listed as unmapped; they are never assigned a guessed anatomical position. The coordinates are a schematic based on the sketch, not measured anatomy or a standard cap montage.

Click a colored electrode for its values. The Channels to review list includes front and back alerts; selecting one turns the model to its surface. Front/back counts prevent alerts on the hidden side being overlooked. Rotate/zoom and selected electrode persist when the time window changes. Starting playback in either window stops playback in the other. Closing the popup cancels its timer; changing analysis inputs clears its old colors.

Display-only side/numbering controls do not recalculate signal metrics. Save project preserves these settings under `display.torso`; old projects use the defaults above. `TorsoLayout` owns channel coordinates, `TorsoView` projects and draws the mesh/markers, and `TorsoWindow` handles the expanded view and shared controls. All three are in `views/`. No new dependencies are required.

## Large BDF recordings

Analysis uses `BdfReader.open_data()` to decode BDF records sequentially. Arrays larger than 64 MiB use a temporary, column-major memory-mapped file in `%TEMP%/electrode-qa-cache/`. Sine fits and detrending process individual electrodes, retaining the original sample rate for gain and crossing times. Whole-record and window results keep the same definitions. Spectral analysis retains its existing band-limited resampling method.

The previous GUI error, "Selected data exceed memory limit", came from an 80-million-value in-memory guard. For example, 85 s x 16384 Hz x 128 channels needs about 1.43 GB for one float64 array alone. The GUI now uses the disk-backed path; changing the window length is not necessary to bypass the old guard. The direct `BdfReader.read()` API remains limited to small in-memory requests.

Temporary files are closed and removed on normal completion or an analysis exception. The cache stays outside the project/OneDrive folder. Cleanup locks produce a console warning without discarding completed results. Sufficient free disk space is checked before allocation. Force-terminating Python can leave a cache directory; remove leftover cache files only after all analyses have stopped. Original BDF/ZIP sources are read-only. Large/high-rate files still take longer to analyze; status messages indicate decoding, fitting and window progress.

Validated on the actual Lab 5 Test 4 recording: 85 s, 16384 Hz, 128 selected channels, 10 s windows / 1 s steps. All 76 windows completed in 208.5 s on this machine; the final 75-85 s GUI view and automatic cache cleanup were verified. Results: `output/memory_validation/lab5_test4.json`. Input calibration was left unconfirmed during this processing check. The test suite also checks numerical equivalence and cleanup failures.

## Exports

When the 3D popup is open, GUI Export also writes `torso_view.png` for its current camera/metric/scope and `torso_layout.json` for the exact schematic coordinates and view settings. The grid exports remain available alongside these files.

`heatmap.png`, `electrodes.csv`, `results.json`, `project.json`, `report.html`, `bench_metrics.csv`, `ecg_windows.csv`, `window_metrics.csv`, `window_summary.csv`, `zero_counts_and_time.csv`, `zero_pairs.csv`.

The PNG/electrodes CSV describe the selected view. JSON retains the full run and the exact exported scope. window_metrics.csv contains every window's component values; window_summary.csv contains per-electrode colors and reasons for the selected export metric across all windows. Window timing summaries retain event counts and delay statistics; detailed zero_* event-pair CSVs remain whole-record results. Pulse events use the existing zero_* CSV names for compatibility; the event_definition field distinguishes midpoint edges. Non-applicable CSV files contain headers only. Projects save the analysis mode and window settings and support migration from the original monopolar configuration.

## Reproduce tests and demonstrations

```powershell
python -m unittest discover -s tests -v
python main.py --headless --demo --mode bench_sine --electrodes 8 --out output/sine-demo
python main.py --headless --demo --mode bench_pulse --electrodes 8 --out output/pulse-demo
python main.py --headless --demo --mode ecg --electrodes 8 --out output/ecg-demo
```

Demo inputs are synthetic and clearly labeled. ECG demo channels include a baseline disturbance, a temporary flatline and broadband noise. The demo's clean waveform is constructed to exercise the provisional pass region; it is not evidence of clinical accuracy.

Known-signal tests cover amplitude, both edge directions, missing-period matching, nonlinear gain, repetition, a 10% harmonic, 2% frequency offset, noisy/flat ECG, short data, waveform routing, project roundtrips, exports and GUI state.

The full suite has 45 passing tests, including anatomical left/right mapping, front/back correspondence, numbering direction, inactive/unmapped channels, 3D picking versus rotation, synchronized time-window colors, playback ownership, stale-result clearing, and layout/export roundtrips. Tail-exclusion tests compare cropped sine, pulse and ECG results against independently written clean-prefix BDFs, and check digital clipping, source preservation, disk-cache cleanup, per-file windows, short data, defaults, migration and exported durations. Example UI captures in `output/torso_preview/` use explicitly labeled synthetic states, not laboratory measurements.

All 17 latest-lab BDFs were processed. Results are in `output/stage_validation/validation.json` and its four group folders. Both actual ECG files are 2 s, so they produce no complete default ECG windows. The 128-channel sine group's worst-record summary is red, driven by low SNR in Test 3; this is not a diagnosis of 128 damaged electrodes.

## Current limits

Offline BDF/ZIP analysis and optional live LSL known-sine screening are supported. Live ECG/pulse, live timing/linearity/repetition, native ActiView TCP, LQMLib and CT condition-pair analysis are not implemented. Signal findings do not identify electrode damage, and clinical/electrode-fault accuracy is not validated. Pulse estimation assumes two reasonably stable levels and is unsuitable for extremely narrow (<~0.5% duty) or complex multilevel pulses. Scope, bandwidth, input calibration and channel mapping must remain explicit.
