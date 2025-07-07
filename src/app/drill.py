import random

_VALUES = list(range(1, 10))


class BaseDrill:
    def __init__(self) -> None:
        self.regen()

    def regen(self) -> None:
        q = _VALUES * 2 + random.sample(_VALUES, 2)
        random.shuffle(q)
        for i in range(len(q) - 1):
            if q[i] == q[i + 1]:
                swap = (i + 2) % len(q)
                q[i + 1], q[swap] = q[swap], q[i + 1]
        self.q = q

    def next(self) -> int:
        if not self.q:
            self.regen()
        return self.q.pop()

    def disp(self, v: int) -> str:
        raise NotImplementedError


class ComplementDrill(BaseDrill):
    def disp(self, v: int) -> str:
        return str(v)


class TenMinusDrill(BaseDrill):
    def disp(self, v: int) -> str:
        return f"10−{v}"
