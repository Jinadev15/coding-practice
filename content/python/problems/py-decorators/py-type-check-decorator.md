---
id: py-type-check-decorator
title: Runtime Type Enforcement
difficulty: Hard
order: 3
tags: decorators, annotations, inspect, introspection
---
## Statement
Write a decorator `enforce_types` that checks arguments **and** the return value against the function's annotations at call time:

- For each parameter with an annotation that is a **class** (like `int` or `str`), the bound argument must satisfy `isinstance(value, annotation)`. Otherwise raise `TypeError` with exactly this message: `argument 'NAME' must be TYPE, got ACTUAL` (using the classes' `__name__`).
- Parameters without annotations, and defaults that aren't overridden, are also checked (defaults are bound too).
- If `return` is annotated with a class, check the result the same way: `return value must be TYPE, got ACTUAL`.
- `bool` is a subclass of `int`. Follow `isinstance` (so `True` passes as `int`).

The driver decorates a few functions and prints results or error messages.

## Starter
```python
import functools
import inspect

def enforce_types(func):
    pass
```

## Driver
```python
@enforce_types
def scale(x: float, factor: int = 2) -> float:
    return x * factor

@enforce_types
def label(name: str, n) -> str:
    return name * n

@enforce_types
def broken(n: int) -> str:
    return n

q = int(input())
for _ in range(q):
    try:
        print(repr(eval(input())))
    except TypeError as e:
        print("TypeError:", e)
print(scale.__name__)
```

## Tests
=== sample
4
scale(1.5)
scale(1.5, 3)
scale(2, 3)
label("ab", 2)
---
3.0
4.5
TypeError: argument 'x' must be float, got int
'abab'
scale
=== hidden
4
label(5, 2)
broken(3)
scale(1.0, factor=2.5)
scale(1.0, True)
---
TypeError: argument 'name' must be str, got int
TypeError: return value must be str, got int
TypeError: argument 'factor' must be int, got float
1.0
scale

## Hints
- Get the signature once, at decoration time: `sig = inspect.signature(func)`.
- In the wrapper: `bound = sig.bind(*args, **kwargs); bound.apply_defaults()`. Then iterate `bound.arguments.items()`.
- `sig.parameters[name].annotation` is `inspect.Parameter.empty` when missing. Careful: `empty` is itself a class, so test `ann is not inspect.Parameter.empty` **before** `isinstance(ann, type)`.
- The return annotation is `sig.return_annotation`.

## Solution
Introspect the signature once when decorating. On each call, bind the arguments exactly as Python would, then check each one against its annotation.

```python
import functools
import inspect

def enforce_types(func):
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            ann = sig.parameters[name].annotation
            if ann is not inspect.Parameter.empty and isinstance(ann, type) \
                    and not isinstance(value, ann):
                raise TypeError(f"argument '{name}' must be {ann.__name__}, "
                                f"got {type(value).__name__}")
        result = func(*args, **kwargs)
        ret = sig.return_annotation
        if ret is not inspect.Signature.empty and isinstance(ret, type) \
                and not isinstance(result, ret):
            raise TypeError(f"return value must be {ret.__name__}, "
                            f"got {type(result).__name__}")
        return result

    return wrapper
```

The `empty` check matters: `inspect.Parameter.empty` is a class, so `isinstance(empty, type)` is `True`, and without the identity test every unannotated parameter would fail (`must be _empty`). `scale(1.0, True)` passes because `bool` is a subclass of `int`, and the result is `1.0 * True == 1.0`. Python's annotations are **not** enforced by the interpreter: they're metadata. Libraries like Pydantic (used by FastAPI) and typeguard do what this decorator does, with full support for generics such as `list[int]`.
