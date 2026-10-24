---
id: py-plugin-framework
title: A Plugin Framework with Class Creation Hooks
difficulty: Hard
order: 1
tags: __init_subclass__, metaclasses, class decorators, registries
---
## Statement
Build the class machinery of a sensor-plugin framework. You'll use **three** class-creation tools for the jobs each does best:

1. **`class Plugin`** with `__init_subclass__(cls, /, kind=None, **kwargs)`:
   - every subclass must pass `kind="..."` (e.g. `class Lidar(Plugin, kind="lidar")`), else `TypeError("Lidar: missing kind")`;
   - duplicate kinds raise `ValueError("duplicate kind 'lidar'")`;
   - a subclass must define a method `read` in its own body, else `TypeError("Lidar: must define read()")`;
   - registered classes are stored in `Plugin.registry` (`dict` kind → class), and each subclass gets a class attribute `kind`.
   - `Plugin.create(kind, *args, **kwargs)` (a classmethod) instantiates the registered class, or raises `KeyError(kind)`.
2. **`def validated(*required)`**: a class decorator factory. It checks at decoration time that the class has every listed attribute name (`hasattr`), else `TypeError("Gps: missing rate_hz")`, and adds a method `describe(self)` returning `"<ClassName kind=K>"`.
3. **`class Frozen(type)`**: a metaclass. Classes created with it raise `AttributeError("cannot modify class Config")` on any attempt to set or delete a **class** attribute after creation (instances are unaffected).

## Starter
```python
class Plugin:
    registry = {}

def validated(*required):
    def deco(cls):
        return cls
    return deco

class Frozen(type):
    pass
```

## Driver
```python
import re
import sys

def define(src):
    exec(src, env)
    return "defined"

SHOW_MESSAGES = True
ASSIGN = re.compile(r"^\s*([A-Za-z_][\w.]*)\s*=(?!=)\s*(.+)$")
env = dict(globals())
for line in sys.stdin.read().splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    m = ASSIGN.match(line)
    try:
        if m and "." not in m.group(1):
            env[m.group(1)] = eval(m.group(2), env)
        elif m:
            exec(line.strip(), env)
        else:
            print(line.strip(), "->", repr(eval(line, env)))
    except Exception as e:
        print(line.strip(), "->", type(e).__name__ + (f": {e}" if SHOW_MESSAGES else ""))
```

## Tests
=== sample
define("class Lidar(Plugin, kind='lidar'):\n    def __init__(self, rng=10): self.rng = rng\n    def read(self): return self.rng")
define("class Imu(Plugin, kind='imu'):\n    def read(self): return 9.81")
sorted(Plugin.registry)
Lidar.kind
Plugin.create("lidar", rng=25).read()
Plugin.create("sonar")
define("class Bad(Plugin):\n    def read(self): pass")
define("class Dup(Plugin, kind='imu'):\n    def read(self): pass")
define("class NoRead(Plugin, kind='x'):\n    pass")
"x" in Plugin.registry
define("@validated('rate_hz')\nclass Gps(Plugin, kind='gps'):\n    rate_hz = 10\n    def read(self): return (0, 0)")
Gps().describe()
define("@validated('rate_hz', 'port')\nclass Cam(Plugin, kind='cam'):\n    rate_hz = 30\n    def read(self): return b''")
define("class Config(metaclass=Frozen):\n    MAX = 3")
Config.MAX
Config.MAX = 4
c = Config()
c.x = 1
c.x
---
define("class Lidar(Plugin, kind='lidar'):\n    def __init__(self, rng=10): self.rng = rng\n    def read(self): return self.rng") -> 'defined'
define("class Imu(Plugin, kind='imu'):\n    def read(self): return 9.81") -> 'defined'
sorted(Plugin.registry) -> ['imu', 'lidar']
Lidar.kind -> 'lidar'
Plugin.create("lidar", rng=25).read() -> 25
Plugin.create("sonar") -> KeyError: 'sonar'
define("class Bad(Plugin):\n    def read(self): pass") -> TypeError: Bad: missing kind
define("class Dup(Plugin, kind='imu'):\n    def read(self): pass") -> ValueError: duplicate kind 'imu'
define("class NoRead(Plugin, kind='x'):\n    pass") -> TypeError: NoRead: must define read()
"x" in Plugin.registry -> False
define("@validated('rate_hz')\nclass Gps(Plugin, kind='gps'):\n    rate_hz = 10\n    def read(self): return (0, 0)") -> 'defined'
Gps().describe() -> '<Gps kind=gps>'
define("@validated('rate_hz', 'port')\nclass Cam(Plugin, kind='cam'):\n    rate_hz = 30\n    def read(self): return b''") -> TypeError: Cam: missing port
define("class Config(metaclass=Frozen):\n    MAX = 3") -> 'defined'
Config.MAX -> 3
Config.MAX = 4 -> AttributeError: cannot modify class Config
c.x -> 1
=== hidden
define("class Base2(Plugin, kind='base2'):\n    def read(self): return 'base'")
define("class Child(Base2, kind='child'):\n    pass")
Plugin.create("child").read()
Child.kind
Base2.kind
isinstance(Plugin.create("child"), Base2)
define("class Child2(Base2):\n    def read(self): pass")
define("class F2(metaclass=Frozen):\n    a = 1")
F2.b = 2
F2.a
define("del F2.a")
define("@validated()\nclass Plain(Plugin, kind='plain'):\n    def read(self): return 1")
Plain().describe()
len(Plugin.registry)
---
define("class Base2(Plugin, kind='base2'):\n    def read(self): return 'base'") -> 'defined'
define("class Child(Base2, kind='child'):\n    pass") -> TypeError: Child: must define read()
Plugin.create("child").read() -> KeyError: 'child'
Child.kind -> NameError: name 'Child' is not defined
Base2.kind -> 'base2'
isinstance(Plugin.create("child"), Base2) -> KeyError: 'child'
define("class Child2(Base2):\n    def read(self): pass") -> TypeError: Child2: missing kind
define("class F2(metaclass=Frozen):\n    a = 1") -> 'defined'
F2.b = 2 -> AttributeError: cannot modify class F2
F2.a -> 1
define("del F2.a") -> AttributeError: cannot modify class F2
define("@validated()\nclass Plain(Plugin, kind='plain'):\n    def read(self): return 1") -> 'defined'
Plain().describe() -> '<Plain kind=plain>'
len(Plugin.registry) -> 2

## Hints
- In `__init_subclass__`, `"read" in cls.__dict__` checks for a method defined in the class **body** itself (inherited ones don't count). Call `super().__init_subclass__(**kwargs)` first, for cooperative inheritance.
- Raise the validation errors **before** registering, so a failed class isn't left in the registry.
- `validated` returns a decorator. Inside it, attach the method with `cls.describe = describe` and `return cls`.
- In the metaclass, override `__setattr__(cls, name, value)` and `__delattr__(cls, name)`. These run when a **class** attribute is set (`Config.MAX = 4`), because the class is an instance of the metaclass. Instance attributes go through the class's own `__setattr__`, which you're not changing.
- Careful: does `type.__new__` itself set attributes through `__setattr__`? (It doesn't, so blocking in `__setattr__` doesn't break class creation.)

## Solution
```python
class Plugin:
    registry = {}

    def __init_subclass__(cls, /, kind=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if kind is None:
            raise TypeError(f"{cls.__name__}: missing kind")
        if kind in Plugin.registry:
            raise ValueError(f"duplicate kind {kind!r}")
        if "read" not in cls.__dict__:
            raise TypeError(f"{cls.__name__}: must define read()")
        cls.kind = kind
        Plugin.registry[kind] = cls

    @classmethod
    def create(cls, kind, *args, **kwargs):
        try:
            klass = Plugin.registry[kind]
        except KeyError:
            raise KeyError(kind) from None
        return klass(*args, **kwargs)


def validated(*required):
    def deco(cls):
        for name in required:
            if not hasattr(cls, name):
                raise TypeError(f"{cls.__name__}: missing {name}")
        def describe(self):
            return f"<{type(self).__name__} kind={type(self).kind}>"
        cls.describe = describe
        return cls
    return deco


class Frozen(type):
    def __setattr__(cls, name, value):
        raise AttributeError(f"cannot modify class {cls.__name__}")

    def __delattr__(cls, name):
        raise AttributeError(f"cannot modify class {cls.__name__}")
```

**Choosing the right hook:**
- **`__init_subclass__`** runs for every subclass of `Plugin`, which is right for a registry and for rules every plugin must follow. Class keyword arguments (`kind="lidar"`) flow straight into it. A failed check raises *while the `class` statement executes*, so a broken plugin fails at import time, not in production.
- **A class decorator** applies to the one class it decorates, which is right for opt-in features (extra validation, generated methods). Note that `@validated` runs *after* `__init_subclass__`, because the class must exist before it can be decorated.
- **A metaclass** is needed only when you must change how the **class object itself** behaves. Setting `Config.MAX` calls `type(Config).__setattr__`, so only a metaclass can intercept it. That's the same mechanism that makes `Enum` members read-only.

