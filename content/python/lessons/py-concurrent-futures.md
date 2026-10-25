# concurrent.futures

`concurrent.futures` is the high-level, unified API for running functions concurrently: **`ThreadPoolExecutor`** for I/O-bound work and **`ProcessPoolExecutor`** for CPU-bound work, with the same interface. It returns **futures**, handles for results that will exist later, which carry return values *and* exceptions back to the caller. For most "run these N things in parallel" jobs, it's the right tool, simpler and safer than raw threads or `multiprocessing.Pool`.

## 1. Executors and futures

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

def fetch(url, timeout=5):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return url, len(r.read())

urls = ["https://example.com", "https://python.org"]
with ThreadPoolExecutor(max_workers=8) as ex:          # the with-block waits for every task at exit
    futures = [ex.submit(fetch, u) for u in urls]      # submit returns a Future immediately
    for fut in as_completed(futures):                  # yields futures as they FINISH
        try:
            url, size = fut.result()                   # re-raises the task's exception here
            print(url, size)
        except Exception as e:
            print("failed:", e)
```

| Future method | Meaning |
|---|---|
| `fut.result(timeout=None)` | wait, then return the value or **raise the task's exception** |
| `fut.exception()` | the exception, or `None` |
| `fut.done()` / `fut.running()` / `fut.cancelled()` | status checks |
| `fut.cancel()` | cancel it if it hasn't started yet |
| `fut.add_done_callback(fn)` | call `fn(fut)` when it finishes (in a worker thread!) |

## 2. `map`, `submit` and `as_completed`

```python
with ThreadPoolExecutor() as ex:
    for size in ex.map(len, ["a", "bb"]):    # results in INPUT order; the first exception is raised when iterating
        ...
```

| Need | Use |
|---|---|
| results in input order, a simple transform | `ex.map(f, items)` |
| handle each result as soon as it's ready | `submit` + `as_completed` |
| wait for all, or for the first, with a timeout | `concurrent.futures.wait(futs, timeout, return_when=FIRST_COMPLETED)` |
| tie results back to their inputs | `{ex.submit(f, x): x for x in items}`, a dict from future to input |

## 3. Threads vs processes: same API

```python
from concurrent.futures import ProcessPoolExecutor

def crunch(n):                        # top-level: must be picklable
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    with ProcessPoolExecutor() as ex:              # defaults to os.cpu_count() workers
        print(list(ex.map(crunch, [10**6] * 8, chunksize=2)))
```

Switching between thread and process pools is one word, so you can benchmark both. All the multiprocessing caveats apply to the process pool: picklable functions and arguments, the `__main__` guard, and per-task overhead.

> [!KEY]
> Choosing `max_workers`: for **I/O-bound** thread pools, use more than the core count (dozens are fine, limited by the remote service's rate limits). For **CPU-bound** process pools, about the number of cores. The default for `ThreadPoolExecutor` is `min(32, os.cpu_count() + 4)`.

## 4. Errors, timeouts and cancellation

```python
from concurrent.futures import TimeoutError as FuturesTimeout

with ThreadPoolExecutor(4) as ex:
    fut = ex.submit(slow_call)
    try:
        value = fut.result(timeout=2.0)     # stop WAITING after 2 s...
    except FuturesTimeout:
        fut.cancel()                        # ...but a task that already started keeps running!
```

> [!WARNING]
> Python threads **can't be killed**: a timeout on `result()` only stops waiting. A running task finishes in the background, and the `with` block still waits for it at exit. For truly abortable work, make tasks check a cancellation `Event`, give the underlying I/O its own timeouts, or use processes (which can be terminated) or asyncio (cooperative cancellation). `ex.shutdown(cancel_futures=True)` cancels the tasks that haven't started.

## 5. Bridging to asyncio

```python
import asyncio
async def main():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, blocking_io)    # run blocking code without freezing the event loop
    result2 = await asyncio.to_thread(blocking_io, arg)       # the simpler 3.9+ form
```

## 6. Exam-ready answers

> [!EXAM]
> **`concurrent.futures`.** The module provides a high-level interface for executing callables asynchronously through executors: `ThreadPoolExecutor` runs tasks in a pool of threads, suited to I/O-bound work, and `ProcessPoolExecutor` runs them in worker processes, suited to CPU-bound work, behind the same interface. `submit` schedules a callable and returns a `Future`, an object representing a pending result whose `result()` method blocks until completion and returns the value or re-raises the exception raised by the task; `map` applies a function to iterables, returning results in input order; and `as_completed` yields futures in completion order. Executors used as context managers wait for outstanding tasks on exit. Timeouts on `result` stop waiting but do not terminate running threads.

## 7. Cheat sheet

| Need | Code |
|---|---|
| parallel I/O | `with ThreadPoolExecutor(16) as ex: list(ex.map(fetch, urls))` |
| parallel CPU | `ProcessPoolExecutor().map(f, items, chunksize=n)` |
| process results as they finish | `for f in as_completed(futs): f.result()` |
| map results back to inputs | `{ex.submit(f, x): x for x in xs}` |
| bounded wait | `fut.result(timeout=s)` |
| blocking call inside asyncio | `await asyncio.to_thread(f, *args)` |

> [!INTERVIEW]
> **"How do you download 10,000 URLs as fast as possible, handling failures?"** It's I/O-bound, so use a `ThreadPoolExecutor` with a bounded number of workers (20–100, respecting the server's rate limits), or asyncio with aiohttp and a semaphore for even higher concurrency. Submit all tasks, keep a dict from future to URL, and iterate `as_completed`, catching each future's exception individually so one failure doesn't stop the batch. Give each request a timeout, retry transient errors with exponential backoff, and stream results to disk instead of keeping everything in memory. Processes would add pickling overhead and no benefit, since the work is waiting, not computing.

## Worked example: threads for I/O, processes for CPU

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time

def io_task(n):                 # waits, like a download
    time.sleep(0.2)
    return n

def cpu_task(n):                # computes, like image processing
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    t = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as ex:
        print(list(ex.map(io_task, range(5))), f"{time.perf_counter() - t:.1f}s")

    with ProcessPoolExecutor() as ex:
        futures = {ex.submit(cpu_task, n): n for n in (10**6, 10**5, 10**4)}
        for f in as_completed(futures):           # in order of completion
            print(futures[f], f.result())
```

Typical output (the `as_completed` order can vary):

```output
[0, 1, 2, 3, 4] 0.2s
10000 333283335000
100000 333328333350000
1000000 333332833333500000
```

- **Five 0.2 s sleeps took 0.2 s in total.** Threads overlap waiting, and the GIL is released during `sleep` and I/O.
- **CPU work needs processes.** Threads would take turns holding the GIL.
- **`map` returns results in input order. `as_completed` yields futures as each one finishes**, so you can show progress early.
- **The `if __name__ == "__main__":` guard is required** for process pools on Windows and macOS, because child processes re-import the module.

## Common mistakes

- **Forgetting `.result()`.** Exceptions raised inside tasks stay hidden in the future until you call it.
- **Sending unpicklable things to processes** (lambdas, open files, locks). Use module-level functions and plain data.
- **Creating a new pool per task.** Create one pool and reuse it.

## Check your understanding

1. Why can threads speed up downloads despite the GIL?
2. What happens to an exception raised inside a submitted task?

<details><summary>Answers</summary>

1. Blocking I/O releases the GIL, so other threads run while one waits for the network.
2. It's stored in the future and re-raised in the caller when `.result()` is called.

</details>
