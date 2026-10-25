# Debugging with GDB

Every C programmer eventually faces a crash with no message, a value that's mysteriously wrong, or a hang. Guessing with `printf` scales badly. A **debugger** lets you stop the program anywhere, inspect any variable or memory, walk the call stack, and watch data change. Sanitizers find many bugs before you ever need one. This lesson covers GDB's essential workflow, post-mortem debugging with core files, watchpoints, debugging optimised and multithreaded code, sanitizers, and a systematic approach to debugging.

## 1. Build for debugging

```bash
gcc -g -O0 -Wall -Wextra -o avg avg.c        # -g: DWARF debug info; -O0: variables are not optimised away
gcc -g3 -Og ...                              # -g3 adds macros; -Og optimises but stays debuggable
```

Debug info maps machine code back to source lines and variables. It doesn't change the code, so `-O2 -g` is fine for release builds, and you can strip and store the symbols separately.

## 2. A first session

```c
typedef struct { int n; double *v; } Series;
double mean(const Series *s) {
    double sum = 0;
    for (int i = 0; i <= s->n; i++) sum += s->v[i];
    return sum / s->n;
}
int main(void) { Series s = { 3, NULL }; printf("%f\n", mean(&s)); }
```

```output
$ gdb -q ./avg
(gdb) run
Program received signal SIGSEGV, Segmentation fault.
0x000055555555519c in mean (s=0x7fffffffd870) at avg.c:6
6	    for (int i = 0; i <= s->n; i++) sum += s->v[i];
(gdb) bt
#0  0x000055555555519c in mean (s=0x7fffffffd870) at avg.c:6
#1  0x0000555555555214 in main () at avg.c:11
(gdb) print *s
$1 = {n = 3, v = 0x0}
(gdb) print i
$2 = 0
```

In three commands we know where it crashed (line 6, called from `main`), why (`v` is NULL), and on which iteration. Reading the line also reveals a second bug: `i <= s->n` reads one element past the end.

## 3. Essential commands

| Command | Short | Purpose |
|---|---|---|
| `run [args] < input` | `r` | start (with redirection) |
| `break file.c:42` / `break func` | `b` | breakpoint |
| `break 42 if i == 999` | | conditional breakpoint |
| `tbreak`, `delete N`, `disable N`, `info breakpoints` | | manage breakpoints |
| `next` / `step` | `n` / `s` | over / into a call |
| `finish` | | run until the current function returns (shows the return value) |
| `continue` | `c` | resume |
| `until 50` / `advance 50` | | run to line 50 (skips the rest of a loop) |
| `backtrace [full]` | `bt` | call stack (`full` adds locals) |
| `frame N`, `up`, `down` | `f` | select a stack frame |
| `print expr` | `p` | evaluate any C expression: `p *arr@10`, `p/x flags`, `p sizeof(Node)` |
| `display expr` | | print at every stop |
| `info locals` / `info args` | | variables |
| `x/16xb ptr` | | examine memory: 16 hex bytes (`x/4dw` = 4 decimal words, `x/s` = string) |
| `ptype var` | | show a type definition |
| `set var x = 5` | | change state and test a hypothesis |
| `watch expr` / `rwatch` / `awatch` | | stop when a value is written / read / accessed |
| `layout src` / `tui enable` | | source window (Ctrl-X A toggles) |

`p *arr@n` prints n elements starting at `arr`, which is essential for heap arrays where GDB doesn't know the length.

## 4. Watchpoints: who changed this variable?

A value is corrupted somewhere among 50 functions. Set a **hardware watchpoint**, and the CPU's debug registers stop the program at the exact instruction that writes it:

```output
(gdb) break main
(gdb) run
(gdb) watch robot.pose.x
Hardware watchpoint 2: robot.pose.x
(gdb) continue
Hardware watchpoint 2: robot.pose.x
Old value = 1.5
New value = -nan(0x8000000000000)
update_odometry (r=0x7ffd...) at odom.c:88
```

x86 provides 4 hardware watchpoints. Software watchpoints single-step and are extremely slow. For a heap object, watch the address: `watch -l node->next`.

## 5. Post-mortem: core dumps

When a program crashes in the field or in CI, debug the **core file**, a snapshot of its memory at the moment of death:

```bash
ulimit -c unlimited                     # allow core files in this shell
./robot                                 # Segmentation fault (core dumped)
coredumpctl list && coredumpctl gdb     # systemd systems keep cores here
gdb ./robot core                        # or open a core file directly
```

`bt`, `frame` and `print` all work. You can't continue execution, but you can see exactly where and why the program died. `gdb -batch -ex bt ./robot core` prints a backtrace non-interactively, which is perfect for CI logs.

## 6. Attaching, threads and optimised code

- `gdb -p PID` attaches to a running (hung) process. `bt` shows where it's stuck: a deadlock shows two threads blocked in `pthread_mutex_lock`.
- `info threads`, `thread 3`, and `thread apply all bt` show every thread's stack, the first command to run for a hang.
- In optimised code, variables show `<optimized out>` and stepping jumps around because the code was reordered. Use `-Og`, or reason from `disassemble` and `info registers`.
- Embedded: GDB talks to the MCU through a debug probe (`openocd` or a J-Link GDB server; `target extended-remote :3333`). The same commands work on hardware breakpoints in flash.

## 7. Sanitizers: let the compiler find bugs first

```bash
gcc -g -fsanitize=address,undefined -fno-omit-frame-pointer prog.c && ./a.out
```

| Sanitizer | Finds | Cost |
|---|---|---|
| AddressSanitizer (`address`) | out-of-bounds (heap, stack, globals), use-after-free, double free, leaks | ~2x time, ~3x memory |
| UndefinedBehaviorSanitizer (`undefined`) | signed overflow, bad shifts, null dereference, misaligned access, invalid enum/bool | small |
| ThreadSanitizer (`thread`) | data races | 5–15x |
| MemorySanitizer (Clang, `memory`) | uninitialised reads | 3x |

ASan reports the bad access with a stack trace, plus where the memory was allocated and freed: often a better answer than a debugger session. **Valgrind** (`valgrind --leak-check=full ./prog`) needs no recompilation but runs 20–50x slower. Run sanitizer builds in CI on every commit.

## 8. A systematic method

1. **Reproduce** reliably: the same input and seed, the smallest failing case. Use `git bisect run ./test.sh` to find the commit that broke it.
2. **Observe**: where does reality diverge from expectation? Use breakpoints, watchpoints and assertions.
3. **Hypothesise**, then test it (`set var`, a small experiment). Don't change code at random.
4. **Fix the cause**, not the symptom. Then add a regression test.

> [!EXAM]
> **A program crashes intermittently in production after hours of running. How do you debug it?**
> Enable core dumps (`ulimit -c unlimited`, or systemd-coredump) and keep the matching debug symbols for the deployed binary. When it crashes, open the core in GDB: `bt` (plus `thread apply all bt`) shows the crash site and every thread's stack, and `frame`/`print` inspect the state. Intermittent behaviour suggests memory corruption or a race, so reproduce under AddressSanitizer/UBSan and ThreadSanitizer with stress tests or fuzzing. Once the corrupted variable is identified, a hardware watchpoint finds the faulty writer.
