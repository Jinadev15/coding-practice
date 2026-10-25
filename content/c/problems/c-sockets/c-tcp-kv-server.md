---
id: c-tcp-kv-server
title: A Line-Protocol TCP Key-Value Server
difficulty: Hard
order: 1
tags: sockets, TCP, bind, listen, accept, framing, poll, network byte order
time_limit: 5
---
## Statement
Write a tiny TCP key–value store, of the kind a robot might expose for runtime parameters, using raw BSD sockets on the loopback interface.

```c
int kv_listen(int *port);
    /* create a TCP socket bound to 127.0.0.1 on an ephemeral port (port 0), listen, store the chosen
       port (host byte order) in *port, return the listening fd (or -1). Set SO_REUSEADDR. */
void kv_serve(int listen_fd, int max_clients);
    /* accept and fully serve max_clients connections, ONE AFTER ANOTHER, then return. Each client sends
       newline-terminated commands (bytes may arrive in arbitrary fragments, and several commands may
       arrive in one read):
         SET <key> <value>  -> "OK"            (keys and values: no spaces, <= 64 chars; update allowed)
         GET <key>          -> the value, or "NOT_FOUND"
         DEL <key>          -> "1" if deleted, "0" if absent
         COUNT              -> the number of keys
         QUIT               -> "BYE", then close this connection
       Unknown commands -> "ERR". Every reply ends with '\n'. The store persists across clients.
       A client may also just disconnect (EOF) without QUIT. Ignore SIGPIPE. */
```

The driver forks: the child runs `kv_listen` and `kv_serve` (sending the port back through a pipe), and the parent connects as a client. It deliberately splits commands across writes, packs several commands into one write, and disconnects abruptly.

## Starter
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int kv_listen(int *port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in a = { .sin_family = AF_INET, .sin_port = 0 };
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    bind(fd, (struct sockaddr *)&a, sizeof a);
    listen(fd, 8);
    *port = 0;                                         /* forgot getsockname */
    return fd;
}
void kv_serve(int listen_fd, int max_clients) { (void)listen_fd; (void)max_clients; }
```

## Driver
```c
#include <sys/wait.h>
#include <time.h>

static void nap(long ms) { struct timespec ts = { ms / 1000, (ms % 1000) * 1000000L }; nanosleep(&ts, NULL); }

static int connect_to(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in a = { .sin_family = AF_INET, .sin_port = htons((unsigned short)port) };
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    for (int tries = 0; tries < 50; tries++) {
        if (connect(fd, (struct sockaddr *)&a, sizeof a) == 0) return fd;
        nap(20);
    }
    return -1;
}

static char rbuf[65536]; static size_t rlen;
static int read_line(int fd, char *out, size_t cap) {          /* client-side framing */
    for (;;) {
        char *nl = memchr(rbuf, '\n', rlen);
        if (nl) {
            size_t L = (size_t)(nl - rbuf);
            if (L >= cap) L = cap - 1;
            memcpy(out, rbuf, L); out[L] = '\0';
            size_t used = (size_t)(nl - rbuf) + 1;
            memmove(rbuf, rbuf + used, rlen - used); rlen -= used;
            return 1;
        }
        ssize_t n = read(fd, rbuf + rlen, sizeof rbuf - rlen);
        if (n <= 0) return 0;
        rlen += (size_t)n;
    }
}

static void send_str(int fd, const char *s) { write(fd, s, strlen(s)); }

int main(void) {
    char line[1024];
    int clients = 0;
    char script[256][256]; int ns = 0;
    while (ns < 256 && fgets(script[ns], sizeof script[ns], stdin)) {
        script[ns][strcspn(script[ns], "\n")] = '\0';
        if (!strcmp(script[ns], "NEWCLIENT")) clients++;
        ns++;
    }
    int pp[2]; pipe(pp);
    fflush(stdout);
    pid_t kid = fork();
    if (kid == 0) {
        close(pp[0]);
        int port = -1;
        int lfd = kv_listen(&port);
        write(pp[1], &port, sizeof port);
        close(pp[1]);
        if (lfd >= 0) kv_serve(lfd, clients);
        _exit(0);
    }
    close(pp[1]);
    int port = 0;
    read(pp[0], &port, sizeof port);
    close(pp[0]);
    printf("server port valid: %d\n", port > 0 && port < 65536);
    int fd = -1, expected = 0;
    for (int i = 0; i < ns; i++) {
        char *s = script[i];
        if (!strcmp(s, "NEWCLIENT")) {
            if (fd >= 0) close(fd);
            rlen = 0;
            fd = connect_to(port);
            printf("-- connected: %d\n", fd >= 0);
            if (fd < 0) break;
        } else if (!strncmp(s, "SPLIT ", 6)) {          /* send a command in 3-byte fragments */
            char msg[300]; snprintf(msg, sizeof msg, "%s\n", s + 6);
            for (size_t k = 0; k < strlen(msg); k += 3) {
                write(fd, msg + k, strlen(msg) - k < 3 ? strlen(msg) - k : 3);
                nap(2);
            }
            expected++;
        } else if (!strncmp(s, "BATCH ", 6)) {          /* several commands separated by ';' in ONE write */
            char msg[300]; size_t L = 0;
            for (char *t = s + 6; *t; t++) { msg[L++] = *t == ';' ? '\n' : *t; expected += *t == ';'; }
            msg[L++] = '\n'; expected++;
            write(fd, msg, L);
        } else if (!strcmp(s, "HANGUP")) {               /* abrupt disconnect */
            close(fd); fd = -1;
            continue;
        } else {
            send_str(fd, s); send_str(fd, "\n");
            expected++;
        }
        while (expected > 0 && fd >= 0) {
            if (!read_line(fd, line, sizeof line)) { printf("(connection closed)\n"); expected = 0; break; }
            printf("%s\n", line);
            expected--;
        }
    }
    if (fd >= 0) close(fd);
    int st; waitpid(kid, &st, 0);
    printf("server finished: %d\n", WIFEXITED(st) && WEXITSTATUS(st) == 0);
    return 0;
}
```

## Tests
=== sample
NEWCLIENT
SET speed 1.5
GET speed
GET missing
COUNT
QUIT
---
server port valid: 1
-- connected: 1
OK
1.5
NOT_FOUND
1
BYE
server finished: 1
=== hidden
NEWCLIENT
SPLIT SET mode autonomous
BATCH SET a 1;SET b 2;GET a;COUNT
DEL b
DEL b
SET a 99
GET a
HELLO
HANGUP
NEWCLIENT
GET mode
GET a
COUNT
SPLIT GET a
QUIT
NEWCLIENT
BATCH DEL a;DEL mode;COUNT;QUIT
---
server port valid: 1
-- connected: 1
OK
OK
OK
1
3
1
0
OK
99
ERR
-- connected: 1
autonomous
99
2
99
BYE
-- connected: 1
1
1
0
BYE
server finished: 1

## Hints
- `kv_listen`: `socket`, `setsockopt(SO_REUSEADDR)`, `bind` to `127.0.0.1:0`, `listen`, then `getsockname` to learn the port (`ntohs`).
- `kv_serve`: for each client, `accept`, then keep a per-connection buffer: append whatever `read` returns, extract every complete line (up to `'\n'`), process it, and keep the leftover partial line for the next read. `read` returning 0 means the client hung up.
- Store keys and values in a fixed array of structs (linear search is fine), or a small hash table.
- Reply with a `write_all` helper. `signal(SIGPIPE, SIG_IGN)` so a vanished client can't kill the server.

## Solution
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int kv_listen(int *port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    int yes = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes);
    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family = AF_INET;
    a.sin_port = htons(0);                               /* ephemeral port */
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    if (bind(fd, (struct sockaddr *)&a, sizeof a) < 0 || listen(fd, 16) < 0) { close(fd); return -1; }
    socklen_t len = sizeof a;
    if (getsockname(fd, (struct sockaddr *)&a, &len) < 0) { close(fd); return -1; }
    *port = ntohs(a.sin_port);
    return fd;
}

typedef struct { char key[65], val[65]; int used; } Entry;
static Entry store[1024];

static Entry *find(const char *k) {
    for (int i = 0; i < 1024; i++) if (store[i].used && !strcmp(store[i].key, k)) return &store[i];
    return NULL;
}

static void write_all(int fd, const char *s, size_t n) {
    while (n) {
        ssize_t w = write(fd, s, n);
        if (w < 0) { if (errno == EINTR) continue; return; }   /* EPIPE: the client vanished */
        s += w; n -= (size_t)w;
    }
}

static int handle(int fd, char *line) {                  /* returns 0 when the client said QUIT */
    char cmd[16] = "", k[65] = "", v[65] = "", out[96];
    int n = sscanf(line, "%15s %64s %64s", cmd, k, v);
    if (!strcmp(cmd, "SET") && n == 3) {
        Entry *e = find(k);
        if (!e) for (int i = 0; i < 1024; i++) if (!store[i].used) { e = &store[i]; e->used = 1; strcpy(e->key, k); break; }
        if (e) { strcpy(e->val, v); snprintf(out, sizeof out, "OK\n"); }
        else snprintf(out, sizeof out, "ERR\n");
    } else if (!strcmp(cmd, "GET") && n == 2) {
        Entry *e = find(k);
        snprintf(out, sizeof out, "%s\n", e ? e->val : "NOT_FOUND");
    } else if (!strcmp(cmd, "DEL") && n == 2) {
        Entry *e = find(k);
        if (e) e->used = 0;
        snprintf(out, sizeof out, "%d\n", e != NULL);
    } else if (!strcmp(cmd, "COUNT") && n == 1) {
        int c = 0;
        for (int i = 0; i < 1024; i++) c += store[i].used;
        snprintf(out, sizeof out, "%d\n", c);
    } else if (!strcmp(cmd, "QUIT") && n == 1) {
        write_all(fd, "BYE\n", 4);
        return 0;
    } else {
        snprintf(out, sizeof out, "ERR\n");
    }
    write_all(fd, out, strlen(out));
    return 1;
}

void kv_serve(int listen_fd, int max_clients) {
    signal(SIGPIPE, SIG_IGN);
    for (int c = 0; c < max_clients; c++) {
        int fd = accept(listen_fd, NULL, NULL);
        if (fd < 0) { if (errno == EINTR) { c--; continue; } break; }
        char buf[8192];
        size_t len = 0;
        int open_conn = 1;
        while (open_conn) {
            ssize_t n = read(fd, buf + len, sizeof buf - 1 - len);
            if (n < 0 && errno == EINTR) continue;
            if (n <= 0) break;                           /* EOF: the client hung up */
            len += (size_t)n;
            char *start = buf, *nl;
            while (open_conn && (nl = memchr(start, '\n', len - (size_t)(start - buf)))) {
                *nl = '\0';
                if (nl > start && nl[-1] == '\r') nl[-1] = '\0';
                open_conn = handle(fd, start);
                start = nl + 1;
            }
            len -= (size_t)(start - buf);                /* keep the partial line */
            memmove(buf, start, len);
        }
        close(fd);
    }
    close(listen_fd);
}
```

- **Binding to port 0** lets the kernel pick a free port, and `getsockname` reveals it. That's how tests and multi-instance services avoid port clashes. The port is converted with `ntohs`, because socket structures use network byte order.
- **TCP is a byte stream**, so the server keeps a per-connection buffer and processes only *complete* lines. A command split across three writes (`SPLIT`) waits until its newline arrives, four commands in one write (`BATCH`) produce four replies, and a leftover fragment is moved to the front of the buffer for the next `read`.
- **Robustness**: `read` returning 0 means the peer closed (the `HANGUP` client), and ignoring SIGPIPE turns writes to a vanished client into harmless `EPIPE` errors. Because the store is global, it outlives individual connections, as the second client's `GET` shows.
