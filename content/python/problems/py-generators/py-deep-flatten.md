---
id: py-deep-flatten
title: Deep Flatten with yield from
difficulty: Medium
order: 3
tags: generators, yield from, recursion
---
## Statement
Write a generator `deep_flatten(obj)` that yields every **atomic** value inside an arbitrarily nested structure, in order:

- Lists and tuples are flattened recursively.
- **Dicts** yield their **values**, flattened recursively, in insertion order.
- **Strings are atoms**: `"abc"` is yielded whole, not split into characters (even though strings are iterable).
- Everything else (numbers, None, booleans) is an atom.

Use `yield from` for the recursion.

## Starter
```python
def deep_flatten(obj):
    pass
```

## Driver
```python
import ast, inspect
assert inspect.isgeneratorfunction(deep_flatten)
for _ in range(int(input())):
    print(list(deep_flatten(ast.literal_eval(input()))))
```

## Tests
=== sample
3
[1, [2, [3, (4, 5)]], 6]
["ab", ["cd", ["e"]]]
{"x": [1, 2], "y": {"z": 3}}
---
[1, 2, 3, 4, 5, 6]
['ab', 'cd', 'e']
[1, 2, 3]
=== hidden
4
7
"solo"
[[], (), {}, [[[]]]]
[None, True, [1.5, {"k": ("a", [False])}]]
---
[7]
['solo']
[]
[None, True, 1.5, 'a', False]

## Hints
- Check `isinstance(obj, dict)` first (yield from its values), then `isinstance(obj, (list, tuple))`, else `yield obj`.
- Don't test "is it iterable?" in general, because strings are iterable and would recurse into characters forever: a 1-character string's first element is itself!

## Solution
Dispatch on the container type. Containers delegate to recursive generators with `yield from`; anything else is yielded as an atom.

```python
def deep_flatten(obj):
    if isinstance(obj, dict):
        for value in obj.values():
            yield from deep_flatten(value)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            yield from deep_flatten(item)
    else:
        yield obj
```

Why not "flatten anything iterable"? `"a"[0] == "a"`, so recursing into strings never terminates. That's the classic trap, and it's why the type check must be explicit. Because it's a generator, `next(deep_flatten(huge))` returns the first atom immediately without walking the whole structure.
