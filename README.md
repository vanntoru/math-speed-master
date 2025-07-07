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
