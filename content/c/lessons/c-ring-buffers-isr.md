# Ring Buffers, Interrupts and Real-Time

Sensors produce data on their own schedule: a UART byte arrives, an encoder ticks, an IMU signals "data ready". The CPU learns about it through **interrupts**. Getting data safely from an interrupt service routine (ISR) to the main loop, without losing bytes, corrupting state or missing deadlines, is the central problem of embedded real-time programming. The standard tool is the **single-producer single-consumer (SPSC) ring buffer**. This lesson covers interrupts and ISR rules, the lock-free ring buffer with C11 atomics, critical sections, latency and jitter, and real-time scheduling.

## 1. Interrupts in one picture

When a peripheral raises an interrupt, the CPU:
1. Finishes the current instruction.
2. Saves registers (on Cortex-M, hardware stacks r0–r3, r12, LR, PC and xPSR automatically).
3. Jumps to the handler listed in the **vector table**.
4. Returns to the interrupted code when the handler finishes.

The **NVIC** prioritises interrupts, and a higher-priority interrupt can preempt a lower-priority ISR.

```c
volatile uint32_t ticks;                    /* shared with the main loop */
void SysTick_Handler(void) { ticks++; }     /* called every 1 ms by hardware */
```

## 2. ISR rules

> [!KEY]
> - **Keep ISRs short**: read the hardware, push to a buffer, clear the flag, return. Do the processing in the main loop or a task.
> - **No blocking**: no `malloc`, `printf`, mutexes, or waiting on other interrupts.
> - **Only call reentrant, async-safe functions** (the same idea as POSIX signal handlers).
> - **Clear the interrupt flag** correctly (often W1C, see the register lesson), or the ISR fires again immediately and forever.
> - **Shared variables** need `volatile` *and* atomic access. On a 32-bit CPU, a 64-bit counter is read in two halves and can tear.

## 3. The SPSC ring buffer

A fixed array plus two indices. The producer (ISR) writes at `head`, and the consumer (main loop) reads at `tail`. Each index is written by only **one** side, so no lock is needed, only correct memory ordering.

```c
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

#define RB_SIZE 256u                          /* power of two */
_Static_assert((RB_SIZE & (RB_SIZE - 1)) == 0, "size must be a power of two");

typedef struct {
    uint8_t data[RB_SIZE];
    _Atomic uint32_t head;                    /* written only by the producer */
    _Atomic uint32_t tail;                    /* written only by the consumer */
} Ring;

bool rb_push(Ring *r, uint8_t b) {            /* producer (ISR) */
    uint32_t h = atomic_load_explicit(&r->head, memory_order_relaxed);
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_acquire);
    if (h - t == RB_SIZE) return false;       /* full: drop and count an overrun */
    r->data[h & (RB_SIZE - 1)] = b;
    atomic_store_explicit(&r->head, h + 1, memory_order_release);   /* publish AFTER the data write */
    return true;
}

bool rb_pop(Ring *r, uint8_t *out) {          /* consumer (main loop) */
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_relaxed);
    uint32_t h = atomic_load_explicit(&r->head, memory_order_acquire);
    if (h == t) return false;                 /* empty */
    *out = r->data[t & (RB_SIZE - 1)];
    atomic_store_explicit(&r->tail, t + 1, memory_order_release);   /* free the slot AFTER reading */
    return true;
}
```

Design choices worth understanding:
- **Free-running indices** with `h - t` as the count: unsigned subtraction wraps correctly, so all `RB_SIZE` slots are usable. The alternative, "keep one slot empty", wastes a slot but works with indices that wrap at N.
- **Power-of-two size**: `& (N-1)` replaces the slow `%`.
- **Release/acquire pairs**: the producer's release-store of `head` makes the data write visible before the consumer, after its acquire-load of `head`, reads the slot. On a single-core MCU, compiler ordering is what matters. On multicore or with DMA, the hardware order matters too.
- **Overrun policy**: drop the newest (shown here), overwrite the oldest (for "latest sensor value" streams; this needs the consumer to tolerate it), or signal an error. Always **count** drops so they're visible in telemetry.

> [!DANGER]
> A `volatile` index without atomics or barriers is not enough on multicore systems, and neither is incrementing `count` from both sides. `count++` in the ISR and `count--` in main is a read-modify-write race. Exactly this bug has lost UART bytes in shipped products.

## 4. Critical sections

When data has multiple writers, or a structure is updated in several steps (a 64-bit timestamp, a struct of pose fields), briefly disable interrupts:

```c
uint32_t primask = __get_PRIMASK();
__disable_irq();
pose_copy = shared_pose;          /* a consistent snapshot */
__set_PRIMASK(primask);           /* restore, rather than blindly enabling (nesting-safe) */
```

Keep critical sections to a few microseconds, because they add directly to interrupt latency. Alternatives: raise `BASEPRI` to mask only lower-priority interrupts, use double buffering (the ISR writes into the inactive buffer and flips an index), or use a **seqlock** (version counter around the write; the reader retries if the counter was odd or changed).

## 5. Latency, jitter and deadlines

| Term | Meaning |
|---|---|
| **Interrupt latency** | event → first ISR instruction (Cortex-M: 12 cycles, plus any time interrupts were disabled) |
| **Response time** | event → work completed |
| **Jitter** | variation in period or latency; it destabilises control loops |
| **Hard real-time** | missing a deadline is a failure (airbag, motor commutation) |
| **Soft real-time** | missing degrades quality (video frame, telemetry) |

A 1 kHz motor current loop must finish within 1 ms *every* time. The average doesn't matter, only the **worst-case execution time (WCET)**. Things that destroy WCET: dynamic allocation, unbounded loops, cache misses, page faults, and priority inversion.

## 6. Real-time scheduling in brief

- **Super-loop**: `for(;;){ read(); compute(); write(); }`, plus ISRs. It's simple, but every task's latency depends on all the others.
- **RTOS** (FreeRTOS, Zephyr, NuttX): preemptive fixed-priority tasks. **Rate-monotonic** priority assignment (shorter period gets higher priority) is optimal for fixed priorities. A task set is schedulable if utilisation `U = Σ Cᵢ/Tᵢ ≤ n(2^{1/n} − 1)`, which tends to ln 2 ≈ 69%.
- **Priority inversion**: a low-priority task holds a mutex, a high-priority task waits for it, and a medium-priority task preempts the low one. The high-priority task then waits indefinitely, which reset the Mars Pathfinder in 1997. The fix is a **priority-inheritance** mutex.
- **Linux with PREEMPT_RT** for ROS 2 control:
  - `SCHED_FIFO` priorities.
  - `mlockall(MCL_CURRENT|MCL_FUTURE)` to avoid page faults.
  - Pre-allocate everything before the loop.
  - `clock_nanosleep(TIMER_ABSTIME)` for drift-free periods.

```c
struct timespec next; clock_gettime(CLOCK_MONOTONIC, &next);
for (;;) {
    control_step();
    next.tv_nsec += 1000000;                         /* 1 ms period, absolute: no drift */
    if (next.tv_nsec >= 1000000000) { next.tv_nsec -= 1000000000; next.tv_sec++; }
    clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
}
```

> [!EXAM]
> **Why is an SPSC ring buffer safe without a lock, and what memory ordering does it need?**
> Each index has exactly one writer: the producer only advances `head` and the consumer only advances `tail`, so there's never a concurrent write to the same variable. Correctness then depends on ordering. The producer must write the data slot *before* publishing the new `head` (release store), and the consumer must read `head` with acquire before reading the slot. Symmetrically, the consumer publishes `tail` with release after reading, so the producer can't overwrite a slot that's still being read. With free-running unsigned indices, `head − tail` gives the fill level even across wrap-around.
