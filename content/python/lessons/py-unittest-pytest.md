# unittest and pytest

Untested code is broken code you haven't found yet. Automated tests let you change code fearlessly, document behaviour precisely, and catch regressions before they reach a robot or a production server. Python ships **`unittest`** (xUnit style, in the standard library), and the ecosystem standard is **`pytest`**: plain functions and plain `assert`, with powerful fixtures and parametrisation. This lesson covers both, how test discovery works, and what makes a good test.

## 1. A first test with pytest

```python
# geometry.py
import math

def distance(p, q):
    return math.dist(p, q)

def heading_deg(dx, dy):
    """Heading in degrees in [0, 360), with 0 = +x, counter-clockwise."""
    return math.degrees(math.atan2(dy, dx)) % 360
```

```python
# test_geometry.py
import math
import pytest
from geometry import distance, heading_deg

def test_distance_345():
    assert distance((0, 0), (3, 4)) == 5

def test_heading_quadrants():
    assert heading_deg(1, 0) == 0
    assert heading_deg(0, 1) == 90
    assert heading_deg(-1, 0) == 180
    assert heading_deg(0, -1) == 270

def test_float_comparison():
    assert 0.1 + 0.2 == pytest.approx(0.3)          # tolerant float comparison
```

```bash
pytest                 # discovers test_*.py / *_test.py, functions named test_*
pytest -q -x           # quiet; stop at the first failure
pytest -k heading      # run only tests whose names match
pytest --lf            # rerun the last failures
```

> [!KEY]
> pytest rewrites `assert` statements to show **both sides** on failure (`assert 4 == 5` with the values and sub-expressions), so you don't need `assertEqual` and friends. Never compare floats with `==`: use `pytest.approx` (or `math.isclose`).

## 2. Testing exceptions and output

```python
def test_bad_input_raises():
    with pytest.raises(ValueError, match="negative"):    # `match` is a regex searched in str(exception)
        sqrt_checked(-1)

def test_prints_banner(capsys):                          # capsys: a built-in fixture capturing stdout/stderr
    print_banner("rover")
    out, err = capsys.readouterr()
    assert "rover" in out
```

## 3. Fixtures: setup with dependency injection

A **fixture** is a function providing a value (or resource) to tests that **name it as a parameter**:

```python
@pytest.fixture
def robot():
    r = Robot("test-bot", battery=100)
    yield r                       # the test runs here
    r.shutdown()                  # teardown, even if the test failed

def test_drive_drains_battery(robot):
    robot.drive(10)
    assert robot.battery < 100

@pytest.fixture
def config_file(tmp_path):        # tmp_path: a built-in fixture (a fresh temporary directory per test)
    p = tmp_path / "robot.yaml"
    p.write_text("max_speed: 2.5\n")
    return p
```

| Built-in fixture | Provides |
|---|---|
| `tmp_path` | a unique temporary directory (`pathlib.Path`) |
| `capsys` / `capfd` | captured stdout/stderr |
| `monkeypatch` | temporarily set attributes, env vars, dict items (auto-undone) |
| `caplog` | captured log records |

Fixture **scope** (`function` default, `class`, `module`, `session`) controls how often it's created: share an expensive resource like a database across a module. Fixtures in `conftest.py` are available to every test in that directory.

## 4. Parametrisation: many cases, one test

```python
@pytest.mark.parametrize("dx, dy, expected", [
    (1, 0, 0),
    (0, 1, 90),
    (-1, 0, 180),
    (1, 1, 45),
    (1, -1, 315),
])
def test_heading(dx, dy, expected):
    assert heading_deg(dx, dy) == pytest.approx(expected)
```

Each tuple becomes a separate test case with its own pass/fail report. Use `pytest.param(..., id="diag")` for readable names, and `marks=pytest.mark.xfail` for known bugs.

## 5. unittest: the standard-library style

```python
import unittest

class TestGeometry(unittest.TestCase):
    def setUp(self):                         # before each test
        self.origin = (0, 0)

    def test_distance(self):
        self.assertEqual(distance(self.origin, (3, 4)), 5)

    def test_raises(self):
        with self.assertRaises(ValueError):
            sqrt_checked(-1)

    def test_close(self):
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=9)

if __name__ == "__main__":
    unittest.main()
```

`unittest` needs no installation and is what you'll find in older codebases and the stdlib itself. pytest **runs unittest-style tests too**, so teams can migrate gradually.

| | unittest | pytest |
|---|---|---|
| Test definition | `TestCase` subclass methods | plain functions (classes optional) |
| Assertions | `self.assertEqual`, `assertIn`, … | plain `assert` with introspection |
| Setup/teardown | `setUp`/`tearDown`, `setUpClass` | fixtures (composable, scoped, injected) |
| Parametrisation | `subTest` loops | `@pytest.mark.parametrize` |
| Plugins | few | a huge ecosystem (coverage, xdist, hypothesis, benchmark) |

## 6. What makes a good test

- **Fast, isolated, deterministic:** no dependence on order, network, wall-clock time or randomness without a seed.
- **One behaviour per test**, named for that behaviour: `test_drive_stops_when_battery_empty`.
- **Arrange–Act–Assert** structure.
- **Test edge cases:** empty inputs, boundaries (0, 1, max), invalid inputs, error paths.
- **Coverage** (`pytest --cov`) shows untested lines, but 100% coverage doesn't mean correct. Property-based testing (`hypothesis`) generates hundreds of random inputs to find edge cases you didn't think of.

## 7. Exam-ready answers

> [!EXAM]
> **Testing with unittest and pytest.** Automated unit tests verify the behaviour of small units of code. `unittest`, in the standard library, organises tests as methods of `unittest.TestCase` subclasses with assertion methods (`assertEqual`, `assertRaises`, `assertAlmostEqual`) and per-test `setUp`/`tearDown` hooks. pytest discovers test functions in files named `test_*.py`, uses plain `assert` statements whose failures are reported with detailed value introspection, provides fixtures (functions injected into tests by parameter name, with configurable scope and `yield`-based teardown, plus built-ins such as `tmp_path`, `capsys` and `monkeypatch`), and supports running a test over many inputs with `@pytest.mark.parametrize`. Good tests are fast, isolated, deterministic and focused on one behaviour, and cover boundary and error cases.

## 8. Cheat sheet

| Need | pytest |
|---|---|
| a basic check | `assert result == expected` |
| floats | `assert x == pytest.approx(y)` |
| expect an exception | `with pytest.raises(ValueError, match="...")` |
| setup/teardown | `@pytest.fixture` + `yield` |
| a temp directory | the `tmp_path` fixture |
| many cases | `@pytest.mark.parametrize("a,b", [...])` |
| capture prints | the `capsys` fixture |
| fake env/attributes | the `monkeypatch` fixture |
| run a subset | `pytest -k name -x -q` |

> [!INTERVIEW]
> **"What's a fixture in pytest, and why is it better than setUp?"** A fixture is a function that produces a resource for tests, requested by naming it as a test parameter (dependency injection). Fixtures compose (fixtures can use other fixtures), have explicit scopes (per test, module or session) to share expensive resources, do teardown with `yield` (run even on failure), and live in `conftest.py` for reuse across files. `setUp` runs the same code for every test in a class, whether needed or not, and can't be shared or composed as cleanly. Built-in fixtures (`tmp_path`, `monkeypatch`, `capsys`) remove most hand-written setup.
