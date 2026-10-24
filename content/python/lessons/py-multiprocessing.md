# Multiprocessing

To use **multiple CPU cores** for pure-Python computation on a standard (GIL) CPython, you run **multiple processes**: each has its own interpreter, its own memory and its own GIL. The `multiprocessing` module makes processes look almost like threads: `Process`, `Pool`, `Queue`, `Lock`. But the separate memory changes everything about how data moves: arguments and results must be **pickled** and copied between processes. This lesson covers process creation, pools, communication, shared memory, start methods, and the pitfalls.

## 1. Processes vs threads

| | Threads | Processes |
|---|---|---|
| Memory | shared | **separate** (data is copied or explicitly shared) |
| GIL | one shared GIL | one GIL **each**: true parallelism |
| Start cost | microseconds | milliseconds (start a new interpreter) |
| Communication | shared objects + locks | pickling over pipes and queues, or shared memory |
| A crash in one | can corrupt shared state | isolated: other processes survive |
| Best for | I/O-bound | **CPU-bound** pure Python |

## 2. Processes and the `__main__` guard

```python
import multiprocessing as mp

def work(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":            # REQUIRED with the spawn/forkserver start methods
    p = mp.Process(target=work, args=(10_000_000,))
    p.start()
    p.join()
    print(p.exitcode)                 # 0 on success
```

> [!DANGER]
> With the **spawn** and **forkserver** start methods, each child process **re-imports your main module**. Without the `if __name__ == "__main__":` guard, every child would start more children: infinite recursion, or a `RuntimeError`. Always put process-launching code under the guard.

## 3. Pools: the usual way

```python
from multiprocessing import Pool

def simulate(seed):                   # must be a top-level function (picklable by name)
    import random
    rng = random.Random(seed)
    return sum(rng.random() for _ in range(1_000_000))

if __name__ == "__main__":
    with Pool(processes=4) as pool:
        results = pool.map(simulate, range(16))              # splits the work, preserves order
        for r in pool.imap_unordered(simulate, range(16)):   # results as they finish
            ...
        r = pool.apply_async(simulate, (42,)).get(timeout=10)
```

`concurrent.futures.ProcessPoolExecutor` offers the same with the `Future` API (next lesson), and is often preferred in new code.

## 4. Pickling: the hidden cost and the big constraint

Everything crossing a process boundary (function arguments, return values, queue items) is **serialised with pickle**, sent through a pipe, and deserialised:

- Functions must be importable by name: **lambdas and nested functions can't be sent** (`PicklingError`). Use top-level functions, or `functools.partial` of top-level functions.
- Large arguments are **copied** each time. Sending a 1 GB array to 8 workers costs time and 8 GB of memory, so pass file paths or use shared memory instead.
- Open files, sockets, locks and database connections can't be pickled: create them **inside** the worker (e.g. with a Pool `initializer`).

> [!KEY]
> Parallelism only pays off when each task does enough work to dwarf the pickling and inter-process overhead. Thousands of tiny tasks run *slower* in a pool than in a loop. Batch them (`chunksize=` in `map`), or make each task larger.

## 5. Communication and shared state

```python
from multiprocessing import Process, Queue, Value, Array, Manager

def producer(q):
    for i in range(5): q.put(i)
    q.put(None)

if __name__ == "__main__":
    q = Queue()                               # pickled messages through a pipe
    Process(target=producer, args=(q,)).start()
    while (item := q.get()) is not None:
        print(item)

    counter = Value("i", 0)                   # a shared C int (in shared memory)
    with counter.get_lock():                  # it still needs locking
        counter.value += 1
```

For large numeric data, `multiprocessing.shared_memory.SharedMemory` gives processes **zero-copy** access to one buffer, typically wrapped in a NumPy array:

```python
from multiprocessing import shared_memory
import numpy as np
shm = shared_memory.SharedMemory(create=True, size=8 * 1_000_000)
arr = np.ndarray((1_000_000,), dtype=np.float64, buffer=shm.buf)    # workers attach by shm.name
...
shm.close(); shm.unlink()                    # unlink exactly once, when everyone is done
```

## 6. Start methods

| Method | How | Default on |
|---|---|---|
| `fork` | copy the parent process (fast; children inherit everything, including threads' locks, which is dangerous) | Linux before 3.14 |
| `spawn` | start a fresh interpreter and import the main module | Windows, macOS |
| `forkserver` | fork from a clean, single-threaded server process | **Linux since 3.14** |

```python
mp.set_start_method("spawn")          # once, at program start; or use mp.get_context("spawn")
```

Forking a process that has running threads can deadlock (a lock held by a thread that doesn't exist in the child), which is why Python moved away from `fork` as the default.

## 7. Exam-ready answers

> [!EXAM]
> **Multiprocessing.** The `multiprocessing` module runs code in separate operating-system processes, each with its own Python interpreter, memory space and GIL, enabling true parallel execution of CPU-bound Python code. It provides `Process` for individual processes and `Pool` (or `concurrent.futures.ProcessPoolExecutor`) for distributing tasks across worker processes. Because memory is not shared, arguments and results are serialised with pickle and copied between processes, which requires picklable, top-level functions and makes small tasks inefficient. Communication uses `Queue` and `Pipe`, while shared state can use `Value`, `Array`, `Manager` objects or `shared_memory` for zero-copy buffers. Child processes may be created by fork, spawn or forkserver; with spawn and forkserver, the main module is re-imported, so process creation must be guarded by `if __name__ == "__main__":`.

## 8. Cheat sheet

| Need | Code |
|---|---|
| parallel map over CPU-bound work | `with Pool() as p: p.map(f, items, chunksize=...)` |
| results as they finish | `p.imap_unordered(f, items)` |
| a safe entry point | `if __name__ == "__main__":` |
| messages between processes | `multiprocessing.Queue` |
| a big shared numeric array | `shared_memory.SharedMemory` + NumPy |
| per-worker setup (DB connections) | `Pool(initializer=init, initargs=...)` |
| choose a start method | `mp.get_context("spawn")` |

> [!INTERVIEW]
> **"You parallelised a function with `multiprocessing.Pool` and it got slower. Why?"** The likely causes: each task is too small, so process startup plus pickling arguments and results dominates (fix by batching with `chunksize` or larger tasks); large data is copied to every worker for every task (fix with shared memory, memory-mapped files, or loading data inside the workers); the work is actually I/O-bound or already parallel inside NumPy, so processes add overhead without benefit; or there are more processes than cores, so they contend. Measure the per-task compute time against the serialisation time. And check that the function isn't a lambda or closure, which would fail to pickle.
