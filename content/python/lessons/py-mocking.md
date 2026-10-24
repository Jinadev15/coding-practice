# Mocking and Test Doubles

Real code talks to the outside world: hardware, networks, databases, clocks, random number generators. Tests must not depend on those (they'd be slow, flaky, or impossible without the robot attached), so we replace them with **test doubles**. Python's `unittest.mock` provides `Mock`, `MagicMock` and `patch`, which are powerful enough to make bad tests easy too. This lesson teaches the kinds of doubles, how `patch` works (and the classic "patch where it's looked up" mistake), and when to prefer fakes and dependency injection over mocks.

## 1. Kinds of test doubles

| Double | What it is | Example |
|---|---|---|
| **dummy** | passed but never used | a placeholder logger argument |
| **stub** | returns canned answers | `sensor.read()` always returns 21.5 |
| **fake** | a working lightweight implementation | an in-memory database, a simulated motor |
| **spy** | records how it was called | counting `send()` calls |
| **mock** | a spy with expectations you assert | "`stop()` was called once with `emergency=True`" |

## 2. `Mock` and `MagicMock`

```python
from unittest.mock import Mock, MagicMock, call

sensor = Mock()
sensor.read.return_value = 21.5               # stub behaviour
sensor.read()                                 # 21.5
sensor.read.assert_called_once_with()         # verify the interaction

motor = Mock()
motor.set_speed(2.0)
motor.set_speed(0)
motor.set_speed.assert_called_with(0)         # the LAST call
assert motor.set_speed.call_count == 2
motor.set_speed.assert_has_calls([call(2.0), call(0)])

flaky = Mock(side_effect=[TimeoutError, TimeoutError, 42])   # successive results; exceptions are raised
flaky(); flaky(); flaky()                     # raises, raises, returns 42

m = MagicMock()                               # also supports magic methods: len(m), m[0], with m: ...
```

> [!WARNING]
> A plain `Mock` accepts **any** attribute and call: `sensor.raed()` (a typo) silently returns another Mock, and your test passes while the real code would crash. Use **`spec`/`autospec`** so the double only allows the real interface:
> ```python
> sensor = Mock(spec=Lidar)                  # attribute access is checked against Lidar
> sensor.raed()                              # AttributeError: Mock object has no attribute 'raed'
> patch("robot.Lidar", autospec=True)        # also checks call signatures
> ```

## 3. `patch`: replace things temporarily

```python
# robot.py
import time
from drivers import Lidar

def wait_for_clear_path(timeout=1.0):
    lidar = Lidar()
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if lidar.min_distance() > 0.5:
            return True
    return False
```

```python
from unittest.mock import patch

@patch("robot.time.monotonic", side_effect=[0.0, 0.1, 0.2, 2.0])   # a fake clock
@patch("robot.Lidar")                                             # patch the name AS USED IN robot.py
def test_times_out(MockLidar, mock_clock):                        # decorators apply bottom-up
    MockLidar.return_value.min_distance.return_value = 0.1        # always blocked
    assert wait_for_clear_path(timeout=1.0) is False

def test_clear_path():
    with patch("robot.Lidar") as MockLidar:
        MockLidar.return_value.min_distance.return_value = 2.0
        assert wait_for_clear_path() is True
```

> [!KEY]
> **Patch where the name is looked up, not where it's defined.** `robot.py` did `from drivers import Lidar`, which creates the name `robot.Lidar`. Patching `drivers.Lidar` changes the `drivers` module but not the reference `robot.py` already holds, so the real Lidar still runs. Patch `"robot.Lidar"`. (If `robot.py` did `import drivers` and called `drivers.Lidar()`, you'd patch `"drivers.Lidar"`.)

`patch.object(obj, "attr", ...)` patches an attribute of a specific object, `patch.dict(os.environ, {...})` patches dict entries, and pytest's `monkeypatch` fixture is a simpler alternative for attributes and environment variables.

## 4. Prefer dependency injection and fakes

Heavy patching is often a **design smell**: the code creates its own dependencies. Pass them in instead:

```python
class Navigator:
    def __init__(self, lidar, clock=time.monotonic):   # dependencies injected, with sane defaults
        self.lidar = lidar
        self.clock = clock

class FakeLidar:                                      # a fake: real behaviour, no hardware
    def __init__(self, distances): self.distances = iter(distances)
    def min_distance(self): return next(self.distances)

def test_navigator_waits_until_clear():
    nav = Navigator(FakeLidar([0.1, 0.2, 1.5]), clock=iter([0, 0.1, 0.2, 0.3]).__next__)
    assert nav.wait_for_clear_path(timeout=1.0)
```

| Approach | Pros | Cons |
|---|---|---|
| `patch` | works on unmodified code | couples tests to implementation details (import paths, call order); brittle |
| dependency injection + fakes | explicit, readable, survives refactoring | requires designing for testability (a good thing!) |

> [!TIP]
> Mock at **boundaries you own** (your hardware abstraction layer, your HTTP client wrapper), not deep inside third-party libraries. Assert on **outcomes** (state, return values) more than on **interactions** ("`foo` was called with exactly these args"). Over-specified interaction tests break on every harmless refactor.

## 5. Exam-ready answers

> [!EXAM]
> **Mocking and test doubles.** Test doubles replace real dependencies during testing so that units can be tested in isolation, quickly and deterministically: dummies fill parameters, stubs return predetermined values, fakes provide simplified working implementations, spies record interactions, and mocks additionally allow assertions about how they were used. Python's `unittest.mock` provides `Mock` and `MagicMock` objects whose `return_value` and `side_effect` configure behaviour, and whose call records support assertions such as `assert_called_once_with`; specifying `spec` or `autospec` restricts them to the real interface. `patch` temporarily replaces an object, as a decorator or context manager, and must target the name where it is looked up by the code under test. Dependency injection with fakes is often preferable to extensive patching because it reduces coupling between tests and implementation details.

## 6. Cheat sheet

| Need | Code |
|---|---|
| a stub return | `m.method.return_value = x` |
| sequence / raise | `m.method.side_effect = [a, Exc, b]` |
| verify a call | `m.method.assert_called_once_with(args)` |
| only the real API | `Mock(spec=Real)` / `patch(..., autospec=True)` |
| replace a module name | `patch("pkg.module.Name")` (where it's used) |
| replace an attribute | `patch.object(obj, "attr")` / `monkeypatch.setattr` |
| fake env vars | `patch.dict(os.environ, {"K": "v"})` / `monkeypatch.setenv` |
| a fake clock | inject `clock`, or `side_effect=[t0, t1, ...]` |

> [!INTERVIEW]
> **"Your test patches `requests.get`, but the real network call still happens. Why?"** The module under test probably did `from requests import get` (or `import requests as r` in some other way), binding its own name at import time. Patching `requests.get` replaces the attribute on the `requests` module, but the module under test still holds the original function object. Patch the name in the namespace where it's looked up: `patch("mymodule.get")`. Better: wrap HTTP access in your own client class and inject a fake in tests, which removes the import-path coupling entirely.
