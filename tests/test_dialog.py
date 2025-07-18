import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import app.gui as gui


class DummyWin:
    def __init__(self):
        self.destroy_called = False

    def destroy(self):
        self.destroy_called = True


def test_enter_closes_open_dialog():
    app = gui.App.__new__(gui.App)
    app.session = False
    app.slow_win = DummyWin()
    app.close_slow_dialog = gui.App.close_slow_dialog.__get__(app)
    app.start = lambda: setattr(app, "started", True)

    app.enter(None)

    assert app.slow_win is None
    assert "started" not in app.__dict__
