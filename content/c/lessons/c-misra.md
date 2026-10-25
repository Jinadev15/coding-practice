# Safety-Critical C (MISRA)

C runs brakes, pacemakers, flight controls and industrial robots, but its undefined behaviour, silent conversions and unchecked memory make it dangerous by default. Safety-critical industries therefore restrict C to a **subset** and back it with process: coding standards (MISRA C, CERT C), static analysis, mandatory reviews, coverage-driven testing, and certification standards. This lesson explains why these standards exist, the key MISRA C:2023 rules and their rationale, and the defensive-programming techniques you should adopt even when no certifier is watching.

## 1. Why a subset of C?

Field failures teach the same lessons repeatedly:
- **Toyota unintended acceleration** (2013 testimony): stack overflow, global-variable soup (about 10,000 globals), recursion, and a watchdog that couldn't catch task death.
- **Therac-25**: race conditions that killed patients.
- **Ariane 5**: an unchecked conversion of a 64-bit float to a 16-bit integer.

The certification standards demand a defined coding standard and evidence of compliance:

| Standard | Domain | Integrity levels |
|---|---|---|
| IEC 61508 | industrial (the generic parent) | SIL 1–4 |
| ISO 26262 | automotive | ASIL A–D |
| DO-178C | avionics | DAL E–A |
| IEC 62304 | medical | Class A–C |
| ISO 10218 / ISO 13849 | industrial robots | PL a–e |

**MISRA C** (first edition 1998, current MISRA C:2023) is the most widely adopted. Its rules are classified as **Mandatory**, **Required** (deviation allowed with documented justification) or **Advisory**, and as decidable (a tool can check them) or undecidable.

## 2. Key rules and their reasons

| Rule (MISRA C:2023, paraphrased) | Why |
|---|---|
| **Dir 4.1, Rule 1.3**: no undefined or critical unspecified behaviour | UB lets the optimiser do anything |
| **10.x Essential type model**: no implicit conversions between essential types (signed↔unsigned, int↔float, narrowing); no mixing in arithmetic | `-1 < 1u` is false; `uint8_t + uint8_t` is `int` |
| **12.2** shift amount must be within the width | `1u << 32` is UB |
| **13.x** no side effects in `&&`/`\|\|` right operands or `sizeof`; increment/decrement not mixed with other side effects | evaluation order traps |
| **14.4** controlling expressions must be essentially Boolean | `if (x = 5)`, `if (ptr)` style is banned |
| **15.5** (advisory) single exit point per function | simplifies reasoning and coverage |
| **15.7** every `if … else if` chain ends in `else` | forces a decision on the remaining case |
| **16.4** every `switch` has a `default` | handles corrupted or unexpected values |
| **17.2** no recursion | stack depth must be statically bounded |
| **17.7** the return value of non-void functions must be used | ignored error codes |
| **18.x** pointer arithmetic only within the same array; no pointers to automatic storage escaping | out-of-bounds and dangling pointers |
| **21.3** no `malloc`/`free` (dynamic memory) | fragmentation, non-deterministic timing, out-of-memory at runtime |
| **21.x** no `<setjmp.h>`, `<signal.h>`, `atoi`, `abort`, `exit`, `system` | undefined or unsafe behaviour |
| **Dir 4.6** use fixed-width typedefs (`int32_t`), not `int` | portability |
| **8.x** objects declared at block scope if used only there; `static` for internal linkage | minimal scope and coupling |
| **Dir 4.7** test every error return | |

## 3. What compliant code looks like

```c
#include <stdint.h>
#include <stdbool.h>

typedef enum { SPEED_OK = 0, SPEED_ERR_NULL, SPEED_ERR_RANGE } SpeedStatus;

#define WHEEL_MAX_RPM   ((int32_t)6000)

/* Converts encoder ticks over dt to RPM; single exit; all paths assign *rpm or report an error. */
SpeedStatus wheel_rpm(int32_t ticks, uint32_t dt_us, uint32_t ticks_per_rev, int32_t *rpm) {
    SpeedStatus status = SPEED_OK;
    if (rpm == NULL) {
        status = SPEED_ERR_NULL;
    } else if ((dt_us == 0u) || (ticks_per_rev == 0u)) {
        status = SPEED_ERR_RANGE;
    } else {
        /* widen before multiplying: ticks * 60e6 overflows int32 */
        int64_t num = (int64_t)ticks * (int64_t)60000000;
        int64_t den = (int64_t)dt_us * (int64_t)ticks_per_rev;
        int64_t v = num / den;
        if ((v > (int64_t)WHEEL_MAX_RPM) || (v < -(int64_t)WHEEL_MAX_RPM)) {
            status = SPEED_ERR_RANGE;
        } else {
            *rpm = (int32_t)v;
        }
    }
    return status;
}
```

Notice:
- Explicit casts at every type change, and `u` suffixes.
- Boolean conditions written explicitly (`rpm == NULL`, not `!rpm`).
- A final `else`, and a single return.
- A status enum instead of magic numbers.
- No dynamic memory.

## 4. Defensive programming techniques

- **Validate at boundaries**: every input from a sensor, a bus or another module is untrusted. Check ranges, lengths, CRCs and sequence counters, and reject stale timestamps.
- **Static allocation**: size every buffer and pool at compile time. Use `_Static_assert` to tie sizes together.
- **Bounded loops**: every loop has a provable maximum iteration count, and polling loops have timeouts.
- **Fail safe**: on an unexpected state (`default:`), go to the safe state (motors off, brakes on). Don't try to continue.
- **Redundancy for critical data**: store critical variables twice (once inverted) and compare before use, to catch RAM bit flips. Use CRC-protected configuration blocks in flash.
- **Watchdog**: hardware that resets the MCU unless "kicked" periodically. Kick it only from the main loop after checking that every task has reported progress, never from a timer ISR (which keeps running after the main loop hangs).
- **Stack monitoring**: paint the stack with a pattern at boot and check the high-water mark. Without recursion, worst-case stack depth can be computed statically (GCC's `-fstack-usage`).
- **Assertions that stay on**: a custom `SAFE_ASSERT` that logs and drives to the safe state, rather than an `assert` compiled out by `NDEBUG`.

## 5. Tooling

| Tool type | Examples |
|---|---|
| Compiler warnings | `-Wall -Wextra -Wconversion -Wsign-conversion -Wshadow -Wcast-qual -Wswitch-enum -Werror` |
| MISRA checkers | PC-lint Plus, Polyspace Bug Finder, LDRA, Helix QAC, Parasoft, cppcheck's MISRA addon |
| Sound static analysis | Polyspace Code Prover, Astrée, Frama-C (prove the absence of runtime errors) |
| Dynamic | sanitizers (`-fsanitize=address,undefined`), Valgrind, fuzzing (libFuzzer, AFL++) on host builds |
| Coverage | statement, branch and **MC/DC** (modified condition/decision coverage, required for DO-178C Level A) via gcov or LDRA |

> [!TIP]
> Even without certification, adopt the cheap high-value subset: `-Wconversion -Werror`, no dynamic allocation after initialisation, fixed-width types, every switch with a default, every return value checked, bounded loops, and sanitizers plus fuzzing in CI. That catches most of what MISRA catches.

> [!EXAM]
> **Why does MISRA ban dynamic memory allocation and recursion?**
> Both make resource usage unbounded and hard to analyse. With `malloc`, fragmentation can make an allocation fail at runtime long after deployment, allocation time is non-deterministic (bad for worst-case execution time), and leaks or double frees become possible. With recursion, the maximum stack depth depends on input data, so it can't be proven statically that the stack never overflows. Without either, all memory is accounted for at compile or link time, and worst-case stack usage can be computed from the call graph.
