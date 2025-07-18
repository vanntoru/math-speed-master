# Math Speed

Math Speed is a small Tkinter application that drills students on the complements of ten.  The
program displays simple flash cards and records reaction times so that repeated practice becomes
visible progress.

## Installation

1. Ensure **Python 3.10** or newer is installed.
2. Install the required packages (`pandas` and `matplotlib`):
   ```bash
   pip install -r requirements.txt
   ```
   These libraries provide the CSV log handling and reaction time graphs.

## Quick Start

After installing the dependencies you can launch the GUI with:

```bash
python -m src.app.gui
```

This opens the training window and starts a session where you can practice ten-complement
calculations at speed.

### Modes

In addition to complement drills (modes A and B), **Mode C** serves two-digit plus
one-digit addition problems. Two-digit numbers never end with zero (10, 20, ... 90
are excluded) and roughly half of the problems include a carry so students can
practice bridging through the tens place.

**Mode D** extends this to two-digit plus two-digit addition. Numbers are
drawn from 10–99 and pairs where both numbers end in zero are skipped. The 20
problems always contain an even split of carry and non-carry cases, providing
practice with and without regrouping.
**Mode E** selects 20 unique integers from a user defined 0–N range. The upper
bound can be set in the side panel when choosing mode E.

### Session History & CSV Logging

After every session a summary line is written to `src/app/reflex_log.csv`
containing the date, time, selected mode, average reaction time and the
number of problems that exceeded the 0.8 s threshold.  Press the
**履歴グラフ** button to open a separate window that plots these values and
shows the underlying table.  Results can be filtered per mode and the
**選択セッションを削除** button permanently removes any highlighted rows from
the CSV.  Deletion cannot be undone, so archive the file manually or rename
it before launching the program if you wish to start with a fresh log.  The
save location can be customised by editing the `REFLEX_LOG` constant inside
`src/app/gui.py`.
