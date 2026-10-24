---
id: py-runtime-typecheck
title: A Runtime Type Checker for Annotations
difficulty: Hard
order: 1
tags: typing, get_origin, get_args, generics, Literal, TypedDict, recursion
---
## Statement
Type hints aren't enforced at run time, but libraries like pydantic and beartype read them with `typing` introspection to validate data. Write `check(value, hint) -> bool` supporting these hints, nested arbitrarily:

| Hint | Accepts |
|---|---|
| `int`, `float`, `str`, `bool`, `bytes`, `type(None)` | `isinstance` checks, except that **`bool` is not accepted as `int`**, and `int` **is** accepted as `float` |
| `typing.Any` | everything |
| `list[T]`, `set[T]`, `frozenset[T]` | that container type, with every element matching `T` |
| `tuple[A, B, C]` / `tuple[T, ...]` | a tuple of exactly those element types / any length of `T` |
| `dict[K, V]` | a dict whose keys match `K` and values match `V` |
| `X \| Y`, `Optional[X]`, `Union[X, Y]` | any alternative |
| `Literal["a", 1]` | equal to one of the literals (and the same type: `Literal[1]` rejects `True`) |
| a `TypedDict` subclass | a dict with exactly the required keys (`__required_keys__`), optional ones (`__optional_keys__`) allowed, no others, and each value matching its annotation |

Also write `explain(value, hint) -> str`, which returns `"ok"` or a message about the **first** mismatch found (checking in order: container elements left to right, dict items in insertion order, TypedDict missing keys in **sorted** order, then unexpected keys, then values). PATH starts at `$`, and appends `[i]` for sequence elements (sets: index after sorting the elements by `repr`), `[repr(key)]` for dict values and TypedDict fields, and `<key repr(k)>` for a bad dict key. The messages:

| Situation | Message |
|---|---|
| wrong type | `PATH: expected NAME, got TYPENAME` (NAME is the class name: `int`, `list`, `dict`, `tuple`, the TypedDict name, …) |
| fixed-length tuple, wrong length | `PATH: expected tuple of length N, got M` |
| Literal mismatch | `PATH: expected one of [LITERALS], got REPR` (the literals as a Python list repr) |
| no union alternative matched | `PATH: no alternative of HINT matched` (HINT is `str(hint)` with `typing.` removed; note that Python 3.14 prints `Optional[int]` as `int \| None`) |
| TypedDict missing key | `PATH: missing key 'name'` |
| TypedDict extra key | `PATH: unexpected key 'x'` |

## Starter
```python
from typing import Any, Literal, Union, get_origin, get_args, is_typeddict
import types

def check(value, hint):
    return isinstance(value, hint)

def explain(value, hint):
    return "ok"
```

## Driver
```python
import re
import sys
from typing import Any, Literal, Optional, Union, TypedDict, NotRequired

class Pose(TypedDict):
    x: float
    y: float
    label: NotRequired[str]

class Robot(TypedDict):
    name: str
    pose: Pose
    sensors: list[Literal["lidar", "imu", "gps"]]

SHOW_MESSAGES = True
ASSIGN = re.compile(r"^\s*([A-Za-z_][\w.]*)\s*=(?!=)\s*(.+)$")
env = dict(globals())
for line in sys.stdin.read().splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    m = ASSIGN.match(line)
    try:
        if m and "." not in m.group(1):
            env[m.group(1)] = eval(m.group(2), env)
        elif m:
            exec(line.strip(), env)
        else:
            print(line.strip(), "->", repr(eval(line, env)))
    except Exception as e:
        print(line.strip(), "->", type(e).__name__ + (f": {e}" if SHOW_MESSAGES else ""))
```

## Tests
=== sample
check(3, int)
check(True, int)
check(3, float)
check([1, 2, 3], list[int])
check([1, "2"], list[int])
check((1, "a", 2.5), tuple[int, str, float])
check((1, 2, 3), tuple[int, ...])
check((1, 2), tuple[int])
check({"a": [1], "b": []}, dict[str, list[int]])
check(None, Optional[int])
check(5, int | str)
check("idle", Literal["idle", "run"])
check(1, Literal[True])
explain([1, 2, "x"], list[int])
explain({"a": 1, "b": None}, dict[str, int])
explain(3.5, int | str)
r = {"name": "rover", "pose": {"x": 1, "y": 2.5}, "sensors": ["lidar"]}
check(r, Robot)
explain({"name": "rover", "pose": {"x": 1, "y": 2.5, "z": 0}, "sensors": []}, Robot)
explain({"name": "rover", "pose": {"x": 1}, "sensors": []}, Robot)
explain({"name": "r", "pose": {"x": 0, "y": 0}, "sensors": ["sonar"]}, Robot)
---
check(3, int) -> True
check(True, int) -> False
check(3, float) -> True
check([1, 2, 3], list[int]) -> True
check([1, "2"], list[int]) -> False
check((1, "a", 2.5), tuple[int, str, float]) -> True
check((1, 2, 3), tuple[int, ...]) -> True
check((1, 2), tuple[int]) -> False
check({"a": [1], "b": []}, dict[str, list[int]]) -> True
check(None, Optional[int]) -> True
check(5, int | str) -> True
check("idle", Literal["idle", "run"]) -> True
check(1, Literal[True]) -> False
explain([1, 2, "x"], list[int]) -> '$[2]: expected int, got str'
explain({"a": 1, "b": None}, dict[str, int]) -> "$['b']: expected int, got NoneType"
explain(3.5, int | str) -> '$: no alternative of int | str matched'
check(r, Robot) -> True
explain({"name": "rover", "pose": {"x": 1, "y": 2.5, "z": 0}, "sensors": []}, Robot) -> "$['pose']: unexpected key 'z'"
explain({"name": "rover", "pose": {"x": 1}, "sensors": []}, Robot) -> "$['pose']: missing key 'y'"
explain({"name": "r", "pose": {"x": 0, "y": 0}, "sensors": ["sonar"]}, Robot) -> "$['sensors'][0]: expected one of ['lidar', 'imu', 'gps'], got 'sonar'"
=== hidden
check({1, 2}, set[int])
check(frozenset({"a"}), frozenset[str])
check({1, 2}, frozenset[int])
check([[1, 2], [3]], list[list[int]])
check({"k": (1, "v")}, dict[str, tuple[int, str]])
check(b"x", bytes)
check(None, type(None))
check(object(), Any)
check([None, 1, "s"], list[Any])
check({"name": "r", "pose": {"x": 0.0, "y": 0.0, "label": "home"}, "sensors": ["imu", "gps"]}, Robot)
check({"name": "r", "pose": {"x": 0.0, "y": 0.0, "label": 5}, "sensors": []}, Robot)
explain([(1, 2), (3, "4")], list[tuple[int, int]])
explain({"x": {"y": {"z": [1, 2, True]}}}, dict[str, dict[str, dict[str, list[int]]]])
explain("s", Optional[int])
explain([1], tuple[int, ...])
explain((1, 2, 3), tuple[int, int])
explain(7, Literal[1, 2])
explain([], Robot)
check(2, Union[str, float])
---
check({1, 2}, set[int]) -> True
check(frozenset({"a"}), frozenset[str]) -> True
check({1, 2}, frozenset[int]) -> False
check([[1, 2], [3]], list[list[int]]) -> True
check({"k": (1, "v")}, dict[str, tuple[int, str]]) -> True
check(b"x", bytes) -> True
check(None, type(None)) -> True
check(object(), Any) -> True
check([None, 1, "s"], list[Any]) -> True
check({"name": "r", "pose": {"x": 0.0, "y": 0.0, "label": "home"}, "sensors": ["imu", "gps"]}, Robot) -> True
check({"name": "r", "pose": {"x": 0.0, "y": 0.0, "label": 5}, "sensors": []}, Robot) -> False
explain([(1, 2), (3, "4")], list[tuple[int, int]]) -> '$[1][1]: expected int, got str'
explain({"x": {"y": {"z": [1, 2, True]}}}, dict[str, dict[str, dict[str, list[int]]]]) -> "$['x']['y']['z'][2]: expected int, got bool"
explain("s", Optional[int]) -> '$: no alternative of int | None matched'
explain([1], tuple[int, ...]) -> '$: expected tuple, got list'
explain((1, 2, 3), tuple[int, int]) -> '$: expected tuple of length 2, got 3'
explain(7, Literal[1, 2]) -> '$: expected one of [1, 2], got 7'
explain([], Robot) -> '$: expected Robot, got list'
check(2, Union[str, float]) -> True

## Hints
- `get_origin(list[int])` is `list` and `get_args(list[int])` is `(int,)`. For `X | Y` the origin is `types.UnionType`, and for `Optional`/`Union` it's `typing.Union`, so handle both. For `Literal`, the origin is `Literal` itself.
- Write `explain` first, as a recursive function returning `None` for "ok" or an error string, threading a `path` argument through. Then `check` is just `explain(...) == "ok"`.
- For plain classes, use `type(value).__name__` in the "got" part, and `hint.__name__` in the "expected" part.
- `typing.is_typeddict(hint)` detects TypedDicts. Their annotations come from `typing.get_type_hints(hint)`, which unwraps `NotRequired[...]`.
- For a union's message, `str(hint).replace("typing.", "")` turns `typing.Optional[int]` into `Optional[int]`, and `int | str` already prints as `int | str`.

## Solution
```python
from typing import Any, Literal, Union, get_origin, get_args, is_typeddict, get_type_hints
import types

def _name(hint):
    return getattr(hint, "__name__", str(hint).replace("typing.", ""))

def _explain(value, hint, path):
    if hint is Any:
        return None
    origin, args = get_origin(hint), get_args(hint)

    if origin in (Union, types.UnionType):
        if any(_explain(value, h, path) is None for h in args):
            return None
        return f"{path}: no alternative of {str(hint).replace('typing.', '')} matched"

    if origin is Literal:
        if any(type(value) is type(a) and value == a for a in args):
            return None
        return f"{path}: expected one of {list(args)!r}, got {value!r}"

    if is_typeddict(hint):
        if not isinstance(value, dict):
            return f"{path}: expected {hint.__name__}, got {type(value).__name__}"
        for key in sorted(hint.__required_keys__):
            if key not in value:
                return f"{path}: missing key {key!r}"
        allowed = hint.__required_keys__ | hint.__optional_keys__
        for key in value:
            if key not in allowed:
                return f"{path}: unexpected key {key!r}"
        hints = get_type_hints(hint)
        for key, v in value.items():
            if (err := _explain(v, hints[key], f"{path}[{key!r}]")) is not None:
                return err
        return None

    if origin in (list, set, frozenset):
        if not isinstance(value, origin):
            return f"{path}: expected {origin.__name__}, got {type(value).__name__}"
        (elem,) = args or (Any,)
        items = enumerate(value) if origin is list else enumerate(sorted(value, key=repr))
        for i, v in items:
            if (err := _explain(v, elem, f"{path}[{i}]")) is not None:
                return err
        return None

    if origin is tuple:
        if not isinstance(value, tuple):
            return f"{path}: expected tuple, got {type(value).__name__}"
        if len(args) == 2 and args[1] is Ellipsis:
            elem_hints = [args[0]] * len(value)
        else:
            if len(value) != len(args):
                return f"{path}: expected tuple of length {len(args)}, got {len(value)}"
            elem_hints = list(args)
        for i, (v, h) in enumerate(zip(value, elem_hints)):
            if (err := _explain(v, h, f"{path}[{i}]")) is not None:
                return err
        return None

    if origin is dict:
        if not isinstance(value, dict):
            return f"{path}: expected dict, got {type(value).__name__}"
        kh, vh = args or (Any, Any)
        for k, v in value.items():
            if (err := _explain(k, kh, f"{path}<key {k!r}>")) is not None:
                return err
            if (err := _explain(v, vh, f"{path}[{k!r}]")) is not None:
                return err
        return None

    # plain classes
    if hint is float and isinstance(value, int) and not isinstance(value, bool):
        return None
    if isinstance(value, bool) and hint is not bool and hint is not object:
        return f"{path}: expected {_name(hint)}, got bool"
    if isinstance(value, hint):
        return None
    return f"{path}: expected {_name(hint)}, got {type(value).__name__}"


def explain(value, hint):
    err = _explain(value, hint, "$")
    return "ok" if err is None else err


def check(value, hint):
    return _explain(value, hint, "$") is None
```

**What you learn about `typing` at run time:**
- **Generic aliases** like `list[int]` are objects: `get_origin` returns the container, and `get_args` the parameters. Recursing on the arguments validates arbitrarily nested types.
- **There are two union representations:** `X | Y` (`types.UnionType`, 3.10+) and `typing.Union`/`Optional`. Real-world validators must handle both.
- **`Literal`** compares values *and* types. Since `True == 1`, a naive `value in args` check would accept `True` for `Literal[1]`.
- **`TypedDict`** classes expose `__required_keys__` and `__optional_keys__`, and `get_type_hints` resolves their annotations, including `NotRequired`.
- **The bool-is-an-int trap:** `isinstance(True, int)` is `True`, so validators special-case `bool` (pydantic's "strict" mode does the same).

This is essentially the core of pydantic's validation and FastAPI's request parsing, minus coercion.

