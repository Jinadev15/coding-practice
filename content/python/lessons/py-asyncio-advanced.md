# asyncio Advanced

Real async systems need more than `gather`: **structured concurrency** (`TaskGroup`), **producer–consumer queues**, **rate limiting** with semaphores, **timeouts**, **cancellation** that cleans up properly, and async iterators and context managers. These are the tools for writing reliable network services and robot communication layers that handle failures gracefully instead of leaking tasks or hanging forever.

## 1. TaskGroup: structured concurrency (3.11+)

```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:          # all tasks are finished when the block exits
        t1 = tg.create_task(fetch("a"))
        t2 = tg.create_task(fetch("b"))
    print(t1.result(), t2.result())
```

If any task raises, the group **cancels all the other tasks** and re-raises the errors together as an `ExceptionGroup`, handled with `except*`:

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(might_fail(1))
        tg.create_task(might_fail(2))
except* ConnectionError as eg:
    for e in eg.exceptions:
        print("connection failed:", e)
```

> [!KEY]
> Prefer `TaskGroup` over bare `create_task` + `gather`. A bare task that nobody awaits can fail silently ("Task exception was never retrieved"), and tasks can outlive the code that created them, which leaks resources. `TaskGroup` guarantees that no child task outlives the block. That's **structured concurrency**, the same principle as Trio's nurseries and Kotlin's coroutine scopes.

## 2. Timeouts

```python
async def main():
    try:
        async with asyncio.timeout(2.0):             # 3.11+: cancels the block's work after 2 s
            data = await read_from_robot()
    except TimeoutError:
        print("robot not responding")

    result = await asyncio.wait_for(fetch(), timeout=1.0)   # older equivalent for a single awaitable
```

## 3. Cancellation

`task.cancel()` raises `asyncio.CancelledError` **inside** the task at its current `await`. The task can clean up in `finally`, but it **must not swallow** the cancellation:

```python
async def stream_telemetry(conn):
    try:
        while True:
            await conn.send(await read_sample())
    except asyncio.CancelledError:
        await conn.send_goodbye()                     # brief cleanup
        raise                                         # ALWAYS re-raise
    finally:
        await conn.close()

task = asyncio.create_task(stream_telemetry(conn))
...
task.cancel()
try:
    await task
except asyncio.CancelledError:
    pass                                              # expected
```

> [!DANGER]
> `except Exception:` doesn't catch `CancelledError` (it's a `BaseException` since 3.8), but `except BaseException:` or a bare `except:` that doesn't re-raise **breaks cancellation**: timeouts and TaskGroups stop working and shutdown hangs. Use `asyncio.shield(aw)` to protect a critical operation from cancellation.

## 4. Queues and producer–consumer pipelines

```python
async def producer(q: asyncio.Queue):
    for i in range(10):
        await q.put(i)                     # waits if the queue is full (backpressure)

async def consumer(name, q: asyncio.Queue):
    while True:
        item = await q.get()
        try:
            await process(item)
        finally:
            q.task_done()

async def main():
    q = asyncio.Queue(maxsize=5)
    async with asyncio.TaskGroup() as tg:
        workers = [tg.create_task(consumer(f"w{i}", q)) for i in range(3)]
        await producer(q)
        await q.join()                     # every item has been processed
        for w in workers:
            w.cancel()                     # stop the infinite consumers
```

(Python 3.13 added `Queue.shutdown()` for a cleaner way to stop consumers.)

## 5. Limiting concurrency: Semaphore

```python
sem = asyncio.Semaphore(10)                # at most 10 requests in flight

async def polite_fetch(session, url):
    async with sem:                        # waits while 10 are already active
        return await session.get(url)

async with asyncio.TaskGroup() as tg:
    for url in urls:                       # 10,000 tasks, but only 10 concurrent requests
        tg.create_task(polite_fetch(session, url))
```

Other primitives: `asyncio.Lock` (rarely needed, except to protect state across an `await`), `asyncio.Event`, `asyncio.Condition`, `asyncio.Barrier`. They're **not thread-safe**: they're for coroutines in one loop.

## 6. Async iterators, generators and context managers

```python
async def ticks(period, n):                # async generator
    for i in range(n):
        await asyncio.sleep(period)
        yield i

async for t in ticks(0.1, 5):              # async for
    print(t)

from contextlib import asynccontextmanager
@asynccontextmanager
async def connected(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()

async with connected("robot.local", 9000) as (r, w):   # async with
    ...
```

The protocols behind them are `__aiter__`/`__anext__` and `__aenter__`/`__aexit__`.

## 7. Exam-ready answers

> [!EXAM]
> **Advanced asyncio.** `asyncio.TaskGroup` implements structured concurrency: tasks created within an `async with` block are awaited when it exits, and if one fails the others are cancelled and the errors are raised as an `ExceptionGroup`, handled with `except*`. `asyncio.timeout` and `wait_for` bound waiting time by cancelling the awaited work. Cancellation raises `CancelledError` at the task's current await point; tasks should release resources in `finally` blocks and re-raise the exception. `asyncio.Queue` supports producer–consumer pipelines with backpressure through bounded queues, `task_done` and `join`, and `asyncio.Semaphore` limits the number of concurrent operations. Asynchronous iterators (`async for`, async generators) and asynchronous context managers (`async with`, `asynccontextmanager`) extend the iteration and resource-management protocols to coroutines.

## 8. Cheat sheet

| Need | Code |
|---|---|
| run tasks safely together | `async with asyncio.TaskGroup() as tg: tg.create_task(...)` |
| handle grouped errors | `except* ValueError as eg:` |
| deadline | `async with asyncio.timeout(s):` |
| cancel and clean up | `task.cancel()`; in the task: `finally:` + re-raise `CancelledError` |
| pipeline | `asyncio.Queue(maxsize=n)` + `task_done()` / `join()` |
| limit concurrency | `async with asyncio.Semaphore(n):` |
| stream values | an async generator + `async for` |
| protect critical work | `await asyncio.shield(aw)` |

> [!INTERVIEW]
> **"Why is swallowing `CancelledError` dangerous?"** Cancellation is how asyncio implements timeouts, TaskGroup failure handling and graceful shutdown: the runtime raises `CancelledError` inside the task and expects it to propagate. A task that catches it and continues makes `asyncio.timeout` never fire, keeps a TaskGroup waiting forever after a sibling failed, and hangs shutdown. Correct code catches it only to clean up (or uses `finally`) and then re-raises. Similarly, broad `except BaseException` blocks must re-raise. Only use `asyncio.shield` deliberately, for short critical sections.

## Worked example: a bounded producer–consumer pipeline

```python
import asyncio

async def producer(q: asyncio.Queue, n: int):
    for i in range(n):
        await q.put(i)                  # waits when the queue is full (backpressure)
    for _ in range(2):
        await q.put(None)               # one stop signal per worker

async def worker(name: str, q: asyncio.Queue, out: list):
    while (item := await q.get()) is not None:
        await asyncio.sleep(0.01)       # pretend to process
        out.append(item * item)

async def main():
    q, out = asyncio.Queue(maxsize=3), []
    async with asyncio.TaskGroup() as tg:          # waits for all; cancels siblings on error
        tg.create_task(producer(q, 6))
        tg.create_task(worker("w1", q, out))
        tg.create_task(worker("w2", q, out))
    print(sorted(out))

asyncio.run(main())
```

```output
[0, 1, 4, 9, 16, 25]
```

The pieces:

- **`Queue(maxsize=3)`:** the producer can't race ahead of the workers, which bounds memory use.
- **Sentinel `None`s:** a clean way to tell each worker to stop.
- **`TaskGroup`:** if any task raises, the others are cancelled and the error propagates. You never leak orphaned tasks.

For a time limit on the whole thing, wrap it: `async with asyncio.timeout(5): ...`.

## Common mistakes

- **Swallowing `CancelledError`** (`except Exception` is fine, but a bare `except:` or `except BaseException` catches cancellation). If you catch it to clean up, re-raise it.
- **`create_task` without keeping a reference.** The task can be garbage-collected mid-flight. `TaskGroup` keeps the references for you.
- **Unbounded `gather` over 10,000 URLs.** Limit concurrency with `asyncio.Semaphore(20)`.

## Check your understanding

1. What does `TaskGroup` do when one child task fails?
2. How do you stop the workers if the producer crashes?

<details><summary>Answers</summary>

1. It cancels the remaining children, waits for them, then raises an `ExceptionGroup` containing the failure(s).
2. Run them all in the same `TaskGroup`. The producer's exception cancels the workers automatically.

</details>
