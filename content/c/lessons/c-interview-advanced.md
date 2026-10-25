# C Interview Deep Dive II

The second interview round goes beneath the language: how a process is laid out in memory, what undefined behaviour really means to an optimiser, how bytes are ordered, how functions are called at the machine level, how programs are linked and loaded, and the embedded-systems questions every robotics firmware interview includes. Each section gives the answer you'd give at a whiteboard, plus the detail that distinguishes an expert.

## 1. Process memory layout

```text
high addresses  +------------------+
                | stack (grows ↓)  |  locals, return addresses, saved registers
                |        ...       |
                | mmap region      |  shared libraries, large malloc blocks, thread stacks
                |        ...       |
                | heap (grows ↑)   |  malloc/free (brk + mmap)
                | .bss             |  zero-initialised globals/statics (no file space)
                | .data            |  initialised globals/statics
                | .rodata          |  string literals, const globals
low addresses   | .text            |  machine code
                +------------------+
```

- **Stack overflow** comes from deep recursion or large local arrays. The default main-thread stack on Linux is 8 MB (`ulimit -s`), while an RTOS task often has only a few KB.
- **ASLR** randomises these bases on each run, which mitigates exploits. Run `cat /proc/self/maps` to see the real layout.
- Returning a pointer to a local variable is a dangling pointer: its stack slot is reused by the next call.

## 2. `malloc` internals, briefly

glibc's ptmalloc keeps size-classed **bins** of free chunks, each with a header (size and flags) just before the user pointer. That's why freeing a pointer `malloc` never returned, or overflowing a buffer into the next chunk's header, corrupts the heap. Large requests (≥ 128 KB by default) use `mmap` directly. Questions to expect:
- `free(NULL)` is a no-op.
- `realloc` may move the block, so always assign the result to a temporary first.
- **Fragmentation** can make allocations fail even when total free memory is enough, which is one reason embedded code avoids the heap after initialisation.

## 3. Undefined behaviour and the optimiser

UB means the standard imposes **no requirements**. Optimisers assume UB never happens and reason from that assumption:

```c
int check(int x) { return x + 1 > x; }     /* compiled to "return 1": signed overflow can't happen */

void f(int *p) {
    int v = *p;                            /* dereference implies p != NULL ... */
    if (p == NULL) return;                 /* ... so this check is deleted */
}
```

The common UB list:
- signed overflow;
- out-of-bounds access, use-after-free, double free;
- NULL dereference;
- uninitialised reads;
- shifts by ≥ the width or of negative values;
- strict-aliasing violations;
- unsequenced modifications (`i = i++`);
- data races;
- a missing `return` value that's then used;
- modifying string literals.

**Implementation-defined** behaviour, such as the signedness of `char`, right-shifting negative numbers and `sizeof(long)`, is documented per platform. **Unspecified** behaviour, such as argument evaluation order, is one of several allowed choices.

> [!INTERVIEW] What is strict aliasing?
> The compiler may assume that pointers to incompatible types don't point to the same object. Accessing a `float` through an `int *` (`*(int *)&f`) is UB, and the optimiser may reorder or cache values. Character types may alias anything. The safe way to reinterpret bits is `memcpy(&i, &f, sizeof i)`, which compiles to a single move, or a union (allowed in C, but not in C++).

## 4. Endianness

Endianness is the byte order of multi-byte values in memory. **Little-endian** (x86, most ARM configurations) stores the least significant byte first. **Big-endian** ("network byte order") stores the most significant byte first.

```c
int is_little(void) { uint32_t x = 1; unsigned char b; memcpy(&b, &x, 1); return b == 1; }

uint32_t read_be32(const uint8_t *p) {           /* portable: shifts don't depend on host order */
    return (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | p[3];
}
```

Use `htonl`/`ntohl` for sockets, and `__builtin_bswap32` when a byte swap is needed. The interview answer is "serialise with shifts, never by casting buffers to struct pointers", because that also avoids alignment and aliasing problems.

## 5. Calling conventions and the stack frame

On x86-64 System V (Linux and macOS):
- The first six integer or pointer arguments go in `rdi, rsi, rdx, rcx, r8, r9`, and floating-point arguments in `xmm0–7`.
- The return value comes back in `rax` (or `xmm0`).
- `rbx, rbp, r12–r15` are callee-saved.
- The stack is 16-byte aligned at each call.

Windows x64 uses `rcx, rdx, r8, r9` plus 32 bytes of shadow space. On ARM AAPCS, arguments go in `r0–r3` (32-bit) or `x0–x7` (AArch64).

A call pushes the return address. The callee typically saves the frame pointer and reserves space for locals, and **stack canaries** (`-fstack-protector`) detect overwrites of the return address. Recursion depth costs one frame per level. Tail calls can be turned into jumps at `-O2`, but C doesn't guarantee it.

## 6. Compilation, linking and loading

**Preprocess** (`gcc -E`), **compile** to assembly (`-S`), **assemble** to object files (`-c`), then **link**.
- Object files contain **symbols** (`nm`): `T` for defined text, `U` for undefined, `D`/`B` for data and bss.
- The linker resolves undefined references, combines sections, and applies relocations.
- Static linking copies code in. Dynamic linking defers it to `ld.so` at load time, using the PLT/GOT and lazy binding.

Classic errors are "undefined reference" (missing definition or library, or wrong link order) and "multiple definition" (a definition in a header). **Weak symbols** (`__attribute__((weak))`) provide overridable defaults, which embedded startup code uses for its default interrupt handlers.

## 7. Embedded questions

| Question | Answer |
|---|---|
| What happens between reset and `main`? | The CPU loads the initial stack pointer and reset vector from the vector table. Startup code copies `.data` from flash to RAM, zeroes `.bss`, sets up clocks and the FPU, runs constructors, then calls `main`. |
| Why is `main` never supposed to return on an MCU? | There's no OS to return to. Firmware runs an infinite loop or hands over to the RTOS scheduler. |
| What's in an ISR, and what isn't? | Short work: read the hardware, clear the flag, push to a queue. Never block, never `malloc`/`printf`. Shared variables need `volatile` plus atomic access or critical sections. |
| How do you share data with an ISR? | An SPSC ring buffer with atomic indices, or briefly disabling interrupts around multi-word updates. |
| What is a watchdog? | A hardware timer that resets the MCU unless it's refreshed periodically. Kick it from the main loop after health checks. |
| What is priority inversion? | A low-priority task holding a resource blocks a high-priority one while medium-priority tasks run. The fix is priority inheritance. |
| Bit-banding and atomic register updates? | Set/reset registers, LDREX/STREX, or disabling interrupts around read-modify-write. |
| How do you find the stack high-water mark? | Paint the stack with a pattern at boot and scan for the deepest overwritten word, or use `-fstack-usage` together with the call graph. |
| Fixed-point vs float on an MCU without an FPU? | Q-format integers: widen, multiply, round, saturate. |
| How do you debug a hard fault on Cortex-M? | Read the stacked PC and LR plus the CFSR/HFSR/MMFAR/BFAR fault status registers in the handler. The stacked PC points at the faulting instruction. |

## 8. Concurrency questions

- **Race condition**: an outcome that depends on timing. A data race on a non-atomic object is UB in C11.
- **Deadlock** needs four conditions: mutual exclusion, hold-and-wait, no preemption, and circular wait. Prevent it with a **global lock ordering**.
- **Mutex vs semaphore**: a mutex has an owner (whoever locked it must unlock it) and may support priority inheritance. A counting semaphore signals resource counts or events and has no owner.
- **`volatile` isn't for threads.** Use `<stdatomic.h>` with appropriate memory orders, or pthread primitives.
- **Spinlock vs mutex**: spinning suits very short critical sections on multicore (or interrupt context). Sleeping suits longer waits.

> [!EXAM]
> **Why can code with undefined behaviour "work" in a debug build and fail in a release build?**
> The C standard places no requirements on a program that executes undefined behaviour, and optimisers rely on that: they assume UB never occurs and transform the code accordingly. They delete overflow checks written after the overflow, remove NULL checks that follow a dereference, cache values across aliasing violations, and reorder unsequenced side effects. At `-O0` the generated code mirrors the source and the bug may be invisible. At `-O2` those assumptions change the program's logic. The fix is to remove the UB (sanitizers like `-fsanitize=undefined,address` find it), not to lower the optimisation level.
