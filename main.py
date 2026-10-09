"""Run the desktop app, or analyze/export without a GUI for repeatable tests."""
from pathlib import Path
import argparse
from config import AnalysisSettings
from services.analysis_service import AnalysisService
from services.demo_data import create_mode_demo
from utils.project_io import load_project
from utils.report_exporter import ReportExporter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--mode", choices=("bench_sine", "bench_pulse", "ecg"), default=None)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--electrodes", type=int, default=8)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent/"output/demo")
    args = parser.parse_args()
    if args.headless:
        if args.demo:
            if not 1 <= args.electrodes <= 256:
                parser.error("Demo electrode count must be between 1 and 256")
            mode = args.mode or "bench_sine"
            records = create_mode_demo(args.out/"synthetic_inputs", args.electrodes, mode)
            settings, channels, reference = AnalysisSettings(analysis_mode=mode), [f"EXG{i+1}" for i in range(args.electrodes)], "EXG1"
            title = "SYNTHETIC DEMO - not laboratory evidence"
        elif args.config:
            records, settings, channels, reference = load_project(args.config)
            if not channels:
                from utils.bdf_reader import BdfReader
                info = BdfReader().inspect(records[0])
                pool = "scalp" if any(not c.upper().startswith("EXG") for c in info.voltage_labels) else "EXG"
                channels = BdfReader.choose_channels(info, args.electrodes, pool)
            reference = reference or channels[0]
            title = "Electrode QA laboratory results"
        else:
            parser.error("--headless requires --demo or --config")
        if args.mode:
            settings.analysis_mode = args.mode
        result = AnalysisService(settings).analyze(records, channels, reference, print)
        report = ReportExporter().save(result, args.out, "ecg_quality" if settings.analysis_mode == "ecg" else "bench_summary", title)
        print(f"{len(result.electrodes)} electrodes, {result.elapsed_s:.3f} s. Report: {report.resolve()}")
    else:
        import tkinter as tk
        from gui import ElectrodeQAApp
        root = tk.Tk()
        app = ElectrodeQAApp(root)
        if args.config:
            app.load_path(args.config)
        if args.demo:
            app.count.set(str(args.electrodes))
            root.after(150, app.load_demo)
        if args.mode:
            from gui import PROFILES
            app.profile.set(next(k for k,v in PROFILES.items() if v == args.mode))
            app.change_profile()
        root.mainloop()


if __name__ == "__main__":
    main()
