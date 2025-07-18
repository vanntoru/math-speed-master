# -*- coding: utf-8 -*-
"""
10 の補数 Reflex Trainer v2.6 – カスタム大字ダイアログ
=====================================================
* セッション終了時、0.8 s 超の問題を **特大フォント (48 pt)** で一覧表示するカスタムウィンドウに変更。
* 既存の機能・デザイン（110 pt 問題フォント／60 pt メッセージ）は維持。
"""

import tkinter as tk
from tkinter import ttk
import time
import sys
import os
import csv
import datetime

try:
    import pandas as pd
    from matplotlib import pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:  # pragma: no cover - optional deps may be missing
    pd = None
    plt = None
    FigureCanvasTkAgg = None

if __package__ is None:
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    from drill import (
        ComplementDrill,
        TenMinusDrill,
        Add2Digit1DigitDrill,
        Add2Digit2DigitDrill,
        RandomNumberDrill,
    )
else:
    from .drill import (
        ComplementDrill,
        TenMinusDrill,
        Add2Digit1DigitDrill,
        Add2Digit2DigitDrill,
        RandomNumberDrill,
    )

# ──────────────────────────────
# 設定値
# ──────────────────────────────
_FONT_PROB = ("Yu Gothic", 110, "bold")  # 問題表示
_FONT_MSG = ("Yu Gothic", 60, "bold")  # 開始・終了メッセージ
_FONT_DLG = ("Consolas", 48)  # 遅延リスト
_CARD_BG, _CARD_FG = "#222222", "#FFFFFF"
_NUM_Q = 20
_THRESH = {"A": 0.8, "B": 0.8, "C": 0.8, "D": 1.5, "E": 0.8}
_KPI = {"A": 0.8, "B": 0.8, "C": 0.8, "D": 1.5, "E": 0.8}
_MODE_E_INCLUDE_ZERO = False
REFLEX_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reflex_log.csv")


def log_session(csv_path, mode, avg, records):
    """Append a session summary row to the CSV log."""
    file_exists = os.path.exists(csv_path)
    slow_count = sum(1 for _d, rt in records if rt > _THRESH.get(mode, 0.8))
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "time", "mode", "avg_rt", "slow_count"])
        writer.writerow(
            [
                datetime.date.today(),
                datetime.datetime.now().strftime("%H:%M:%S"),
                mode,
                f"{avg:.2f}",
                slow_count,
            ]
        )


# ──────────────────────────────
# GUI アプリ
# ──────────────────────────────


class App(tk.Tk):
    W, H = 900, 580

    def __init__(self):
        super().__init__()
        self.title("Reflex v2.6")
        self.geometry(f"{self.W}x{self.H}")
        self.resizable(False, False)

        self.mode = tk.StringVar(value="A")
        self.drill = ComplementDrill()
        self.random_max = 99

        self.records = []
        self.session = False

        self.build()
        self.bind_all()

    # UI
    def build(self):
        self.card = tk.Frame(self, bg=_CARD_BG, width=640, height=580)
        self.card.pack(side=tk.LEFT, fill=tk.BOTH)

        self.lbl = tk.Label(
            self.card,
            text="Enter\nで開始",
            font=_FONT_MSG,
            bg=_CARD_BG,
            fg=_CARD_FG,
            justify="center",
        )
        self.lbl.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        side = tk.Frame(self, width=260)
        side.pack(side=tk.RIGHT, fill=tk.Y)

        lf = tk.LabelFrame(side, text="モード", padx=5, pady=5)
        lf.pack(pady=(10, 5))
        tk.Radiobutton(
            lf,
            text="A: 補数",
            variable=self.mode,
            value="A",
            command=self.set_mode,
        ).pack(anchor=tk.W)
        tk.Radiobutton(
            lf,
            text="B: 10−□",
            variable=self.mode,
            value="B",
            command=self.set_mode,
        ).pack(anchor=tk.W)
        tk.Radiobutton(
            lf,
            text="C: 2桁＋1桁",
            variable=self.mode,
            value="C",
            command=self.set_mode,
        ).pack(anchor=tk.W)
        tk.Radiobutton(
            lf,
            text="D: 2桁＋2桁",
            variable=self.mode,
            value="D",
            command=self.set_mode,
        ).pack(anchor=tk.W)
        tk.Radiobutton(
            lf,
            text="E: 任意数字",
            variable=self.mode,
            value="E",
            command=self.set_mode,
        ).pack(anchor=tk.W)

        self.e_var = tk.StringVar(value="99")
        self.e_frame = tk.Frame(side)
        tk.Entry(self.e_frame, width=6, textvariable=self.e_var).pack(side=tk.LEFT)
        tk.Button(self.e_frame, text="設定", command=self.apply_e_setting).pack(side=tk.LEFT)
        self.e_frame.pack_forget()

        tk.Label(side, text="履歴", font=("Yu Gothic", 12, "bold")).pack()
        self.tree = ttk.Treeview(side, columns=("#", "RT"), show="headings", height=9)
        self.tree.heading("#", text="#")
        self.tree.column("#", width=40, anchor=tk.CENTER)
        self.tree.heading("RT", text="RT(s)")
        self.tree.column("RT", width=80, anchor=tk.CENTER)
        self.tree.pack(pady=5)

        self.stat = tk.StringVar(value="平均 RT: -- s")
        self.stat_lbl = tk.Label(
            side,
            textvariable=self.stat,
            font=("Yu Gothic", 12, "bold"),
            bg="#CCCCCC",
        )
        self.stat_lbl.pack(fill=tk.X, padx=5, pady=5)

        self.reset_btn = tk.Button(
            side,
            text="Reset (Esc)",
            width=18,
            command=self.reset,
            state=tk.DISABLED,
        )
        self.reset_btn.pack(pady=8)
        tk.Button(
            side,
            text="履歴グラフ",
            width=18,
            command=self.show_history,
        ).pack(pady=(0, 8))
        tk.Label(side, text="Enter▶回答＆開始  Esc▶Reset", font=("Yu Gothic", 8)).pack()

    def apply_e_setting(self):
        try:
            val = int(self.e_var.get())
        except ValueError:
            tk.messagebox.showwarning("入力エラー", "数値を入力してください")
            return
        if val + 1 < _NUM_Q:
            tk.messagebox.showwarning("入力エラー", "値が小さすぎます")
            return
        self.random_max = val
        if self.mode.get() == "E":
            self.drill = RandomNumberDrill(self.random_max, include_zero=_MODE_E_INCLUDE_ZERO)
            self.lbl.config(text="Enter\nで開始", font=_FONT_MSG)

    # bindings
    def bind_all(self):
        self.bind("<Return>", self.enter)
        self.bind("<Escape>", lambda e: self.reset())

    # mode
    def set_mode(self):
        if self.session:
            tk.messagebox.showinfo("モード変更", "終了後に変更してください")
            if isinstance(self.drill, ComplementDrill):
                self.mode.set("A")
            elif isinstance(self.drill, TenMinusDrill):
                self.mode.set("B")
            elif isinstance(self.drill, Add2Digit1DigitDrill):
                self.mode.set("C")
            elif isinstance(self.drill, Add2Digit2DigitDrill):
                self.mode.set("D")
            else:
                self.mode.set("E")
            return

        if self.mode.get() == "A":
            self.drill = ComplementDrill()
            self.e_frame.pack_forget()
        elif self.mode.get() == "B":
            self.drill = TenMinusDrill()
            self.e_frame.pack_forget()
        elif self.mode.get() == "C":
            self.drill = Add2Digit1DigitDrill()
            self.e_frame.pack_forget()
        elif self.mode.get() == "D":
            self.drill = Add2Digit2DigitDrill()
            self.e_frame.pack_forget()
        else:
            self.e_frame.pack(pady=5)
            self.drill = RandomNumberDrill(self.random_max, include_zero=_MODE_E_INCLUDE_ZERO)

        self.lbl.config(text="Enter\nで開始", font=_FONT_MSG)

    # flow
    def start(self):
        self.session = True
        self.records = []
        self.clear_tree()
        self.update_stat()
        self.reset_btn.config(state=tk.NORMAL)
        self.drill.regen()
        self.next()

    def next(self):
        v = self.drill.next()
        self.current_disp = self.drill.disp(v)
        self.lbl.config(text=self.current_disp, font=_FONT_PROB)
        self.t0 = time.perf_counter()

    def finish(self):
        avg = sum(rt for _, rt in self.records) / len(self.records)
        log_session(REFLEX_LOG, self.mode.get(), avg, self.records)
        self.session = False
        self.lbl.config(text=f"{_NUM_Q}問終了！\n平均 {avg:.2f} s", font=_FONT_MSG)
        self.stat.set(f"平均 RT: {avg:.2f} s")
        self.stat_lbl.config(
            bg="#66CC66" if avg <= _KPI[self.mode.get()] else "#CCCCCC"
        )
        slow = [
            (d, rt) for d, rt in self.records if rt > _THRESH[self.mode.get()]
        ]
        self.show_slow_dialog(slow)

    # custom dialog
    def show_slow_dialog(self, slow):
        win = tk.Toplevel(self)
        thr = _THRESH[self.mode.get()]
        win.title(f"{thr} 秒より遅かった問題")
        win.configure(bg=_CARD_BG)

        if slow:
            for d, rt in slow:
                tk.Label(
                    win,
                    text=f"{d}   {rt:.2f}s",
                    font=_FONT_DLG,
                    fg=_CARD_FG,
                    bg=_CARD_BG,
                    padx=10,
                ).pack(anchor=tk.W)
        else:
            tk.Label(
                win,
                text=f"すべて {thr} 秒以内でした！",
                font=_FONT_DLG,
                fg=_CARD_FG,
                bg=_CARD_BG,
            ).pack(padx=20, pady=20)

        tk.Button(win, text="OK", command=win.destroy).pack(pady=10)
        win.transient(self)
        win.grab_set()
        self.wait_window(win)

    def show_history(self):
        if pd is None or plt is None:
            tk.messagebox.showerror(
                "Missing Dependency",
                "pandas と matplotlib をインストールしてください",
            )
            return
        HistoryWindow(self)

    def reset(self):
        self.session = False
        self.records = []
        self.clear_tree()
        self.lbl.config(text="Enter\nで開始", font=_FONT_MSG)
        self.stat.set("平均 RT: -- s")
        self.stat_lbl.config(bg="#CCCCCC")
        self.reset_btn.config(state=tk.DISABLED)

    def clear_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

    # key
    def enter(self, _):
        if not self.session:
            self.start()
            return

        rt = time.perf_counter() - self.t0
        self.records.append((self.current_disp, rt))
        self.tree.insert("", 0, values=(len(self.records), f"{rt:.2f}"))

        if len(self.tree.get_children()) > 20:
            self.tree.delete(self.tree.get_children()[-1])

        self.update_stat()

        if len(self.records) >= _NUM_Q:
            self.finish()
        else:
            self.next()

    def update_stat(self):
        if not self.records:
            self.stat.set("平均 RT: -- s")
            self.stat_lbl.config(bg="#CCCCCC")
            return

        avg = sum(rt for _, rt in self.records) / len(self.records)
        self.stat.set(f"平均 RT: {avg:.2f} s")
        self.stat_lbl.config(
            bg="#66CC66" if avg <= _KPI[self.mode.get()] else "#CCCCCC"
        )


class HistoryWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("履歴グラフ")
        self.df = self.load_data()

        self.filter_var = tk.StringVar(value="all")
        opt_frame = tk.Frame(self)
        opt_frame.pack(pady=5)
        for text, val in [
            ("全モード表示", "all"),
            ("モードAのみ", "A"),
            ("モードBのみ", "B"),
            ("モードCのみ", "C"),
            ("モードDのみ", "D"),
            ("モードEのみ", "E"),
        ]:
            tk.Radiobutton(
                opt_frame,
                text=text,
                variable=self.filter_var,
                value=val,
                command=self.update_view,
            ).pack(side=tk.LEFT)

        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        cols = ("date", "time", "mode", "avg_rt", "slow_count")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=80, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(
            self,
            text="選択セッションを削除",
            command=self.delete_selected,
        ).pack(pady=5)

        self.update_view()

    def load_data(self):
        if os.path.exists(REFLEX_LOG):
            df = pd.read_csv(REFLEX_LOG)
        else:
            df = pd.DataFrame(columns=["date", "time", "mode", "avg_rt", "slow_count"])
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["avg_rt"] = pd.to_numeric(df["avg_rt"], errors="coerce")
        return df

    def update_view(self):
        if self.filter_var.get() == "all":
            df = self.df
        else:
            df = self.df[self.df["mode"] == self.filter_var.get()]

        self.ax.clear()
        if not df.empty:
            self.ax.plot(df["date"], df["avg_rt"], marker="o")
        kpi = _KPI.get(self.filter_var.get(), _KPI["A"])
        self.ax.axhline(kpi, color="red", linestyle="--")
        self.ax.set_xlabel("date")
        self.ax.set_ylabel("avg_rt")
        self.fig.autofmt_xdate()
        self.canvas.draw()

        for i in self.tree.get_children():
            self.tree.delete(i)
        for _, row in df.iterrows():
            self.tree.insert(
                "",
                "end",
                values=(
                    row["date"].strftime("%Y-%m-%d"),
                    row["time"],
                    row["mode"],
                    row["avg_rt"],
                    row["slow_count"],
                ),
            )

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if not tk.messagebox.askyesno(
            "削除確認", f"{values[0]} {values[1]} のセッションを削除しますか?"
        ):
            return

        mask = (
            (self.df["date"].dt.strftime("%Y-%m-%d") == values[0])
            & (self.df["time"] == values[1])
            & (self.df["mode"] == values[2])
        )
        self.df = self.df[~mask]
        self.df.to_csv(REFLEX_LOG, index=False)
        self.update_view()


if __name__ == "__main__":
    App().mainloop()
