---
id: py-tag-builder
title: HTML Tag Builder
difficulty: Medium
order: 2
tags: **kwargs, positional-only, keyword-only
---
## Statement
Write `tag(name, content="", /, *, self_closing=False, **attrs)` that returns an HTML string:

- Attributes come from `attrs`, written as `key="value"` in **the order they were passed**.
- `class` is a Python keyword, so callers write `class_`. Strip **one trailing underscore** from every attribute name. In the same way, an underscore inside a name becomes a dash: `data_id` → `data-id`.
- An attribute whose value is `True` is written as a bare name (`disabled`). `False` or `None` attributes are omitted.
- `self_closing=True` → `<name attrs />` (content ignored). Otherwise `<name attrs>content</name>`.
- No attributes → no extra space: `<p>hi</p>`.

`name` and `content` are positional-only; the flags are keyword-only.

The driver reads calls in a small format: `name | content | key=value key=value ...`, where values `True`, `False` and `None` are converted.

## Starter
```python
def tag(name, content="", /, *, self_closing=False, **attrs):
    pass
```

## Driver
```python
import inspect
ps = inspect.signature(tag).parameters
assert ps["name"].kind == inspect.Parameter.POSITIONAL_ONLY
assert ps["self_closing"].kind == inspect.Parameter.KEYWORD_ONLY
conv = {"True": True, "False": False, "None": None}
t = int(input())
for _ in range(t):
    name, content, opts = [p.strip() for p in input().split("|")]
    kwargs = {}
    for item in opts.split():
        k, v = item.split("=", 1)
        kwargs[k] = conv.get(v, v)
    print(tag(name, content, **kwargs))
```

## Tests
=== sample
3
p | hello |
a | docs | href=/docs class_=link
img | | src=a.png alt=logo self_closing=True
---
<p>hello</p>
<a href="/docs" class="link">docs</a>
<img src="a.png" alt="logo" />
=== hidden
3
button | Go | disabled=True type=submit hidden=False
div | x | data_id=7 aria_label=box id=main
input | | required=True self_closing=True value=None
---
<button disabled type="submit">Go</button>
<div data-id="7" aria-label="box" id="main">x</div>
<input required />
=== hidden
2
br | ignored | self_closing=True
span | |
---
<br />
<span></span>

## Hints
- `key.removesuffix("_").replace("_", "-")` converts the name.
- Build a list of attribute strings, then `" ".join(...)`. Prepend a space only if the list is non-empty.
- `**attrs` preserves the order of the keyword arguments (guaranteed since Python 3.6).

## Solution
The signature uses all three special markers: `/` keeps `name` and `content` positional, `*` makes `self_closing` keyword-only, and `**attrs` collects everything else in call order.

```python
def tag(name, content="", /, *, self_closing=False, **attrs):
    parts = []
    for key, value in attrs.items():
        if value is False or value is None:
            continue
        attr = key.removesuffix("_").replace("_", "-")
        parts.append(attr if value is True else f'{attr}="{value}"')
    attr_text = (" " + " ".join(parts)) if parts else ""
    if self_closing:
        return f"<{name}{attr_text} />"
    return f"<{name}{attr_text}>{content}</{name}>"
```

Why positional-only? A caller could legitimately want an HTML attribute literally called `name` (`<input name="email">`). If `name` were a normal parameter, `tag("input", name="email")` would raise "multiple values for argument 'name'". With `/`, the keyword `name=` lands in `**attrs`. This exact clash is why PEP 570 added positional-only parameters.
