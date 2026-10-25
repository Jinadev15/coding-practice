# Study guide: Special quiz 1

This quiz brings together the **Foundations** modules. There are no new language features here. The challenge is **combining** what you know into small programs that are correct on every input. Read each section before you start the matching problem.

## 1. Expression Evaluator — tokenising and recursive descent

An arithmetic expression like `2 + 3 * (4 - 1)` has **structure**: `*` binds tighter than `+`, and parentheses override both. You handle that in two steps.

**Step 1: the tokenizer.** Turn the string into a list of meaningful pieces:

```python
def tokenize(s):
    tokens, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            tokens.append(int(s[i:j])); i = j
        elif c in "+-*/()":
            tokens.append(c); i += 1
        else:
            raise ValueError(f"bad character {c!r}")
    return tokens
```

**Step 2: a grammar, with one function per rule.** Each level of precedence becomes one function, and lower-precedence functions call higher-precedence ones:

```text
expr   := term   (('+' | '-') term)*
term   := factor (('*' | '/') factor)*
factor := NUMBER | '(' expr ')' | '-' factor
```

```python
class Parser:
    def __init__(self, tokens): self.t, self.i = tokens, 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else None
    def eat(self):  tok = self.peek(); self.i += 1; return tok

    def expr(self):
        v = self.term()
        while self.peek() in ("+", "-"):
            v = v + self.term() if self.eat() == "+" else v - self.term()
        return v
    def term(self):
        v = self.factor()
        while self.peek() in ("*", "/"):
            op = self.eat(); r = self.factor()
            v = v * r if op == "*" else v / r
        return v
    def factor(self):
        tok = self.eat()
        if isinstance(tok, int): return tok
        if tok == "-": return -self.factor()
        if tok == "(":
            v = self.expr()
            if self.eat() != ")": raise ValueError("expected )")
            return v
        raise ValueError(f"unexpected {tok!r}")
```

Trace `2 + 3 * 4`: `expr` calls `term`, which reads `2`. `expr` sees `+` and calls `term` again. That `term` reads `3`, sees `*`, reads `4`, and returns `12`. The result is `2 + 12 = 14`. Precedence comes **from the call structure**, not from special cases.

> [!DANGER] Common mistakes
> - Using `if` instead of `while` in `expr`/`term`. With `if`, `1 - 2 - 3` breaks.
> - Forgetting to check that all tokens were consumed. `2 3` must be an error.
> - Integer vs true division: read the statement to see which one it wants.

## 2. Warehouse Inventory Engine — dicts as a database

Treat the problem as **commands that change state**. Keep the state in a `dict` (`sku -> quantity`) and write one small function per command. Validate the **whole** command before you change anything. If a removal would make stock negative, reject it and leave the state untouched.

```python
stock: dict[str, int] = {}
def remove(sku, qty):
    have = stock.get(sku, 0)
    if qty <= 0 or qty > have:
        return "ERROR"
    stock[sku] = have - qty
    if stock[sku] == 0:
        del stock[sku]
    return "OK"
```

For reports, `sorted(items, key=lambda kv: (-kv[1], kv[0]))` sorts by quantity descending, then by name ascending. Negating the number is the standard trick for a mixed sort direction.

## 3. Robot Map Islands — BFS on a grid

A grid of `#` (land) and `.` (water) is a **graph**: each cell is a node, and edges go to its 4 neighbours. An "island" is a **connected component**. To find them all, scan every cell. Each time you find unvisited land, start a breadth-first search from it and mark everything it reaches.

```python
from collections import deque
def islands(grid):
    R, C = len(grid), len(grid[0])
    seen, sizes = set(), []
    for r in range(R):
        for c in range(C):
            if grid[r][c] != "#" or (r, c) in seen: continue
            q, size = deque([(r, c)]), 0
            seen.add((r, c))
            while q:
                y, x = q.popleft(); size += 1
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < R and 0 <= nx < C and grid[ny][nx] == "#" and (ny, nx) not in seen:
                        seen.add((ny, nx)); q.append((ny, nx))
            sizes.append(size)
    return sizes
```

Mark a cell as seen **when you enqueue it**, not when you pop it. Otherwise the same cell can be queued many times.

## 4. User Session Analyzer — generators and grouping

Logs can be huge, so read them **lazily** with a generator. Each stage below is a generator that pulls from the previous one:

```python
def parse(lines):
    for n, line in enumerate(lines, 1):
        try:
            ts, user, action = line.split()
            yield int(ts), user, action
        except ValueError:
            yield from ()          # skip malformed lines (or record them)
```

A "session" is a run of events with gaps of no more than `T` seconds. Group the events per user, sort each user's events by time, then split wherever the gap is larger than `T`. `itertools.groupby` works only on input that is **already sorted** by the key. That is the most common bug here.

## Checklist before you submit

- Did you handle the empty input and single-element cases?
- Are ties broken the way the statement says?
- Does your output match the format exactly, including spaces and decimals?
