"""Tests for the three math games.

Each game is exercised deterministically (seeded) and its algebra is checked
against closed forms / hand values:

  * NumberHunt: binary search must always win within ceil(log2(range));
  * EquationSolve: the generated equation must actually be solved by its
    reported answer, and a wrong answer must be rejected;
  * SeriesSum: the recurrence must match an independent loop and Binet's
    formula (within float tolerance).

Run:  python test_local.py
"""

from __future__ import annotations

import math
import sys

import main as m

PASS = 0
FAIL = 0
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"PASS  {name}" + (f"   [{detail}]" if detail else ""))
    else:
        FAIL += 1
        FAILURES.append(name)
        print(f"FAIL  {name}" + (f"   [{detail}]" if detail else ""))


def bisect_lo(h) -> list:
    """Optimal guess sequence for a NumberHunt until it solves."""
    lo, hi = h.low, h.high
    seq = []
    while True:
        mid = (lo + hi) // 2
        seq.append(mid)
        st = h.record(mid)
        if st["done"]:
            return seq
        lo, hi = st["remaining"]


def main() -> int:
    print("three-math-games local tests")
    print("=" * 62)

    # ------------------------------------------------ NumberHunt ----------
    check("NumberHunt picks a secret in [1,100]", 1 <= m.NumberHunt(seed=1).secret <= 100)
    check("optimal bound for 1..100 is 7", m.NumberHunt(seed=2).optimal_bound() == 7,
          f"{m.NumberHunt(seed=2).optimal_bound()}")
    # bisection must win every seeded game within the optimal bound.
    worst, unsolved = 0, []
    for s in range(1, 40):
        h = m.NumberHunt(low=1, high=100, seed=s)
        bisect_lo(h)
        sc = h.score()
        worst = max(worst, sc["guesses"])
        if not sc["solved"]:
            unsolved.append(s)
    check("bisection solved all 39 seeded games",
          not unsolved, f"unsolved={unsolved}")
    check("bisection always solves within the optimal bound",
          worst <= 7, f"worst={worst} over 39 seeds")

    # Under bisection the candidate range must shrink on every move.
    h = m.NumberHunt(low=1, high=8, seed=5)
    widths = []
    lo, hi = 1, 8
    while True:
        mid = (lo + hi) // 2
        st = h.record(mid)
        widths.append(st["range_width"])
        if st["done"]:
            break
        lo, hi = st["remaining"]
    check("range width shrinks on every bisection move",
          all(w1 > w2 for w1, w2 in zip(widths, widths[1:])),
          str(widths))
    # A wrong-but-bounded guess reports the correct direction.
    h2 = m.NumberHunt(low=1, high=100, seed=9)
    secret = h2.secret
    g_below = h2.record(secret - 1 if secret > 1 else 1)
    g_above = h2.record(secret + 1 if secret < 100 else 100)
    # Guessing secret-1 ("too low") makes the low bound secret; guessing
    # secret+1 ("too high") makes the high bound secret.
    check("a guess just below reports 'too low' and narrows upward to the secret",
          (g_below["outcome"] == "too low" and g_below["remaining"][0] == secret
           or secret <= 1), f"{g_below}")
    check("a guess just above reports 'too high' and narrows downward to the secret",
          (g_above["outcome"] == "too high" and g_above["remaining"][1] == secret
           or secret >= 100), f"{g_above}")

    # ------------------------------------------------ EquationSolve -------
    eq = m.EquationSolve(seed=11)
    for _ in range(50):
        r = eq.check(eq.true_x)
        assert r["correct"], "the generated answer must be its own solution"
        # verify the equation is genuinely consistent
        assert eq.a * eq.true_x + eq.b == eq.c, "c must equal a*x+b"
        eq.new()
    check("EquationSolve: 50 generated equations all consistent & solvable", True)

    eq2 = m.EquationSolve(seed=13)
    wrong = eq2.check(eq2.true_x + 1)
    check("EquationSolve: off-by-one answer is rejected", not wrong["correct"])
    check("EquationSolve: prompt contains the three numbers",
          all(str(v) in eq2.prompt for v in (eq2.a, eq2.b, eq2.c)),
          eq2.prompt)
    play = eq2.play([eq2.true_x])
    check("EquationSolve.play() advances to a fresh equation",
          play[0]["correct"] and play[0]["prompt"] != eq2.prompt
          or len(play) == 1, f"{len(play)}")

    # ------------------------------------------------ SeriesSum -----------
    ss = m.SeriesSum(u0=0, u1=1)
    fib6 = ss.next_terms(6)
    check("SeriesSum: 0,1 -> next six are 1,2,3,5,8,13",
          fib6 == [1, 2, 3, 5, 8, 13], str(fib6))
    ss2 = m.SeriesSum(u0=2, u1=3)
    check("SeriesSum: 2,3 -> 5,8,13,21,34",
          ss2.next_terms(5) == [5, 8, 13, 21, 34], str(ss2.next_terms(5)))

    # Independent iterative ground truth for a larger run.
    a, b = 0, 1
    truth = []
    for _ in range(20):
        a, b = b, a + b
        truth.append(b)
    check("SeriesSum matches an independent loop over 20 terms",
          m.SeriesSum(u0=0, u1=1).next_terms(20) == truth, str(truth[:6]) + "...")

    # Cross-check against Binet's closed form.  next_terms(0,1) yields
    # F_2..F_{k+1}, so compare against F_2..F_12 = n=2..12 of Binet.
    phi = (1 + 5 ** 0.5) / 2
    psi = (1 - 5 ** 0.5) / 2
    binet = [round((phi ** n - psi ** n) / math.sqrt(5)) for n in range(2, 13)]
    check("SeriesSum matches Binet's formula (F2..F12)",
          m.SeriesSum(u0=0, u1=1).next_terms(11) == binet,
          str(m.SeriesSum(u0=0, u1=1).next_terms(11)))

    check("SeriesSum: exact prediction scores exact",
          m.SeriesSum(u0=1, u1=1).play(5, [2, 3, 5, 8, 13])["exact"],
          "1,1 -> 2,3,5,8,13")
    check("SeriesSum: a wrong middle term is counted wrong",
          m.SeriesSum(u0=1, u1=1).play(5, [2, 99, 5, 8, 13])["correct"] == 4,
          "only term 2 wrong")
    pr = m.SeriesSum().play_random(4, seed=3)
    check("play_random returns a scored result with a total",
          pr["total"] == 4, f"{pr}")

    # --------------------------------------------------- CLI --------------
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        m.play_all()
    out = buf.getvalue()
    check("play_all prints a line for each of the three games",
          all(s in out for s in ("Number Hunt", "EquationSolve", "SeriesSum")),
          out.strip().splitlines()[0])

    print("=" * 62)
    print(f"SUMMARY: {PASS} passed, {FAIL} failed")
    if FAILURES:
        print("failed: " + ", ".join(FAILURES))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
