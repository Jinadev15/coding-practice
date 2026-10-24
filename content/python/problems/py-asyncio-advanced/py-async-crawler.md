---
id: py-async-crawler
title: Rate-Limited Async Crawler with TaskGroup
difficulty: Hard
order: 1
tags: asyncio, TaskGroup, Semaphore, Queue, timeout, cancellation
time_limit: 3
---
## Statement
Crawl a website graph asynchronously. The driver provides a fake async HTTP client:

```python
async def get(url: str) -> list[str]
    # awaits a latency, then returns the links on that page; may raise ConnectionError,
    # or hang forever on "trap" pages (it never returns)
```

Implement:

```python
async def crawl(start: str, max_concurrency: int, page_timeout: float, max_pages: int) -> dict
```

- **Breadth-first discovery**: starting from `start`, visit every reachable URL **once**.
- At most **`max_concurrency`** `get` calls may be in flight at any moment (use `asyncio.Semaphore`). The driver measures the peak.
- Each `get` gets at most **`page_timeout`** seconds (`asyncio.timeout`). Timed-out pages count as `"timeout"`, and pages raising `ConnectionError` count as `"error"`. Neither stops the crawl.
- Stop discovering new pages once `max_pages` pages have been **scheduled** (the start page counts). Pages are scheduled in **discovery order**.
- Use structured concurrency (a `TaskGroup`, or worker tasks plus an `asyncio.Queue`). When `crawl` returns, **no task may still be running**: the driver checks.
- Return `{"ok": sorted URLs fetched successfully, "timeout": sorted, "error": sorted, "links": total number of links seen on ok pages}`.

## Starter
```python
import asyncio

async def crawl(start, max_concurrency, page_timeout, max_pages):
    seen, ok, timeout, error, links = {start}, [], [], [], 0
    frontier = [start]
    while frontier:
        url = frontier.pop(0)
        try:
            out = await get(url)
        except ConnectionError:
            error.append(url)
            continue
        ok.append(url)
        links += len(out)
        for u in out:
            if u not in seen and len(seen) < max_pages:
                seen.add(u)
                frontier.append(u)
    return {"ok": sorted(ok), "timeout": sorted(timeout), "error": sorted(error), "links": links}
```

## Driver
```python
import sys
import zlib

GRAPH = {}
inflight = 0
peak = 0

async def get(url):
    global inflight, peak
    inflight += 1
    peak = max(peak, inflight)
    try:
        if url.startswith("trap"):
            await asyncio.Event().wait()                     # hangs forever
        await asyncio.sleep(0.05 + (zlib.crc32(url.encode()) % 50) / 1000)
        if url.startswith("down"):
            raise ConnectionError(url)
        return GRAPH.get(url, [])
    finally:
        inflight -= 1

async def main():
    data = sys.stdin.read().split("\n")
    conc, timeout, max_pages = data[0].split()
    for line in data[1:]:
        if ":" in line:
            page, _, links = line.partition(":")
            GRAPH[page.strip()] = links.split()
    res = await crawl("home", int(conc), float(timeout), int(max_pages))
    pending = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    print("ok:", " ".join(res["ok"]))
    print("timeout:", " ".join(res["timeout"]) or "-")
    print("error:", " ".join(res["error"]) or "-")
    print("links:", res["links"])
    print("peak concurrency within limit:", peak <= int(conc), "| tasks left running:", len(pending))

asyncio.run(main())
```

## Tests
=== sample
2 0.3 100
home: a b c
a: b d trap1
b: down1 home
c: e
d:
e: a
---
ok: a b c d e home
timeout: trap1
error: down1
links: 10
peak concurrency within limit: True | tasks left running: 0
=== hidden
1 0.2 3
home: p1 p2 p3 p4
p1: p5
---
ok: home p1 p2
timeout: -
error: -
links: 5
peak concurrency within limit: True | tasks left running: 0
=== hidden
5 0.25 1000
home: p32 p41 p25 p30 p24 p105
p1: 
p2: p60 trap2
p3: p78 p30 p18 p71
p4: p84 p64 home p108 p35
p5: 
p6: down1 p63 p22 p101 p104 p24
p7: p106 p49 p23 p42
p8: p15 p11
p9: p99 p33 p68 p60
p10: p28
p11: p9
p12: 
p13: p25 p89 p71 p115 p56 p76
p14: p68 p9 p12 p107 p102
p15: p94 p27 p95 p42 p108
p16: 
p17: 
p18: p59 p105 p10 p117
p19: p100 p68 down3 p13 p34 p56
p20: p99 p117 p70 down3 p15
p21: p119 p67
p22: 
p23: p107 p98 down3 p51 p96 p74
p24: p67 p31 p28 p73
p25: p51 p94 p17
p26: p102 p49 p1 trap2 p4 p6
p27: p80 p5 p95
p28: p97 p55
p29: 
p30: p64 p115
p31: p88 p62 p7 p83
p32: p105 p88 p83
p33: 
p34: p38
p35: p11 p2 p107 p62
p36: p118 p104
p37: p53 p73 home p7 p101 p61
p38: p97
p39: p96 p115 p3 p89 p1 p30
p40: 
p41: p118 p59 p14 p110 p49
p42: p13 p113 p109
p43: p30
p44: p26 p98
p45: p11 p20 p21 p19 p3 p6
p46: p29 p85 p64 p98 p48 down2
p47: p91 p93 p76 p53
p48: p64 p34 p76
p49: p113 p13 p60 p79 p53 p37
p50: p35 p36 p58 p111
p51: p2
p52: p62 p9 p4 p2
p53: p18 p1 p11 p84 p112
p54: 
p55: p26 p86 p10 p99
p56: p21 p13 trap2
p57: p49 p36 p58 p112 p62
p58: p88 p104 p98 p51
p59: p112
p60: p83 p54 p108 p32 p36 p110
p61: p11 p109 p67 p41 p40 p116
p62: p99
p63: down3 p47
p64: p92 p87 p61 p95 p98 p99
p65: p67 p50 p64 p68 p51
p66: p32 p48 down3 p95 p112 p71
p67: p90 p84 p39 p118 p10 p35
p68: p13 p18 p17 p46 p118
p69: p89 p6 p27 p116 p105 p75
p70: p71 p77 p86 p74
p71: 
p72: p2 p109 p92 down2
p73: p15 p81 p88 p105
p74: p34
p75: p20 p83 down3 p43 p7 p86
p76: p93 p79 p74 down1
p77: p11 p112 p89
p78: p10 p46
p79: p82 p79 p94
p80: home p6 p57 p95 p107 p19
p81: p51 p100 p68
p82: p104 p9 p55 home p14 p4
p83: p99 p16 p4
p84: p81 p103 p33 p104 p76 p119
p85: p81 p116
p86: p22 p69 p114 p85 p11 p8
p87: 
p88: p93 p49 p65 p91
p89: 
p90: p94
p91: p26 p69 p72
p92: p94 p41 p41 p60 p29 p24
p93: p73 p55 trap1
p94: p49 p94 p84 p111
p95: p100 p25 p51 p89
p96: 
p97: p100
p98: p83 p82 p39 p82
p99: p42 p43 down2 p82 p54
p100: p64
p101: p45 p100 p82 p27
p102: p45 p101
p103: trap1
p104: p44
p105: p18 p106 p33 p67 down1
p106: p37 p38 p63
p107: p89
p108: 
p109: p75 p87 p8
p110: p37 p22
p111: 
p112: p74 p53
p113: p66 p67 p78
p114: p88 p51 p112
p115: p102 p13 p87 p56 p103 p110
p116: p45 p60 p62 p117
p117: p114 p21 p49
p118: p111 p70 p54
p119: p96 p33 p3 down2
---
ok: home p1 p10 p100 p101 p102 p103 p104 p105 p106 p107 p108 p109 p11 p110 p111 p112 p113 p114 p115 p116 p117 p118 p119 p12 p13 p14 p15 p16 p17 p18 p19 p2 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p3 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p4 p40 p41 p42 p43 p44 p45 p46 p47 p48 p49 p5 p50 p51 p53 p54 p55 p56 p57 p58 p59 p6 p60 p61 p62 p63 p64 p65 p66 p67 p68 p69 p7 p70 p71 p72 p73 p74 p75 p76 p77 p78 p79 p8 p80 p81 p82 p83 p84 p85 p86 p87 p88 p89 p9 p90 p91 p92 p93 p94 p95 p96 p97 p98 p99
timeout: trap1 trap2
error: down1 down2 down3
links: 382
peak concurrency within limit: True | tasks left running: 0

## Hints
- A simple structure: an `asyncio.Queue` of URLs, a `seen` set, and N worker tasks created in a `TaskGroup`. Each worker loops: `url = await queue.get()`, fetch it (under the semaphore and timeout), enqueue new URLs, `queue.task_done()`. The main coroutine does `await queue.join()`, then cancels the workers.
- Timeout per page: `async with sem: async with asyncio.timeout(page_timeout): links = await get(url)`, and catch `TimeoutError`.
- Scheduling limit: add a URL to `seen` and the queue only while `len(seen) < max_pages`. Discovery order is deterministic as long as you enqueue a page's links in order.
- The "trap" page never returns, so the timeout must cancel it. Cancelling the workers after `join()` ends the `TaskGroup` cleanly, leaving no stragglers.

## Solution
```python
import asyncio

async def crawl(start, max_concurrency, page_timeout, max_pages):
    sem = asyncio.Semaphore(max_concurrency)
    queue = asyncio.Queue()
    seen = {start}
    ok, timed_out, errors = [], [], []
    links_seen = 0
    await queue.put(start)

    async def worker():
        nonlocal links_seen
        while True:
            url = await queue.get()
            try:
                async with sem:                                  # cap requests in flight
                    async with asyncio.timeout(page_timeout):    # cap time per page
                        links = await get(url)
            except TimeoutError:
                timed_out.append(url)
            except ConnectionError:
                errors.append(url)
            else:
                ok.append(url)
                links_seen += len(links)
                for link in links:
                    if link not in seen and len(seen) < max_pages:
                        seen.add(link)
                        queue.put_nowait(link)
            finally:
                queue.task_done()

    async with asyncio.TaskGroup() as tg:
        workers = [tg.create_task(worker()) for _ in range(max_concurrency)]
        await queue.join()                                       # every scheduled page is processed
        for w in workers:
            w.cancel()                                           # stop the idle workers; the group then exits
    return {"ok": sorted(ok), "timeout": sorted(timed_out), "error": sorted(errors), "links": links_seen}
```

- **Structured concurrency:** all workers live inside a `TaskGroup`, so when `crawl` returns, every task has finished, which the driver verifies. If a worker crashed unexpectedly, the group would cancel the others and propagate the error instead of leaking tasks.
- **Two independent limits:** the `Semaphore` caps simultaneous requests (politeness and rate limiting), while `asyncio.timeout` caps time per request. A hung "trap" page is cancelled after `page_timeout`, and its `CancelledError` becomes a `TimeoutError` at the `async with` boundary.
- **Queue + `join()`:** `task_done()` is called for every page, even on errors (`finally`), so `join()` reliably signals completion. Cancelling the workers afterwards is clean, because they're idle at `queue.get()`.
- **Single-threaded safety:** `seen`, the result lists and `links_seen` are mutated only between `await`s, so no locks are needed. That's one of asyncio's big simplifications.
