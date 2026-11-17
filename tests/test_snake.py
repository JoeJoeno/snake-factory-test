"""Tests for the terminal snake game."""
from snake import Board, Snake, GameOver, load_high_score, save_high_score


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


def test_render_status_line_shows_high_score():
    b = Board(w=12, h=6)
    b.high_score = 7
    out = b.render()
    last = out.splitlines()[-1]
    assert last == f"score={b.score} len={len(b.snake)} High: 7"


def test_render_status_line_defaults_high_score_to_zero():
    b = Board(w=12, h=6)
    out = b.render()
    assert out.splitlines()[-1].endswith(" High: 0")


def test_load_high_score_missing_file(tmp_path):
    assert load_high_score(str(tmp_path / "nope.txt")) == 0


def test_load_high_score_valid_file(tmp_path):
    p = tmp_path / "highscore.txt"
    p.write_text("42\n")
    assert load_high_score(str(p)) == 42


def test_load_high_score_corrupt_file(tmp_path):
    p = tmp_path / "highscore.txt"
    p.write_text("not-a-number")
    assert load_high_score(str(p)) == 0


def test_load_high_score_empty_file(tmp_path):
    p = tmp_path / "highscore.txt"
    p.write_text("")
    assert load_high_score(str(p)) == 0


def test_save_only_updates_on_new_high(tmp_path):
    p = tmp_path / "highscore.txt"
    p.write_text("10\n")
    # A lower or equal final score leaves the file unchanged (play() logic).
    original = p.read_text()
    for score in (5, 10):
        if score > load_high_score(str(p)):
            save_high_score(score, str(p))
    assert p.read_text() == original
    # A higher score updates the file.
    if 11 > load_high_score(str(p)):
        save_high_score(11, str(p))
    assert p.read_text() == "11\n"


def test_round_trip_persists_across_restart(tmp_path):
    p = tmp_path / "highscore.txt"
    # First "session": no file yet, so high score starts at 0.
    high = load_high_score(str(p))
    b = Board()
    b.high_score = high
    b.score = 3
    if b.score > b.high_score:
        save_high_score(b.score, str(p))
    assert p.read_text() == "3\n"
    # Second "session": restart must load the persisted high score.
    assert load_high_score(str(p)) == 3
