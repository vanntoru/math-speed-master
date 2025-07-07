import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import drill


def test_disp():
    assert drill.ComplementDrill().disp(3) == "3"
