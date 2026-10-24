# Type Hints

Type hints let you write down what types a function expects and returns: `def area(w: float, h: float) -> float`. Python **does not enforce them at run time**. They're metadata read by tools: type checkers (mypy, pyright), IDEs (autocomplete, refactoring) and frameworks (FastAPI and Pydantic validate request data from them; dataclasses build classes from them). In professional and AI codebases, typed signatures are the norm, because they turn a whole category of bugs into editor warnings before the code ever runs.

## 1. Basic syntax

> [!SYNTAX]
> ```python
> def func(param: Type, other: Type = default) -> ReturnType:
>     ...
> variable: Type = value
> ```

```python
def greet(name: str, times: int = 1) -> str:
    return ("Hello " + name + "! ") * times

count: int = 0
ratio: float = 0.75
names: list[str] = []
```

Notice `times: int = 1`: when a parameter has both an annotation and a default, put spaces around `=` (PEP 8).

> [!KEY]
> Annotations are **not checked when the program runs**:
> ```python
> def double(x: int) -> int:
>     return x * 2
> print(double("ab"))     # 'abab': no error at run time
> ```
> They're stored in `func.__annotations__`, and **static** checkers analyse the code without running it:
> ```text
> $ mypy app.py
> app.py:3: error: Argument 1 to "double" has incompatible type "str"; expected "int"
> ```

## 2. Built-in and collection types

Since Python 3.9 you can parameterise the built-in collections directly:

| Hint | Meaning |
|---|---|
| `int`, `float`, `str`, `bool`, `bytes` | the plain types |
| `list[int]` | a list of ints |
| `dict[str, float]` | a dict from str keys to float values |
| `set[str]` | a set of strings |
| `tuple[int, str]` | **exactly** two items: an int, then a str |
| `tuple[int, ...]` | any number of ints |
| `None` | the function returns nothing useful |

`float` also accepts `int` values (numeric promotion), so `def f(x: float)` accepts `f(3)`.

## 3. Optional and union types

```python
def find_user(user_id: int) -> str | None:     # Python 3.10+: "str or None"
    ...

def parse(value: int | str) -> int:
    return value if isinstance(value, int) else int(value)
```

Older equivalents that you'll see in existing code: `Optional[str]` means `str | None`, and `Union[int, str]` means `int | str`. Both come from `typing`.

> [!WARNING]
> `Optional[X]` doesn't mean "an optional parameter". It means "X or None". A parameter is optional because it has a **default**: `def f(x: int | None = None)`.

### Narrowing

Type checkers understand control flow. After a check, the type is "narrowed":

```python
def length(s: str | None) -> int:
    if s is None:
        return 0
    return len(s)          # the checker knows s is str here
```

## 4. Callables and `Any`

```python
from collections.abc import Callable
from typing import Any

def apply(f: Callable[[int, int], int], a: int, b: int) -> int:
    return f(a, b)        # f takes two ints and returns an int

def log(value: Any) -> None:     # Any switches checking off for this value
    print(value)
```

`Callable[..., R]` means "any arguments, returns R". Prefer the `collections.abc` versions of abstract types: `Iterable[T]`, `Sequence[T]`, `Mapping[K, V]`.

## 5. Accept general types, return specific ones

```python
from collections.abc import Iterable, Sequence

def total(values: Iterable[float]) -> float:   # works with lists, tuples, generators, sets…
    return sum(values)

def first(items: Sequence[str]) -> str:        # needs indexing, so Sequence, not Iterable
    return items[0]
```

> [!TIP]
> **Postel's principle for types**: be liberal in what you accept (abstract types like `Iterable`, `Mapping`) and specific in what you return (`list[str]`, `dict[str, int]`). This makes functions more reusable without weakening guarantees for callers.

## 6. Type aliases and more expressive types

```python
type Vector = list[float]                 # Python 3.12+ `type` statement
type Matrix = list[Vector]

def norm(v: Vector) -> float:
    return sum(x * x for x in v) ** 0.5
```

| Tool (from `typing`) | Use |
|---|---|
| `Literal["r", "w"]` | only these exact values |
| `Final` | a constant that must not be reassigned |
| `TypedDict` | a dict with a fixed set of typed keys (JSON shapes) |
| `NamedTuple` | a typed record tuple |
| `Protocol` | structural "duck" typing (Advanced Typing lesson) |
| `TypeVar`, `Generic`, `def f[T](x: T) -> T` | generics (Advanced Typing lesson) |

```python
from typing import Literal, Final
MAX_SPEED: Final = 2.5
def open_file(path: str, mode: Literal["r", "w"] = "r") -> None: ...
```

## 7. How annotations are stored (and what's new in 3.14)

```python
def f(x: int, y: "str" = "a") -> list[int]: ...
print(f.__annotations__)
# {'x': <class 'int'>, 'y': 'str', 'return': list[int]}
```

Python 3.14 implements **deferred evaluation of annotations** (PEP 649): annotations are evaluated lazily, only when someone asks for them. A function can therefore refer to a class defined **later** in the file without quotes, and an undefined name in an annotation doesn't fail at `def` time:

```python
def make() -> Robot:      # fine in 3.14 even though Robot is defined below
    return Robot()

class Robot: ...
```

In older versions you'd write `-> "Robot"` (a string "forward reference") or put `from __future__ import annotations` at the top of the file. You'll still see both styles. The `annotationlib` module (3.14) reads annotations safely in various formats.

## 8. Checking types: mypy and friends

```bash
uv pip install mypy
mypy --strict app.py
```

Gradual typing: start by annotating function **signatures**. Local variables are usually inferred (`count = 0` is inferred as `int`). Use `--strict` on new code. `reveal_type(expr)` asks the checker what type it inferred.

> [!NOTE]
> Run-time validation is a separate concern. If data comes from users, files or networks, the static checker can't see it. Validate it at the boundary (Pydantic models, explicit checks). You wrote a mini version of that as the `enforce_types` decorator.

## 9. Why type hints matter for OOP and large projects

When you split a project into classes and files, signatures **are** the contracts between parts:

```python
class Motor:
    def set_speed(self, rpm: float) -> None: ...

class Controller:
    def __init__(self, left: Motor, right: Motor) -> None: ...
```

Reading only the signatures tells you how the pieces connect: a `Controller` needs two `Motor`s. That's exactly the skill of "seeing" a multi-file OOP design.

## 10. Exam-ready answers

> [!EXAM]
> **Type hints.** Type hints (annotations) are optional notations that specify the expected types of function parameters, return values and variables, for example `def f(x: int) -> str`. They are stored in the `__annotations__` attribute and are not enforced by the Python interpreter at run time. Static type checkers such as mypy and pyright analyse annotated code to detect type errors before execution, and IDEs use them for completion and refactoring. Common forms include built-in generics (`list[int]`, `dict[str, float]`), unions (`int | None`), `Callable`, `Any`, `Literal` and type aliases. Python is therefore dynamically typed with optional, gradual static typing.

## 11. Cheat sheet

| Need | Hint |
|---|---|
| list of ints | `list[int]` |
| dict | `dict[str, int]` |
| maybe missing | `X \| None` |
| either type | `int \| str` |
| function argument | `Callable[[int], str]` |
| any iterable input | `Iterable[T]` |
| fixed tuple | `tuple[int, int]` |
| variable-length tuple | `tuple[int, ...]` |
| alias | `type Name = ...` |
| constant | `NAME: Final = ...` |
| no return value | `-> None` |

> [!INTERVIEW]
> **"Does `def f(x: int)` stop someone passing a string?"** No. Python ignores annotations at run time; they're for tools. Enforcement comes from static checking in CI (mypy/pyright) or from run-time validators at system boundaries (Pydantic, attrs validators). Being clear on this distinction marks you as someone who has worked on typed Python codebases.
