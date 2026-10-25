# Sockets and Networking

Below HTTP sit **sockets**: the operating system's endpoint for network communication. Robot telemetry over UDP, a custom TCP command protocol to a motor controller, a discovery beacon, a WebSocket dashboard: all of them are sockets underneath. This lesson covers TCP vs UDP, Python's `socket` module, **message framing** (the bug behind most homemade protocols), timeouts and errors, concurrent servers with threads, `selectors` and **asyncio streams**, plus binary encoding with `struct`.

## 1. TCP and UDP

| | TCP (`SOCK_STREAM`) | UDP (`SOCK_DGRAM`) |
|---|---|---|
| Connection | handshake, then a connected stream | connectionless datagrams |
| Reliability | ordered, retransmitted, no duplicates | may be lost, duplicated or reordered |
| Message boundaries | **none: a byte stream** | preserved: one `sendto` is one datagram |
| Use | commands, file transfer, HTTP, databases | high-rate sensor streams, video, discovery, DDS (ROS 2) |

An address is `(host, port)`. Ports below 1024 need privileges, and port **0** asks the OS for any free port, which is ideal for tests.

## 2. A TCP echo server and client

```python
import socket

def serve_once(srv: socket.socket) -> None:
    conn, addr = srv.accept()                     # blocks until a client connects
    with conn:
        while data := conn.recv(4096):            # b"" means the peer closed the connection
            conn.sendall(data)                    # sendall loops until every byte is written

srv = socket.create_server(("127.0.0.1", 0))      # bind + listen; port 0 = any free port
port = srv.getsockname()[1]
# ... in another thread or process:
with socket.create_connection(("127.0.0.1", port), timeout=2.0) as c:
    c.sendall(b"hello")
    print(c.recv(4096))
```

> [!DANGER]
> `recv(4096)` returns **whatever has arrived**: maybe half a message, maybe three messages glued together. TCP has no message boundaries. Code that assumes one `send` equals one `recv` works on localhost in testing and breaks on a real network. You must **frame** messages.

## 3. Framing

Two standard techniques:

**Delimiter-based** (newline-terminated text, like Redis, SMTP and JSON Lines):

```python
class LineReader:
    def __init__(self, sock): self.sock, self.buf = sock, b""
    def readline(self) -> bytes | None:
        while b"\n" not in self.buf:
            chunk = self.sock.recv(4096)
            if not chunk: return None                 # connection closed
            self.buf += chunk
            if len(self.buf) > 65536: raise ValueError("line too long")   # bound memory!
        line, _, self.buf = self.buf.partition(b"\n")
        return line
```

**Length-prefixed** (binary protocols, gRPC, MQTT):

```python
import struct

def send_msg(sock, payload: bytes) -> None:
    sock.sendall(struct.pack("!I", len(payload)) + payload)       # 4-byte big-endian length

def recv_exact(sock, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk: raise ConnectionError("peer closed mid-message")
        buf += chunk
    return bytes(buf)

def recv_msg(sock, max_len: int = 1 << 20) -> bytes:
    (n,) = struct.unpack("!I", recv_exact(sock, 4))
    if n > max_len: raise ValueError("message too large")           # never trust the length field
    return recv_exact(sock, n)
```

`struct` format characters: `!` network (big-endian) order, `B` u8, `H` u16, `I` u32, `q` i64, `f` float32, `d` float64. For example, `struct.pack("!HHfff", msg_type, seq, x, y, theta)` packs a pose message into 16 bytes.

## 4. Timeouts and errors

- `sock.settimeout(2.0)` makes blocking calls raise `TimeoutError` (`socket.timeout`) instead of hanging forever. Every robot-side socket should have one.
- `ConnectionRefusedError` (nobody listening), `ConnectionResetError` (peer crashed), `BrokenPipeError` (writing to a closed connection).
- Set `SO_REUSEADDR` so a restarted server can rebind immediately (`create_server` does this on POSIX). Use `TCP_NODELAY` to disable Nagle's algorithm for small, latency-sensitive control messages.

## 5. UDP

```python
rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); rx.bind(("127.0.0.1", 0))
tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tx.sendto(struct.pack("!Id", 42, 0.75), rx.getsockname())
data, addr = rx.recvfrom(2048)                     # one whole datagram
seq, value = struct.unpack("!Id", data)
```

Add your own **sequence numbers** to detect loss and reordering, and timestamps to discard stale data. For a control loop, the newest reading matters more than a retransmitted old one, which is exactly why UDP suits it.

## 6. Serving many clients

1. **Thread per connection**: `socketserver.ThreadingTCPServer` or `threading.Thread(target=handle, args=(conn,))`. It's simple and fine for tens of clients.
2. **I/O multiplexing**: `selectors` (epoll/kqueue) watches many sockets in one thread.
3. **asyncio streams**: the modern choice for thousands of concurrent connections:

```python
import asyncio

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    peer = writer.get_extra_info("peername")
    try:
        while line := await reader.readline():             # framing handled for you
            cmd = line.decode().strip()
            writer.write(f"ack {cmd}\n".encode())
            await writer.drain()                            # backpressure: wait if the send buffer is full
    except ConnectionResetError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def main() -> None:
    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(b"status\n"); await writer.drain()
    print(await reader.readline())                          # b'ack status\n'
    writer.close(); await writer.wait_closed()
    server.close(); await server.wait_closed()

asyncio.run(main())
```

`reader.readexactly(n)` handles length-prefixed framing. `asyncio.wait_for(reader.readline(), 5)` adds timeouts. Shared state between handlers needs no locks, as long as you don't `await` in the middle of an update.

## 7. Security and robustness

- Treat every byte from the network as hostile. Bound line and message sizes, validate fields, and handle partial and malformed input without crashing.
- Bind to `127.0.0.1` unless remote access is intended. `0.0.0.0` exposes the service on every interface.
- Encrypt with TLS (`ssl.create_default_context().wrap_socket(...)` or asyncio's `ssl=` parameter) whenever data crosses an untrusted network. ROS 2 has SROS2 for DDS security.

> [!EXAM]
> **Why do TCP protocols need message framing, and what are the common approaches?**
> TCP delivers a reliable, ordered **byte stream** with no message boundaries. A single `recv` may return part of a message or several messages concatenated, depending on segmentation, buffering and timing. The application must define where messages end. Use delimiters (newline-terminated lines, with escaping and a maximum length) or a length prefix (a fixed-size header giving the payload size, read with a loop until exactly that many bytes have arrived, with an upper bound on the length). UDP preserves datagram boundaries but not delivery or order.
