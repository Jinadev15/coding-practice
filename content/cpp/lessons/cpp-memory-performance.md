# Memory Layout, Cache and Performance

Modern CPUs execute several instructions per nanosecond, but a main-memory access costs about 100 ns. For most data-heavy code, **memory access patterns dominate performance**, not instruction counts. Big-O doesn't capture this. A linked list and a vector are both O(n) to traverse, yet the vector is often 10–50× faster. This lesson explains the memory hierarchy, object layout and alignment, cache-friendly data-oriented design, false sharing, and how to measure instead of guessing. It's the knowledge behind fast perception pipelines, physics engines, and real-time controllers.

## 1. The memory hierarchy in numbers

| Level | Typical size | Latency | Notes |
|---|---|---|---|
| register | ~16–32 × 64 bit | 0 cycles | |
| L1 data cache | 32–48 KB per core | ~4 cycles (~1 ns) | |
| L2 | 1–2 MB per core | ~12–15 cycles | |
| L3 | 16–100 MB shared | ~40–60 cycles | |
| DRAM | GBs | ~200–300 cycles (~80–100 ns) | |
| NVMe SSD | TBs | ~20–100 µs | 1000× DRAM |

Memory moves between levels in **cache lines** of 64 bytes (128 on Apple M-series for some levels). Touching one byte loads the whole line. Two consequences:
- **Spatial locality** pays: after loading `a[0]`, `a[1..15]` (ints) are free.
- **Temporal locality** pays: reusing recently touched data hits in cache.

Hardware **prefetchers** detect sequential and strided access patterns and fetch ahead, so a linear scan approaches memory *bandwidth* (tens of GB/s), while pointer chasing pays full *latency* on every hop.

## 2. Object layout, alignment and padding

Every type has a size and an **alignment** (its address must be a multiple of `alignof(T)`). The compiler inserts **padding** so every member is aligned:

```cpp
struct Bad  { char tag; double value; char flag; };   // 1 + 7 pad + 8 + 1 + 7 pad = 24 bytes
struct Good { double value; char tag; char flag; };   // 8 + 1 + 1 + 6 pad          = 16 bytes
static_assert(sizeof(Bad) == 24 && sizeof(Good) == 16);
static_assert(offsetof(Good, tag) == 8);
```

> [!KEY]
> Order members from largest alignment to smallest to minimise padding. The struct's size is a multiple of its alignment, so arrays keep every element aligned. `alignas(64)` raises alignment, which you use for cache-line separation and for SIMD (`alignas(32)` for AVX).

Tools: `sizeof`, `alignof`, `offsetof`, `pahole` (shows holes in compiled structs) and `-Wpadded`.

Other layout facts:
- **Empty base optimisation** (EBO) and C++20 **`[[no_unique_address]]`**: an empty member (a stateless allocator, comparator or policy) can occupy zero bytes.
- **Virtual functions** add a vptr, 8 bytes per object on 64-bit, usually at offset 0.
- `std::vector<bool>` packs bits. `std::bitset` is fixed size.

## 3. Array of Structs vs Struct of Arrays

```cpp
// AoS: natural OOP layout
struct Particle { float x, y, z, vx, vy, vz, mass; int id; };     // 32 bytes
std::vector<Particle> ps;
for (auto& p : ps) p.x += p.vx * dt;           // uses 8 of every 32 bytes loaded: 75% wasted bandwidth

// SoA: data-oriented layout
struct Particles { std::vector<float> x, y, z, vx, vy, vz, mass; std::vector<int> id; };
for (size_t i = 0; i < P.x.size(); ++i) P.x[i] += P.vx[i] * dt;    // every loaded byte is used; auto-vectorises
```

| | AoS | SoA |
|---|---|---|
| Access all fields of one entity | ✓ one cache line | ✗ several streams |
| Process one field across all entities | ✗ wasted bandwidth | ✓ dense, SIMD-friendly |
| Code clarity | ✓ | needs discipline |

**Data-oriented design** (as in game engines and ECS architectures like EnTT and Unity DOTS) organises data by *how it's processed*. Hot fields (positions updated every frame) are separated from cold fields (names, debug info). A **hot/cold split** of one struct is the cheap version: move rarely used members behind a pointer or into a parallel array.

## 4. Containers through the cache lens

| Container | Memory pattern | Verdict |
|---|---|---|
| `std::vector` / `std::array` | contiguous | the default; insertion in the middle (O(n) `memmove`) is usually still faster than `list` for n ≲ 10⁴–10⁵ |
| `std::deque` | chunks of contiguous blocks | good for push at both ends |
| `std::list`, `std::map`, `std::set` | one heap node per element, pointer chasing | slow traversal; use only when you need iterator stability or splicing |
| `std::unordered_map` | buckets + nodes (separate chaining) | node-based; flat hash maps (`absl::flat_hash_map`, `boost::unordered_flat_map`) are 2–5× faster |
| sorted `std::vector` + `lower_bound` | contiguous | beats `std::map` for read-mostly data (C++23 `std::flat_map`) |

## 5. Loop order and blocking

C++ arrays are **row-major**: `a[i][j]` and `a[i][j+1]` are adjacent.

```cpp
// fast: inner loop walks contiguous memory
for (size_t i = 0; i < N; ++i)
    for (size_t j = 0; j < N; ++j) sum += a[i][j];

// slow for big N: each access jumps N*8 bytes → a cache miss per element
for (size_t j = 0; j < N; ++j)
    for (size_t i = 0; i < N; ++i) sum += a[i][j];
```

For matrix multiplication, the `i-k-j` loop order (so the inner loop streams through rows of B and C) beats the textbook `i-j-k` order by 5–10×. **Tiling** or **blocking** (working on B×B sub-blocks that fit in L1/L2) improves it further. That's what BLAS and Eigen do internally.

## 6. False sharing

Two threads writing **different** variables that share a **cache line** force the line to bounce between cores (the MESI protocol invalidates each copy on every write). Performance can drop 10× even though there's no logical sharing.

```cpp
struct Counters { std::atomic<long> a, b; };                 // a and b share one line: false sharing

struct alignas(64) Padded { std::atomic<long> v; };          // one counter per line
Padded per_thread[8];

// C++17: portable constant (may be unavailable or warn on some compilers)
// alignas(std::hardware_destructive_interference_size)
```

Fix it with per-thread data padded to the cache line, or accumulate locally and combine once at the end, which is usually the best option.

## 7. Branches, SIMD and other CPU effects

- **Branch prediction**: a mispredicted branch costs about 15–20 cycles. Sorting the data first can make a data-dependent `if` predictable, and branch-free code (`x = cond ? a : b` compiled to `cmov`, or arithmetic masks) avoids the problem. `[[likely]]` and `[[unlikely]]` (C++20) give layout hints.
- **Auto-vectorisation**: simple loops over contiguous arrays with no aliasing compile to SIMD (4–16 elements per instruction). Help it with `-O3 -march=native`, `__restrict`, SoA layouts, and no function calls or early exits in the loop. Check the report with `-fopt-info-vec`.
- **Allocation**: `new` and `malloc` cost roughly 20–100 ns plus possible lock contention, and fragment memory. Reserve containers up front (`v.reserve(n)`), reuse buffers, and use arenas (next lesson).
- **Indirection**: every `virtual` call or `std::function` call is an indirect branch and blocks inlining. In hot loops, prefer templates, `std::variant` with `std::visit`, or sorting objects by type.

## 8. Measure, don't guess

| Tool | Use |
|---|---|
| `std::chrono::steady_clock` | quick wall-clock timing (repeat runs, discard warm-up) |
| Google Benchmark | micro-benchmarks with statistical repetition, `benchmark::DoNotOptimize` |
| `perf stat -e cache-misses,branch-misses ./app` | hardware counters (Linux) |
| `perf record` + `perf report` / flame graphs | where time goes |
| Valgrind `cachegrind`, Intel VTune, AMD uProf | cache simulation, microarchitecture analysis |
| Compiler Explorer (godbolt.org) | read the assembly your code becomes |

> [!WARNING]
> Micro-benchmark traps:
> - The optimiser deletes work whose result is unused, so you measure nothing.
> - Data that fits in cache in the benchmark won't in production.
> - Debug builds measure the wrong thing.
> - CPU frequency scaling and turbo add noise.
>
> Always benchmark an `-O2`/`-O3` build on realistic data sizes.

## 9. Exam-ready answers

> [!EXAM]
> **Cache locality.** Processors transfer memory between DRAM and caches in fixed-size cache lines, typically 64 bytes, and a cache hit is one to two orders of magnitude faster than a DRAM access. Programs benefit from spatial locality, using data located near recently accessed data, and temporal locality, reusing recently accessed data. Contiguous containers traversed sequentially use every loaded byte and allow hardware prefetching, whereas node-based structures such as linked lists and trees incur a potential cache miss per node. Data-oriented layouts such as struct-of-arrays, loop orders that follow the memory layout, and blocking for cache size exploit locality.

> [!EXAM]
> **False sharing.** False sharing occurs when threads on different cores repeatedly write distinct variables that reside in the same cache line. The coherence protocol invalidates the line in the other cores' caches on every write, so the line migrates between cores and performance degrades severely even though no data is logically shared. It's avoided by aligning or padding per-thread data to the cache-line size, for example with `alignas(64)` or `std::hardware_destructive_interference_size`, or by accumulating results in thread-local variables and combining them once.

## 10. Cheat sheet

| Goal | Technique |
|---|---|
| less padding | order members by decreasing alignment; check with `sizeof`/`pahole` |
| fast iteration over one field | SoA / hot-cold split |
| default container | `std::vector`; `reserve()` when the size is known |
| ordered lookups, read-mostly | sorted vector / `std::flat_map` |
| 2-D traversal | inner loop over the last index (row-major) |
| per-thread counters | `alignas(64)` or thread-local accumulation |
| avoid allocation in hot paths | reuse buffers, arenas/PMR |
| know, don't guess | `perf`, Google Benchmark, godbolt |

> [!INTERVIEW]
> **"Why can `std::vector` beat `std::list` even for insertions in the middle?"** Inserting into a list is O(1) *after* you find the position, but finding it is an O(n) pointer chase with a cache miss per node. A vector finds the position with a cache-friendly scan (or binary search) and shifts elements with `memmove` at memory bandwidth. Bjarne Stroustrup's benchmark shows the vector winning up to very large n. Mention that lists still win when you already hold the iterator, or when iterators must stay valid.
