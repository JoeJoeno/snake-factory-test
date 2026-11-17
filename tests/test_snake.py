"""Tests for the terminal snake game."""
import os
import tempfile
from io import BytesIO, TextIOWrapper

from snake import Board, Snake, GameOver


def test_snake_steps_forward():
    s = Snake((5, 5), (1, 0))
    s.step()
    assert s.head() == (6, 5)


def test_snake_cannot_reverse_onto_neck():
    s = Snake((5, 5), (1, 0))
    s.body.append((4, 5))  # give it a neck behind it
    s.turn((-1, 0))        # attempting to reverse is ignored
    assert s.direction == (1, 0)


def test_snake_reverses_when_single_cell():
    s = Snake((5, 5), (1, 0))
    s.turn((-1, 0))        # single cell may reverse
    assert s.direction == (-1, 0)


def test_moves_to_food_detects_contact():
    s = Snake((4, 3), (1, 0))
    s.step()                       # head is now at (5,3)
    assert s.moves_to_food((5, 3))
    assert not s.moves_to_food((4, 3))


def test_board_wall_collision_ends_game():
    b = Board(w=10, h=8)
    b.snake = Snake((9, 4), (1, 0))  # one step from right wall
    try:
        b.tick()
        assert b.over, "expected wall collision to set over"
    except GameOver as e:
        assert e.args == ("wall",)
    assert b.over


def test_board_self_collision_ends_game():
    b = Board(w=20, h=10)
    # U-shaped body: tail (3,5) (3,6) (4,6) head (5,6) moving right.
    # After step, head is (6,6); body[:-1] still contains (3,6),(4,6),(5,6),
    # none equal (6,6) -> not a self hit. Instead, make the head run into
    # the body: head (4,6) moving right -> next (5,6) which is in body.
    s = Snake((0, 0), (1, 0))
    # Body ordered tail->head; last element is the head.
    # Head (4,6) moving right -> next (5,6), which is an earlier body cell.
    s.body = [(3, 5), (3, 6), (5, 6), (4, 6)]
    s.direction = (1, 0)
    b.snake = s
    b.food = (0, 0)  # irrelevant
    try:
        b.tick()
        assert b.over
    except GameOver as e:
        assert e.args == ("self",)
    assert b.over


def test_board_eating_food_grows_and_scores():
    b = Board(w=20, h=10)
    b.snake = Snake((5, 5), (1, 0))
    b.snake.body = [(4, 5), (5, 5)]
    b.food = (6, 5)          # right next to head
    before = len(b.snake)
    b.tick()
    assert b.score == 1
    assert len(b.snake) == before + 1, "snake should have grown"


def test_board_spawn_food_avoids_snake():
    b = Board(w=8, h=6)
    b.snake.body = [(i, 0) for i in range(8)]  # whole top row occupied
    b.spawn_food()
    assert b.food not in b.snake.body
    assert 0 <= b.food[0] < 8 and 0 <= b.food[1] < 6


def test_render_contains_food_and_body():
    b = Board(w=12, h=6)
    out = b.render()
    assert "*" in out, "food marker should render"
    assert "#" in out, "body marker should render"
    # Render must work under a pipe (no TTY) — we just called it here.


def test_no_title_escape_in_piped_output(capsys, monkeypatch):
    import snake
    # Play with a real (non-TTY) pipe for stdout and an exhausted pipe for
    # stdin so read_key() returns "" and play() quits immediately. Any
    # title escape would be written to the pipe; a TTY would be.
    pipe = tempfile.TemporaryFile("w+b")
    pipe_fd = pipe.fileno()
    monkeypatch.setattr(snake.sys, "stdout", os.fdopen(pipe_fd, "w", buffering=1))
    monkeypatch.setattr(snake.sys, "stdin", TextIOWrapper(BytesIO(b"")))
    snake.play()
    captured = capsys.readouterr()
    assert "\033]0;" not in captured.out
    pipe.seek(0)
    data = pipe.read()
    assert b"\033]0;" not in data
    assert b"quit" in data
    pipe.close()
