---
id: py-plugin-registry
title: A Validating Plugin Registry
difficulty: Medium
order: 1
tags: factory, registry, class decorators, __init_subclass__, inspect.signature, validation
time_limit: 5
---
## Statement
Build the plugin system a robot stack uses to create controllers, planners and sensors from configuration files.

**`class PluginError(Exception)`**

**`class Registry`**
- `Registry(kind)`: `kind` is a label used in messages (`"controller"`, …).
- `register(...)` works in **both** forms:
  - `@reg.register` registers under `cls.__name__.lower()`.
  - `@reg.register("name")` registers under the given name.

  It returns the class unchanged. A duplicate name raises `PluginError("duplicate <kind> '<name>'")`.
- `create(name, **cfg)` builds an instance after **validating `cfg` against the class's `__init__` signature**:
  - unknown name: `PluginError("unknown <kind> '<name>'")`
  - an option that isn't a parameter: `PluginError("unexpected option '<opt>' for <name>")`, checked in sorted option order
  - a missing required parameter: `PluginError("missing option '<param>' for <name>")`, checked in signature order
  - a parameter annotated with `int`, `float`, `str` or `bool` whose value has the wrong type: `PluginError("option '<param>' for <name> must be <type>")`. An `int` is accepted where `float` is expected, but a `bool` is never accepted as an `int` or `float`. Other annotations aren't checked.

  Unexpected options are checked first, then missing ones, then types.
- `names()` returns a sorted list. Also support `name in reg` and `len(reg)`.

**Automatic registration**: a module-level `CONTROLLERS = Registry("controller")` and a base class `Controller`. Subclasses defined as `class PID(Controller, key="pid")` are registered automatically under `key`, using `__init_subclass__`. Subclasses without `key` (abstract intermediates) aren't registered.

## Starter
```python
class PluginError(Exception):
    pass


class Registry:
    def __init__(self, kind):
        self.kind = kind
        self.items = {}

    def register(self, name):
        def deco(cls):
            self.items[name] = cls
            return cls
        return deco

    def create(self, name, **cfg):
        return self.items[name](**cfg)

    def names(self):
        return list(self.items)


CONTROLLERS = Registry("controller")


class Controller:
    pass
```

## Driver
```python
import sys

def attempt(label, fn):
    try:
        r = fn()
        print(f"{label}: {r!r}")
    except PluginError as e:
        print(f"{label}: PluginError: {e}")

class Lidar:
    def __init__(self, port: str, rate_hz: float = 10.0, enabled: bool = True):
        self.port, self.rate_hz, self.enabled = port, rate_hz, enabled
    def __repr__(self): return f"Lidar({self.port}, {self.rate_hz}, {self.enabled})"

class Sonar:
    def __init__(self, pin: int, samples: int = 3, label="sonar"):
        self.pin, self.samples, self.label = pin, samples, label
    def __repr__(self): return f"Sonar({self.pin}, {self.samples}, {self.label!r})"

for cmd in sys.stdin.read().split():
    if cmd == "register":
        S = Registry("sensor")
        print(S.register(Lidar) is Lidar, S.register("ultra")(Sonar) is Sonar)
        attempt("names", S.names)
        attempt("dup", lambda: S.register(Lidar))
        attempt("dup named", lambda: S.register("ultra")(Lidar))
        print("contains", "lidar" in S, "sonar" in S, len(S))
        @S.register("cam")
        class Camera:
            def __init__(self, fps: int = 30): self.fps = fps
            def __repr__(self): return f"Camera({self.fps})"
        attempt("names", S.names)
        attempt("cam", lambda: S.create("cam"))
    elif cmd == "create":
        S = Registry("sensor"); S.register(Lidar); S.register("ultra")(Sonar)
        attempt("lidar", lambda: S.create("lidar", port="/dev/ttyUSB0", rate_hz=20))
        attempt("lidar int->float", lambda: S.create("lidar", port="p", rate_hz=5))
        attempt("unknown", lambda: S.create("radar"))
        attempt("unexpected", lambda: S.create("lidar", port="p", zeta=1, alpha=2))
        attempt("missing", lambda: S.create("lidar", rate_hz=1.0))
        attempt("unexpected before missing", lambda: S.create("lidar", baud=9600))
        attempt("bad str", lambda: S.create("lidar", port=5))
        attempt("bad float", lambda: S.create("lidar", port="p", rate_hz="fast"))
        attempt("bool as float", lambda: S.create("lidar", port="p", rate_hz=True))
        attempt("bad bool", lambda: S.create("lidar", port="p", enabled=1))
        attempt("bool as int", lambda: S.create("ultra", pin=True))
        attempt("float as int", lambda: S.create("ultra", pin=3.0))
        attempt("unannotated", lambda: S.create("ultra", pin=4, label=99))
    elif cmd == "auto":
        class PID(Controller, key="pid"):
            def __init__(self, kp: float, ki: float = 0.0, kd: float = 0.0): self.g = (kp, ki, kd)
            def __repr__(self): return f"PID{self.g}"
        class Tracker(Controller):
            pass
        class PurePursuit(Tracker, key="pure_pursuit"):
            def __init__(self, lookahead: float): self.l = lookahead
            def __repr__(self): return f"PurePursuit({self.l})"
        attempt("controllers", CONTROLLERS.names)
        attempt("pid", lambda: CONTROLLERS.create("pid", kp=1.2, kd=0.1))
        attempt("pp", lambda: CONTROLLERS.create("pure_pursuit", lookahead=0.8))
        attempt("pp missing", lambda: CONTROLLERS.create("pure_pursuit"))
        attempt("tracker", lambda: CONTROLLERS.create("tracker"))
        try:
            class PID2(Controller, key="pid"):
                pass
        except PluginError as e:
            print("dup subclass:", e)
        print("isinstance", isinstance(CONTROLLERS.create("pid", kp=1), Controller))
```

## Tests
=== sample
register
---
True True
names: ['lidar', 'ultra']
dup: PluginError: duplicate sensor 'lidar'
dup named: PluginError: duplicate sensor 'ultra'
contains True False 2
names: ['cam', 'lidar', 'ultra']
cam: Camera(30)
=== hidden
create
---
lidar: Lidar(/dev/ttyUSB0, 20, True)
lidar int->float: Lidar(p, 5, True)
unknown: PluginError: unknown sensor 'radar'
unexpected: PluginError: unexpected option 'alpha' for lidar
missing: PluginError: missing option 'port' for lidar
unexpected before missing: PluginError: unexpected option 'baud' for lidar
bad str: PluginError: option 'port' for lidar must be str
bad float: PluginError: option 'rate_hz' for lidar must be float
bool as float: PluginError: option 'rate_hz' for lidar must be float
bad bool: PluginError: option 'enabled' for lidar must be bool
bool as int: PluginError: option 'pin' for ultra must be int
float as int: PluginError: option 'pin' for ultra must be int
unannotated: Sonar(4, 3, 99)
=== hidden
auto
---
controllers: ['pid', 'pure_pursuit']
pid: PID(1.2, 0.0, 0.1)
pp: PurePursuit(0.8)
pp missing: PluginError: missing option 'lookahead' for pure_pursuit
tracker: PluginError: unknown controller 'tracker'
dup subclass: duplicate controller 'pid'
isinstance True

## Hints
- Support both decorator forms by checking `isinstance(name, type)`: if the argument is a class, register it directly, otherwise return a decorator.
- `inspect.signature(cls.__init__).parameters` includes `self`, so skip it. A parameter with `p.default is inspect.Parameter.empty` is required.
- With a plain annotation (not from `__future__ import annotations`), `p.annotation` is the class object itself.
- `def __init_subclass__(cls, /, key=None, **kw): super().__init_subclass__(**kw); ...`

## Solution
```python
import inspect


class PluginError(Exception):
    pass


_CHECKED = {int, float, str, bool}


def _type_ok(value, expected):
    if expected is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected is int:
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, expected)


class Registry:
    def __init__(self, kind):
        self.kind = kind
        self._items = {}

    def _add(self, name, cls):
        if name in self._items:
            raise PluginError(f"duplicate {self.kind} '{name}'")
        self._items[name] = cls
        return cls

    def register(self, name=None):
        if isinstance(name, type):                    # used bare: @reg.register
            return self._add(name.__name__.lower(), name)
        def deco(cls):
            return self._add(name or cls.__name__.lower(), cls)
        return deco

    def create(self, name, **cfg):
        cls = self._items.get(name)
        if cls is None:
            raise PluginError(f"unknown {self.kind} '{name}'")
        params = [p for p in inspect.signature(cls.__init__).parameters.values()
                  if p.name != "self" and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
        names = {p.name for p in params}
        for opt in sorted(cfg):
            if opt not in names:
                raise PluginError(f"unexpected option '{opt}' for {name}")
        for p in params:
            if p.default is inspect.Parameter.empty and p.name not in cfg:
                raise PluginError(f"missing option '{p.name}' for {name}")
        for p in params:
            if p.name in cfg and p.annotation in _CHECKED and not _type_ok(cfg[p.name], p.annotation):
                raise PluginError(f"option '{p.name}' for {name} must be {p.annotation.__name__}")
        return cls(**cfg)

    def names(self):
        return sorted(self._items)

    def __contains__(self, name):
        return name in self._items

    def __len__(self):
        return len(self._items)


CONTROLLERS = Registry("controller")


class Controller:
    def __init_subclass__(cls, /, key=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if key is not None:
            CONTROLLERS._add(key, cls)
```

- **Classes as values**: the registry is a dict from names to classes, so no factory hierarchy is needed. New plugins are added by registration, never by editing the factory.
- **Dual-form decorator**: `@reg.register` passes the class itself, while `@reg.register("x")` passes a name and expects a decorator back. One `isinstance(name, type)` check supports both.
- **Validate configuration at the boundary**: `inspect.signature` turns each plugin's own `__init__` into its config schema. A typo in a YAML file then gives a precise message ("unexpected option 'baud' for lidar") instead of a `TypeError` deep in a constructor, or a silently wrong default.
- **`bool` is a subclass of `int`**, so `True` would pass naive `isinstance(v, int)` checks. Real config loaders must special-case it.
- **`__init_subclass__`** registers subclasses the moment they're defined, with no decorator to forget. Intermediate abstract classes opt out by not passing `key`.
