# C plan: complete language, systems and embedded coverage

Planner: Agent 1. Format follows `HEAD_PLAYBOOK.md`. CEO priority 3: existing content stays; thin topics get more problems; gaps get new topics.

## How to read this plan

- Every existing C topic has 0–2 problems, so all are **existing-thin**. Keep existing problems (an old broad problem goes last) and **add** the listed ones; the target total is 4–5.
- **new**: a missing topic.
- Judge: stdin/stdout, hidden driver, compiled with ASan/UBSan/LSan. Drivers free everything. POSIX problems run inside one process (fork/pipe/socketpair/threads are allowed; no network beyond loopback/socketpair). Embedded problems simulate registers and interrupts in plain C.
- Milestone folders (`milestone-1..4`) are unchanged.

## Priority: what authors build first

1. **Pointers and Memory (Modules 04–05)**: the core of C, and the most common interview material.
2. **Foundations, Functions, Arrays/Strings (01–03)**: quick top-ups that every learner meets first.
3. **Data structures and algorithms in C (09–10)**, including the new dynamic array, trie and bitset topics.
4. **Systems programming (12)** including the new files/dirs, mmap, event-driven server and C11 threads topics.
5. **Embedded (13)** including the new protocols, RTOS and startup/linker topics.
6. **User-defined types, preprocessor, files (06–08)**, then **Advanced C (11)**, **Tooling (14)**, **security**, **interview (15)** and **OOP in C (16)**.

## Module map

| # | Module | Topics |
|---|---|---|
| 01 | Foundations | 9 thin |
| 02 | Functions | 5 thin + 1 new |
| 03 | Arrays and Strings | 4 thin |
| 04 | Pointers | 7 thin |
| 05 | Memory | 4 thin |
| 06 | User-Defined Types | 3 thin |
| 07 | Preprocessor | 2 thin |
| 08 | Files and I/O | 3 thin + 1 new |
| 09 | Data Structures in C | 6 thin + 3 new |
| 10 | Algorithms in C | 5 thin |
| 11 | Advanced C | 4 thin + 2 new |
| 12 | Systems Programming | 6 thin + 4 new |
| 13 | Embedded and Robotics C | 5 thin + 3 new |
| 14 | Tooling | 3 thin + 2 new |
| 15 | Security and Interview | 2 thin + 1 new |
| 16 | Master OOP in C | 6 thin |

---

## Module 01: Foundations

### c-compilation | How a C Program Is Built | Beginner | status: existing-thin
Existing: c-fix-link-error, c-hello-judge.
Lesson must cover: preprocessing, compilation, assembly, linking; `gcc -E/-S/-c`; object files and symbols; warnings flags.
Problems to add (2):
3. Exit Status and stderr [Easy]: return codes and writing errors to stderr.
4. Symbol Table Reasoner [Medium]: from `nm`-style listings, report undefined and multiply defined symbols.

### c-program-structure | Program Structure, main and printf | Beginner | status: existing-thin
Existing: c-printf-table, c-prototype-order.
Problems to add (2):
3. Reading Until EOF with scanf Return Values [Easy].
4. Multi-Function Report Program [Medium]: decompose a task into functions with prototypes.

### c-data-types | Data Types and Sizes | Beginner | status: existing-thin
Existing: c-byte-inspector, c-type-sizes.
Lesson must cover: integer ranks, `<stdint.h>`, `<limits.h>`, signedness of char, float/double, sizes are implementation-defined.
Problems to add (2):
3. Fixed-Width Overflow Detection [Medium]: detect overflow before it happens for int32/uint32.
4. Endianness Detector and Byte Swap [Medium].

### c-variables-constants | Variables, Constants and Literals | Beginner | status: existing-thin
Existing: c-unit-converter.
Problems to add (3):
2. Literal Suffixes and Types [Easy]: print the value of expressions mixing `U`, `L`, `f` suffixes.
3. const vs #define vs enum Constants [Easy].
4. Character and Escape Sequences Decoder [Medium]: interpret C escape sequences in input strings.

### c-operators | Operators and Precedence | Beginner | status: existing-thin
Existing: c-bit-flags, c-trunc-vs-floor.
Problems to add (2):
3. Sequence Points and Side Effects [Medium]: rewrite UB expressions to defined ones with expected output.
4. Precedence-Correct Evaluator [Medium]: evaluate C integer expressions with C precedence and associativity.

### c-type-conversion | Type Conversion and Promotion | Intermediate | status: existing-thin
Existing: c-average-trap.
Problems to add (3):
2. Signed/Unsigned Comparison Trap [Medium].
3. Usual Arithmetic Conversions Table [Medium]: report result type and value for operand pairs.
4. Safe Narrowing Casts [Medium].

### c-io | Formatted I/O: printf and scanf | Beginner | status: existing-thin
Existing: c-safe-input.
Problems to add (3):
2. printf Width and Precision Table [Easy].
3. fgets + sscanf Robust Parsing [Medium].
4. strtol with Full Error Checking [Medium].

### c-control-flow | Conditionals and switch | Beginner | status: existing-thin
Existing: c-calc-switch.
Problems to add (3):
2. Grade Classifier [Easy].
3. Day-of-Week from Date (Zeller) [Medium].
4. switch Fallthrough Command Decoder [Medium].

### c-loops | Loops | Beginner | status: existing-thin
Existing: c-collatz-c, c-number-patterns.
Problems to add (2):
3. Prime Sieve up to N [Easy].
4. Nested Loop Matrix Patterns with break/continue [Medium].

## Module 02: Functions

### c-functions | Functions and Prototypes | Beginner | status: existing-thin
Existing: c-minmax-out.
Problems to add (3):
2. Pass-by-Value Pitfall [Easy]: fix a swap via pointers.
3. Array Parameters and Length [Easy].
4. Function Returning Struct by Value [Medium].

### c-storage-classes | Scope, Lifetime and Storage Classes | Intermediate | status: existing-thin
Existing: c-id-generator.
Problems to add (3):
2. static Local Counter [Easy].
3. Internal vs External Linkage Across TUs [Medium].
4. Dangling Pointer to Automatic Variable [Medium]: fix with static or caller-provided buffer.

### c-recursion | Recursion | Intermediate | status: existing-thin
Existing: c-flood-depth, c-permutations.
Problems to add (2):
3. Tower of Hanoi Moves [Easy].
4. Recursive Descent Expression Parser [Hard].

### c-multifile | Header Files and Multi-File Programs | Intermediate | status: existing-thin
Existing: c-vector-module.
Problems to add (3):
2. Include Guards and Redefinition [Easy].
3. extern Globals Done Right [Medium].
4. Header Dependency Order [Medium]: topological include order from a dependency list.

### c-variadic | Variadic Functions | Advanced | status: existing-thin
Existing: c-mini-printf.
Problems to add (3):
2. Variadic Sum with Sentinel [Easy].
3. va_copy Double Pass [Medium].
4. Variadic Logger with vsnprintf [Medium].

### c-callbacks-generic | Callbacks and Higher-Order C | Intermediate | status: new
Summary: Passing behaviour into functions in C.
Lesson must cover: callback signatures, `void *` context, comparator contracts, event handler tables, `qsort`/`bsearch` design.
Problems (4):
1. Apply Function to Array [Easy].
2. Generic Filter with Context [Medium].
3. Event Handler Table [Medium].
4. Generic bsearch Reimplementation [Medium].

## Module 03: Arrays and Strings

### c-arrays | Arrays | Beginner | status: existing-thin
Existing: c-rotate-dedupe.
Problems to add (3):
2. Prefix Sums and Range Queries [Easy].
3. In-Place Reverse and Two Pointers [Easy].
4. Frequency Counting with a Lookup Array [Medium].

### c-2d-arrays | Multidimensional Arrays | Intermediate | status: existing-thin
Existing: c-matrix-ops.
Problems to add (3):
2. Spiral Traversal [Medium].
3. VLA vs Fixed vs Pointer-to-Array Parameters [Medium].
4. Game of Life Step [Medium].

### c-strings | Strings and string.h | Intermediate | status: existing-thin
Existing: c-string-utils.
Problems to add (3):
2. Implement strlen/strcpy/strcmp [Easy].
3. Word Reversal In Place [Medium].
4. Safe Concatenation with Truncation Reporting [Medium].

### c-ctype-parsing | Character Handling and Parsing | Intermediate | status: existing-thin
Existing: c-nmea-parser.
Problems to add (3):
2. Tokenizer with ctype [Easy].
3. INI File Parser [Medium].
4. CSV with Quoted Fields [Hard].

## Module 04: Pointers

### c-pointers-basics | Pointer Basics | Intermediate | status: existing-thin
Existing: c-sort3-pointers.
Problems to add (3):
2. Out Parameters for Division [Easy].
3. Pointer to Struct Updates [Easy].
4. Null-Safe Linked Access [Medium].

### c-pointer-arithmetic | Pointer Arithmetic | Intermediate | status: existing-thin
Existing: c-two-pointer-sum.
Problems to add (3):
2. Walk an Array with Pointers Only [Easy].
3. ptrdiff_t and One-Past-End [Medium].
4. Byte-Level Struct Walk [Medium]: `unsigned char *` traversal with `offsetof`.

### c-pointers-arrays | Pointers and Arrays | Intermediate | status: existing-thin
Existing: c-longest-run-ptr.
Problems to add (3):
2. Array Decay and sizeof [Easy].
3. Array of Pointers vs Pointer to Array [Medium].
4. Jagged Array of Strings [Medium].

### c-pointer-to-pointer | Pointers to Pointers | Advanced | status: existing-thin
Existing: c-list-head-ops.
Problems to add (3):
2. Allocate a 2D Matrix via double pointer [Medium].
3. Remove from List with Pointer-to-Pointer (Linus style) [Medium].
4. argv-Style String Array Builder [Medium].

### c-function-pointers | Function Pointers | Advanced | status: existing-thin
Existing: c-qsort-records.
Problems to add (3):
2. Calculator Dispatch Table [Easy].
3. State Machine with Function Pointers [Medium].
4. Plugin Registry by Name [Medium].

### c-const-pointers | const Correctness and Complex Declarations | Advanced | status: existing-thin
Existing: c-const-words.
Problems to add (3):
2. const Placement Quiz Implemented [Medium]: functions that compile only with correct const.
3. Declaration Decoder (cdecl) [Hard]: translate C declarations to English.
4. typedef Simplification of Function Pointer Types [Medium].

### c-void-pointers | void Pointers and Generic Code | Advanced | status: existing-thin
Existing: c-generic-vec.
Problems to add (3):
2. Generic Swap with memcpy [Easy].
3. Generic Max with Comparator [Medium].
4. Generic Hash Map with void* Keys [Hard].

## Module 05: Memory

### c-dynamic-memory | Dynamic Memory: malloc, calloc, realloc, free | Intermediate | status: existing-thin
Existing: c-line-reverser.
Problems to add (3):
2. Growable Buffer with realloc [Easy].
3. realloc Failure Handling [Medium].
4. Read Arbitrary-Length Lines [Medium].

### c-memory-layout | Memory Layout of a Process | Advanced | status: existing-thin
Existing: none (0 problems).
Lesson must cover: text/data/bss/heap/stack segments, stack frames, alignment, `size` output, stack growth, ASLR.
Problems (4):
1. Classify Variables by Segment [Easy]: report segment for described declarations.
2. Stack Frame Simulator [Medium]: push/pop frames with locals and return addresses.
3. Address Ordering Experiments [Medium]: compare addresses of locals/globals/heap without relying on UB.
4. Stack Depth Estimator [Medium]: compute max stack usage from a call graph with frame sizes.

### c-memory-bugs | Memory Bugs: Leaks, Dangling Pointers, Overflows | Advanced | status: existing-thin
Existing: c-fix-labels.
Problems to add (3):
2. Fix the Leak [Easy].
3. Fix the Use-After-Free [Medium].
4. Fix the Off-by-One Overflow [Medium].

### c-allocators | Custom Allocators and Arenas | Expert | status: existing-thin
Existing: c-arena-alloc, c-pool-alloc.
Problems to add (2):
3. Free-List malloc with Coalescing [Hard].
4. Buddy Allocator [Hard].

## Module 06: User-Defined Types

### c-structs | Structures | Intermediate | status: existing-thin
Existing: c-fleet-report.
Problems to add (3):
2. Struct Sorting by Multiple Keys [Easy].
3. Nested Structs and Designated Initializers [Medium].
4. Flexible Array Member Packet [Medium].

### c-unions-enums | Unions, Enums and typedef | Intermediate | status: existing-thin
Existing: c-dynamic-rpn.
Problems to add (3):
2. Tagged Union Shapes [Easy].
3. Enum to String Tables (X-macro) [Medium].
4. Union Type Punning for Float Bits [Medium].

### c-bitfields-alignment | Bit Fields, Padding and Alignment | Advanced | status: existing-thin
Existing: c-telemetry-codec.
Problems to add (3):
2. Predict sizeof and Offsets [Medium].
3. Reorder Fields to Minimize Padding [Medium].
4. Portable Bit Packing without Bit Fields [Hard].

## Module 07: Preprocessor

### c-macros | Macros | Intermediate | status: existing-thin
Existing: c-macro-toolkit.
Problems to add (3):
2. Safe MIN/MAX and Double Evaluation [Easy].
3. Stringizing and Token Pasting [Medium].
4. X-Macro Command Table [Medium].

### c-conditional-compilation | Conditional Compilation | Intermediate | status: existing-thin
Existing: c-mini-preprocessor.
Problems to add (3):
2. Feature Flags via #ifdef [Easy].
3. Platform Abstraction Header [Medium].
4. #if Expression Evaluator [Hard].

## Module 08: Files and I/O

### c-file-io | File Handling | Intermediate | status: existing-thin
Existing: c-record-store.
Problems to add (3):
2. Line Counter (wc) [Easy].
3. Binary File Record Update with fseek [Medium].
4. File Copy with Buffered Chunks [Medium].

### c-error-handling | Error Handling in C | Intermediate | status: existing-thin
Existing: c-config-validator.
Problems to add (3):
2. errno and perror Usage [Easy].
3. goto-Cleanup Pattern [Medium].
4. Error Code Enum with Message Table [Medium].

### c-cli-args | Command-Line Arguments | Intermediate | status: existing-thin
Existing: c-cli-parser.
Problems to add (3):
2. argc/argv Echo with Indexing [Easy].
3. getopt Option Parsing [Medium].
4. Long Options with getopt_long [Medium].

### c-serialization | Binary Formats and Serialization | Advanced | status: new
Summary: Reading and writing portable binary data.
Lesson must cover: endianness, fixed-width fields, alignment-free packing, versioned headers, checksums, BMP/WAV headers.
Problems (4):
1. Big-Endian Integer Pack/Unpack [Easy].
2. BMP Header Parser [Medium].
3. WAV Header Writer [Medium].
4. Versioned Record Format with CRC [Hard].

## Module 09: Data Structures in C

### c-linked-lists | Linked Lists in C | Intermediate | status: existing-thin
Existing: c-list-surgery.
Problems to add (3):
2. Reverse a List Iteratively and Recursively [Easy].
3. Doubly Linked List with Sentinel [Medium].
4. Intrusive Lists (container_of) [Hard].

### c-stacks-queues | Stacks and Queues | Intermediate | status: existing-thin
Existing: c-sensor-ring.
Problems to add (3):
2. Array Stack for Bracket Matching [Easy].
3. Linked Queue [Easy].
4. Deque on Circular Buffer [Medium].

### c-hash-tables | Hash Tables | Advanced | status: existing-thin
Existing: c-string-hashmap.
Problems to add (3):
2. Separate Chaining Integer Map [Medium].
3. Open Addressing with Tombstones [Hard].
4. Resizing and Load Factor [Medium].

### c-trees | Binary Trees and BSTs | Advanced | status: existing-thin
Existing: c-order-stats-bst.
Problems to add (3):
2. BST Insert/Search/Delete [Medium].
3. Level-Order Traversal with Queue [Medium].
4. AVL Insert [Hard].

### c-heaps | Heaps and Priority Queues | Advanced | status: existing-thin
Existing: c-kway-merge.
Problems to add (3):
2. Binary Min-Heap [Easy].
3. Heap Sort [Medium].
4. Event Scheduler with Priority Queue [Medium].

### c-graphs | Graphs | Advanced | status: existing-thin
Existing: c-graph-toolkit.
Problems to add (3):
2. Adjacency List with Dynamic Arrays + BFS [Medium].
3. Dijkstra with Binary Heap [Hard].
4. Topological Sort [Medium].

### c-dynamic-arrays | Dynamic Arrays (Vectors) in C | Intermediate | status: new
Summary: Growable arrays and amortized analysis.
Lesson must cover: capacity doubling, amortized O(1) proof, macro-based generic vectors, iteration, shrink policies.
Problems (4):
1. Int Vector [Easy].
2. Generic Vector via Macros [Medium].
3. Insert/Erase at Index [Medium].
4. String Builder [Medium].

### c-tries | Tries in C | Advanced | status: new
Summary: Prefix trees with manual memory management.
Lesson must cover: array-of-children vs compact nodes, insert/search/prefix count, deletion and freeing, memory cost.
Problems (4):
1. Trie Insert/Search [Easy].
2. Prefix Count [Medium].
3. Autocomplete Lexicographic [Medium].
4. Compressed (Radix) Trie [Hard].

### c-bitsets-dsu | Bitsets and Union-Find in C | Advanced | status: new
Summary: Compact sets and disjoint sets.
Lesson must cover: bit arrays with macros, set algebra, popcount, union-find with path compression and union by rank.
Problems (4):
1. Bitset Set Operations [Easy].
2. Bitset Sieve Memory Savings [Medium].
3. Union-Find Connectivity Queries [Medium].
4. Kruskal MST [Medium].

## Module 10: Algorithms in C

### c-sorting | Sorting Algorithms | Intermediate | status: existing-thin
Existing: c-sort-records.
Problems to add (3):
2. Insertion and Selection Sort [Easy].
3. Merge Sort with Temp Buffer [Medium].
4. Quicksort with 3-Way Partition [Medium].

### c-searching | Searching and Binary Search | Intermediate | status: existing-thin
Existing: c-binary-search-suite.
Problems to add (3):
2. Lower and Upper Bound [Easy].
3. Search in Rotated Array [Medium].
4. Binary Search on Answer: Minimum Capacity [Medium].

### c-dp | Dynamic Programming in C | Advanced | status: existing-thin
Existing: c-dtw-gestures, c-knapsack-lis.
Problems to add (2):
3. Edit Distance [Medium].
4. Coin Change Ways [Medium].

### c-bit-manipulation | Bit Manipulation | Advanced | status: existing-thin
Existing: c-bit-toolkit, c-can-signals.
Problems to add (2):
3. Popcount Three Ways [Easy].
4. Subset Enumeration with Masks [Medium].

### c-string-algorithms | String Algorithms in C | Advanced | status: existing-thin
Existing: c-pattern-toolkit.
Problems to add (3):
2. KMP Search [Medium].
3. Rabin–Karp [Medium].
4. Longest Palindromic Substring [Medium].

## Module 11: Advanced C

### c-undefined-behavior | Undefined Behavior | Expert | status: existing-thin
Existing: c-safe-arith.
Problems to add (3):
2. Strict Aliasing Fix [Medium].
3. Shift UB Guarded [Medium].
4. Uninitialized Read Fix [Medium].

### c-volatile-restrict | volatile, restrict and inline | Expert | status: existing-thin
Existing: c-mmio-uart.
Problems to add (3):
2. restrict-Enabled memcpy Variant [Medium].
3. volatile Flag for Signal Handlers [Medium].
4. inline Functions vs Macros [Easy].

### c-modern-c | Modern C: C11, C17, C23 | Advanced | status: existing-thin
Existing: c-generic-values.
Problems to add (3):
2. _Static_assert Layout Checks [Easy].
3. Anonymous Structs/Unions and Compound Literals [Medium].
4. C23 Features: typeof, nullptr, constexpr, #embed concepts [Medium].

### c-number-representation | Integer and Floating-Point Representation | Advanced | status: existing-thin
Existing: c-ieee-inspector.
Problems to add (3):
2. Two's Complement Converter [Easy].
3. Float Comparisons with ULPs [Medium].
4. Software Float Addition [Hard].

### c-setjmp-nonlocal | setjmp/longjmp and Non-Local Control | Expert | status: new
Summary: Non-local jumps and their dangers.
Lesson must cover: setjmp/longjmp semantics, volatile locals, error recovery, exception emulation, coroutines idea.
Problems (4):
1. Error Recovery in a Parser [Medium].
2. TRY/CATCH Macro Emulation [Hard].
3. volatile Locals after longjmp [Medium].
4. Resource Cleanup Stack with longjmp [Hard].

### c-secure-coding | Secure Coding in C | Expert | status: new
Summary: Avoiding vulnerabilities.
Lesson must cover: buffer overflows, format string bugs, integer overflow in sizes, TOCTOU, safe APIs, CERT C rules.
Problems (4):
1. Fix the Format String Bug [Easy].
2. Overflow-Safe Allocation Size [Medium].
3. Bounded Parsing of Untrusted Input [Medium].
4. Harden a Packet Decoder [Hard].

## Module 12: Systems Programming

### c-processes | Processes: fork, exec, wait | Expert | status: existing-thin
Existing: c-pipeline-runner.
Problems to add (3):
2. fork and wait Exit Codes [Medium].
3. exec with Argument Vectors [Medium].
4. Process Tree Reporter [Medium].

### c-signals | Signals | Expert | status: existing-thin
Existing: c-signal-supervisor.
Problems to add (3):
2. sigaction with SIGINT Counter [Medium].
3. Self-Pipe Trick [Hard].
4. Alarm-Based Timeout [Medium].

### c-pthreads | POSIX Threads | Expert | status: existing-thin
Existing: c-blocking-queue.
Problems to add (3):
2. Parallel Array Sum [Easy].
3. Mutex-Protected Counter and Race Fix [Medium].
4. Thread Pool [Hard].

### c-ipc | Inter-Process Communication | Expert | status: existing-thin
Existing: c-framed-rpc.
Problems to add (3):
2. Pipe Parent-Child Messaging [Medium].
3. Shared Memory Ring between Processes [Hard].
4. Named Pipe (FIFO) Protocol [Medium].

### c-sockets | Socket Programming | Expert | status: existing-thin
Existing: c-tcp-kv-server.
Problems to add (3):
2. socketpair Echo [Easy].
3. Length-Prefixed Framing [Medium].
4. Minimal HTTP Request Handler over socketpair [Hard].

### c-syscalls-fd | System Calls and File Descriptors | Expert | status: existing-thin
Existing: c-fd-utils.
Problems to add (3):
2. dup2 Redirection [Medium].
3. Partial read/write Loops [Medium].
4. Nonblocking I/O with O_NONBLOCK [Medium].

### c-filesystem-dirs | Files, Directories and Metadata | Advanced | status: new
Summary: Walking and inspecting the filesystem.
Lesson must cover: stat, dirent, permissions, symlinks, nftw, temp directories.
Problems (4):
1. stat File Info [Easy].
2. Recursive Directory Size [Medium].
3. Permission String Formatter [Easy].
4. find-Like Filter Tool [Medium].

### c-mmap | Memory-Mapped Files | Expert | status: new
Summary: mmap for files and shared memory.
Lesson must cover: mmap/munmap, MAP_SHARED vs PRIVATE, msync, page faults, anonymous mappings.
Problems (4):
1. mmap Word Count [Medium].
2. In-Place File Edit via mmap [Medium].
3. Anonymous Shared Mapping between Parent/Child [Medium].
4. Memory-Mapped Record Database [Hard].

### c-event-driven-io | poll/epoll Event Loops | Expert | status: new
Summary: Serving many connections from one thread.
Lesson must cover: select, poll, epoll (level vs edge triggered), nonblocking sockets, buffers, timers.
Problems (4):
1. poll Multiplexed Echo over socketpairs [Medium].
2. Per-Connection Buffers and Framing [Hard].
3. epoll Edge-Triggered Reader [Hard].
4. Timer Heap Integrated with poll [Hard].

### c-threads-atomics | C11 Threads and Atomics | Expert | status: new
Summary: Portable concurrency in standard C.
Lesson must cover: `<threads.h>`, `<stdatomic.h>`, memory orders, `call_once`, thread-local storage.
Problems (4):
1. Atomic Counter [Easy].
2. call_once Initialization [Medium].
3. SPSC Queue with Atomics [Hard].
4. Thread-Local Error Codes [Medium].

## Module 13: Embedded and Robotics C

### c-embedded-registers | Bitwise Register Programming | Advanced | status: existing-thin
Existing: c-gpio-hal.
Problems to add (3):
2. Set/Clear/Toggle Bit Macros [Easy].
3. Register Field Read-Modify-Write [Medium].
4. Simulated Timer Peripheral [Medium].

### c-fixed-point | Fixed-Point Arithmetic | Expert | status: existing-thin
Existing: c-q16-dsp.
Problems to add (3):
2. Q15 Multiply with Rounding and Saturation [Medium].
3. Fixed-Point Square Root [Medium].
4. Fixed-Point PID Controller [Hard].

### c-state-machines | State Machines in C | Advanced | status: existing-thin
Existing: c-robot-behaviour-fsm.
Problems to add (3):
2. Table-Driven Traffic Light [Easy].
3. Event Queue Driven FSM [Medium].
4. Hierarchical FSM [Hard].

### c-ring-buffers-isr | Ring Buffers, Interrupts and Real-Time | Expert | status: existing-thin
Existing: c-spsc-ring.
Problems to add (3):
2. Power-of-Two Ring Buffer Masking [Easy].
3. ISR-to-Main Handoff Simulation [Medium].
4. Debounce and Edge Detection [Medium].

### c-misra | Safety-Critical C (MISRA) | Expert | status: existing-thin
Existing: c-defensive-imu-parser.
Problems to add (3):
2. Rule Violation Finder [Medium]: detect a subset of MISRA rule violations in token streams.
3. Defensive Range-Checked API [Medium].
4. No-Dynamic-Memory Redesign [Medium].

### c-embedded-protocols | Embedded Communication Protocols | Advanced | status: new
Summary: Serial links and data integrity.
Lesson must cover: UART framing, SLIP/COBS, CRC-8/16/32, CAN frames, Modbus RTU, I2C/SPI transactions.
Problems (5):
1. CRC-16 and CRC-32 [Easy].
2. COBS Encoder/Decoder [Medium].
3. Modbus RTU Frame Parser [Medium].
4. I2C Transaction Simulator [Medium].
5. Frame Resynchronization [Hard].

### c-rtos-concepts | RTOS Concepts | Expert | status: new
Summary: Tasks, scheduling and synchronization on microcontrollers.
Lesson must cover: tasks and TCBs, preemptive vs cooperative scheduling, priorities, semaphores/mutexes, priority inversion, tick timers.
Problems (4):
1. Cooperative Scheduler [Medium].
2. Priority Preemptive Scheduler Simulation [Hard].
3. Counting Semaphore Simulation [Medium].
4. Priority Inheritance Demo [Hard].

### c-startup-linker | Startup Code, Linker Scripts and Bare Metal | Expert | status: new
Summary: What happens before main on a microcontroller.
Lesson must cover: vector table, reset handler, .data copy and .bss zeroing, linker script sections, memory maps, map files.
Problems (4):
1. Simulated .data/.bss Initialization [Medium].
2. Linker Map File Analyzer [Medium].
3. Vector Table Dispatcher [Medium].
4. Section Placement Checker [Hard]: check sections fit FLASH/RAM regions.

## Module 14: Tooling

### c-make | Make and Build Systems | Intermediate | status: existing-thin
Existing: c-mini-make.
Problems to add (3):
2. Pattern Rule Expansion [Medium].
3. Automatic Variables ($@ $< $^) [Easy].
4. Out-of-Date Detection with Timestamps [Medium].

### c-gdb | Debugging with GDB | Intermediate | status: existing-thin
Existing: c-debug-channel-log.
Problems to add (3):
2. Read a Backtrace and Fix [Easy].
3. Watchpoint-Style Corruption Finder [Medium].
4. Core-Dump-Style State Reconstruction [Medium].

### c-libraries | Static and Shared Libraries | Advanced | status: existing-thin
Existing: c-abi-stable-library.
Problems to add (3):
2. Symbol Visibility Planner [Medium].
3. dlopen/dlsym Plugin Loader (simulated registry) [Medium].
4. Library Link Order Resolver [Medium].

### c-testing | Unit Testing in C | Intermediate | status: new
Summary: Testing C code without heavy frameworks.
Lesson must cover: assert-based tests, minimal test frameworks with macros, test doubles via function pointers/link seams, coverage.
Problems (4):
1. Minimal Test Macro Framework [Easy].
2. Test Doubles via Function Pointers [Medium].
3. Tests that Kill Mutants [Medium].
4. Table-Driven Tests [Easy].

### c-sanitizers-analysis | Sanitizers, Valgrind and Static Analysis | Advanced | status: new
Summary: Tools that find bugs.
Lesson must cover: ASan/UBSan/TSan reports, valgrind memcheck, `-fanalyzer`, cppcheck/clang-tidy, fuzzing.
Problems (4):
1. Fix What ASan Reports [Easy].
2. Fix What UBSan Reports [Medium].
3. Fix What TSan Reports [Medium].
4. Mini Mutation Fuzzer [Hard].

## Module 15: Security and Interview

### c-interview-core | C Interview Deep Dive I | Advanced | status: existing-thin
Existing: c-libc-from-scratch.
Problems to add (3):
2. Implement memcpy/memmove [Medium].
3. Implement atoi with Overflow [Medium].
4. Implement strtok_r [Medium].

### c-interview-advanced | C Interview Deep Dive II | Expert | status: existing-thin
Existing: c-linked-list-classics.
Problems to add (3):
2. Implement malloc on a Static Buffer [Hard].
3. Detect Endianness and Swap [Easy].
4. Implement a Generic Queue with void* [Medium].

### c-interview-bits-puzzles | C Puzzles and Bit Tricks | Advanced | status: new
Summary: Classic C interview puzzles.
Lesson must cover: macros pitfalls, sizeof puzzles, pointer puzzles, bit tricks.
Problems (4):
1. Swap Without Temp [Easy].
2. Count Trailing Zeros [Easy].
3. Reverse Bits in a Word [Medium].
4. offsetof and container_of Implemented [Medium].

## Module 16: Master OOP in C

### c-oop-encapsulation | OOP in C: Encapsulation with Opaque Types | Advanced | status: existing-thin
Existing: c-opaque-matrix.
Problems to add (3):
2. Opaque Stack ADT [Easy].
3. Opaque String Type [Medium].
4. Opaque Handle Table with Generation Counters [Hard].

### c-oop-inheritance | OOP in C: Inheritance via Struct Embedding | Expert | status: existing-thin
Existing: c-intrusive-fleet.
Problems to add (3):
2. Base Struct First Member Casting [Medium].
3. container_of Upcasts/Downcasts [Medium].
4. Multi-Level Shape Hierarchy [Medium].

### c-oop-polymorphism | OOP in C: Polymorphism with vtables | Expert | status: existing-thin
Existing: c-sensor-vtables.
Problems to add (3):
2. Shape vtable [Easy].
3. Stream Interface with File/Memory Backends [Medium].
4. Interface Composition (multiple vtables) [Hard].

### c-oop-modular-design | Modular Design Across Files | Advanced | status: existing-thin
Existing: c-scheduler-module.
Problems to add (3):
2. Module with Init/Deinit Lifecycle [Medium].
3. Dependency-Inverted Logger Module [Medium].
4. Layered Driver Stack [Hard].

### c-oop-case-inventory | Case Study: Inventory System in C | Expert | status: existing-thin
Existing: c-inventory-system (keep last).
Problems to add (3):
1. Item Store with Hash Index [Medium].
2. Order Processing with Validation [Medium].
3. Persistence to Binary File [Medium].

### c-oop-case-robot | Case Study: Sensor and Motor Drivers | Expert | status: existing-thin
Existing: c-robot-drive-stack (keep last).
Problems to add (3):
1. Sensor Driver Interface with Fakes [Medium].
2. Motor Ramp Controller [Medium].
3. Fault Manager and Safe State [Hard].
