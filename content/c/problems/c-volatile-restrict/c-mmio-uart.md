---
id: c-mmio-uart
title: Driving a Memory-Mapped UART (volatile in Action)
difficulty: Hard
order: 1
tags: volatile, memory-mapped I/O, registers, polling, restrict, embedded
time_limit: 2
---
## Statement
You're writing the driver for a UART peripheral whose registers are **memory-mapped**. The judge simulates the hardware with a background thread that reads and writes the register block **behind your back**, exactly like real hardware does.

```c
typedef struct {
    uint32_t data;      /* write: byte to transmit (low 8 bits); read: last received byte */
    uint32_t status;    /* bit 0 TX_EMPTY: set by hardware when it can take a byte
                           bit 1 RX_READY: set by hardware when a received byte is in data */
    uint32_t control;   /* bit 0 ENABLE, bits 4..5 PARITY (0 none, 1 even, 2 odd), bits 8..15 BAUD_DIV */
} UartRegs;             /* keep the field names and order, but YOU decide the qualifiers */
```

Implement:

```c
void uart_configure(UartRegs *u, unsigned parity, unsigned baud_div);  /* set PARITY and BAUD_DIV fields,
                                       preserve all other control bits, then set ENABLE */
void uart_write(UartRegs *u, const char *s);       /* for each char: wait until TX_EMPTY is set, write data,
                                       then CLEAR TX_EMPTY to hand the byte to the hardware */
size_t uart_read_line(UartRegs *u, char *buf, size_t cap);   /* for each char: wait until RX_READY, read data,
                                       then CLEAR RX_READY to acknowledge; stop after '\n' (not stored)
                                       or when cap-1 chars are stored; NUL-terminate; return the length */
void mix(float *restrict out, const float *restrict a, const float *restrict b, size_t n, float g);
                                     /* out[i] = a[i] + g * b[i] (buffers never overlap) */
```

The status flags form a handshake: hardware sets a flag, and the driver clears it (as with "write-1-to-clear" status bits on real chips). **The catch**: compiled at `-O2`, a polling loop on an ordinary (non-`volatile`) field is "optimised" into a single read and an infinite loop, because the compiler can't see the hardware thread. The starter has exactly that bug. It times out.

## Starter
```c
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint32_t data;
    uint32_t status;
    uint32_t control;
} UartRegs;

#define TX_EMPTY 0x1u
#define RX_READY 0x2u

void uart_configure(UartRegs *u, unsigned parity, unsigned baud_div) {
    u->control = 1u | (parity << 4) | (baud_div << 8);
}

void uart_write(UartRegs *u, const char *s) {
    for (; *s; s++) {
        while (!(u->status & TX_EMPTY)) { }
        u->data = (uint8_t)*s;
        u->status &= ~TX_EMPTY;
    }
}

size_t uart_read_line(UartRegs *u, char *buf, size_t cap) {
    size_t n = 0;
    while (n + 1 < cap) {
        while (!(u->status & RX_READY)) { }
        char c = (char)u->data;
        u->status &= ~RX_READY;
        if (c == '\n') break;
        buf[n++] = c;
    }
    buf[n] = '\0';
    return n;
}

void mix(float *restrict out, const float *restrict a, const float *restrict b, size_t n, float g) {
    for (size_t i = 0; i < n; i++) out[i] = a[i] + g * b[i];
}
```

## Driver
```c
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <stdatomic.h>
#include <threads.h>

static UartRegs regs;
static volatile uint32_t *const HW_DATA = (volatile uint32_t *)&regs.data;
static volatile uint32_t *const HW_STATUS = (volatile uint32_t *)&regs.status;
static atomic_int hw_stop, hw_mode;          /* 1: transmit sink, 2: receive source */
static char tx_log[4096];
static size_t tx_len;
static const char *rx_src;
static size_t rx_pos;

static void tiny_sleep(void) { thrd_sleep(&(struct timespec){.tv_nsec = 20000}, NULL); }

static void *hardware(void *arg) {
    (void)arg;
    while (!atomic_load(&hw_stop)) {
        int mode = atomic_load(&hw_mode);
        if (mode == 1 && !(*HW_STATUS & TX_EMPTY)) {          /* the driver handed us a byte */
            char c = (char)*HW_DATA;
            tiny_sleep();                                       /* shifting it out on the wire */
            tx_log[tx_len++] = c;
            *HW_STATUS |= TX_EMPTY;
        } else if (mode == 2 && rx_src[rx_pos] && !(*HW_STATUS & RX_READY)) {
            tiny_sleep();                                       /* a byte arrives */
            *HW_DATA = (uint8_t)rx_src[rx_pos++];
            *HW_STATUS |= RX_READY;
        }
        tiny_sleep();
    }
    return NULL;
}

int main(void) {
    char cmd[16];
    pthread_t hw;
    *HW_STATUS = TX_EMPTY;
    pthread_create(&hw, NULL, hardware, NULL);
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "config")) {
            unsigned ctrl, par, div;
            if (scanf("%x %u %u", &ctrl, &par, &div) != 3) return 1;
            regs.control = ctrl;
            uart_configure(&regs, par, div);
            printf("config 0x%X parity=%u div=%u -> control=0x%08X\n", ctrl, par, div, (unsigned)regs.control);
        } else if (!strcmp(cmd, "write")) {
            char text[256];
            if (scanf(" %255[^\n]", text) != 1) return 1;
            tx_len = 0;
            atomic_store(&hw_mode, 1);
            uart_write(&regs, text);
            while (!(*HW_STATUS & TX_EMPTY)) tiny_sleep();     /* wait for the last byte to leave */
            atomic_store(&hw_mode, 0);
            printf("write -> wire saw \"%.*s\" (%zu bytes)\n", (int)tx_len, tx_log, tx_len);
        } else if (!strcmp(cmd, "read")) {
            static char src[512];
            size_t cap;
            if (scanf("%zu %511s", &cap, src) != 2) return 1;
            for (char *p = src; *p; p++) if (*p == '|') *p = '\n';
            rx_src = src;
            rx_pos = 0;
            *HW_STATUS &= ~RX_READY;
            atomic_store(&hw_mode, 2);
            char buf[512];
            size_t n = uart_read_line(&regs, buf, cap);
            atomic_store(&hw_mode, 0);
            thrd_sleep(&(struct timespec){.tv_nsec = 2000000}, NULL);   /* let in-flight hardware work finish */
            printf("read cap=%zu -> \"%s\" (len %zu)\n", cap, buf, n);
        } else if (!strcmp(cmd, "mix")) {
            size_t n; float g;
            if (scanf("%zu %f", &n, &g) != 2) return 1;
            float a[64], b[64], out[64];
            for (size_t i = 0; i < n; i++) { a[i] = (float)i; b[i] = (float)(i * i) * 0.5f; }
            mix(out, a, b, n, g);
            printf("mix n=%zu g=%.2f ->", n, (double)g);
            for (size_t i = 0; i < n; i++) printf(" %.2f", (double)out[i]);
            printf("\n");
        }
    }
    atomic_store(&hw_stop, 1);
    pthread_join(hw, NULL);
    return 0;
}
```

## Tests
=== sample
config 0 2 26
write HELLO
read 64 ok|ignored
mix 4 2.0
---
config 0x0 parity=2 div=26 -> control=0x00001A21
write -> wire saw "HELLO" (5 bytes)
read cap=64 -> "ok" (len 2)
mix n=4 g=2.00 -> 0.00 2.00 6.00 12.00
=== hidden
config FFFFFFFF 0 0
config 30 1 255
config 8000000E 1 13
write robot ready
write x
read 4 abcdef|
read 64 |x
read 64 status:OK|
mix 1 -1.0
mix 6 0.5
---
config 0xFFFFFFFF parity=0 div=0 -> control=0xFFFF00CF
config 0x30 parity=1 div=255 -> control=0x0000FF11
config 0x8000000E parity=1 div=13 -> control=0x80000D1F
write -> wire saw "robot ready" (11 bytes)
write -> wire saw "x" (1 bytes)
read cap=4 -> "abc" (len 3)
read cap=64 -> "" (len 0)
read cap=64 -> "status:OK" (len 9)
mix n=1 g=-1.00 -> 0.00
mix n=6 g=0.50 -> 0.00 1.25 3.00 5.25 8.00 11.25

## Hints
- Make the register fields `volatile uint32_t`. Every read in the polling loop is then a real load, and the loop sees the hardware's change. That's the whole fix for the timeout.
- `uart_configure` is a read-modify-write. Clear the PARITY field (`0x3u << 4`) and the BAUD field (`0xFFu << 8`), OR in the new values (masked), then set ENABLE, keeping every other bit.
- In real code, prefer `#define UART0 ((UartRegs *)0x4000C000u)` with volatile members, or `volatile UartRegs *`.
- `restrict` on `mix` is a promise that lets the compiler vectorise. The judge never passes overlapping buffers.

## Solution
```c
#include <stdint.h>
#include <stddef.h>

typedef struct {
    volatile uint32_t data;
    volatile uint32_t status;
    volatile uint32_t control;
} UartRegs;

#define TX_EMPTY 0x1u
#define RX_READY 0x2u
#define CTRL_ENABLE       0x1u
#define CTRL_PARITY_SHIFT 4u
#define CTRL_PARITY_MASK  (0x3u << CTRL_PARITY_SHIFT)
#define CTRL_BAUD_SHIFT   8u
#define CTRL_BAUD_MASK    (0xFFu << CTRL_BAUD_SHIFT)

void uart_configure(UartRegs *u, unsigned parity, unsigned baud_div) {
    uint32_t c = u->control;                                     /* one real read */
    c &= ~(CTRL_PARITY_MASK | CTRL_BAUD_MASK);
    c |= ((uint32_t)parity << CTRL_PARITY_SHIFT) & CTRL_PARITY_MASK;
    c |= ((uint32_t)baud_div << CTRL_BAUD_SHIFT) & CTRL_BAUD_MASK;
    c |= CTRL_ENABLE;
    u->control = c;                                              /* one real write */
}

void uart_write(UartRegs *u, const char *s) {
    for (; *s; s++) {
        while (!(u->status & TX_EMPTY)) { }                      /* volatile: re-read every iteration */
        u->data = (uint8_t)*s;
        u->status &= ~TX_EMPTY;                                  /* hand the byte over */
    }
}

size_t uart_read_line(UartRegs *u, char *buf, size_t cap) {
    size_t n = 0;
    while (n + 1 < cap) {
        while (!(u->status & RX_READY)) { }
        char c = (char)u->data;
        u->status &= ~RX_READY;                                  /* acknowledge */
        if (c == '\n') break;
        buf[n++] = c;
    }
    buf[n] = '\0';
    return n;
}

void mix(float *restrict out, const float *restrict a, const float *restrict b, size_t n, float g) {
    for (size_t i = 0; i < n; i++) out[i] = a[i] + g * b[i];
}
```

The bug in the starter is the classic embedded failure. At `-O2`, the compiler sees `while (!(u->status & TX_EMPTY)) { }` with nothing in the loop that could change `u->status`, so it loads the value once and spins forever. Declaring the register fields `volatile` makes every access an observable side effect, so each iteration really reads the hardware.

`uart_configure` shows the second register idiom, **read–modify–write with masks**: read once into a local, clear the fields, insert the masked values and write once. That preserves the bits you don't own and avoids extra bus accesses (each volatile access is a real one).

`restrict` is the opposite promise: no one else touches this memory, so optimise freely. On real multi-core systems or DMA buffers, you'd also need memory barriers or cache maintenance. `volatile` only stops the compiler from removing accesses; it doesn't order them for other cores.
