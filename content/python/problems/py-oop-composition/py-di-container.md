---
id: py-di-container
title: A Dependency Injection Container with Lifetimes
difficulty: Expert
order: 1
tags: dependency injection, composition, inspect, type hints, lifetimes, context managers, cycle detection
time_limit: 5
---
## Statement
Large applications compose hundreds of objects. Write the small DI container behind them: it **auto-wires constructor dependencies from type hints**, manages **lifetimes**, supports **scopes**, detects **cycles**, and allows **test overrides**.

`class ResolutionError(Exception)`, and `class Container` with:

| Method | Contract |
|---|---|
| `register(iface, provider=None, *, lifetime="transient")` | `provider` is a class or callable (default: `iface` itself). Lifetimes are `"transient"` (a new object per resolve), `"singleton"` (one per root container, created lazily) or `"scoped"` (one per scope). Others raise `ValueError`. Re-registering replaces the old registration (and drops a cached singleton). |
| `register_instance(iface, obj)` | Always returns `obj`. |
| `resolve(iface)` | Calls the provider, passing each parameter whose **type annotation is registered** as a resolved dependency. Parameters with defaults and unregistered annotations keep their default. Anything else raises `ResolutionError("cannot resolve parameter '<name>' of <Provider>")`. An unregistered `iface` raises `ResolutionError("<Name> is not registered")`. |
| cycles | `ResolutionError("dependency cycle: A -> B -> A")`, using `__name__`s in resolution order. |
| `scope()` | A child container sharing the registrations and singletons. **Scoped** services get one instance per scope. Resolving a scoped service from the root raises `ResolutionError("scoped service <Name> requires a scope")`. |
| `override(iface, provider)` | A **context manager** that temporarily replaces the registration (as transient), and restores the original registration **and** its cached singleton afterwards, even on exceptions. |

Use `typing.get_type_hints` on the provider (on `__init__` for classes), so forward references and string annotations resolve. The judge's classes refer to classes defined after them, which Python 3.14's deferred annotations allow.

## Starter
```python
class ResolutionError(Exception):
    pass


class Container:
    def __init__(self):
        self.providers = {}

    def register(self, iface, provider=None, *, lifetime="transient"):
        self.providers[iface] = provider or iface

    def resolve(self, iface):
        return self.providers[iface]()
```

## Driver
```python
import sys
import itertools

def attempt(label, fn):
    try:
        r = fn()
        print(f"{label}: {r}")
    except (ResolutionError, ValueError) as e:
        print(f"{label}: {type(e).__name__}: {e}")

_ids = itertools.count(1)

class Clock:
    def __init__(self): self.id = next(_ids)
    def __repr__(self): return f"Clock#{self.id}"

class Config:
    def __init__(self, name: str = "default"): self.name = name
    def __repr__(self): return f"Config({self.name})"

class Database:
    def __init__(self, config: Config, clock: Clock): self.config, self.clock, self.id = config, clock, next(_ids)
    def __repr__(self): return f"Database#{self.id}({self.config}, {self.clock})"

class Session:
    def __init__(self, db: Database): self.db, self.id = db, next(_ids)
    def __repr__(self): return f"Session#{self.id}"

class Repo:
    def __init__(self, session: Session, retries: int = 3): self.session, self.retries = session, retries
    def __repr__(self): return f"Repo({self.session}, retries={self.retries})"

class NeedsSecret:
    def __init__(self, secret): self.secret = secret

class A:
    def __init__(self, b: B): pass
class B:
    def __init__(self, c: C): pass
class C:
    def __init__(self, a: A): pass

def make_config() -> Config:
    return Config("from-factory")

for cmd in sys.stdin.read().split():
    c = Container()
    if cmd == "wiring":
        c.register(Clock, lifetime="singleton")
        c.register(Config, make_config)
        c.register(Database)
        d1, d2 = c.resolve(Database), c.resolve(Database)
        print(d1, d2, d1 is d2, d1.clock is d2.clock)
        c.register(Database, lifetime="singleton")
        print(c.resolve(Database) is c.resolve(Database))
        attempt("unregistered", lambda: c.resolve(Session))
        c.register(NeedsSecret)
        attempt("unresolvable", lambda: c.resolve(NeedsSecret))
        attempt("bad lifetime", lambda: c.register(Clock, lifetime="forever"))
        c.register_instance(Config, Config("prod"))
        c.register(Database)
        print(c.resolve(Database).config, c.resolve(Config) is c.resolve(Config))
        for k in (A, B, C): c.register(k)
        attempt("cycle", lambda: c.resolve(A))
        attempt("cycle from B", lambda: c.resolve(B))
    elif cmd == "scopes":
        c.register(Clock, lifetime="singleton")
        c.register(Config)
        c.register(Database, lifetime="singleton")
        c.register(Session, lifetime="scoped")
        c.register(Repo)
        attempt("scoped at root", lambda: c.resolve(Session))
        s1, s2 = c.scope(), c.scope()
        r1, r1b, r2 = s1.resolve(Repo), s1.resolve(Repo), s2.resolve(Repo)
        print(r1, r1b, r2)
        print("same session in scope:", r1.session is r1b.session, "different across scopes:", r1.session is not r2.session)
        print("shared singleton db:", r1.session.db is r2.session.db is c.resolve(Database))
        nested = s1.scope()
        print("nested scope has its own session:", nested.resolve(Session) is not s1.resolve(Session))
    elif cmd == "override":
        c.register(Clock, lifetime="singleton")
        c.register(Config)
        c.register(Database)
        real = c.resolve(Clock)
        class FakeClock(Clock):
            def __repr__(self): return "FakeClock"
        with c.override(Clock, FakeClock):
            print("inside:", c.resolve(Database).clock, c.resolve(Clock) is c.resolve(Clock))
        print("after:", c.resolve(Clock) is real, c.resolve(Database).clock)
        try:
            with c.override(Config, lambda: Config("temp")):
                print("temp:", c.resolve(Database).config)
                raise RuntimeError("boom")
        except RuntimeError:
            pass
        print("restored after exception:", c.resolve(Config))
    elif cmd == "load":
        c.register(Clock, lifetime="singleton"); c.register(Config); c.register(Database, lifetime="singleton")
        c.register(Session, lifetime="scoped"); c.register(Repo)
        sessions = set(); dbs = set()
        for i in range(3000):
            s = c.scope()
            for _ in range(5):
                s.resolve(Repo)
            sessions.add(s.resolve(Session).id); dbs.add(s.resolve(Database).id)
        print("distinct sessions", len(sessions), "distinct dbs", len(dbs))
```

## Tests
=== sample
wiring
---
Database#2(Config(from-factory), Clock#1) Database#3(Config(from-factory), Clock#1) False True
True
unregistered: ResolutionError: Session is not registered
unresolvable: ResolutionError: cannot resolve parameter 'secret' of NeedsSecret
bad lifetime: ValueError: unknown lifetime forever
Config(prod) True
cycle: ResolutionError: dependency cycle: A -> B -> C -> A
cycle from B: ResolutionError: dependency cycle: B -> C -> A -> B
=== hidden
scopes
---
scoped at root: ResolutionError: scoped service Session requires a scope
Repo(Session#3, retries=3) Repo(Session#3, retries=3) Repo(Session#4, retries=3)
same session in scope: True different across scopes: True
shared singleton db: True
nested scope has its own session: True
=== hidden
override
---
inside: FakeClock False
after: True Clock#1
temp: Config(temp)
restored after exception: Config(default)
=== hidden
load
---
distinct sessions 3000 distinct dbs 1

## Hints
- Store `self._registry` (iface → `(provider, lifetime)`) and `self._singletons` in a **root** object shared by all scopes. Each scope has its own `self._scoped` cache plus a reference to the root.
- `inspect.signature(provider).parameters` gives the parameters (for a class, the signature excludes `self`). `typing.get_type_hints(provider.__init__ if inspect.isclass(provider) else provider)` maps names to annotation objects.
- Cycle detection: keep a **resolution stack** (a list of ifaces being resolved). Seeing an iface already on the stack is a cycle: print the stack from that iface, plus the iface again.
- `override` is easiest as a `@contextlib.contextmanager`: save the registry entry and the singleton cache entry, replace them, `yield`, and restore both in `finally`.

## Solution
```python
import contextlib
import inspect
import typing

LIFETIMES = ("transient", "singleton", "scoped")


class ResolutionError(Exception):
    pass


class Container:
    def __init__(self, _root: "Container | None" = None):
        self._root = _root or self
        if _root is None:
            self._registry: dict = {}
            self._singletons: dict = {}
        self._scoped: dict = {}
        self._is_scope = _root is not None

    # --- registration (always on the root) ---
    def register(self, iface, provider=None, *, lifetime="transient"):
        if lifetime not in LIFETIMES:
            raise ValueError(f"unknown lifetime {lifetime}")
        root = self._root
        root._registry[iface] = (provider or iface, lifetime)
        root._singletons.pop(iface, None)

    def register_instance(self, iface, obj):
        root = self._root
        root._registry[iface] = (lambda: obj, "singleton")
        root._singletons[iface] = obj

    def scope(self) -> "Container":
        return Container(_root=self._root)

    @contextlib.contextmanager
    def override(self, iface, provider):
        root = self._root
        saved_reg = root._registry.get(iface)
        had_single = iface in root._singletons
        saved_single = root._singletons.pop(iface, None)
        root._registry[iface] = (provider, "transient")
        try:
            yield self
        finally:
            if saved_reg is None:
                root._registry.pop(iface, None)
            else:
                root._registry[iface] = saved_reg
            root._singletons.pop(iface, None)
            if had_single:
                root._singletons[iface] = saved_single

    # --- resolution ---
    def resolve(self, iface):
        return self._resolve(iface, [])

    def _resolve(self, iface, stack):
        root = self._root
        if iface not in root._registry:
            raise ResolutionError(f"{getattr(iface, '__name__', iface)} is not registered")
        if iface in stack:
            chain = stack[stack.index(iface):] + [iface]
            raise ResolutionError("dependency cycle: " + " -> ".join(t.__name__ for t in chain))
        provider, lifetime = root._registry[iface]
        if lifetime == "singleton" and iface in root._singletons:
            return root._singletons[iface]
        if lifetime == "scoped":
            if not self._is_scope:
                raise ResolutionError(f"scoped service {iface.__name__} requires a scope")
            if iface in self._scoped:
                return self._scoped[iface]
        stack.append(iface)
        try:
            obj = provider(**self._arguments(provider, stack))
        finally:
            stack.pop()
        if lifetime == "singleton":
            root._singletons[iface] = obj
        elif lifetime == "scoped":
            self._scoped[iface] = obj
        return obj

    def _arguments(self, provider, stack) -> dict:
        target = provider.__init__ if inspect.isclass(provider) else provider
        try:
            hints = typing.get_type_hints(target)
        except Exception:
            hints = {}
        kwargs = {}
        for name, param in inspect.signature(provider).parameters.items():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            ann = hints.get(name)
            if ann is not None and ann in self._root._registry:
                kwargs[name] = self._resolve(ann, stack)
            elif param.default is param.empty:
                pname = getattr(provider, "__name__", repr(provider))
                raise ResolutionError(f"cannot resolve parameter '{name}' of {pname}")
        return kwargs
```

- **Composition, automated**: classes declare what they need in their constructor signatures (`Database(config: Config, clock: Clock)`), and the container builds the whole graph. No class constructs its own collaborators, so any of them can be swapped.
- **Lifetimes are a container concern**, not a class concern: the same `Database` class can be transient in tests and a singleton in production, which is just a registration change.
- **Scopes** model per-request or per-mission state. Each scope gets its own `Session` while sharing singletons like the database pool. This is exactly how web frameworks scope database sessions.
- **Cycle detection** with an explicit resolution stack gives a readable `A -> B -> C -> A` instead of a `RecursionError`, and it points straight at the design problem.
- **Overrides as a context manager** let tests replace a dependency (a fake clock) and guarantee restoration, including the cached singleton, even when the test raises.
