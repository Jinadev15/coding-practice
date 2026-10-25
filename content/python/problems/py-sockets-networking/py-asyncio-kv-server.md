---
id: py-asyncio-kv-server
title: An asyncio TCP Key-Value Server
difficulty: Hard
order: 1
tags: asyncio, TCP, streams, framing, protocol design, concurrency, backpressure
time_limit: 15
---
## Statement
Robots on the shop floor share small pieces of state (zone locks, counters, map versions) through a tiny TCP key-value server. Implement `async def start_kv_server(host, port) -> asyncio.Server` with **asyncio streams**. The judge connects real TCP clients on `127.0.0.1` (port 0), many of them concurrently.

**Protocol**: UTF-8 lines terminated by `\n` (strip a trailing `\r`). Commands are case-insensitive, and arguments are separated by single spaces. One response line per command, in order:

| Command | Response |
|---|---|
| `SET key value` | `OK` (the value is the rest of the line and may contain spaces) |
| `GET key` | `VALUE <value>` or `NIL` |
| `DEL key` | `INT 1` if it existed, else `INT 0` |
| `INCR key` | `INT <n>`, where a missing key counts as 0. If the value isn't an integer: `ERR not an integer` |
| `KEYS prefix` | `KEYS k1 k2 …` (keys starting with the prefix, sorted). A bare `KEYS` matches everything. No matches gives `KEYS` alone. |
| `QUIT` | `BYE`, then close the connection |
| an empty line | ignored (no response) |
| anything else | `ERR unknown command`. Wrong argument counts give `ERR wrong arguments` (keys can't contain spaces). |

**Robustness rules:**
- Commands may arrive **split across TCP writes**, or **several in one write** (pipelining).
- A line longer than **1024 bytes** (excluding the newline) gets `ERR line too long`, and the server closes **that** connection. Other clients are unaffected.
- A client disconnecting abruptly must not crash the server.
- All clients share one store. `INCR` from many concurrent clients must never lose an update.

## Starter
```python
import asyncio


async def start_kv_server(host, port):
    store = {}

    async def handle(reader, writer):
        data = await reader.read(1024)
        parts = data.decode().split()
        if parts[0] == "SET":
            store[parts[1]] = parts[2]
            writer.write(b"OK\n")
        elif parts[0] == "GET":
            writer.write(f"VALUE {store[parts[1]]}\n".encode())
        writer.close()

    return await asyncio.start_server(handle, host, port)
```

## Driver
```python
import sys

async def session(port, payload_chunks, expect_lines, delay=0.0):
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    for chunk in payload_chunks:
        writer.write(chunk)
        await writer.drain()
        if delay:
            await asyncio.sleep(delay)
    out = []
    try:
        for _ in range(expect_lines):
            line = await asyncio.wait_for(reader.readline(), 3)
            if not line:
                out.append("<closed>")
                break
            out.append(line.decode().rstrip("\n"))
    except asyncio.TimeoutError:
        out.append("<timeout>")
    writer.close()
    try:
        await writer.wait_closed()
    except (ConnectionError, OSError):
        pass
    return out

async def main(cmds):
    server = await start_kv_server("127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    for cmd in cmds:
        if cmd == "basic":
            script = b"SET robot:1 idle at dock\nGET robot:1\nget missing\nINCR jobs\nincr jobs\nSET name rover\nINCR name\nDEL name\nDEL name\nKEYS rob\nKEYS\nKEYS zzz\nPING\nGET\nSET onlykey\n\nQUIT\nGET robot:1\n"
            for line in await session(port, [script], 18):
                print(line)
        elif cmd == "framing":
            print(await session(port, [b"SE", b"T k1 v", b"alue one\r\nGE", b"T k1\n", b"INCR c\nINCR c\nINCR c\n"], 5, delay=0.02))
            print(await session(port, [b"GET k1\n"], 1))
        elif cmd == "limits":
            print(await session(port, [b"SET big " + b"x" * 1100 + b"\nGET k\n"], 2))
            ok = await session(port, [b"SET edge " + b"y" * (1024 - 9) + b"\n", b"GET edge\n"], 2)
            print(ok[0], len(ok[1]))
            r, w = await asyncio.open_connection("127.0.0.1", port)
            w.write(b"SET half"); await w.drain(); w.transport.abort()     # abrupt disconnect
            await asyncio.sleep(0.05)
            print(await session(port, [b"SET alive yes\nGET alive\n"], 2))
        elif cmd == "concurrent":
            async def worker(i):
                lines = b"".join(b"INCR hits\n" for _ in range(200)) + f"SET w{i:02d} done\n".encode()
                res = await session(port, [lines[j:j + 97] for j in range(0, len(lines), 97)], 201)
                return res[-1]
            results = await asyncio.gather(*(worker(i) for i in range(40)))
            print(set(results))
            print(await session(port, [b"GET hits\nKEYS w0\n"], 2))
    server.close()
    await server.wait_closed()

asyncio.run(main(sys.stdin.read().split()))
```

## Tests
=== sample
basic
---
OK
VALUE idle at dock
NIL
INT 1
INT 2
OK
ERR not an integer
INT 1
INT 0
KEYS robot:1
KEYS jobs robot:1
KEYS
ERR unknown command
ERR wrong arguments
ERR wrong arguments
BYE
<closed>
=== hidden
framing
---
['OK', 'VALUE value one', 'INT 1', 'INT 2', 'INT 3']
['VALUE value one']
=== hidden
limits
---
['ERR line too long', '<closed>']
OK 1021
['OK', 'VALUE yes']
=== hidden
concurrent
---
{'OK'}
['VALUE 8000', 'KEYS w00 w01 w02 w03 w04 w05 w06 w07 w08 w09']

## Hints
- `asyncio.start_server(handle, host, port, limit=...)`. Use `await reader.readuntil(b"\n")` and catch `asyncio.LimitOverrunError` (line too long) and `asyncio.IncompleteReadError` (the peer closed). Or call `reader.readline()` with a stream limit just above 1024 and check the length yourself.
- `line.split(" ", 2)` gives command, key and value-with-spaces.
- In one handler, between two `await`s, nothing else runs, so `store[k] = int(store.get(k, 0)) + 1` is atomic without a lock.
- Wrap the handler body in `try/except (ConnectionError, asyncio.IncompleteReadError)` and `finally: writer.close()`.

## Solution
```python
import asyncio

MAX_LINE = 1024


async def start_kv_server(host, port):
    store: dict[str, str] = {}

    def execute(line: str) -> str:
        parts = line.split(" ", 2)
        cmd = parts[0].upper()
        args = parts[1:]
        if cmd == "SET":
            if len(args) != 2 or not args[0]:
                return "ERR wrong arguments"
            store[args[0]] = args[1]
            return "OK"
        if cmd in ("GET", "DEL", "INCR"):
            if len(args) != 1 or not args[0]:
                return "ERR wrong arguments"
            key = args[0]
            if cmd == "GET":
                return f"VALUE {store[key]}" if key in store else "NIL"
            if cmd == "DEL":
                return f"INT {int(store.pop(key, None) is not None)}"
            try:
                n = int(store.get(key, "0")) + 1          # atomic: no await in between
            except ValueError:
                return "ERR not an integer"
            store[key] = str(n)
            return f"INT {n}"
        if cmd == "KEYS":
            if len(args) > 1:
                return "ERR wrong arguments"
            prefix = args[0] if args else ""
            return " ".join(["KEYS", *sorted(k for k in store if k.startswith(prefix))])
        return "ERR unknown command"

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while True:
                try:
                    raw = await reader.readuntil(b"\n")
                except asyncio.IncompleteReadError:
                    break                                   # peer closed (possibly mid-line)
                except asyncio.LimitOverrunError:
                    writer.write(b"ERR line too long\n")
                    await writer.drain()
                    break
                line = raw[:-1]
                if line.endswith(b"\r"):
                    line = line[:-1]
                if len(line) > MAX_LINE:
                    writer.write(b"ERR line too long\n")
                    await writer.drain()
                    break
                text = line.decode("utf-8", errors="replace")
                if not text:
                    continue
                if text.upper() == "QUIT":
                    writer.write(b"BYE\n")
                    await writer.drain()
                    break
                writer.write((execute(text) + "\n").encode())
                await writer.drain()                        # backpressure for slow readers
        except ConnectionError:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionError:
                pass

    # stream limit slightly above the protocol limit: longer lines raise LimitOverrunError
    return await asyncio.start_server(handle, host, port, limit=MAX_LINE + 2)
```

- **Framing**: `readuntil(b"\n")` buffers partial data across TCP segments and returns exactly one line, so split commands and pipelined commands both work. The starter's single `read(1024)` treats whatever arrived as one command.
- **Bounded input**: the stream `limit` stops the server from buffering an endless line (a trivial memory-exhaustion attack). The offending connection gets an error and is closed, while other clients carry on.
- **Atomicity without locks**: asyncio is single-threaded and only switches tasks at `await`. The read-modify-write in `INCR` contains no `await`, so 40 clients × 200 increments always total exactly 8000. With threads, this would need a lock.
- **Backpressure**: `await writer.drain()` pauses a handler when the client isn't reading, instead of growing the output buffer without bound.
- **Clean failure handling**: abrupt disconnects end only that handler, and `finally` always closes the transport.
