# -*- coding: utf-8 -*-
"""
10 の補数 Reflex Trainer v2.6 – カスタム大字ダイアログ
=====================================================
* セッション終了時、0.8 s 超の問題を **特大フォント (48 pt)** で一覧表示するカスタムウィンドウに変更。
* 既存の機能・デザイン（110 pt 問題フォント／60 pt メッセージ）は維持。
"""

import tkinter as tk
from tkinter import ttk
import random, time, threading, pyttsx3

# ──────────────────────────────
# 設定値
# ──────────────────────────────
_TTS_RATE = 220
_FONT_PROB = ("Yu Gothic", 110, "bold")  # 問題表示
_FONT_MSG  = ("Yu Gothic", 60, "bold")   # 開始・終了メッセージ
_FONT_DLG  = ("Consolas", 48)             # 遅延リスト
_CARD_BG, _CARD_FG = "#222222", "#FFFFFF"
_NUM_Q, _THRESH, _KPI = 20, 0.80, 0.80
_VALUES = list(range(1, 10))

# ──────────────────────────────
# TTS
# ──────────────────────────────

def _init_tts():
    e = pyttsx3.init()
    for v in e.getProperty("voices"):
        if any(n in v.name for n in ("Japanese", "Haruka", "Ayumi")):
            e.setProperty("voice", v.id); break
    e.setProperty("rate", _TTS_RATE)
    return e

_tts = _init_tts()

def speak_async(t):
    threading.Thread(target=lambda: (_tts.say(t), _tts.runAndWait()), daemon=True).start()

# ──────────────────────────────
# Drill
# ──────────────────────────────

class BaseDrill:
    def __init__(self): self.regen()
    def regen(self):
        q = _VALUES * 2 + random.sample(_VALUES, 2)
        random.shuffle(q)
        for i in range(len(q) - 1):
            if q[i] == q[i + 1]: swap = (i + 2) % len(q); q[i + 1], q[swap] = q[swap], q[i + 1]
        self.q = q
    def next(self):
        if not self.q: self.regen()
        return self.q.pop()
    def disp(self, v): ...
    def spk(self, v): ...

class ComplementDrill(BaseDrill):
    def disp(self, v): return str(v)
    def spk(self, v): speak_async(f"{v} の 10 の補数は？")

class TenMinusDrill(BaseDrill):
    def disp(self, v): return f"10−{v}"
    def spk(self, v): speak_async(f"10 ひく {v} は？")

# ──────────────────────────────
# GUI アプリ
# ──────────────────────────────

class App(tk.Tk):
    W, H = 900, 580
    def __init__(self):
        super().__init__(); self.title("Reflex v2.6"); self.geometry(f"{self.W}x{self.H}"); self.resizable(False, False)
        self.mode = tk.StringVar(value="A"); self.drill = ComplementDrill()
        self.records, self.session = [], False; self.build(); self.bind_all()
    # UI
    def build(self):
        self.card = tk.Frame(self, bg=_CARD_BG, width=640, height=580); self.card.pack(side=tk.LEFT, fill=tk.BOTH)
        self.lbl = tk.Label(self.card, text="Enter\nで開始", font=_FONT_MSG, bg=_CARD_BG, fg=_CARD_FG, justify="center")
        self.lbl.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        side = tk.Frame(self, width=260); side.pack(side=tk.RIGHT, fill=tk.Y)
        lf = tk.LabelFrame(side, text="モード", padx=5, pady=5); lf.pack(pady=(10, 5))
        tk.Radiobutton(lf, text="A: 補数", variable=self.mode, value="A", command=self.set_mode).pack(anchor=tk.W)
        tk.Radiobutton(lf, text="B: 10−□", variable=self.mode, value="B", command=self.set_mode).pack(anchor=tk.W)

        tk.Label(side, text="履歴", font=("Yu Gothic", 12, "bold")).pack()
        self.tree = ttk.Treeview(side, columns=("#", "RT"), show="headings", height=9)
        self.tree.heading("#", text="#"); self.tree.column("#", width=40, anchor=tk.CENTER)
        self.tree.heading("RT", text="RT(s)"); self.tree.column("RT", width=80, anchor=tk.CENTER)
        self.tree.pack(pady=5)

        self.stat = tk.StringVar(value="平均 RT: -- s")
        self.stat_lbl = tk.Label(side, textvariable=self.stat, font=("Yu Gothic", 12, "bold"), bg="#CCCCCC")
        self.stat_lbl.pack(fill=tk.X, padx=5, pady=5)

        self.reset_btn = tk.Button(side, text="Reset (Esc)", width=18, command=self.reset, state=tk.DISABLED)
        self.reset_btn.pack(pady=8)
        tk.Label(side, text="Enter▶回答＆開始  Esc▶Reset", font=("Yu Gothic", 8)).pack()
    # bindings
    def bind_all(self): self.bind("<Return>", self.enter); self.bind("<Escape>", lambda e: self.reset())
    # mode
    def set_mode(self):
        if self.session:
            tk.messagebox.showinfo("モード変更", "終了後に変更してください"); self.mode.set("A" if isinstance(self.drill, ComplementDrill) else "B"); return
        self.drill = ComplementDrill() if self.mode.get() == "A" else TenMinusDrill(); self.lbl.config(text="Enter\nで開始", font=_FONT_MSG)
    # flow
    def start(self):
        self.session, self.records = True, []; self.clear_tree(); self.update_stat(); self.reset_btn.config(state=tk.NORMAL); self.drill.regen(); self.next()
    def next(self):
        v = self.drill.next(); self.current_disp = self.drill.disp(v); self.lbl.config(text=self.current_disp, font=_FONT_PROB); self.drill.spk(v); self.t0 = time.perf_counter()
    def finish(self):
        avg = sum(rt for _, rt in self.records) / len(self.records)
        self.session = False; self.lbl.config(text=f"{_NUM_Q}問終了！\n平均 {avg:.2f} s", font=_FONT_MSG)
        self.stat.set(f"平均 RT: {avg:.2f} s"); self.stat_lbl.config(bg="#66CC66" if avg <= _KPI else "#CCCCCC")
        slow = [(d, rt) for d, rt in self.records if rt > _THRESH]
        self.show_slow_dialog(slow)
    # custom dialog
    def show_slow_dialog(self, slow):
        win = tk.Toplevel(self); win.title("0.8 秒より遅かった問題"); win.configure(bg=_CARD_BG)
        if slow:
            for d, rt in slow:
                tk.Label(win, text=f"{d}   {rt:.2f}s", font=_FONT_DLG, fg=_CARD_FG, bg=_CARD_BG, padx=10).pack(anchor=tk.W)
        else:
            tk.Label(win, text="すべて 0.8 秒以内でした！", font=_FONT_DLG, fg=_CARD_FG, bg=_CARD_BG).pack(padx=20, pady=20)
        tk.Button(win, text="OK", command=win.destroy).pack(pady=10)
        win.transient(self); win.grab_set(); self.wait_window(win)
    def reset(self):
        self.session, self.records = False, []; self.clear_tree(); self.lbl.config(text="Enter\nで開始", font=_FONT_MSG); self.stat.set("平均 RT: -- s"); self.stat_lbl.config(bg="#CCCCCC"); self.reset_btn.config(state=tk.DISABLED)
    def clear_tree(self):
        for i in self.tree.get_children(): self.tree.delete(i)
    # key
    def enter(self, _):
        if not self.session: self.start(); return
        rt = time.perf_counter() - self.t0; self.records.append((self.current_disp, rt)); self.tree.insert("", 0, values=(len(self.records), f"{rt:.2f}"));
        if len(self.tree.get_children()) > 20: self.tree.delete(self.tree.get_children()[-1])
        self.update_stat();
        if len(self.records) >= _NUM_Q: self.finish()
        else: self.next()
    def update_stat(self):
        if not self.records: self.stat.set("平均 RT: -- s"); self.stat_lbl.config(bg="#CCCCCC"); return
        avg = sum(rt for _, rt in self.records) / len(self.records); self.stat.set(f"平均 RT: {avg:.2f} s"); self.stat_lbl.config(bg="#66CC66" if avg <= _KPI else "#CCCCCC")

if __name__ == "__main__": App().mainloop()
