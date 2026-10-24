---
id: py-futures-fetcher
title: Concurrent Fetcher with Retries and Timeouts
difficulty: Medium
order: 1
tags: concurrent.futures, ThreadPoolExecutor, as_completed, retries, error handling
time_limit: 3
---
## Statement
Fetch many "URLs" concurrently with a `ThreadPoolExecutor`. The driver provides a deterministic fake network:

```python
def fetch(url: str, attempt: int) -> str
    # sleeps (simulated latency), then returns a payload, or raises ConnectionError / TimeoutError / ValueError
```

Implement:

```python
def fetch_all(urls: list[str], workers: int, retries: int) -> dict:
    # returns {"ok": {url: payload}, "failed": {url: "ExceptionName"}, "attempts": {url: n}}
```

- Run the URLs concurrently with at most `workers` threads.
- `ConnectionError` and `TimeoutError` are **transient**: retry up to `retries` additional attempts (pass `attempt = 1, 2, …` to `fetch`). `ValueError` is **permanent**: don't retry it.
- A URL fails with the name of the **last** exception raised.
- One failure must never stop the others.

There are up to 60 URLs, each with ~0.1 s latency. Sequential fetching would take far longer than the time limit.

## Starter
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_all(urls, workers, retries):
    ok, failed, attempts = {}, {}, {}
    for url in urls:
        attempts[url] = 1
        try:
            ok[url] = fetch(url, 1)
        except Exception as e:
            failed[url] = type(e).__name__
    return {"ok": ok, "failed": failed, "attempts": attempts}
```

## Driver
```python
import sys
import time
import zlib

def fetch(url, attempt):
    time.sleep(0.1)
    h = zlib.crc32(url.encode())
    if "bad" in url:
        raise ValueError(url)
    if "flaky" in url and attempt < 1 + h % 3:
        raise ConnectionError(url)
    if "slow" in url and attempt < 3:
        raise TimeoutError(url)
    return f"<{url}:{h % 1000}>"

data = sys.stdin.read().split()
workers, retries = int(data[0]), int(data[1])
urls = data[2:]
res = fetch_all(urls, workers, retries)
for url in urls:
    if url in res["ok"]:
        print(f"{url} ok {res['ok'][url]} attempts={res['attempts'][url]}")
    else:
        print(f"{url} FAILED {res['failed'][url]} attempts={res['attempts'][url]}")
print(f"ok={len(res['ok'])} failed={len(res['failed'])}")
```

## Tests
=== sample
4 2
a.com flaky1.com bad.com slow.com flaky2.com
---
a.com ok <a.com:961> attempts=1
flaky1.com ok <flaky1.com:733> attempts=3
bad.com FAILED ValueError attempts=1
slow.com ok <slow.com:994> attempts=3
flaky2.com ok <flaky2.com:749> attempts=3
ok=4 failed=1
=== hidden
8 0
x.com slow.com bad.com flaky9.com
---
x.com ok <x.com:250> attempts=1
slow.com FAILED TimeoutError attempts=1
bad.com FAILED ValueError attempts=1
flaky9.com FAILED ConnectionError attempts=1
ok=1 failed=3
=== hidden
20 3
bad0.io site1.io slow2.io slow3.io flaky4.io flaky5.io site6.io site7.io slow8.io site9.io bad10.io site11.io site12.io slow13.io site14.io site15.io site16.io site17.io site18.io bad19.io flaky20.io site21.io bad22.io site23.io bad24.io flaky25.io flaky26.io flaky27.io site28.io site29.io flaky30.io site31.io site32.io site33.io site34.io bad35.io site36.io site37.io slow38.io flaky39.io site40.io flaky41.io site42.io bad43.io site44.io slow45.io flaky46.io bad47.io slow48.io slow49.io site50.io flaky51.io site52.io site53.io bad54.io site55.io bad56.io bad57.io flaky58.io site59.io
---
bad0.io FAILED ValueError attempts=1
site1.io ok <site1.io:87> attempts=1
slow2.io ok <slow2.io:524> attempts=3
slow3.io ok <slow3.io:401> attempts=3
flaky4.io ok <flaky4.io:361> attempts=3
flaky5.io ok <flaky5.io:380> attempts=2
site6.io ok <site6.io:710> attempts=1
site7.io ok <site7.io:843> attempts=1
slow8.io ok <slow8.io:864> attempts=3
site9.io ok <site9.io:472> attempts=1
bad10.io FAILED ValueError attempts=1
site11.io ok <site11.io:672> attempts=1
site12.io ok <site12.io:390> attempts=1
slow13.io ok <slow13.io:635> attempts=3
site14.io ok <site14.io:370> attempts=1
site15.io ok <site15.io:511> attempts=1
site16.io ok <site16.io:537> attempts=1
site17.io ok <site17.io:668> attempts=1
site18.io ok <site18.io:746> attempts=1
bad19.io FAILED ValueError attempts=1
flaky20.io ok <flaky20.io:112> attempts=3
site21.io ok <site21.io:912> attempts=1
bad22.io FAILED ValueError attempts=1
site23.io ok <site23.io:307> attempts=1
bad24.io FAILED ValueError attempts=1
flaky25.io ok <flaky25.io:666> attempts=3
flaky26.io ok <flaky26.io:244> attempts=2
flaky27.io ok <flaky27.io:177> attempts=3
site28.io ok <site28.io:450> attempts=1
site29.io ok <site29.io:679> attempts=1
flaky30.io ok <flaky30.io:528> attempts=2
site31.io ok <site31.io:296> attempts=1
site32.io ok <site32.io:782> attempts=1
site33.io ok <site33.io:811> attempts=1
site34.io ok <site34.io:274> attempts=1
bad35.io FAILED ValueError attempts=1
site36.io ok <site36.io:441> attempts=1
site37.io ok <site37.io:132> attempts=1
slow38.io ok <slow38.io:746> attempts=3
flaky39.io ok <flaky39.io:738> attempts=3
site40.io ok <site40.io:501> attempts=1
flaky41.io ok <flaky41.io:589> attempts=2
site42.io ok <site42.io:710> attempts=1
bad43.io FAILED ValueError attempts=1
site44.io ok <site44.io:226> attempts=1
slow45.io ok <slow45.io:807> attempts=3
flaky46.io ok <flaky46.io:660> attempts=2
bad47.io FAILED ValueError attempts=1
slow48.io ok <slow48.io:186> attempts=3
slow49.io ok <slow49.io:55> attempts=3
site50.io ok <site50.io:469> attempts=1
flaky51.io ok <flaky51.io:613> attempts=1
site52.io ok <site52.io:662> attempts=1
site53.io ok <site53.io:283> attempts=1
bad54.io FAILED ValueError attempts=1
site55.io ok <site55.io:703> attempts=1
bad56.io FAILED ValueError attempts=1
bad57.io FAILED ValueError attempts=1
flaky58.io ok <flaky58.io:967> attempts=3
site59.io ok <site59.io:623> attempts=1
ok=49 failed=11

## Hints
- Submit one task per URL. Each task does the retry loop itself: `for attempt in range(1, retries + 2): try: return url, fetch(url, attempt), attempt, None except (ConnectionError, TimeoutError) as e: last = e except ValueError as e: return url, None, attempt, e`.
- Collect with `as_completed`. Because each task catches its own exceptions and returns them as data, a failing URL can't crash the collection loop.
- Retries inside the worker overlap with other URLs' work. Re-submitting from the main thread would also work, but it's more complex.

## Solution
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

TRANSIENT = (ConnectionError, TimeoutError)

def fetch_all(urls, workers, retries):
    def task(url):
        last = None
        for attempt in range(1, retries + 2):
            try:
                return url, fetch(url, attempt), attempt, None
            except TRANSIENT as e:
                last = e                          # retry
            except ValueError as e:
                return url, None, attempt, e      # permanent: give up immediately
        return url, None, retries + 1, last

    ok, failed, attempts = {}, {}, {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(task, u) for u in urls]
        for fut in as_completed(futures):
            url, payload, n, err = fut.result()
            attempts[url] = n
            if err is None:
                ok[url] = payload
            else:
                failed[url] = type(err).__name__
    return {"ok": ok, "failed": failed, "attempts": attempts}
```

- **I/O-bound, so threads:** each `fetch` spends its time sleeping (waiting on the "network"), the GIL is released, and many fetches overlap. Total time ≈ (slowest URL's attempts × latency) × ⌈URLs / workers⌉, instead of the sum of all latencies.
- **Errors as data:** catching inside the task and returning the outcome means `fut.result()` never raises, and every URL is accounted for. Classifying exceptions as transient or permanent is the core of any robust client.
- **`as_completed`** processes results as soon as each finishes. Output order is restored afterwards by iterating the original list.
- Production versions add exponential backoff with jitter between retries, and a per-call timeout.
