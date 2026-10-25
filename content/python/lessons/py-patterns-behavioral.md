# Behavioral Patterns in Python

Behavioral patterns organise **communication and responsibility** between objects. In Python, first-class functions turn Strategy and Command into plain callables, generators are built-in Iterators, `weakref` makes Observer memory-safe, `functools.singledispatch` and `match` replace much of Visitor, and dictionaries make table-driven State machines trivial. This lesson covers Observer and event buses, Command with undo, Strategy, State, Iterator, Template Method, Chain of Responsibility and Visitor, with the Python-specific pitfalls: memory leaks via strong references, and exceptions inside callbacks.

## 1. Observer, and the leak it causes

```python
class Battery:
    def __init__(self): self._observers = []
    def subscribe(self, fn): self._observers.append(fn)
    def set_level(self, level):
        for fn in list(self._observers):        # copy: observers may unsubscribe during the loop
            fn(level)
```

> [!DANGER]
> `battery.subscribe(widget.on_level)` stores a **bound method**, which holds a strong reference to `widget`. The widget can never be garbage collected while the battery lives: a classic leak in GUIs and long-running robots. Use **weak references**: `weakref.WeakMethod` for bound methods and `weakref.ref` for objects, or return an unsubscribe handle and make the subscriber call it.

```python
import inspect, weakref

class Signal:
    def __init__(self): self._slots = []
    def connect(self, fn):
        ref = weakref.WeakMethod(fn) if inspect.ismethod(fn) else (lambda f=fn: f)   # Python-level bound methods only
        self._slots.append(ref)
        return lambda: self._slots.remove(ref) if ref in self._slots else None    # unsubscribe handle
    def emit(self, *args):
        for ref in list(self._slots):
            fn = ref()
            if fn is None:                       # subscriber was garbage-collected
                self._slots.remove(ref)
            else:
                fn(*args)
```

**Event buses** decouple publishers from subscribers by topic, much like ROS topics in-process. Production concerns:
- **Isolate exceptions**: one failing handler must not stop the others. Catch, log and continue.
- **Ordering**: priorities, or insertion order.
- **Re-entrancy**: publishing from inside a handler.
- **Threads**: use a lock around the subscription list, but don't hold it while calling handlers.

## 2. Command, with undo

Commands are objects (or closures) representing actions: queue them, log them, replay them, undo them.

```python
from dataclasses import dataclass, field

@dataclass
class SetSpeed:
    robot: "Robot"; value: float
    _prev: float = field(default=0.0, init=False)
    def execute(self): self._prev, self.robot.speed = self.robot.speed, self.value
    def undo(self): self.robot.speed = self._prev

class History:
    def __init__(self): self.done, self.undone = [], []
    def run(self, cmd): cmd.execute(); self.done.append(cmd); self.undone.clear()
    def undo(self):
        if self.done: cmd = self.done.pop(); cmd.undo(); self.undone.append(cmd)
    def redo(self):
        if self.undone: cmd = self.undone.pop(); cmd.execute(); self.done.append(cmd)
```

For simple deferred actions, a callable *is* a command: `queue.append(functools.partial(arm.move, joint=2, angle=0.5))`.

## 3. Strategy: pass a function

```python
def manhattan(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
def euclid(a, b): return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def astar(grid, start, goal, heuristic=manhattan): ...
path = astar(grid, s, g, heuristic=euclid)
sorted(robots, key=lambda r: r.battery)          # `key` is a strategy
```

Use a class (or a `Protocol`) only when the strategy has configuration or state, like a `PIDController(kp, ki, kd)` versus an `MPCController(horizon)`.

## 4. State machines

A **transition table** in a dict is explicit, data-driven and easy to test exhaustively:

```python
from enum import Enum, auto

class S(Enum): IDLE = auto(); MOVING = auto(); FAULT = auto()
class E(Enum): GO = auto(); ARRIVED = auto(); ERROR = auto(); RESET = auto()

TRANSITIONS = {
    (S.IDLE, E.GO): S.MOVING,
    (S.MOVING, E.ARRIVED): S.IDLE,
    (S.MOVING, E.ERROR): S.FAULT,
    (S.IDLE, E.ERROR): S.FAULT,
    (S.FAULT, E.RESET): S.IDLE,
}

def step(state: S, event: E) -> S:
    return TRANSITIONS.get((state, event), state)          # unknown pairs: stay
```

For behaviour that differs per state, use the State pattern with one class per state, or `match state:` in a handler. Libraries such as `transitions` add entry and exit callbacks, guards and diagrams.

## 5. Iterator: generators

The Iterator pattern is built into the language: anything with `__iter__`/`__next__` works in `for`, comprehensions, `zip` and `itertools`. Generators produce iterators with no boilerplate, lazily and in constant memory:

```python
def scan_windows(readings, size):
    from collections import deque
    win = deque(maxlen=size)
    for r in readings:
        win.append(r)
        if len(win) == size:
            yield sum(win) / size

for avg in scan_windows(sensor_stream(), 5): ...      # works on infinite streams
```

## 6. Template Method, Chain of Responsibility, Visitor

- **Template Method**: a base class method calls overridable hooks (`unittest.TestCase.setUp`/`tearDown`, and `run()` in `threading.Thread`). Keep invariant steps in the base class.
- **Chain of Responsibility**: a list of handler callables, each returning a result or `None` to pass the request on. Safety checks on a velocity command (e-stop, then geofence, then speed limit) and WSGI/ASGI middleware are chains.

```python
def estop(cmd, ctx):   return {"v": 0.0, "w": 0.0} if ctx["estop"] else None
def geofence(cmd, ctx): return {"v": 0.0, "w": cmd["w"]} if ctx["outside"] else None

def filter_cmd(cmd, ctx, chain=(estop, geofence)):
    for handler in chain:
        if (out := handler(cmd, ctx)) is not None:
            return out
    return cmd
```

- **Visitor**: operations over a family of types. `functools.singledispatch` dispatches on the first argument's type, and structural pattern matching (`match node: case Add(l, r): ...`) handles tree-shaped data such as ASTs and messages.

```python
from functools import singledispatch

@singledispatch
def describe(shape) -> str: raise TypeError(type(shape))
@describe.register
def _(c: Circle) -> str: return f"circle r={c.r}"
@describe.register
def _(r: Rect) -> str: return f"rect {r.w}x{r.h}"
```

> [!EXAM]
> **How would you implement a memory-safe, robust Observer in Python?**
> Store subscriptions as weak references (`weakref.WeakMethod` for bound methods, `weakref.ref` for objects) so subscribers can be garbage-collected, prune dead references during notification, and also return an explicit unsubscribe handle. Iterate over a copy of the subscriber list so handlers may subscribe or unsubscribe during notification. Wrap each handler call in try/except so one failing observer doesn't prevent the others from running (log or collect the errors). With threads, protect the list with a lock but invoke handlers outside it.
