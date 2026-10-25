# Organizing an OOP Project Across Files

Real projects span dozens of modules and packages. How you split the code decides import complexity, circular-dependency bugs, test speed, and whether the architecture stays visible as the codebase grows. This lesson covers packages and `__init__.py`, absolute vs relative imports, a layered package layout (domain, services, adapters), avoiding circular imports, public APIs with `__all__`, `if TYPE_CHECKING`, entry points, and tooling to enforce boundaries.

## 1. A layered layout

```text
fleetops/                       project root (has pyproject.toml)
  src/fleetops/
    __init__.py                 public API: re-exports and __all__
    domain/                     pure business objects: no I/O, no framework imports
      __init__.py
      robot.py
      mission.py
      errors.py
    services/                   use cases orchestrating the domain through ports
      __init__.py
      dispatcher.py
      ports.py                  Protocols for repositories, clocks, notifiers
    adapters/                   I/O implementations of the ports
      __init__.py
      sqlite_repo.py
      http_notifier.py
    cli.py                      composition root + command line
  tests/
    test_dispatcher.py
```

**Dependency rule**: `adapters → services → domain`. The domain imports nothing from the other layers, and services depend on `ports.py`, not on adapters. This is clean architecture at the package level.

## 2. Imports

```python
# absolute (preferred for clarity)
from fleetops.domain.robot import Robot

# relative (within a package; fine for siblings)
from .errors import RobotUnavailable
from ..domain.mission import Mission
```

- Never rely on the current working directory or on `sys.path` hacks. Install the project in editable mode (`pip install -e .`), so `import fleetops` works everywhere.
- Running a module inside a package: `python -m fleetops.cli`, not `python src/fleetops/cli.py`, because otherwise relative imports fail.

## 3. `__init__.py` as the public face

```python
# fleetops/__init__.py
from .domain.robot import Robot
from .domain.mission import Mission
from .services.dispatcher import Dispatcher

__all__ = ["Robot", "Mission", "Dispatcher"]     # what `from fleetops import *` exports and what docs show
__version__ = "1.4.0"
```

Users write `from fleetops import Robot` without knowing the internal layout, so you can reorganise the internals without breaking them. Keep `__init__` imports light: heavy imports there slow down every `import fleetops`.

## 4. Circular imports

`a.py` imports `b`, `b.py` imports `a`: Python executes `a` partially, imports `b`, and `b` finds `a` half-initialised, giving `ImportError: cannot import name ... (most likely due to a circular import)`.

Fixes, best first:
1. **Fix the design**: move the shared concept to a third module that both import. Cycles usually reveal a misplaced responsibility.
2. **Depend on abstractions**: a `Protocol` in `ports.py` instead of importing the concrete class.
3. **Type-only imports**:

```python
from __future__ import annotations      # annotations are not evaluated at runtime
from typing import TYPE_CHECKING
if TYPE_CHECKING:                        # only type checkers see this import
    from .mission import Mission

class Robot:
    def assign(self, mission: Mission) -> None: ...
```

4. Import inside a function (a local import) as a last resort.

## 5. Entry points and the composition root

```toml
[project.scripts]
fleetops = "fleetops.cli:main"
```

`cli.main()` is the **composition root**: it reads the configuration, builds the adapters (the SQLite repository, the HTTP notifier), injects them into the services, and runs. It's the only module that imports from every layer.

## 6. Enforcing boundaries

- **import-linter** contracts (`domain` must not import `adapters`) run in CI.
- `mypy` or `pyright` check that types match across modules.
- `ruff` flags unused and wildcard imports.
- A test that parses modules with `ast` and asserts on their imports is a lightweight custom contract. This module's problem does exactly that.

> [!EXAM]
> **What causes circular imports in Python, and how do you fix them properly?**
> During an import, Python executes the module top to bottom and registers it in `sys.modules` before it finishes. If module A imports B while B (directly or indirectly) imports names from A, B sees a partially initialised A and fails with an `ImportError` or `AttributeError`. The proper fix is structural: move the shared definitions into a separate lower-level module, or invert the dependency with an abstraction (a `Protocol` in a ports module), so the import graph becomes acyclic and layered. Imports needed only for type hints can go under `if TYPE_CHECKING:` with postponed evaluation of annotations. Function-local imports are a last resort.

## Worked example: from one file to a package

Start with a single `app.py` that has grown to 400 lines. The move happens in four steps:

```text
fleet/
├── pyproject.toml
├── src/fleetops/
│   ├── __init__.py        # public API: from .domain import Robot; from .service import FleetService
│   ├── domain.py          # Robot, Mission (pure logic, no I/O)
│   ├── repository.py      # SqliteRobotRepository (talks to the database)
│   ├── service.py         # FleetService (use cases; depends on a repository *protocol*)
│   └── cli.py             # main(): parses args, builds objects, calls the service
└── tests/
    └── test_service.py    # uses an in-memory fake repository
```

1. **Move pure classes first** (`domain.py`). They import nothing from your project.
2. **Move I/O next** (`repository.py`). It imports `domain`.
3. **Use cases** (`service.py`) import `domain` and a `Protocol` describing the repository, never the concrete SQLite class.
4. **Wiring** (`cli.py`) is the only module that knows about everything. It creates `SqliteRobotRepository(...)` and passes it to `FleetService`.

```python
# cli.py: the composition root
from fleetops.repository import SqliteRobotRepository
from fleetops.service import FleetService

def main() -> None:
    service = FleetService(SqliteRobotRepository("fleet.db"))
    print(service.available_robots())
```

The import arrows all point **inward**: cli → service → domain. That one rule prevents circular imports.

## Common mistakes

- **Circular imports** (`a.py` imports `b`, `b.py` imports `a`). Move the shared piece into a third module, or depend on a `Protocol`.
- **Running a module inside a package as a script** (`python src/fleetops/cli.py`) breaks relative imports. Use `python -m fleetops.cli` or an entry point.
- **Putting heavy code in `__init__.py`.** Keep it to re-exports, so importing the package stays fast and side-effect free.

## Check your understanding

1. Which module should create the database connection, and why?
2. What does `__all__` control?

<details><summary>Answers</summary>

1. The composition root (`cli.py` or a `create_app()`). Everything else receives it, so tests can pass an in-memory version.
2. What `from package import *` exports. It also documents the public API.

</details>
