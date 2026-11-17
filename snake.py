"""Terminal snake game.

Board is a fixed WxH grid. Snake grows as it eats food. Game over on wall or
self collision. The renderer also works when stdout is a pipe (no TTY
required) so tests can capture it.

Run:  python snake.py            (interactive, needs a TTY)
"""
from __future__ import annotations

import os
import random
import sys
import time

W, H = 30, 12          # board dimensions
STEP_SECONDS = 0.10    # per-tick delay
EMPTY = " "
BODY = "#"
FOOD = "*"

ARROWS = {
    "a": (-1, 0),
    "h": (-1, 0),
    "s": (0, 1),
    "j": (0, 1),
    "d": (1, 0),
    "l": (1, 0),
    "w": (0, -1),
    "k": (0, -1),
}


class GameOver(Exception):
    """Raised when the snake hits a wall or itself."""


class Snake:
    def __init__(self, pos: tuple[int, int], direction: tuple[int, int]):
        # Body is a list of (x, y); head is body[-1].
        self.body = [pos]
        self.direction = direction

    def head(self) -> tuple[int, int]:
        return self.body[-1]

    def turn(self, d: tuple[int, int]) -> None:
        # No reversing straight back onto the neck.
        if (d[0], d[1]) == (-self.direction[0], -self.direction[1]) and len(self.body) > 1:
            return
        self.direction = d

    def step(self) -> None:
        hx, hy = self.head()
        dx, dy = self.direction
        self.body.append((hx + dx, hy + dy))

    def grow(self) -> None:
        # Mark that the next step should keep the tail.
        self._keep_tail = True

    def __len__(self) -> int:
        return len(self.body)

    def collides(self, food_pos: tuple[int, int]) -> bool:
        """True if the current head overlaps another body segment."""
        hx, hy = self.head()
        for (x, y) in self.body[:-1]:
            if (x, y) == (hx, hy):
                return True
        return False

    def moves_to_food(self, food_pos: tuple[int, int]) -> bool:
        # Called after step(); head already moved. Just compare head to food.
        return self.head() == food_pos


class Board:
    def __init__(self, w: int = W, h: int = H):
        self.w, self.h = w, h
        self.snake = Snake((w // 2, h // 2), (1, 0))
        self.food: tuple[int, int] = (0, 0)
        self.score = 0
        self.over = False
        self._rng = random.Random()
        self.spawn_food()

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def spawn_food(self) -> None:
        free = [
            (x, y)
            for x in range(self.w)
            for y in range(self.h)
            if (x, y) != self.snake.head() and (x, y) not in self.snake.body
        ]
        self.food = self._rng.choice(free) if free else (0, 0)

    def handle_key(self, key: str) -> None:
        if key in ARROWS:
            self.snake.turn(ARROWS[key])

    def tick(self) -> None:
        if self.over:
            return
        self.snake.step()
        hx, hy = self.snake.head()
        if not self.in_bounds(hx, hy):
            self.over = True
            raise GameOver("wall")
        if self.snake.collides(self.food):
            self.over = True
            raise GameOver("self")
        if self.snake.moves_to_food(self.food):
            self.snake.grow()
            self.score += 1
            self.spawn_food()
        # Drop the tail unless we grew this tick.
        if not getattr(self.snake, "_keep_tail", False):
            self.snake.body.pop(0)
        else:
            self.snake._keep_tail = False

    def render(self) -> str:
        grid = [
            [EMPTY] * self.w
            for _ in range(self.h)
        ]
        for (x, y) in self.snake.body:
            if self.in_bounds(x, y):
                grid[y][x] = BODY
        if self.in_bounds(self.food[0], self.food[1]):
            grid[self.food[1]][self.food[0]] = FOOD
        lines = ["+" + "-" * self.w + "+"]
        for row in grid:
            lines.append("|" + "".join(row) + "|")
        lines.append("+" + "-" * self.w + "+")
        lines.append(f"score={self.score} len={len(self.snake)}")
        return "\n".join(lines)


def read_key() -> str:
    """Read a single keypress without requiring a TTY echo.

    Falls back to line input (Enter-terminated) when not a TTY, which is what
    happens under pipes and tests.
    """
    if sys.stdin.isatty():
        os.system("stty raw -echo")
        ch = sys.stdin.read(1)
        os.system("stty -raw echo")
        if ch in ("q", "Q", "\x03", ""):
            sys.exit(0)
        return ch
    line = sys.stdin.readline()
    return line.strip()


def play() -> None:
    board = Board()
    print(board.render())
    while not board.over:
        key = read_key()
        if key in ("q", "Q", ""):
            break
        board.handle_key(key)
        try:
            board.tick()
        except GameOver as e:
            break
        print()
        print(board.render())
    if board.over:
        print("game over")
    else:
        print(f"quit: score={board.score}")


if __name__ == "__main__":
    play()
