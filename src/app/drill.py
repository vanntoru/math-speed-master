import random

_VALUES = list(range(1, 10))


class BaseDrill:
    def __init__(self):
        self.regen()

    def regen(self):
        q = _VALUES * 2 + random.sample(_VALUES, 2)
        random.shuffle(q)
        for i in range(len(q) - 1):
            if q[i] == q[i + 1]:
                swap = (i + 2) % len(q)
                q[i + 1], q[swap] = q[swap], q[i + 1]
        self.q = q

    def next(self):
        if not self.q:
            self.regen()
        return self.q.pop()

    def disp(self, v): ...

    def spk(self, v): ...


class ComplementDrill(BaseDrill):
    def disp(self, v):
        return str(v)

    def spk(self, v):
        pass


class TenMinusDrill(BaseDrill):
    def disp(self, v):
        return f"10−{v}"

    def spk(self, v):
        pass


class Add2Digit1DigitDrill(BaseDrill):
    """Two-digit plus one-digit addition drill."""

    def regen(self):
        addends = _VALUES * 2 + random.sample(_VALUES, 2)
        tens = _VALUES * 2 + random.sample(_VALUES, 2)
        random.shuffle(addends)
        random.shuffle(tens)

        carry_indices = set(random.sample(range(20), 10))

        # ensure any addend 9 problems become carry problems so that
        # the two-digit number never ends with 0
        for i, a in enumerate(addends):
            if a == 9 and i not in carry_indices:
                for j in list(carry_indices):
                    if addends[j] != 9:
                        carry_indices.remove(j)
                        carry_indices.add(i)
                        break

        q = []
        for i in range(20):
            a = addends[i]
            t = tens[i]
            if i in carry_indices:
                ones = random.randint(10 - a, 9)
            else:
                ones = random.randint(1, 9 - a)
            q.append((t * 10 + ones, a))

        random.shuffle(q)
        for i in range(len(q) - 1):
            if q[i] == q[i + 1]:
                swap = (i + 2) % len(q)
                q[i + 1], q[swap] = q[swap], q[i + 1]
        self.q = q

    def disp(self, v):
        left, right = v
        return f"{left}+{right}"

    def spk(self, v):
        pass
