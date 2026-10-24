---
id: py-transaction
title: All-or-Nothing Transaction
difficulty: Medium
order: 2
tags: context managers, rollback, exception suppression
---
## Statement
Write a context manager class `Transaction(store)` for a dict-based key/value store:

- On enter: take a **snapshot** of the store and return the store.
- On normal exit: keep the changes (commit).
- On exception: **restore** the store to the snapshot (rollback), mutating the same dict object since other code holds references to it. Then:
  - suppress `ValueError` (it's a "validation failed" signal, so rollback is enough)
  - let every other exception propagate after rolling back

Values are plain ints or strings, so a shallow snapshot is enough.

## Starter
```python
class Transaction:
    def __init__(self, store):
        pass
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc, tb):
        pass
```

## Driver
```python
store = {}
for block in input().split("|"):
    ops = block.split()
    try:
        with Transaction(store) as s:
            for op in ops:
                if op == "BAD":
                    raise ValueError("validation failed")
                if op == "CRASH":
                    raise KeyError("boom")
                k, v = op.split("=")
                s[k] = int(v)
        print("commit", dict(sorted(store.items())))
    except KeyError:
        print("crash", dict(sorted(store.items())))
    else:
        pass
```

## Tests
=== sample
a=1 b=2|a=5 BAD|c=3
---
commit {'a': 1, 'b': 2}
commit {'a': 1, 'b': 2}
commit {'a': 1, 'b': 2, 'c': 3}
=== hidden
x=1|x=2 y=3 CRASH|z=9 BAD
---
commit {'x': 1}
crash {'x': 1}
commit {'x': 1}
=== hidden
k=7|k=8
---
commit {'k': 7}
commit {'k': 8}

## Hints
- Snapshot with `dict(store)` in `__enter__`.
- Roll back **in place**: `self.store.clear(); self.store.update(self.snapshot)`. Rebinding `self.store = snapshot` wouldn't change the caller's dict.
- Return `exc_type is ValueError` from `__exit__` (that's `True` only for `ValueError`). But on success, `exc_type is None`, so make sure you return a falsy value then. (Returning `False` is harmless when there's no exception.)

## Solution
Snapshot on enter. On exit with an exception, restore in place, then decide whether to suppress based on the exception type.

```python
class Transaction:
    def __init__(self, store):
        self.store = store
        self.snapshot = None

    def __enter__(self):
        self.snapshot = dict(self.store)
        return self.store

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            return False                      # commit: keep the changes
        self.store.clear()
        self.store.update(self.snapshot)      # rollback, in place
        return issubclass(exc_type, ValueError)
```

On a `ValueError` the with-block "succeeds" from the caller's view (the print says `commit`), but the store is unchanged. That's the rollback. `KeyError` propagates after rolling back, which the driver reports as `crash`. Databases (`sqlite3` connections used as context managers) behave the same way: commit on success, roll back on exception.
