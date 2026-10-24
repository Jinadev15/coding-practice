# Advanced Typing and Generics

Type hints don't change how Python runs, but in large codebases they're indispensable: static checkers (mypy, pyright) catch bugs before running, IDEs autocomplete accurately, and signatures document intent. The basics (`int`, `list[str]`, `Optional`) came earlier. This lesson covers the advanced tools used in professional libraries: **generics** (`TypeVar`, the PEP 695 `class Box[T]` syntax), **variance**, `ParamSpec` for typing decorators, `@overload`, `TypedDict`, `Literal`, `Final`, `Self` and `TypeGuard`.

## 1. Generic functions and classes

A **type variable** stands for "some type, the same one throughout this signature":

```python
# Python 3.12+ syntax (PEP 695)
def first[T](items: list[T]) -> T:
    return items[0]

x = first([1, 2, 3])        # the checker infers int
s = first(["a", "b"])       # str

class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []
    def push(self, item: T) -> None:
        self._items.append(item)
    def pop(self) -> T:
        return self._items.pop()

ints = Stack[int]()
ints.push(3)
ints.push("x")              # type checker error: expected int

type Pair[T] = tuple[T, T]  # generic type alias (3.12+)
```

The older syntax, still everywhere in existing code:

```python
from typing import TypeVar, Generic
T = TypeVar("T")
class Stack(Generic[T]): ...
def first(items: list[T]) -> T: ...
```

### Bounds and constraints

```python
def largest[T: (int, float)](xs: list[T]) -> T: ...      # constrained: exactly int OR float
from typing import Protocol
class Comparable(Protocol):
    def __lt__(self, other, /) -> bool: ...
def max_of[T: Comparable](xs: list[T]) -> T:             # bounded: any type with __lt__
    return max(xs)
```

## 2. Variance: when is `Box[Dog]` a `Box[Animal]`?

If `Dog` is a subtype of `Animal`:

| Variance | `C[Dog]` vs `C[Animal]` | Safe when the container... | Examples |
|---|---|---|---|
| **covariant** | `C[Dog]` is a subtype of `C[Animal]` | is read-only (produces T) | `Sequence[T]`, `tuple[T, ...]`, `frozenset[T]` |
| **contravariant** | `C[Animal]` is a subtype of `C[Dog]` | only consumes T | `Callable[[T], None]` parameters |
| **invariant** | neither | both reads and writes T | `list[T]`, `dict[K, V]` |

```python
def feed_all(animals: list[Animal]) -> None:
    animals.append(Cat())               # legal for list[Animal]...

dogs: list[Dog] = [Dog()]
feed_all(dogs)                          # type ERROR: list is invariant, or a Cat would end up in dogs
def count(animals: Sequence[Animal]) -> int: ...
count(dogs)                             # OK: Sequence is read-only, so covariant
```

> [!KEY]
> **Accept the most general read-only type in parameters** (`Sequence`, `Mapping`, `Iterable`) and **return precise types**. A parameter typed `list[Animal]` rejects `list[Dog]` for good reason. With PEP 695 syntax, the checker infers the variance of your own generic classes automatically.

## 3. Typing callables and decorators: `ParamSpec`

```python
from collections.abc import Callable
import functools

def logged[**P, R](func: Callable[P, R]) -> Callable[P, R]:   # P captures the whole parameter list
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("calling", func.__name__)
        return func(*args, **kwargs)
    return wrapper

@logged
def move(x: float, y: float, *, speed: float = 1.0) -> bool: ...
move(1, 2, speed="fast")    # the checker still catches this: the decorated signature is preserved
```

Without `ParamSpec`, a decorator typed `Callable[..., Any]` erases the signature, and every call to a decorated function goes unchecked.

## 4. `@overload`: multiple signatures for one function

```python
from typing import overload

@overload
def parse(x: str) -> int: ...
@overload
def parse(x: bytes) -> str: ...
def parse(x: str | bytes) -> int | str:      # the single real implementation
    return int(x) if isinstance(x, str) else x.decode()

n = parse("42")      # the checker knows n is int
```

## 5. Precise types for data

```python
from typing import TypedDict, Literal, Final, NotRequired, Self, TypeGuard

class Telemetry(TypedDict):          # a dict with a known shape (JSON payloads)
    robot: str
    battery: float
    error: NotRequired[str]

Mode = Literal["idle", "run", "fault"]
def set_mode(m: Mode) -> None: ...
set_mode("runnning")                 # checker error: not one of the literals

MAX_SPEED: Final = 2.5               # reassignment is a checker error

class Builder:
    def with_speed(self, v: float) -> Self:    # subclasses' methods return the subclass type
        self.speed = v
        return self

def is_str_list(xs: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in xs)  # after `if is_str_list(v):`, v is list[str]
```

At run time a `TypedDict` is just a `dict`, and `Literal`/`Final` are just annotations. They only affect static checking. For **run-time validation** of untrusted data, use pydantic or attrs validators.

## 6. Runtime introspection

```python
from typing import get_type_hints, get_origin, get_args
get_type_hints(move)                 # {'x': float, 'y': float, 'speed': float, 'return': bool}
get_origin(list[int]), get_args(dict[str, int])   # (list, (str, int))
```

Frameworks like FastAPI, pydantic and dataclasses read annotations at run time to generate validation, serialisation and APIs.

## 7. Exam-ready answers

> [!EXAM]
> **Generics and advanced typing.** Type hints are annotations checked by static tools rather than the interpreter. Type variables, declared with `TypeVar` or the PEP 695 syntax `def f[T](...)` and `class C[T]`, express generic functions and classes whose types are related across a signature; they may be bounded or constrained. Variance describes subtyping of generic types: covariant types such as `Sequence[T]` and `tuple` accept subtypes of their parameters, contravariant positions such as callable parameters accept supertypes, and mutable containers such as `list` are invariant. `ParamSpec` captures a callable's parameter list so that decorators preserve signatures, `@overload` declares multiple signatures for one implementation, and `TypedDict`, `Literal`, `Final`, `Self` and `TypeGuard` express dictionary shapes, permitted values, constants, fluent return types and type-narrowing predicates.

## 8. Cheat sheet

| Need | Syntax |
|---|---|
| generic function | `def f[T](x: T) -> T` |
| generic class | `class Box[T]:` |
| bounded type var | `[T: Comparable]` |
| read-only parameter (covariant) | `Sequence[T]`, `Mapping[K, V]`, `Iterable[T]` |
| typed decorator | `def deco[**P, R](f: Callable[P, R]) -> Callable[P, R]` |
| several signatures | `@overload` |
| dict with a known shape | `TypedDict` |
| fixed set of strings | `Literal["a", "b"]` |
| return the subclass type | `-> Self` |
| a type-narrowing predicate | `-> TypeGuard[X]` / `TypeIs[X]` (3.13) |

> [!INTERVIEW]
> **"Why is `list[Dog]` not accepted where `list[Animal]` is expected, when every Dog is an Animal?"** Because lists are mutable, so invariant. If it were allowed, the function could `append(Cat())` to what is really your list of dogs, breaking the caller's type guarantee. Read-only abstractions are covariant: if the function only reads, type the parameter `Sequence[Animal]` (or `Iterable[Animal]`), which accepts `list[Dog]` safely. The same rule appears in Java's wildcards (`List<? extends Animal>`) and C#'s `IEnumerable<out T>`.
