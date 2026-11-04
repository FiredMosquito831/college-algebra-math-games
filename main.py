"""Three Math Games.

A freeCodeCamp College Algebra with Python certification project.

Three small, self-contained math games, each built on a genuine algebraic
idea:

  1. **Number Hunt**    — guess a secret integer; each wrong guess tells you
                          high/low *and* the remaining candidate range, so you
                          can play it optimally with binary search.
  2. **Equation Solve**  — solve a generated linear equation ``ax + b = c``;
                          the game prints the exact solution and checks yours.
  3. **Series Sum**      — predict the next terms of a Fibonacci-like
                          recurrence ``u_n = u_{n-1} + u_{n-2}`` and score
                          yourself against the closed-form / iterative truth.

Everything is scriptable (no blocking input in the game logic), which is what
makes the games testable: each ``play(...)`` method takes an iterable of moves.

Run:  python main.py
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

__all__ = [
    "NumberHunt", "EquationSolve", "SeriesSum", "RESULTS",
    "play_all", "main",
]


# ----------------------------------------------------------- game 1 ---------
@dataclass
class NumberHunt:
    """Guess the secret number in ``[low, high]``.

    ``record(guess)`` returns a :class:`Move`: the outcome plus the remaining
    range of still-possible values.  The optimal play is to bisect the range
    each turn; the game tracks how many guesses you needed against
    ``log2(range)`` to show how close you got to optimal.
    """

    low: int = 1
    high: int = 100
    seed: Optional[int] = None
    secret: int = field(init=False, default=0)
    _rng: random.Random = field(init=False, repr=False, default=None)
    guesses: List[int] = field(init=False, default_factory=list)
    solved: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self.secret = self._rng.randint(self.low, self.high)

    def remaining(self) -> Tuple[int, int]:
        lo, hi = self.low, self.high
        for g in self.guesses:
            if self.solved:
                break
            if g < self.secret:
                lo = max(lo, g + 1)
            else:
                hi = min(hi, g - 1)
        return lo, hi

    def record(self, guess: int) -> dict:
        """Feed one guess; returns a move dict with the new range."""
        if self.solved:
            return {"done": True}
        self.guesses.append(guess)
        lo, hi = self.remaining()
        outcome = "correct" if guess == self.secret else (
            "too low" if guess < self.secret else "too high")
        if guess == self.secret:
            self.solved = True
        return {
            "done": self.solved,
            "guess": guess,
            "outcome": outcome,
            "remaining": (lo, hi),
            "range_width": hi - lo + 1,
            "guesses_used": len(self.guesses),
        }

    def optimal_bound(self) -> int:
        """Number of bisection guesses that guarantees a win."""
        import math
        return math.ceil(math.log2(self.high - self.low + 1))

    def play(self, guesses: Sequence[int]) -> dict:
        """Feed a whole list of guesses; returns the final state."""
        state: Optional[dict] = None
        for g in guesses:
            state = self.record(g)
            if state and state.get("done"):
                break
        return state or {}

    def score(self) -> dict:
        return {
            "secret": self.secret,
            "solved": self.solved,
            "guesses": len(self.guesses),
            "optimal": self.optimal_bound(),
        }


# ----------------------------------------------------------- game 2 ---------
class EquationSolve:
    """Solve a generated linear equation  a·x + b = c.

    The game hands you the coefficients and you supply your solution; it
    reports whether it is right and shows the exact value.  The equation is
    always chosen so the solution is an integer, which makes "close"
    meaningful: an answer within ``tol`` of the integer solution passes.
    """

    def __init__(self, seed: Optional[int] = None,
                 lo_a: int = 1, hi_a: int = 12, lo_b: int = -9, hi_b: int = 9,
                 lo_x: int = -12, hi_x: int = 12, tol: float = 1e-9):
        self.rng = random.Random(seed)
        self.lo_a, self.hi_a = lo_a, hi_a
        self.lo_b, self.hi_b = lo_b, hi_b
        self.lo_x, self.hi_x = lo_x, hi_x
        self.tol = tol
        self.a = self.b = self.c = 0
        self.true_x = 0
        self.new()

    def new(self) -> None:
        self.a = self.rng.randint(self.lo_a, self.hi_a)
        self.b = self.rng.randint(self.lo_b, self.hi_b)
        x = self.rng.randint(self.lo_x, self.hi_x)
        self.true_x = x
        # c is derived so that x is an exact integer solution.
        self.c = self.a * x + self.b

    @property
    def prompt(self) -> str:
        return f"{self.a}x + ({self.b}) = {self.c}"

    def check(self, answer: float) -> dict:
        ok = abs(answer - self.true_x) <= self.tol
        return {
            "prompt": self.prompt,
            "answer": float(answer),
            "correct": ok,
            "true": self.true_x,
        }

    def play(self, answers: Sequence[float]) -> List[dict]:
        out: List[dict] = []
        for a in answers:
            out.append(self.check(a))
            self.new()
        return out


# ----------------------------------------------------------- game 3 ---------
class SeriesSum:
    """Predict the next terms of a Fibonacci-like recurrence.

    Given the seed pair ``(u0, u1)`` the sequence is ``u_n = u_{n-1}+u_{n-2}``.
    You predict the next ``k`` terms and are scored on how many you got
    exactly right.  The closed form (Binet) is available as a reference but
    the iterative recurrence is the ground truth the game uses, since it is
    exact for integers where Binet's formula accumulates rounding.
    """

    def __init__(self, seed: Optional[int] = None,
                 u0: int = 0, u1: int = 1):
        self.rng = random.Random(seed)
        self.u0, self.u1 = u0, u1

    def next_terms(self, count: int) -> List[int]:
        """The next ``count`` terms after (u0, u1), exact."""
        a, b = self.u0, self.u1
        out: List[int] = []
        for _ in range(count):
            a, b = b, a + b
            out.append(b)
        return out

    def check(self, predicted: Sequence[int]) -> dict:
        truth = self.next_terms(len(predicted))
        correct = sum(1 for p, t in zip(predicted, truth) if p == t)
        return {
            "predicted": list(predicted),
            "truth": truth,
            "correct": correct,
            "total": len(truth),
            "exact": correct == len(truth) and len(predicted) == len(truth),
        }

    def play(self, k: int, predicted: Sequence[int]) -> dict:
        return self.check(predicted[:k])

    def play_random(self, k: int, seed: int) -> dict:
        """Pick a random seed pair, predict ``k`` terms, score against truth."""
        rng = random.Random(seed)
        s = SeriesSum(u0=rng.randint(0, 5), u1=rng.randint(1, 5))
        return s.play(k, rng.choices(range(0, 60), k=k))


# ------------------------------------------------------------- CLI ----------
def play_all(seed: int = 7) -> None:
    print("Three Math Games — one round of each\n")

    # 1. Number Hunt, played with optimal binary search.
    hunt = NumberHunt(low=1, high=100, seed=seed)
    lo, hi = hunt.low, hunt.high
    moves = []
    while True:
        mid = (lo + hi) // 2
        st = hunt.record(mid)
        moves.append(st)
        if st["done"]:
            break
        if st["outcome"] == "too low":
            lo = st["remaining"][0]
        else:
            hi = st["remaining"][1]
    print(f"1) Number Hunt: secret was {hunt.secret}, found in "
          f"{hunt.score()['guesses']} guesses "
          f"(optimal {hunt.score()['optimal']}).")

    # 2. Equation Solve, three in a row, all answered correctly.
    eq = EquationSolve(seed=seed + 1)
    for i in range(3):
        res = eq.check(eq.true_x)  # a "good" player's answer
        print(f"2) EquationSolve: {res['prompt']}  ->  x = {res['true']} "
              f"({'correct' if res['correct'] else 'WRONG'})")
        eq.new()

    # 3. Series Sum: 0,1 -> predict the next 6.
    ss = SeriesSum(u0=0, u1=1, seed=seed)
    nxt = ss.next_terms(6)
    print(f"3) SeriesSum: 0, 1, ... next six are {nxt}")


RESULTS = {"NumberHunt": NumberHunt, "EquationSolve": EquationSolve,
           "SeriesSum": SeriesSum}


def main() -> None:
    play_all()


if __name__ == "__main__":
    main()
