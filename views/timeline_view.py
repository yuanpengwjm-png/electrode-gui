"""Cached-window scrubber and playback. This view never calculates signal metrics."""
import tkinter as tk
from tkinter import ttk
from config import COLORS


class TimelineView(ttk.Frame):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.on_select = on_select
        self.items = []  # (global frame index, start seconds, end seconds, color)
        self.key = None
        self.position = None
        self.playing = False
        self.timer = None
        self.setting_scale = False
        self.speed = tk.StringVar(value='1x')
        self.caption = tk.StringVar(value='Run analysis to build time windows.')
        row = ttk.Frame(self)
        row.pack(fill='x')
        self.previous = ttk.Button(row, text='Previous', command=lambda: self.step(-1))
        self.play = ttk.Button(row, text='Play', command=self.toggle)
        self.following = ttk.Button(row, text='Next', command=lambda: self.step(1))
        self.alert = ttk.Button(row, text='Next alert', command=self.next_alert)
        for button in (self.previous, self.play, self.following, self.alert):
            button.pack(side='left', padx=(0, 4))
        self.speed_combo = ttk.Combobox(row, textvariable=self.speed, values=('0.5x', '1x', '2x', '4x'),
                                       state='readonly', width=5)
        self.speed_combo.pack(side='left', padx=5)
        ttk.Label(self, textvariable=self.caption, wraplength=660).pack(fill='x', pady=(4, 0))
        self.scale = ttk.Scale(self, from_=0, to=1, orient='horizontal', command=self._scrub)
        self.scale.pack(fill='x', pady=(4, 0))
        self.bar = tk.Canvas(self, height=17, bg='#e4eaf0', highlightthickness=0)
        self.bar.pack(fill='x')
        self.bar.bind('<Configure>', lambda _: self._draw())
        self.bar.bind('<Button-1>', self._bar_click)
        self.bind('<Destroy>', self._destroyed)
        self.clear()

    def clear(self, message='Run analysis to build time windows.'):
        self.pause()
        self.items = []
        self.key = self.position = None
        self.caption.set(message)
        self._enabled(False)
        self._draw()

    def _enabled(self, enabled):
        for widget in (self.previous, self.play, self.following, self.alert, self.scale):
            widget.configure(state='normal' if enabled else 'disabled')
        self.speed_combo.configure(state='readonly' if enabled else 'disabled')

    def show(self, key, items, current=None, message='No complete windows.'):
        if not items:
            self.clear(message)
            return
        if key != self.key:
            self.pause()
        self.key, self.items = key, items
        self.position = next((i for i, item in enumerate(items) if item[0] == current), None)
        if self.position is None:
            self.pause()
        self.setting_scale = True
        try:
            self.scale.configure(to=max(1, len(items)-1))
            self.scale.set(self.position or 0)
        finally:
            self.setting_scale = False
        self._enabled(True)
        if self.position is None:
            self.caption.set(f'{len(items)} windows ready. Drag or Play to inspect a segment.')
        else:
            _, start, end, _ = items[self.position]
            self.caption.set(f'Window {self.position+1}/{len(items)}: {start:.3f}-{end:.3f} s')
        self._draw()

    def _draw(self):
        self.bar.delete('all')
        if not self.items:
            return
        width = max(1, self.bar.winfo_width())
        for i, item in enumerate(self.items):
            self.bar.create_rectangle(i*width/len(self.items), 0, (i+1)*width/len(self.items), 17,
                                      fill=COLORS[item[3]], outline='')
        if self.position is not None:
            left, right = self.position*width/len(self.items), (self.position+1)*width/len(self.items)
            self.bar.create_rectangle(left+1, 1, right-1, 16, outline='#172b3a', width=2)

    def _emit(self, index):
        if self.items:
            index = max(0, min(len(self.items)-1, int(index)))
            self.position = index
            self.on_select(self.items[index][0])

    def _scrub(self, value):
        if self.setting_scale or not self.items:
            return
        self.pause()
        index = max(0, min(len(self.items)-1, round(float(value))))
        if index != self.position:
            self._emit(index)

    def _bar_click(self, event):
        if self.items:
            self.pause()
            self._emit(int(event.x/max(1, self.bar.winfo_width())*len(self.items)))

    def step(self, direction):
        self.pause()
        self._emit(0 if self.position is None else self.position+direction)

    def next_alert(self):
        self.pause()
        start = -1 if self.position is None else self.position
        for i in range(start+1, len(self.items)):
            if self.items[i][3] != 'green':
                self._emit(i)
                return
        self.caption.set('No later alerts for this metric.')

    def toggle(self):
        if self.playing:
            self.pause()
            return
        if not self.items:
            return
        # Also notify the owner when resuming a middle window: linked views
        # must transfer playback ownership before the first timer fires.
        self._emit(0 if self.position is None or self.position == len(self.items)-1 else self.position)
        self.playing = True
        self.play.configure(text='Pause')
        self._schedule()

    def _schedule(self):
        if not self.playing or self.position is None or self.position >= len(self.items)-1:
            self.pause()
            return
        seconds = self.items[self.position+1][1] - self.items[self.position][1]
        delay = max(40, round(seconds*1000/float(self.speed.get().rstrip('x'))))
        self.timer = self.after(delay, self._tick)

    def _tick(self):
        self.timer = None
        if self.playing and self.position is not None:
            self._emit(self.position+1)
            self._schedule()

    def pause(self):
        self.playing = False
        if self.timer is not None:
            self.after_cancel(self.timer)
            self.timer = None
        self.play.configure(text='Play')

    def _destroyed(self, event):
        if event.widget == self:
            if self.timer is not None:
                self.after_cancel(self.timer)
                self.timer = None
            self.playing = False
