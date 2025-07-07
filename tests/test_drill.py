import random
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.drill import BaseDrill, Add2Digit1DigitDrill


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


def test_add2digit1digitdrill_queue():
    random.seed(0)
    d = Add2Digit1DigitDrill()
    q = d.q

    assert len(q) == 20

    addends = [b for _, b in q]
    for n in range(1, 10):
        assert addends.count(n) >= 2

    tens = [a // 10 for a, _ in q]
    for n in range(1, 10):
        assert tens.count(n) >= 2

    carry = sum(1 for a, b in q if a % 10 + b >= 10)
    assert carry == 10

    for x, y in zip(q, q[1:]):
        assert x != y


def test_add2digit1digitdrill_disp():
    d = Add2Digit1DigitDrill()
    assert d.disp((52, 7)) == "52+7"
