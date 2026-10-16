"""Peer entry points for real-time monitoring and post-recording analysis."""
import tkinter as tk
from tkinter import ttk


class WorkspaceApp:
    def __init__(self, root):
        self.root = root
        self.live_window = self.post_window = self.post_app = None
        self.selector = None
        root.withdraw()
        ttk.Style(root).theme_use('clam')
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.show_selector()

    def show_selector(self):
        self.selector = tk.Toplevel(self.root)
        self.selector.title('Electrode QA | Real-time / Post')
        self.selector.geometry('900x470'); self.selector.minsize(760, 430)
        page = ttk.Frame(self.selector, padding=32); page.pack(fill='both', expand=True)
        ttk.Label(page, text='Electrode QA', font=('Segoe UI', 26, 'bold')).pack(anchor='w')
        ttk.Label(page, text='Choose when to analyze your signals', font=('Segoe UI', 13)).pack(anchor='w', pady=(8, 24))
        cards = ttk.Frame(page); cards.pack(fill='both', expand=True)
        for col, title, description, action in (
            (0, 'Real-time', 'Live LSL monitoring\nAutomatic source discovery and connection\nECG quality / known-sine tests', self.open_live),
            (1, 'Post analysis', 'Analyze saved BDF / ZIP records\nBench validation / ECG quality\nReview windows and export reports', self.open_post)):
            cards.columnconfigure(col, weight=1, uniform='mode')
            card = ttk.LabelFrame(cards, text=title, padding=20)
            card.grid(row=0, column=col, sticky='nsew', padx=(0,12) if col==0 else (12,0))
            ttk.Label(card, text=description, justify='left', wraplength=320).pack(anchor='w', pady=(0,20))
            ttk.Button(card, text='Open '+title, command=action).pack(fill='x')
        ttk.Label(page, text='Signal-quality screening; channel alerts include reasons and require interpretation.').pack(anchor='w', pady=(24,0))
        self.selector.protocol('WM_DELETE_WINDOW', self.close)

    def dismiss_selector(self):
        if self.selector is not None:
            self.selector.destroy()
            self.selector = None

    def open_live(self):
        from views.live_window import LiveWindow
        if self.live_window is None or not self.live_window.winfo_exists():
            self.live_window = LiveWindow(self.root, on_post=self.open_post)
            self.live_window.protocol('WM_DELETE_WINDOW', self.return_to_selector)
        if self.post_window is not None:
            self.post_app.timeline.pause()
            if self.post_app.torso_window is not None:
                self.post_app.torso_window.close()
            self.post_window.withdraw()
        self.live_window.deiconify(); self.live_window.lift()
        self.dismiss_selector()

    def open_post(self):
        from gui import ElectrodeQAApp
        if self.post_window is None or not self.post_window.winfo_exists():
            self.post_window = tk.Toplevel(self.root)
            self.post_app = ElectrodeQAApp(self.post_window)
            self.post_app.workspace = self
            self.post_window.protocol('WM_DELETE_WINDOW', self.return_to_selector)
        if self.live_window is not None:
            self.live_window.withdraw()
        self.post_window.deiconify(); self.post_window.lift()
        self.dismiss_selector()

    def close_analysis_windows(self):
        if self.live_window is not None and self.live_window.winfo_exists():
            self.live_window.close()
        if self.post_window is not None and self.post_window.winfo_exists():
            self.post_app.close()
        self.live_window = None
        self.post_window = self.post_app = None

    def return_to_selector(self):
        self.close_analysis_windows()
        self.show_selector()

    def close(self):
        self.close_analysis_windows()
        self.root.destroy()
