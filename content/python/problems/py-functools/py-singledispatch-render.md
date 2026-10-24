---
id: py-singledispatch-render
title: Type-Dispatched Renderer
difficulty: Medium
order: 3
tags: functools.singledispatch, recursion, serialization
---
## Statement
Write `render(value)` with `functools.singledispatch` that turns Python data into **JSON text**:

| Type | Output |
|---|---|
| `None` | `null` |
| `bool` | `true` / `false` (**must not** render as a number, even though `bool` subclasses `int`) |
| `int`, `float` | the `repr` (e.g. `3`, `2.5`) |
| `str` | double-quoted, with `\` → `\\` and `"` → `\"` escaped |
| `list`, `tuple` | `[a,b,c]` (no spaces), elements rendered recursively |
| `dict` | `{"k":v,...}`, keys rendered as strings (via `str(key)` then quoted), values recursive |
| anything else | `"<unsupported>"` (the fallback) |

Register one implementation per type. **No** `isinstance` chains in the main function.

## Starter
```python
from functools import singledispatch

@singledispatch
def render(value):
    pass
```

## Driver
```python
import ast
for _ in range(int(input())):
    line = input()
    value = {1, 2} if line == "SET" else ast.literal_eval(line)
    print(render(value))
```

## Tests
=== sample
4
[1, 2.5, None, True]
{"a": [1, {"b": False}]}
'say "hi"'
SET
---
[1,2.5,null,true]
{"a":[1,{"b":false}]}
"say \"hi\""
"<unsupported>"
=== hidden
3
(1, (2, 3))
{1: 'x', 'y': None}
'back\\slash'
---
[1,[2,3]]
{"1":"x","y":null}
"back\\slash"
=== hidden
2
[]
{}
---
[]
{}

## Hints
- `@render.register(type(None))` registers the `None` case.
- Register `bool` explicitly. Because the most specific class wins, it takes priority over `int` for `True`/`False`.
- One function can be registered for both `list` and `tuple` by stacking `@render.register(list)` and `@render.register(tuple)`.

## Solution
Each type gets its own small function, and recursion happens naturally by calling `render` on the elements, which dispatches again on *their* types.

```python
from functools import singledispatch

@singledispatch
def render(value):
    return '"<unsupported>"'

@render.register(type(None))
def _(value):
    return "null"

@render.register(bool)
def _(value):
    return "true" if value else "false"

@render.register(int)
@render.register(float)
def _(value):
    return repr(value)

@render.register(str)
def _(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'

@render.register(list)
@render.register(tuple)
def _(value):
    return "[" + ",".join(render(v) for v in value) + "]"

@render.register(dict)
def _(value):
    return "{" + ",".join(render(str(k)) + ":" + render(v) for k, v in value.items()) + "}"
```

Escape the **backslash first**, or the backslashes added for quotes would themselves get doubled. `singledispatch` resolves `True` to the `bool` handler because dispatch uses the MRO: `bool → int → object`, and the most specific registered class wins. The real `json.dumps` also handles Unicode escapes, `NaN` and indentation. This version is the core of it.
