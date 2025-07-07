import time
import tkinter as tk
from tkinter import ttk, messagebox

from .drill import ComplementDrill, TenMinusDrill

_FONT_PROB = ("Yu Gothic", 110, "bold")
_FONT_MSG = ("Yu Gothic", 60, "bold")
_FONT_DLG = ("Consolas", 48)
_CARD_BG = "#222222"
_CARD_FG = "#FFFFFF"
_NUM_Q = 20
_THRESH = 0.80
_KPI = 0.80


class App(tk.Tk):
    W, H = 900, 580

    def __init__(self) -> None:
        super().__init__()
        self.title("Reflex v2.6")
        self.geometry(f"{self.W}x{self.H}")
        self.resizable(False, False)

        self.mode = tk.StringVar(value="A")
        self.drill = ComplementDrill()
        self.records: list[tuple[str, float]] = []
        self.session = False
        self.build()
        self.bind_all_events()

    def build(self) -> None:
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
            lf, text="A: 補数", variable=self.mode, value="A", command=self.set_mode
        ).pack(anchor=tk.W)
        tk.Radiobutton(
            lf, text="B: 10−□", variable=self.mode, value="B", command=self.set_mode
        ).pack(anchor=tk.W)

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
        tk.Label(side, text="Enter▶回答＆開始  Esc▶Reset", font=("Yu Gothic", 8)).pack()

    def bind_all_events(self) -> None:
        self.bind("<Return>", self.enter)
        self.bind("<Escape>", lambda _event: self.reset())

    def set_mode(self) -> None:
        if self.session:
            messagebox.showinfo("モード変更", "終了後に変更してください")
            self.mode.set("A" if isinstance(self.drill, ComplementDrill) else "B")
            return

        self.drill = ComplementDrill() if self.mode.get() == "A" else TenMinusDrill()
        self.lbl.config(text="Enter\nで開始", font=_FONT_MSG)

    def start(self) -> None:
        self.session = True
        self.records = []
        self.clear_tree()
        self.update_stat()
        self.reset_btn.config(state=tk.NORMAL)
        self.drill.regen()
        self.next()

    def next(self) -> None:
        v = self.drill.next()
        self.current_disp = self.drill.disp(v)
        self.lbl.config(text=self.current_disp, font=_FONT_PROB)
        self.t0 = time.perf_counter()

    def finish(self) -> None:
        avg = sum(rt for _, rt in self.records) / len(self.records)
        self.session = False
        self.lbl.config(text=f"{_NUM_Q}問終了！\n平均 {avg:.2f} s", font=_FONT_MSG)
        self.stat.set(f"平均 RT: {avg:.2f} s")
        self.stat_lbl.config(bg="#66CC66" if avg <= _KPI else "#CCCCCC")
        slow = [(d, rt) for d, rt in self.records if rt > _THRESH]
        self.show_slow_dialog(slow)

    def show_slow_dialog(self, slow: list[tuple[str, float]]) -> None:
        win = tk.Toplevel(self)
        win.title("0.8 秒より遅かった問題")
        win.configure(bg=_CARD_BG)
        if slow:
            for disp, rt in slow:
                tk.Label(
                    win,
                    text=f"{disp}   {rt:.2f}s",
                    font=_FONT_DLG,
                    fg=_CARD_FG,
                    bg=_CARD_BG,
                    padx=10,
                ).pack(anchor=tk.W)
        else:
            tk.Label(
                win,
                text="すべて 0.8 秒以内でした！",
                font=_FONT_DLG,
                fg=_CARD_FG,
                bg=_CARD_BG,
            ).pack(padx=20, pady=20)
        tk.Button(win, text="OK", command=win.destroy).pack(pady=10)
        win.transient(self)
        win.grab_set()
        self.wait_window(win)

    def reset(self) -> None:
        self.session = False
        self.records = []
        self.clear_tree()
        self.lbl.config(text="Enter\nで開始", font=_FONT_MSG)
        self.stat.set("平均 RT: -- s")
        self.stat_lbl.config(bg="#CCCCCC")
        self.reset_btn.config(state=tk.DISABLED)

    def clear_tree(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def enter(self, _event) -> None:
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

    def update_stat(self) -> None:
        if not self.records:
            self.stat.set("平均 RT: -- s")
            self.stat_lbl.config(bg="#CCCCCC")
            return
        avg = sum(rt for _, rt in self.records) / len(self.records)
        self.stat.set(f"平均 RT: {avg:.2f} s")
        self.stat_lbl.config(bg="#66CC66" if avg <= _KPI else "#CCCCCC")


if __name__ == "__main__":
    App().mainloop()
