---
id: py-signature-binder
title: Argument Binding Simulator
difficulty: Hard
order: 3
tags: parameters, binding rules, interpreters
---
## Statement
Simulate exactly how Python binds call arguments to parameters, without using `inspect` or `exec`. This is the algorithm the interpreter runs on every call.

**Signature line**: space-separated tokens, in valid Python order:

- `a`: a parameter without a default
- `a=5`: a parameter with an integer default
- `/`: everything before it is positional-only
- `*`: a bare star; everything after it is keyword-only
- `*args`: variable positional (everything after it is keyword-only)
- `**kw`: variable keyword (always last)

**Call line**: space-separated arguments. An integer `7` is positional; `name=7` is keyword. (Positionals always come before keywords.)

Output: if the binding succeeds, print each parameter **in signature order** as `name=value`, separated by spaces. `*args` prints as a Python tuple (`args=(1, 2)` or `args=()`) and `**kw` as a dict (`kw={'x': 1}` or `kw={}`). If binding fails, print `TypeError`.

The rules (Python's):

1. Positional arguments fill the positional parameters (positional-only, then normal) left to right. Extras go to `*args`; without `*args`, that's an error.
2. Keyword arguments bind to the normal or keyword-only parameter with that name. A keyword naming a **positional-only** parameter goes to `**kw` if it exists, or is an error otherwise. A keyword for an already-filled parameter is an error. An unknown name goes to `**kw`, or is an error.
3. Unfilled parameters take their default; a missing one without a default is an error.

## Starter
```python
def bind(signature_tokens, call_tokens):
    # return the output line as a string
    pass
```

## Driver
```python
t = int(input())
for _ in range(t):
    sig = input().split()
    call = input().split()
    print(bind(sig, call))
```

## Tests
=== sample
4
a b=2
1
a b=2
1 b=3
a b=2
1 2 3
a / b
a=1 b=2
---
a=1 b=2
a=1 b=3
TypeError
TypeError
=== hidden
5
a b=2 *args c d=4 **kw
1 5 6 7 c=3 e=9
a *args
1
a * b
1 2
a * b
1 b=2
a / b **kw
1 a=5 b=2
---
a=1 b=5 args=(6, 7) c=3 d=4 kw={'e': 9}
a=1 args=()
TypeError
a=1 b=2
a=1 b=2 kw={'a': 5}
=== hidden
5
a b
1 a=2
a b
b=2 a=1
x=1 y=2 / z=0
3 z=4
**kw

x=1
2
---
TypeError
a=1 b=2
x=3 y=2 z=4
kw={}
x=2
=== hidden
4
a * b=1 c
5 c=7
p q=0 *rest **opts
1 2 3 4 q=9
*args
1 2 3
a=1 b
3
---
a=5 b=1 c=7
TypeError
args=(1, 2, 3)
TypeError

## Hints
- First parse the signature into lists: `posonly`, `normal`, `varargs` (a name or None), `kwonly` and `varkw`, plus a `defaults` dict.
- Note the signature `a=1 b` in the last test: Python itself would reject that definition, but here the rule is simply "missing argument → TypeError". Treat the definition as given.
- Python's real order for "got multiple values" vs "unexpected keyword" doesn't matter here, since every failure prints `TypeError`.

## Solution
Parse the signature into its five regions, then apply the three binding phases in order: positional, keyword, defaults. Every rule violation raises, and is reported as `TypeError`.

```python
def bind(signature_tokens, call_tokens):
    posonly, normal, kwonly = [], [], []
    varargs = varkw = None
    defaults = {}
    region = "normal"          # becomes "kwonly" after * or *args
    for tok in signature_tokens:
        if tok == "/":
            posonly, normal = normal, []
        elif tok == "*":
            region = "kwonly"
        elif tok.startswith("**"):
            varkw = tok[2:]
        elif tok.startswith("*"):
            varargs = tok[1:]
            region = "kwonly"
        else:
            name, eq, val = tok.partition("=")
            if eq:
                defaults[name] = int(val)
            (kwonly if region == "kwonly" else normal).append(name)

    positional_params = posonly + normal
    pos_args = [int(t) for t in call_tokens if "=" not in t]
    kw_args = [t.split("=") for t in call_tokens if "=" in t]

    bound, extra_pos, extra_kw = {}, [], {}
    try:
        for i, value in enumerate(pos_args):
            if i < len(positional_params):
                bound[positional_params[i]] = value
            elif varargs is not None:
                extra_pos.append(value)
            else:
                raise TypeError
        for name, raw in kw_args:
            value = int(raw)
            if name in normal or name in kwonly:
                if name in bound:
                    raise TypeError
                bound[name] = value
            elif varkw is not None and name not in extra_kw:
                extra_kw[name] = value      # includes positional-only names
            else:
                raise TypeError
        for name in positional_params + kwonly:
            if name not in bound:
                if name not in defaults:
                    raise TypeError
                bound[name] = defaults[name]
    except TypeError:
        return "TypeError"

    out = [f"{n}={bound[n]}" for n in positional_params]
    if varargs is not None:
        out.append(f"{varargs}={tuple(extra_pos)}")
    out += [f"{n}={bound[n]}" for n in kwonly]
    if varkw is not None:
        out.append(f"{varkw}={extra_kw}")
    return " ".join(out)
```

This is essentially CPython's argument parsing in `Python/ceval.c` (`_PyEval_MakeFrame` / `initialize_locals`), minus the specific error messages. Note the case `a / b **kw` with the call `1 a=5 b=2`: the keyword `a=5` doesn't clash with the positional-only `a`. It just lands in `**kw`. That's legal Python and the exact use case for positional-only parameters. After this exercise, no signature should confuse you.
