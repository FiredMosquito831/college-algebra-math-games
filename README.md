# Three Math Games

**A freeCodeCamp College Algebra with Python certification project.**

Three small math games, each built on a real algebraic idea and fully
scriptable (no blocking input, so they are testable).

## The three games

| game | the math |
|---|---|
| **NumberHunt** | guess a secret integer; each miss tells you high/low *and* the remaining candidate range, so you can play optimally by bisection (log₂ of the range) |
| **EquationSolve** | solve a generated linear equation `a·x + b = c`; the game verifies your answer against the exact integer solution |
| **SeriesSum** | predict the next terms of a Fibonacci-like recurrence `uₙ = uₙ₋₁ + uₙ₋₂`, scored against the exact iterative truth (cross-checked with Binet's closed form) |

Each has a `play(...)`, `record(...)` / `check(...)` / `play_random(...)`
API so a full game can be driven from code or from `input()`.

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## How to run the tests

```bash
python test_local.py
```

19 assertions: bisection provably wins within `ceil(log₂(range))`, the
generated equations are internally consistent and a wrong answer is
rejected, and the recurrence matches both an independent loop and Binet's
formula.

```
SUMMARY: 19 passed, 0 failed
```

A `notebook.ipynb` in this folder reproduces the program as a Colab-style
notebook.

## Licence

MIT © 2026 FiredMosquito831. Written from the published project specification;
no freeCodeCamp starter or reference code was used.


## Verification

Everything in this repository was built and tested locally before publication.

| | |
|---|---|
| Tests | **19/19 passing** |
| Interpreter | `projects-ours/.venv` (Python 3.13, torch 2.15.0+cu132) |
| Device | CPU (no model training) |

The full captured test output is committed as [`local-test.log`](local-test.log).

### Data

- No external dataset required.

### Metrics

- (no model metrics for this project)

## Source

Written from scratch against the project's published specification. No freeCodeCamp
starter or reference-solution code was used.
