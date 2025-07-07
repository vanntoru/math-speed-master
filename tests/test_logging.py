import os
import csv
import datetime

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import app.gui as gui


class DummyWidget:
    def __init__(self):
        self.config_called = []

    def config(self, **kwargs):
        self.config_called.append(kwargs)


class DummyVar:
    def __init__(self):
        self.value = None

    def set(self, value):
        self.value = value


class DummyMode:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


def create_dummy_app(mode_value, records):
    app = gui.App.__new__(gui.App)
    app.records = records
    app.mode = DummyMode(mode_value)
    app.lbl = DummyWidget()
    app.stat = DummyVar()
    app.stat_lbl = DummyWidget()
    app.show_slow_dialog = lambda slow: None
    return app


def read_csv_rows(path):
    with open(path, newline="") as f:
        return list(csv.reader(f))


def test_finish_creates_csv_with_header(tmp_path, monkeypatch):
    csv_path = tmp_path / "log.csv"
    monkeypatch.setattr(gui, "REFLEX_LOG", str(csv_path))

    app = create_dummy_app("A", [("1", 1.0), ("2", 0.5)])
    app.finish()

    rows = read_csv_rows(csv_path)
    assert rows[0] == ["date", "time", "mode", "avg_rt", "slow_count"]
    assert rows[1][2] == "A"
    assert rows[1][3] == "0.75"
    assert rows[1][4] == "1"
    assert rows[1][0] == str(datetime.date.today())
    assert len(rows[1][1].split(":")) == 3


def test_finish_appends_without_header(tmp_path, monkeypatch):
    csv_path = tmp_path / "log.csv"
    with open(csv_path, "w", newline="") as f:
        csv.writer(f).writerow(["date", "time", "mode", "avg_rt", "slow_count"])

    monkeypatch.setattr(gui, "REFLEX_LOG", str(csv_path))

    app = create_dummy_app("B", [("1", 0.1), ("2", 0.2)])
    app.finish()

    rows = read_csv_rows(csv_path)
    assert rows[0] == ["date", "time", "mode", "avg_rt", "slow_count"]
    assert len(rows) == 2
    assert rows[1][2] == "B"
    assert rows[1][3] == "0.15"
