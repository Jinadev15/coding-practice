# Structural Pattern Matching

Python 3.10 added `match`/`case` (PEP 634). It isn't just a switch statement: it **destructures** data by its shape, matching sequences, mappings and objects, binding variables, and testing guards in one readable construct. It shines for parsing commands, handling JSON or messages, walking ASTs, implementing interpreters and state machines. Its semantics have sharp edges, the capture-pattern trap above all, that this lesson makes explicit.

## 1. The basic form

```python
def handle(cmd: str) -> str:
    match cmd.split():
        case ["quit"]:
            return "bye"
        case ["go", direction]:                       # captures the second word into `direction`
            return f"going {direction}"
        case ["go", *_]:
            return "go where?"
        case ["pick", "up", item] | ["take", item]:   # alternatives
            return f"took {item}"
        case _:                                       # wildcard: matches anything, binds nothing
            return "unknown command"
```

Cases are tried **top to bottom**, and the first match wins. Without a matching case and no `case _`, nothing happens (no error).

## 2. Pattern kinds

| Pattern | Example | Matches |
|---|---|---|
| literal | `case 0:`, `case "go":`, `case None:` | equal values (`None`, `True` and `False` by identity) |
| capture | `case x:` | **anything**, binding it to `x` |
| wildcard | `case _:` | anything, binding nothing |
| value | `case Color.RED:`, `case math.pi:` | equal to a **dotted name** (constant) |
| sequence | `case [a, b]:`, `case [first, *rest]:`, `case (x, y):` | sequences of matching length (not `str` or `bytes`!) |
| mapping | `case {"type": "move", "dx": dx}:` | dicts containing those keys (extra keys allowed) |
| class | `case Point(x=0, y=y):`, `case int(n):` | `isinstance` plus attribute patterns |
| OR | `case 1 \| 2 \| 3:` | any alternative |
| AS | `case [Point() as p, *_]:` | binds the matched subpattern |
| guard | `case int(n) if n < 0:` | the pattern plus a condition |

```python
def describe(x):
    match x:
        case 0:
            return "zero"
        case int(n) if n < 0:
            return "negative int"
        case [a, b]:
            return f"pair {a}, {b}"
        case [first, *rest]:
            return f"starts with {first}, {len(rest)} more"
        case {"type": "move", "dx": dx}:
            return f"move by {dx}"
        case str() | bytes():
            return "text"
        case _:
            return "other"

describe([1, 2])                                  # 'pair 1, 2'
describe((1, 2))                                  # 'pair 1, 2': tuples match sequence patterns too
describe({"type": "move", "dx": 3, "extra": 1})   # 'move by 3': extra keys are ignored
describe("hi")                                    # 'text': strings DON'T match [a, b]
```

## 3. The capture-pattern trap

> [!DANGER]
> A **bare name** in a pattern is a *capture*, never a comparison:
> ```python
> RED = "red"
> match color:
>     case RED:            # captures ANY value into a new variable RED: always matches!
>         print("red")
>     case "blue":         # SyntaxError in fact: "name capture 'RED' makes remaining patterns unreachable"
>         ...
> ```
> To compare against a constant, use a **dotted name** (`case Color.RED:`, `case config.LIMIT:`) or a literal. That's one reason enums and pattern matching go together so well.

## 4. Class patterns and `__match_args__`

```python
from dataclasses import dataclass

@dataclass
class Move:
    dx: float
    dy: float

@dataclass
class Rotate:
    angle: float

def apply(cmd):
    match cmd:
        case Move(dx=0, dy=0):
            return "no-op"
        case Move(dx, dy):                   # positional: uses Move.__match_args__ == ('dx', 'dy')
            return f"move {dx},{dy}"
        case Rotate(angle=a) if abs(a) > 180:
            return "normalise first"
        case Rotate(a):
            return f"rotate {a}"
```

Dataclasses and namedtuples set `__match_args__` automatically. For a plain class, define `__match_args__ = ("x", "y")` to allow positional sub-patterns. Built-ins like `int(n)` and `str(s)` match by type and bind the whole value.

## 5. Real use: an expression evaluator

```python
def evaluate(node):
    match node:
        case int() | float():
            return node
        case ("+", left, right):
            return evaluate(left) + evaluate(right)
        case ("*", left, right):
            return evaluate(left) * evaluate(right)
        case ("neg", operand):
            return -evaluate(operand)
        case _:
            raise ValueError(f"bad node {node!r}")

evaluate(("+", 2, ("*", 3, ("neg", 4))))   # -10
```

Compare that with the equivalent `isinstance`/`len`/indexing chain. Pattern matching expresses **the shape of the data** directly, which is why it suits compilers, message handlers and JSON processing.

## 6. Exam-ready answers

> [!EXAM]
> **Structural pattern matching.** The `match` statement compares a subject value against a sequence of `case` patterns, executing the block of the first pattern that matches. Patterns can be literals, capture patterns that bind names, the wildcard `_`, value patterns using dotted names, sequence patterns (including starred subpatterns, but excluding strings), mapping patterns that require the given keys and ignore others, class patterns that check the type and match attributes by keyword or positionally via `__match_args__`, OR patterns, and AS patterns, optionally followed by a guard `if condition`. Unlike a switch statement, it destructures data and binds variables; bare names always capture rather than compare, so constants must be referenced with dotted names.

## 7. Cheat sheet

| Need | Pattern |
|---|---|
| a fixed command word | `case ["stop"]:` |
| a command with arguments | `case ["go", dist]:` |
| variable length | `case [head, *tail]:` |
| a JSON message type | `case {"type": "move", **rest}:` |
| a dataclass by fields | `case Move(dx=0):` |
| a type check + binding | `case int(n):` |
| a condition | `case x if x > 0:` |
| compare to a constant | `case Color.RED:` (dotted!) |
| a default | `case _:` |

> [!INTERVIEW]
> **"What's printed?** `x = 5; match 3: case x: print(x)`" It prints **3**. `case x` is a capture pattern: it matches anything and *rebinds* `x` to the subject. It doesn't compare with the existing `x`. To compare against a value, use a literal or a dotted name such as `case Config.LIMIT:`, or a guard: `case n if n == x:`. This is the most common pattern-matching bug.
