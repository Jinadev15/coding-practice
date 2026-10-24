# Memory Bugs: Leaks, Dangling Pointers, Overflows

Memory errors are the most expensive bug class in software. Microsoft and Google have both reported that **about 70% of their serious security vulnerabilities** are memory-safety bugs in C and C++. They're dangerous because they often don't crash where they happen: a write one byte past an array can corrupt allocator metadata and crash minutes later in unrelated code, or silently hand an attacker control. This lesson catalogues the bug types, shows what each looks like, and teaches the tools that find them (**AddressSanitizer**, **UBSan**, **Valgrind**), plus the habits that prevent them.

## 1. The catalogue

| Bug | What happens | Typical symptom |
|---|---|---|
| **Memory leak** | allocated memory is never freed, and the last pointer to it is lost | memory use grows until OOM; long-running daemons and robots die after hours |
| **Use-after-free** (UAF) | accessing a block after `free` | garbage reads, corruption; a top exploit primitive |
| **Double free** | `free` called twice on the same block | allocator corruption, abort ("double free detected") |
| **Heap buffer overflow** | writing past the end of a `malloc` block | corrupts the neighbouring block's metadata, crashing later |
| **Stack buffer overflow** | writing past a local array | overwrites the return address: the classic exploit |
| **Dangling stack pointer** | using a pointer to a local after its function returned | garbage that changes "randomly" |
| **Uninitialised read** | reading a local or `malloc` memory before writing it | non-deterministic behaviour (works in debug, fails in release) |
| **NULL dereference** | using an unchecked `malloc` result or a missing lookup | SIGSEGV (immediate, at least) |
| **Invalid free** | `free(p + 1)`, or freeing stack memory | abort ("free(): invalid pointer") |
| **Off-by-one** | `i <= n`, forgetting space for `'\0'` | any of the overflow symptoms |

## 2. Examples

```c
// LEAK: the pointer is overwritten, so the first block is unreachable
char *buf = malloc(100);
buf = malloc(200);              // 100 bytes leaked
free(buf);

// LEAK on an error path: the most common real-world leak
int process(const char *path) {
    char *data = malloc(4096);
    FILE *f = fopen(path, "r");
    if (!f) return -1;          // data leaked!
    /* ... */
}

// USE-AFTER-FREE
int *a = malloc(4 * sizeof *a);
free(a);
a[1] = 7;                       // writes into memory the allocator may have reused

// DOUBLE FREE through an alias
int *p = malloc(16), *q = p;
free(p);
free(q);                        // same block again

// OFF-BY-ONE heap overflow: no room for the terminator
char *copy = malloc(strlen(src));
strcpy(copy, src);              // writes strlen+1 bytes

// DANGLING STACK POINTER
int *make(void) { int x = 42; return &x; }   // gcc warns: function returns address of local
```

> [!DANGER]
> A program with these bugs often **appears to work**. Undefined behaviour means *anything* can happen, including the right answer, until a different input, compiler version or optimisation level changes the memory layout. Testing alone can't prove their absence. Use tools.

## 3. AddressSanitizer (ASan): your first line of defence

Compile with `-fsanitize=address -g` (gcc and clang). The compiler instruments every memory access and surrounds allocations with poisoned "red zones". Freed memory is quarantined so use-after-free is caught. The cost is about 2× slowdown and about 3× memory. Use it in every debug build and test run.

```bash
gcc -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer prog.c -o prog
./prog
```

The use-after-free example above produces (abridged):

```output
==16110==ERROR: AddressSanitizer: heap-use-after-free on address 0x6d59be9e0014 ...
READ of size 4 at 0x6d59be9e0014 thread T0
    #0 main uaf.c:2
freed by thread T0 here:
    #1 main uaf.c:2
previously allocated by thread T0 here:
    #1 main uaf.c:2
SUMMARY: AddressSanitizer: heap-use-after-free uaf.c:2 in main
```

It gives you the exact line of the bad access, **where the block was freed**, and **where it was allocated**. **LeakSanitizer** (included in ASan on Linux) reports leaks at exit:

```output
==16119==ERROR: LeakSanitizer: detected memory leaks
Direct leak of 100 byte(s) in 1 object(s) allocated from:
    #1 main leak.c:2
SUMMARY: AddressSanitizer: 100 byte(s) leaked in 1 allocation(s).
```

| Tool | Catches | Cost | How |
|---|---|---|---|
| **ASan** (+ LSan) | overflows (heap, stack, global), UAF, double free, leaks | ~2× | `-fsanitize=address` |
| **UBSan** | signed overflow, bad shifts, misaligned access, NULL deref | small | `-fsanitize=undefined` |
| **MSan** (clang) | reads of uninitialised memory | ~3× | `-fsanitize=memory` |
| **TSan** | data races between threads | 5–15× | `-fsanitize=thread` |
| **Valgrind memcheck** | leaks, invalid accesses, uninitialised use, **without recompiling** | 20–50× | `valgrind --leak-check=full ./prog` |
| compiler warnings | many obvious cases | none | `-Wall -Wextra`, gcc's `-fanalyzer` |

> [!TIP]
> ASan and TSan can't be combined in one build. Run your test suite once per sanitizer in CI. Robotics teams run their unit tests under ASan and UBSan on every commit, because a memory bug in a motion controller is a physical safety bug.

## 4. Prevention habits

1. **Pair every allocation with its free at design time.** Know who owns each pointer (previous lesson), and write the `free` the moment you write the `malloc`.
2. **Single exit with `goto cleanup`** for functions that acquire several resources:

```c
int process(const char *path) {
    int rc = -1;
    char *data = NULL;
    FILE *f = NULL;

    data = malloc(4096);
    if (!data) goto out;
    f = fopen(path, "r");
    if (!f) goto out;
    /* ... work ... */
    rc = 0;
out:                        // every path releases everything; free(NULL) is fine
    if (f) fclose(f);
    free(data);
    return rc;
}
```

3. **NULL after free** (`free(p); p = NULL;`). A later double free becomes harmless, and a later use becomes an immediate segfault instead of silent corruption.
4. **Size with `sizeof *p`**, always budget `+1` for string terminators, and prefer `snprintf` and `memcpy` with explicit lengths over `strcpy` and `sprintf`.
5. **Bounds come with pointers**: pass `(ptr, len)` pairs, never a bare buffer pointer.
6. **Avoid ownership ambiguity**: one owner per block, and document "borrowed" vs "owned" in every API comment.

## 5. Exam-ready answers

> [!EXAM]
> **Common memory errors.** A memory leak occurs when dynamically allocated memory is no longer reachable but has not been freed, so it cannot be reclaimed. A dangling pointer is a pointer to memory that has been freed or to an automatic object whose lifetime has ended; using it (use-after-free) is undefined behaviour. A double free releases the same block twice, corrupting the allocator. A buffer overflow writes beyond the bounds of an array on the stack or heap, overwriting adjacent data, allocator metadata or return addresses, and is a major source of security vulnerabilities. These errors are detected with dynamic analysis tools such as AddressSanitizer and Valgrind, and prevented by clear ownership rules, consistent cleanup patterns, bounds-checked operations and setting freed pointers to NULL.

## 6. Cheat sheet

| Situation | Tool or habit |
|---|---|
| every debug and test build | `-g -fsanitize=address,undefined` |
| binary you can't rebuild | `valgrind --leak-check=full ./prog` |
| threads | a separate `-fsanitize=thread` build |
| several resources in one function | `goto cleanup` with a single exit |
| after free | `p = NULL;` |
| strings | `malloc(len + 1)`, `snprintf` |
| buffers | always pass `(ptr, len)` |

> [!INTERVIEW]
> **"Your service's memory grows slowly over days. How do you find out why?"** First confirm it's a leak rather than fragmentation or a legitimately growing cache (track RSS and heap stats over time). Then reproduce it under LeakSanitizer or `valgrind --leak-check=full` with a representative workload; both report the allocation stack of each unfreed block. For production processes that can't be restarted under a tool, use heap profilers (heaptrack, jemalloc or tcmalloc profiling) to compare snapshots and see which call sites' live bytes keep increasing. Usual culprits: error paths that skip cleanup, containers that only grow, and caches without eviction.
