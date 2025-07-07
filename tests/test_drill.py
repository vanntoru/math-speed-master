import random
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.drill import BaseDrill


def test_base_drill_regen_counts():
    random.seed(0)
    d = BaseDrill()
    q = d.q
    assert len(q) == 20
    for n in range(1, 10):
        assert q.count(n) >= 2


def test_next_cycles_and_regenerates():
    random.seed(0)
    d = BaseDrill()
    q_initial = d.q.copy()

    results = [d.next() for _ in range(25)]

    # first 20 values come from the initial queue in reverse order
    assert results[:20] == q_initial[::-1]
    # after consuming 25 items, 5 should remain in the new queue
    assert len(d.q) == 15
