---
id: py-pipeline
title: Function Pipelines
difficulty: Medium
order: 1
tags: higher-order functions, composition, reduce
---
## Statement
Write `pipeline(*funcs)` that returns a **single function** applying `funcs` **left to right**: `pipeline(f, g, h)(x) == h(g(f(x)))`. With no functions, it returns the identity.

The driver builds pipelines from named steps:

| Step | Meaning |
|---|---|
| `add:k` | x + k |
| `mul:k` | x × k |
| `neg` | −x |
| `sq` | x² |
| `clamp:lo:hi` | keep x within [lo, hi] |

Each query line is `x step step ...`. Print the result.

## Starter
```python
from functools import reduce

def pipeline(*funcs):
    pass
```

## Driver
```python
def make_step(spec):
    name, *args = spec.split(":")
    args = list(map(int, args))
    if name == "add":
        return lambda x: x + args[0]
    if name == "mul":
        return lambda x: x * args[0]
    if name == "neg":
        return lambda x: -x
    if name == "sq":
        return lambda x: x * x
    if name == "clamp":
        return lambda x: max(args[0], min(args[1], x))

t = int(input())
for _ in range(t):
    x, *specs = input().split()
    print(pipeline(*map(make_step, specs))(int(x)))
```

## Tests
=== sample
3
3 add:1 sq
3 sq add:1
5
---
16
10
5
=== hidden
3
-4 neg mul:3 clamp:0:10
7 clamp:0:5 sq neg add:100
2 sq sq sq sq
---
10
75
65536
=== hidden
1
0 add:1 add:2 add:3 mul:2
---
12

## Hints
- `reduce` over the functions: start with `x`, then apply each function to the running value: `reduce(lambda acc, f: f(acc), funcs, x)`.
- Return a function (a closure over `funcs`). Don't compute anything until it's called.

## Solution
The pipeline is a closure over the tuple of functions. When called, it **folds** the value through them with `reduce`, with `x` as the initial accumulator.

```python
from functools import reduce

def pipeline(*funcs):
    def run(x):
        return reduce(lambda acc, f: f(acc), funcs, x)
    return run
```

With no functions, `reduce` returns the initial value unchanged: the identity, as required. The loop version is equally fine. This pattern (a list of transformations applied in order) is exactly what scikit-learn's `Pipeline` and PyTorch's `nn.Sequential` / `torchvision.transforms.Compose` implement.
