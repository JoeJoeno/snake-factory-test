# Snake

A tiny terminal snake game in Python. The board is a fixed-size grid drawn
with plain-text blocks in the terminal; the snake grows as it eats food, and
the game ends on wall or self collision — or in a win when the snake reaches
length 10.

## Files

- `snake.py` — the game: `Board`, `Snake`, and the main loop.
- `tests/test_snake.py` — pytest tests for the game logic.

## Conventions

- Plain Python 3.11+, no external dependencies.
- Keep functions small; the board and snake are separate classes.
- Use `pytest` for tests; run them from the repo root.
- The terminal renderer uses half-blocks for colour; don't assume a TTY —
  the renderer must also work when stdout is a pipe (tests capture it).

## Commands

```bash
python -m pytest -q          # run the test suite
python snake.py              # play (interactive, needs a TTY)
```

Add tests when you change behaviour; keep the suite green.
