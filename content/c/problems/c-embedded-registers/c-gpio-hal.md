---
id: c-gpio-hal
title: A GPIO Driver Against a Register Map
difficulty: Medium
order: 1
tags: registers, bit fields, volatile, BSRR, write-1-to-clear
time_limit: 2
---
## Statement
Write the lowest layer of a microcontroller GPIO driver. The register block is given (don't change it). The judge points your code at a block in RAM and **emulates the hardware** after each call, the way host-based firmware unit tests do.

```c
typedef struct {
    volatile uint32_t MODER;   /* 2 bits per pin: 0 input, 1 output, 2 alternate, 3 analog */
    volatile uint32_t PUPDR;   /* 2 bits per pin: 0 none, 1 pull-up, 2 pull-down          */
    volatile uint32_t IDR;     /* input levels, bit n = pin n (read only)                 */
    volatile uint32_t ODR;     /* output levels: NEVER write it directly                  */
    volatile uint32_t BSRR;    /* write-only: bit n sets pin n, bit n+16 resets pin n     */
    volatile uint32_t ISR;     /* interrupt flags, write-1-to-clear                       */
} Gpio;
```

Implement:

| Function | Behaviour |
|---|---|
| `uint32_t field_get(uint32_t reg, unsigned shift, unsigned width)` | Bits `[shift, shift+width)` of `reg`. Width 1..32, `shift + width <= 32`. |
| `uint32_t field_set(uint32_t reg, unsigned shift, unsigned width, uint32_t value)` | `reg` with that field replaced by `value` (masked to `width` bits). Other bits are unchanged. |
| `void gpio_mode(Gpio *g, unsigned pin, unsigned mode)` | Set the pin's 2-bit MODER field. |
| `void gpio_pull(Gpio *g, unsigned pin, unsigned pull)` | Set the pin's 2-bit PUPDR field. |
| `void gpio_write(Gpio *g, unsigned pin, int high)` | Exactly **one write to BSRR**. Don't touch ODR. |
| `void gpio_write_mask(Gpio *g, uint16_t set, uint16_t reset)` | One BSRR write that sets the `set` pins and resets the `reset` pins. |
| `int gpio_read(const Gpio *g, unsigned pin)` | 0 or 1 from IDR. |
| `void gpio_irq_clear(Gpio *g, uint32_t flags)` | Clear exactly `flags` in the W1C register `ISR`. |

- Pins are 0..15. For any **pin > 15** or **mode/pull > 3**, the call does nothing and writes no register (and `gpio_read` returns -1).
- Width 32 and shift 31 must work without undefined behaviour.

The emulator models real hardware:
- After each call, the value written to BSRR is applied to ODR (set bits win over reset bits), and BSRR reads back as 0.
- ISR is applied as W1C: `ISR = pending & ~written`.
- So `ISR |= f` clears *every* pending flag, and `ODR |= ...` is detected.

## Starter
```c
#include <stdint.h>

typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t ISR;
} Gpio;

uint32_t field_get(uint32_t reg, unsigned shift, unsigned width) {
    return (reg >> shift) & ((1u << width) - 1);
}
uint32_t field_set(uint32_t reg, unsigned shift, unsigned width, uint32_t value) {
    return reg | (value << shift);
}
void gpio_mode(Gpio *g, unsigned pin, unsigned mode) { g->MODER |= mode << (2 * pin); }
void gpio_pull(Gpio *g, unsigned pin, unsigned pull) { g->PUPDR |= pull << (2 * pin); }
void gpio_write(Gpio *g, unsigned pin, int high) {
    if (high) g->ODR |= 1u << pin; else g->ODR &= ~(1u << pin);
}
void gpio_write_mask(Gpio *g, uint16_t set, uint16_t reset) { g->ODR = (g->ODR | set) & ~reset; }
int gpio_read(const Gpio *g, unsigned pin) { return (g->IDR >> pin) & 1; }
void gpio_irq_clear(Gpio *g, uint32_t flags) { g->ISR |= flags; }
```

## Driver
```c
#include <stdio.h>
#include <string.h>

static uint32_t rng = 1;
static uint32_t rnd(void) { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; return rng; }

typedef struct { uint32_t odr, isr_pending; int bad; } Hw;
static Gpio G;
static Hw H;

static void hw_begin(void) { G.ODR = H.odr; G.ISR = H.isr_pending; G.BSRR = 0; }
static void hw_end(void) {
    if (G.ODR != H.odr) { H.bad |= 1; }                          /* ODR written directly */
    uint32_t b = G.BSRR, set = b & 0xFFFFu, reset = (b >> 16) & 0xFFFFu;
    H.odr = (H.odr & ~reset) | set;
    H.isr_pending &= ~G.ISR;                                    /* W1C: written ones clear */
    G.ODR = H.odr; G.BSRR = 0; G.ISR = H.isr_pending;
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "fields")) {
            printf("%08x %08x %08x %08x\n", field_get(0xDEADBEEFu, 4, 8), field_get(0xDEADBEEFu, 0, 32),
                   field_get(0x80000000u, 31, 1), field_get(0x12345678u, 28, 4));
            printf("%08x %08x %08x %08x\n", field_set(0xFFFFFFFFu, 4, 3, 5u), field_set(0, 0, 32, 0xCAFEBABEu),
                   field_set(0x7FFFFFFFu, 31, 1, 1u), field_set(0x0F0F0F0Fu, 8, 8, 0x1FFu));
            uint64_t h = 1469598103934665603ull;
            for (int i = 0; i < 200000; i++) {
                unsigned w = 1 + rnd() % 32, s = rnd() % (33 - w);
                uint32_t r = rnd(), v = rnd();
                h = (h ^ field_get(r, s, w)) * 1099511628211ull;
                h = (h ^ field_set(r, s, w, v)) * 1099511628211ull;
            }
            printf("fuzz %016llx\n", (unsigned long long)h);
        } else if (!strcmp(cmd, "config")) {
            memset(&G, 0, sizeof G); G.MODER = 0xABFFFFFFu; G.PUPDR = 0x24000000u;
            gpio_mode(&G, 5, 1); gpio_mode(&G, 15, 0); gpio_mode(&G, 0, 3); gpio_mode(&G, 13, 2);
            gpio_pull(&G, 5, 1); gpio_pull(&G, 14, 0); gpio_pull(&G, 2, 2);
            printf("MODER=%08x PUPDR=%08x\n", (unsigned)G.MODER, (unsigned)G.PUPDR);
            gpio_mode(&G, 16, 1); gpio_mode(&G, 3, 4); gpio_pull(&G, 99, 1); gpio_pull(&G, 1, 7);
            printf("after invalid: MODER=%08x PUPDR=%08x\n", (unsigned)G.MODER, (unsigned)G.PUPDR);
        } else if (!strcmp(cmd, "outputs")) {
            memset(&G, 0, sizeof G); memset(&H, 0, sizeof H); H.odr = 0x00F0u;
            int pins[] = {0, 5, 4, 15, 7, 0}, lv[] = {1, 1, 0, 1, 0, 0};
            for (int i = 0; i < 6; i++) { hw_begin(); gpio_write(&G, (unsigned)pins[i], lv[i]); hw_end(); printf("%04x ", (unsigned)H.odr); }
            hw_begin(); gpio_write(&G, 16, 1); hw_end(); printf("%04x ", (unsigned)H.odr);
            hw_begin(); gpio_write_mask(&G, 0x0003u, 0x8020u); hw_end(); printf("%04x ", (unsigned)H.odr);
            hw_begin(); gpio_write_mask(&G, 0x0100u, 0x0101u); hw_end(); printf("%04x\n", (unsigned)H.odr);
            printf("odr written directly: %s\n", H.bad ? "yes" : "no");
        } else if (!strcmp(cmd, "inputs")) {
            memset(&G, 0, sizeof G); G.IDR = 0x8421u;
            for (unsigned p = 0; p < 17; p++) printf("%d", gpio_read(&G, p) < 0 ? 9 : gpio_read(&G, p));
            printf("\n");
        } else if (!strcmp(cmd, "irq")) {
            memset(&G, 0, sizeof G); memset(&H, 0, sizeof H); H.isr_pending = 0x0000F00Fu;
            hw_begin(); gpio_irq_clear(&G, 0x1u); hw_end(); printf("%08x ", (unsigned)H.isr_pending);
            hw_begin(); gpio_irq_clear(&G, 0x3000u); hw_end(); printf("%08x ", (unsigned)H.isr_pending);
            hw_begin(); gpio_irq_clear(&G, 0x0u); hw_end(); printf("%08x\n", (unsigned)H.isr_pending);
        } else if (!strcmp(cmd, "random")) {
            memset(&G, 0, sizeof G); memset(&H, 0, sizeof H); rng = 2024;
            uint64_t h = 1469598103934665603ull;
            for (int i = 0; i < 300000; i++) {
                unsigned op = rnd() % 5, pin = rnd() % 18, v = rnd() % 5;
                hw_begin();
                if (op == 0) gpio_mode(&G, pin, v);
                else if (op == 1) gpio_pull(&G, pin, v);
                else if (op == 2) gpio_write(&G, pin, (int)(v & 1));
                else if (op == 3) gpio_write_mask(&G, (uint16_t)rnd(), (uint16_t)rnd());
                else { H.isr_pending |= rnd() & 0xFFFFu; hw_begin(); gpio_irq_clear(&G, rnd() & 0xFFu); }
                hw_end();
                h = (h ^ G.MODER) * 1099511628211ull; h = (h ^ G.PUPDR) * 1099511628211ull;
                h = (h ^ H.odr) * 1099511628211ull;   h = (h ^ H.isr_pending) * 1099511628211ull;
            }
            printf("state %016llx bad=%d\n", (unsigned long long)h, H.bad);
        }
    }
    return 0;
}
```

## Tests
=== sample
fields
config
---
000000ee deadbeef 00000001 00000001
ffffffdf cafebabe ffffffff 0f0fff0f
fuzz 1c7de5316080f131
MODER=2bfff7ff PUPDR=04000420
after invalid: MODER=2bfff7ff PUPDR=04000420
=== hidden
outputs
inputs
---
00f1 00f1 00e1 80e1 8061 8060 8060 0043 0142
odr written directly: no
10000100001000019
=== hidden
irq
---
0000f00e 0000c00e 0000c00e
=== hidden
random
---
state 714c5f7ca59d35e1 bad=0

## Hints
- Build the mask without UB: `width == 32 ? 0xFFFFFFFFu : ((1u << width) - 1u)`.
- `field_set`: `(reg & ~(mask << shift)) | ((value & mask) << shift)`.
- The register helpers become one-liners: `g->MODER = field_set(g->MODER, 2 * pin, 2, mode);`.
- BSRR: `g->BSRR = high ? 1u << pin : 1u << (pin + 16)`. For the mask version, `(uint32_t)set | ((uint32_t)reset << 16)`.
- A W1C clear is a plain assignment: `g->ISR = flags;`.

## Solution
```c
#include <stdint.h>

typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t ISR;
} Gpio;

static uint32_t mask_of(unsigned width) { return width >= 32u ? 0xFFFFFFFFu : ((1u << width) - 1u); }

uint32_t field_get(uint32_t reg, unsigned shift, unsigned width) {
    return (reg >> shift) & mask_of(width);
}

uint32_t field_set(uint32_t reg, unsigned shift, unsigned width, uint32_t value) {
    const uint32_t m = mask_of(width);
    return (reg & ~(m << shift)) | ((value & m) << shift);
}

void gpio_mode(Gpio *g, unsigned pin, unsigned mode) {
    if (pin > 15u || mode > 3u) return;
    g->MODER = field_set(g->MODER, 2u * pin, 2u, mode);
}

void gpio_pull(Gpio *g, unsigned pin, unsigned pull) {
    if (pin > 15u || pull > 3u) return;
    g->PUPDR = field_set(g->PUPDR, 2u * pin, 2u, pull);
}

void gpio_write(Gpio *g, unsigned pin, int high) {
    if (pin > 15u) return;
    g->BSRR = high ? (1u << pin) : (1u << (pin + 16u));      /* one atomic write, no read */
}

void gpio_write_mask(Gpio *g, uint16_t set, uint16_t reset) {
    g->BSRR = (uint32_t)set | ((uint32_t)reset << 16);
}

int gpio_read(const Gpio *g, unsigned pin) {
    if (pin > 15u) return -1;
    return (int)field_get(g->IDR, pin, 1u);
}

void gpio_irq_clear(Gpio *g, uint32_t flags) {
    g->ISR = flags;                                            /* W1C: write exactly the bits to clear */
}
```

- **Masks** are built without undefined behaviour: `1u << 32` is UB, so width 32 is special-cased. Everything is unsigned.
- **`field_set`** clears the field before ORing, so it works whatever the field held before. The starter's `|=` versions only ever turn bits on.
- **BSRR** makes output changes atomic. There's no read-modify-write window for an ISR to slip into, and ODR is never written.
- **W1C**: `ISR = flags` clears exactly those flags. `ISR |= flags` writes back every pending flag as 1, so it acknowledges interrupts that were never serviced. Those events are silently lost: a classic firmware bug.
- **Argument validation** at the API boundary means a bad pin number can't corrupt a neighbouring field or shift by 32+.
