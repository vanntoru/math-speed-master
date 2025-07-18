import random
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.drill import (
    BaseDrill,
    Add2Digit1DigitDrill,
    Add2Digit2DigitDrill,
    RandomNumberDrill,
)


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

    # two-digit numbers should never end with zero
    assert all(a % 10 != 0 for a, _ in q)

    carry = sum(1 for a, b in q if a % 10 + b >= 10)
    assert carry == 10

    for x, y in zip(q, q[1:]):
        assert x != y


def test_add2digit1digitdrill_disp():
    d = Add2Digit1DigitDrill()
    assert d.disp((52, 7)) == "52+7"


def test_add2digit1digitdrill_seeded_properties():
    """Queue construction should be reproducible and balanced."""
    random.seed(123)
    d = Add2Digit1DigitDrill()
    q = d.q

    # The drill should always create exactly 20 problems
    assert len(q) == 20

    # Each one-digit addend should appear at least twice
    addends = [b for _, b in q]
    for n in range(1, 10):
        assert addends.count(n) >= 2

    # Tens digits for the two-digit number should also be evenly distributed
    tens = [a // 10 for a, _ in q]
    for n in range(1, 10):
        assert tens.count(n) >= 2

    # Roughly half of the problems should require a carry
    carries = sum(1 for a, b in q if a % 10 + b >= 10)
    assert carries == 10

    # Two-digit numbers should never end with zero
    assert all(a % 10 != 0 for a, _ in q)


def test_add2digit2digitdrill_queue_properties():
    random.seed(0)
    d = Add2Digit2DigitDrill()
    q = d.q

    assert len(q) == 20
    assert len(set(q)) == 20
    assert len({tuple(sorted(p)) for p in q}) == 20

    assert all(10 <= a <= 99 and 10 <= b <= 99 for a, b in q)
    assert all(not (a % 10 == 0 and b % 10 == 0) for a, b in q)

    carry = sum(1 for a, b in q if a % 10 + b % 10 >= 10)
    assert carry == 10
    assert sum(1 for a, b in q if a % 10 + b % 10 < 10) == 10


def test_add2digit2digitdrill_disp():
    d = Add2Digit2DigitDrill()
    assert d.disp((12, 34)) == "12+34"


def test_random_number_drill_unique_within_range():
    random.seed(0)
    d = RandomNumberDrill(30)
    q = d.q

    assert len(q) == 20
    assert len(set(q)) == 20
    assert all(0 <= n <= 30 for n in q)


def test_random_number_drill_excludes_zero_when_requested():
    random.seed(0)
    d = RandomNumberDrill(30, include_zero=False)
    q = d.q

    assert len(q) == 20
    assert len(set(q)) == 20
    assert all(1 <= n <= 30 for n in q)
