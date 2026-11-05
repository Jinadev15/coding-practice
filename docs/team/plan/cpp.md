# C++ plan: from zero to industry-ready in any field

Planner: Agent 1. Source of truth for *what* C++ authors build. Format follows `HEAD_PLAYBOOK.md`.

## How to read this plan

- **status: existing-ok**: built to the bar and committed; do not touch (listed for completeness only).
- **status: existing-thin**: topic exists (lesson + usually 1 old "suite" problem). Bring the lesson to the CEO bar and **add** the listed problems. The old suite problem stays as the final mixed-review problem (its `order:` goes after the new ones). Final count = old + new, inside the 4–6 (non-DSA) or 6–10 (DSA) band.
- **status: rebuild**: old broad topic with 1 suite problem; rewrite the lesson for the narrower scope given here and author a full problem set (old suite kept last).
- **status: new**: new topic id. Head files it into `curriculum.csv` from the author's request.
- Judging: stdin/stdout with a hidden driver. No internet, no GUI. Available: STL, Eigen, OpenCV, GoogleTest, fmt, spdlog, Boost headers (incl. Asio, Graph, Geometry), nlohmann/json. Anything visual (rasterizer, ray tracer, plots) is judged by printing pixel buffers, hashes, ASCII art or numbers. Networking problems are judged in-process: parsers, state machines, `socketpair()`/loopback within one process, or a simulated event loop fed from stdin.
- Each problem line = one distinct idea. Authors may rename problems but must keep the idea and the Easy→Hard order.

## Priority: what authors build first

1. **DSA core in flight (Wave 1):** Modules 13 (rest), 14, 15 part 1, 16 part 1. Already assigned.
2. **DSA rest, in teaching order:** 15 part 2 (balanced BST, tries, segment tree, Fenwick, range queries, tree-advanced) → 16 part 2 (DSU/MST, connectivity, Euler, flows) → 17 (backtracking, D&C, bits, search) → 18 (greedy) → 19 (DP, all 11 topics) → 20 (strings, math, geometry) → 21 (interview mastery). This finishes CEO priority 1a.
3. **Robotics (Module 22)**, which builds on Eigen and DSA graphs.
4. **OOP mastery, all 23 GoF patterns and LLD case studies (Modules 23–24)**, then thin-topic top-ups of Modules 01–09 (language core) so the foundations reach 5 problems each.
5. **Systems and performance:** concurrency extras (08), performance (26), systems/networking (27).
6. **Engineering computing (28) and geometry/CAD (29)**, then graphics/games (30).
7. **Embedded (31), tooling/libraries (25), interop (32), interview theory (33).**

Language-core thin topics (01–09) can be done in parallel with any of the above by a separate author because they have no DSA dependencies.

## Module map (proposed order for `curriculum.csv`)

| # | Module | Topics |
|---|---|---|
| 01 | Foundations | 10 (8 thin, 2 new) |
| 02 | Memory and Ownership | 6 thin |
| 03 | OOP Basics | 7 thin |
| 04 | STL | 12 (10 thin, 2 new) |
| 05 | Templates | 7 thin |
| 06 | Error Handling | 2 thin |
| 07 | Modern C++ | 4 thin |
| 08 | Concurrency | 8 (6 thin, 2 new) |
| 09 | Advanced C++ | 4 thin |
| 10–21 | DSA (complete, from zero) | 66 (16 existing-ok, 5 rebuild, 45 new) |
| 22 | Robotics | 12 new |
| 23 | OOP Mastery and Design Patterns | 12 (7 thin, 5 new) |
| 24 | Low-Level Design Case Studies | 10 (3 thin, 7 new) |
| 25 | Tooling and Libraries | 8 (6 thin, 2 new) |
| 26 | Performance Engineering | 4 new |
| 27 | Systems and Networking | 6 new |
| 28 | Engineering and Scientific Computing | 8 new |
| 29 | Geometry and CAD Kernels | 7 new |
| 30 | Graphics and Games | 6 new |
| 31 | Embedded C++ | 6 new |
| 32 | Interop: C, Python, WebAssembly | 3 new |
| 33 | Interview Theory | 2 thin |

The old module labels "10 DSA in C++", "11 Libraries and Frameworks", "12 Design Patterns", "13 Interview Theory", "14 Master OOP" collide with the new DSA numbering; the Head should relabel them to 25, 23, 33 and 23/24 as above.

---

## Module 01: Foundations

### cpp-intro-build | C++ vs C, Compilation and Build | Beginner | status: existing-thin
Summary: How a C++ program becomes an executable and what C++ adds over C.
Lesson must cover:
- preprocess → compile → assemble → link; translation units; headers vs sources; include guards and `#pragma once`
- ODR, `inline` variables/functions, declarations vs definitions, linker errors decoded
- `-std=c++20 -O2 -Wall -Wextra -Wpedantic`, debug vs release, `main` return codes
Existing: cpp-hello-stl (keep last).
Problems to add (4):
1. Echo with Exit Codes [Easy]: read lines, echo them, return the status the driver checks; trains `main`, streams and return values.
2. Fix the ODR Violation [Easy]: starter defines a function in a "header" section twice; make it `inline`/`static` correctly so the multi-TU driver links.
3. Declaration Order Puzzle [Medium]: implement mutually recursive functions (is_even/is_odd over a parsed expression tree) that need forward declarations.
4. Mini Linker [Hard]: given object files' defined/undefined symbol tables on stdin, resolve link order, report unresolved and duplicate symbols like `ld`.

### cpp-io-streams | I/O Streams | Beginner | status: existing-thin
Summary: Formatted and unformatted stream I/O, fast I/O and manipulators.
Lesson must cover:
- `cin`/`cout`/`cerr`, extraction failure states (`fail`, `eof`, `clear`, `ignore`), `getline` + `>>` mixing bug
- manipulators (`setw`, `setfill`, `setprecision`, `fixed`, `hex`, `boolalpha`), `stringstream`
- `ios::sync_with_stdio(false)`, `cin.tie(nullptr)`, `'\n'` vs `endl`
Existing: cpp-report-format (keep last).
Problems to add (4):
1. Robust Integer Reader [Easy]: read tokens, sum the valid integers, count rejects, recovering the stream state after each bad token.
2. Line-by-Line CSV Totals [Easy]: mix `getline` and `stringstream` to parse comma-separated rows with blanks and quoted-free fields.
3. Hex Dump [Medium]: print an `xxd`-style dump of stdin bytes with offsets, hex pairs and printable ASCII, using manipulators only.
4. Fast Reader Under Pressure [Medium]: sum 10⁷ integers within 1 s; starter uses `endl` + synced streams and times out.

### cpp-types-auto | Types, auto and Initialization | Beginner | status: existing-thin
Summary: Fundamental types, sizes, overflow, `auto`/`decltype` and the many initialization forms.
Lesson must cover:
- integer/floating types, `<cstdint>`, `numeric_limits`, signed overflow UB vs unsigned wraparound
- brace init and narrowing, value/default/aggregate/list init, most vexing parse
- `auto` deduction rules (drops ref/const), `decltype`, `decltype(auto)`
Existing: cpp-narrowing-safe (keep last).
Problems to add (4):
1. Type Range Table [Easy]: print min/max/digits for each fundamental type via `numeric_limits`.
2. Checked Arithmetic [Medium]: implement add/mul for `int64_t` that report overflow without UB (`__builtin_*_overflow` or manual checks).
3. Float Equality Done Right [Medium]: compare doubles with relative+absolute epsilon and ULP distance; classify pairs.
4. Deduction Detective [Hard]: for given declarations, print what `auto`, `auto&`, `decltype(x)` and `decltype((x))` deduce (driver checks via type traits and your returned strings).

### cpp-references | References | Beginner | status: existing-thin
Summary: Lvalue references, const references and reference parameters/returns.
Lesson must cover:
- reference vs pointer, binding rules, const ref extends temporaries, dangling references
- pass by value / ref / const ref decision table; returning references safely
Existing: cpp-ref-params (keep last).
Problems to add (4):
1. Swap and Rotate [Easy]: implement `swap3(a,b,c)` rotation through references.
2. Min-Max Out Parameters [Easy]: return min, max and argmax of an array through reference parameters.
3. Safe Accessor [Medium]: return `T&` into a container for in-place updates (bank balances) and avoid returning references to locals.
4. Reference Wrapper Sort [Medium]: sort a `vector<reference_wrapper<Record>>` view by key without copying records; output original order unchanged.

### cpp-const-constexpr | const, constexpr and consteval | Intermediate | status: existing-thin
Summary: Const-correctness and compile-time computation.
Lesson must cover:
- const objects, const member functions, `mutable`, const pointers vs pointers to const
- `constexpr` functions/variables, `consteval`, `constinit`, `if constexpr`, compile-time tables
Existing: cpp-constexpr-table (keep last).
Problems to add (4):
1. Const-Correct Matrix [Easy]: add the missing const overloads of `at()` so a const driver compiles and reads correctly.
2. Compile-Time Primes [Medium]: build a `constexpr std::array` of primes < N and answer queries from it.
3. Compile-Time CRC Table [Medium]: generate a CRC-32 table with `constexpr` and checksum stdin lines.
4. consteval Unit Parser [Hard]: `consteval` function turns string literals like `"12.5mm"` into SI values; driver static_asserts and runtime-checks.

### cpp-namespaces | Namespaces | Beginner | status: existing-thin
Summary: Namespaces, ADL and organizing names.
Lesson must cover:
- nested and inline namespaces, anonymous namespaces vs `static`, `using` declarations vs directives
- argument-dependent lookup, versioning with inline namespaces
Existing: cpp-namespace-units (keep last).
Problems to add (3):
1. Two Libraries, One Name [Easy]: wrap two clashing `log()` functions in namespaces and dispatch by command.
2. ADL Swap [Medium]: provide a `swap` in the type's namespace so generic code's `using std::swap; swap(a,b);` picks it (driver counts calls).
3. Versioned API [Medium]: inline namespace `v2` as default with `v1` still callable; outputs differ per version.

### cpp-control-flow | Control Flow | Beginner | status: existing-thin
Summary: Branches, loops, switch, range-for and structured flow.
Lesson must cover:
- if/else with initializers, switch with fallthrough and `[[fallthrough]]`, loops, `break`/`continue`, range-for
Existing: cpp-grade-buckets (keep last).
Problems to add (4):
1. FizzBuzz Variants [Easy]: rule table driven loop with arbitrary divisor/word pairs.
2. Number Spiral Printer [Easy]: nested loops print an n×n spiral of numbers.
3. Command Interpreter [Medium]: `switch` on command codes with fallthrough-sharing cases for a tiny calculator.
4. Collatz Statistics [Medium]: loops with early exit and caching for the longest chain ≤ N.

### cpp-functions | Functions, Overloading and Default Arguments | Beginner | status: existing-thin
Summary: Functions, overload resolution, default arguments and inline.
Lesson must cover:
- overload resolution ranking, ambiguity, default arguments placement, `inline`, `[[nodiscard]]`, recursion basics
Existing: cpp-overloads (keep last).
Problems to add (4):
1. Area Overloads [Easy]: overloads for circle/rect/triangle by parameter types.
2. Default Argument Formatter [Easy]: `format_money(amount, currency = "USD", decimals = 2)`.
3. Overload Ranking Quiz [Medium]: implement overload set so each driver call resolves to the expected promotion/conversion overload (prints which ran).
4. Function Table Calculator [Medium]: map operator names to function pointers and evaluate RPN.

### cpp-enums-structs | Enums, Structs and Aggregates | Beginner | status: new
Summary: `enum class`, plain structs, aggregates, designated initializers and structured bindings.
Lesson must cover:
- unscoped vs scoped enums, underlying type, enum ↔ string mapping
- aggregates, designated initializers (C++20), default member initializers, structured bindings
Problems (4):
1. Traffic Light Cycle [Easy]: `enum class` state with a next-state function and string conversion.
2. Student Records [Easy]: aggregate struct, sort by multiple keys, structured bindings in output loop.
3. Bit-Flag Enum [Medium]: overload `|`, `&`, `~` for an `enum class Permission` and evaluate permission queries.
4. Config Struct Diff [Medium]: designated-initialized defaults vs parsed overrides; print changed fields.

### cpp-arrays-cstrings | Raw Arrays, C Strings and std::span | Beginner | status: new
Summary: Built-in arrays, decay, C strings, and safe views with `std::span`.
Lesson must cover:
- array decay, `sizeof` traps, multidimensional arrays, C-string functions and their dangers
- `std::span`, `std::array` vs raw arrays, bounds safety
Problems (4):
1. Array Stats with span [Easy]: functions take `span<const int>` and work on raw arrays, vectors and `std::array`.
2. strtok-Free Tokenizer [Medium]: split a C string in place without `strtok`, returning `span` of `string_view`s.
3. Safe strcpy [Medium]: implement bounded copy/concat returning truncation flags (strlcpy semantics).
4. Matrix as Flat Array [Medium]: 2D indexing on a flat buffer with `span`, transpose in place for square matrices.

## Module 02: Memory and Ownership

### cpp-pointers-memory | Pointers and Dynamic Memory | Intermediate | status: existing-thin
Summary: Raw pointers, `new`/`delete`, arrays on the heap and ownership hazards.
Lesson must cover:
- address-of, deref, nullptr, pointer arithmetic, `new[]`/`delete[]`, leaks, double free, dangling; ASan output reading
Existing: cpp-ownership-refactor (keep last).
Problems to add (4):
1. Dynamic Array Resize [Easy]: grow a heap array by doubling with manual copy and correct `delete[]`.
2. Pointer Walk [Easy]: compute stats over a range given as `[begin, end)` pointers.
3. Jagged Matrix [Medium]: allocate rows of varying lengths, answer queries, free everything (LSan checked).
4. Intrusive Free List [Hard]: fixed-size object pool with a free list threaded through unused slots.

### cpp-raii | RAII | Intermediate | status: existing-thin
Summary: Tie resource lifetime to object lifetime.
Lesson must cover:
- constructors acquire, destructors release, stack unwinding, scope guards, RAII wrappers for C APIs
Existing: cpp-scope-guard (keep last).
Problems to add (4):
1. File Handle Wrapper [Easy]: RAII over a simulated C handle API; driver counts open/close.
2. Lock Counter Guard [Medium]: guard that increments/decrements a resource count even on early returns and exceptions.
3. Transaction Rollback [Medium]: RAII transaction that rolls back unless `commit()` called.
4. Unique Handle Template [Hard]: generic `unique_handle<Traits>` with move-only semantics over int descriptors.

### cpp-smart-pointers | Smart Pointers | Intermediate | status: existing-thin
Summary: `unique_ptr`, `shared_ptr`, `weak_ptr`, custom deleters and ownership design.
Lesson must cover:
- exclusive vs shared ownership, `make_unique/make_shared`, control blocks, cycles and `weak_ptr`, `enable_shared_from_this`, custom deleters
Existing: cpp-ownership-tree (keep last).
Problems to add (4):
1. Unique Ownership Transfer [Easy]: move `unique_ptr` jobs between queues; output final owners.
2. Observer Without Leaks [Medium]: subject keeps `weak_ptr` observers, prunes expired ones.
3. Break the Cycle [Medium]: parent/child graph leaking via `shared_ptr` cycle; fix with `weak_ptr` (driver checks destructor counts).
4. Mini shared_ptr [Hard]: implement a ref-counted pointer with weak count, copy/move, and `use_count`.

### cpp-value-categories | Value Categories | Advanced | status: existing-thin
Summary: lvalues, prvalues, xvalues and how they drive overloads and moves.
Lesson must cover:
- glvalue/rvalue taxonomy, temporaries materialization, reference binding, `std::move` is a cast, overload on `&`/`&&`
Existing: cpp-overload-category (keep last).
Problems to add (3):
1. Category Classifier [Medium]: a macro/template that reports the category of given expressions; fill in the trait.
2. Ref-Qualified Getters [Medium]: `get() &` returns ref, `get() &&` moves out; driver counts copies.
3. Lifetime Extension Traps [Hard]: fix functions that return references to temporaries; driver checks values under ASan.

### cpp-move-semantics | Move Semantics and Perfect Forwarding | Advanced | status: existing-thin
Summary: Moving resources, forwarding references and `std::forward`.
Lesson must cover:
- move ctor/assignment, moved-from state, `noexcept` and vector growth, forwarding refs, reference collapsing, `emplace`
Existing: cpp-move-counter (keep last).
Problems to add (4):
1. Movable Buffer [Easy]: implement move ctor/assign for a heap buffer; copies counted.
2. noexcept Matters [Medium]: make vector reallocation move instead of copy by marking moves `noexcept`.
3. Perfect Forwarding Factory [Medium]: `make<T>(args...)` that forwards exactly; driver counts copies/moves per argument category.
4. Small-Buffer Move [Hard]: SSO-like string where moves must handle inline vs heap storage correctly.

### cpp-rule-of-five | Rule of 0, 3 and 5 | Advanced | status: existing-thin
Summary: Special member functions and when to write them.
Lesson must cover:
- implicit generation rules, copy-and-swap, self-assignment, rule of zero via members
Existing: cpp-string-buffer (keep last).
Problems to add (3):
1. Rule of Zero Refactor [Easy]: replace raw members by `vector`/`unique_ptr` so defaults are correct.
2. Copy-and-Swap Matrix [Medium]: strong exception guarantee assignment via copy-and-swap.
3. Deep-Copy Polymorphic Container [Hard]: container of `unique_ptr<Shape>` that deep copies via `clone()`.

## Module 03: OOP Basics

### cpp-classes | Classes and Objects | Beginner | status: existing-thin
Summary: Classes, access control, member functions and invariants.
Lesson must cover:
- struct vs class, public/private, `this`, invariants, getters vs behaviour methods, const members
Existing: cpp-account-class (keep last).
Problems to add (4):
1. Rectangle Class [Easy]: area/perimeter/scale/contains with validated dimensions.
2. Stopwatch [Easy]: start/stop/lap/reset state machine as a class.
3. Inventory Item Invariants [Medium]: class keeping quantity ≥ 0 and price consistent across operations; reject illegal commands.
4. Big Integer Class [Hard]: add/subtract/multiply arbitrary-size non-negative integers.

### cpp-constructors | Constructors and Destructors | Intermediate | status: existing-thin
Summary: Initialization order, delegating and explicit constructors, destructors.
Lesson must cover:
- member init lists and order, delegating ctors, `explicit`, default/deleted ctors, destruction order
Existing: cpp-time-of-day (keep last).
Problems to add (3):
1. Construction Order Trace [Easy]: print construction/destruction order of members and bases to match the expected log.
2. explicit Conversion Guard [Medium]: stop accidental `Meters m = 5;` conversions; driver tests overloads.
3. Delegating Date Constructors [Medium]: several ctor forms delegate to one validating ctor.

### cpp-static-friend | Static Members and friend | Intermediate | status: existing-thin
Summary: Class-level state, static functions, friends.
Lesson must cover:
- static data/functions, inline static, static init order fiasco, friend functions/classes and when to use them
Existing: cpp-robot-registry (keep last).
Problems to add (3):
1. Instance Counter [Easy]: count live/total objects via static members.
2. Friend Stream Operator [Medium]: `operator<<`/`>>` as friends for a `Vec3` parser/printer.
3. Meyers Singleton Registry [Medium]: function-local static registry avoiding init order fiasco.

### cpp-operator-overloading | Operator Overloading | Intermediate | status: existing-thin
Summary: Making user types behave like built-ins.
Lesson must cover:
- member vs free operators, symmetric ops, compound assignment, `<=>` and `==`, subscript, call operator, conversions
Existing: cpp-fraction (keep last).
Problems to add (4):
1. Vec2 Arithmetic [Easy]: `+ - * dot cross ==` for 2D vectors.
2. Spaceship Versions [Medium]: semantic version type with defaulted/custom `<=>`; sort versions.
3. Matrix with operator() [Medium]: 2D indexing and multiplication with bounds checks.
4. Polynomial Algebra [Hard]: add/multiply/evaluate/derive polynomials with operators.

### cpp-inheritance | Inheritance | Intermediate | status: existing-thin
Summary: Public inheritance, access, slicing and multiple inheritance.
Lesson must cover:
- is-a, protected, constructors in hierarchies, slicing, name hiding and `using`, multiple and virtual inheritance (diamond)
Existing: cpp-vehicle-chain (keep last).
Problems to add (3):
1. Employee Hierarchy [Easy]: base pay + derived bonus rules.
2. Name Hiding Fix [Medium]: overloads hidden in derived class; fix with `using Base::f`.
3. Diamond Resolver [Hard]: virtual inheritance so a shared base is constructed once; trace output.

### cpp-virtual-polymorphism | Virtual Functions and Polymorphism | Intermediate | status: existing-thin
Summary: Dynamic dispatch, abstract classes, virtual destructors.
Lesson must cover:
- virtual, override, final, pure virtual, virtual destructor necessity, calling virtuals in ctors, `dynamic_cast`
Existing: cpp-expr-tree, cpp-shape-zoo (keep last).
Problems to add (3):
1. Payment Methods [Easy]: abstract `Payment` with card/wallet/bank implementations.
2. Virtual Destructor Leak [Medium]: fix base without virtual destructor; driver checks derived dtor runs.
3. Plugin Dispatch with dynamic_cast [Medium]: capability interfaces discovered with `dynamic_cast`.

### cpp-vtable-internals | vtables and Object Layout | Advanced | status: existing-thin
Summary: How dynamic dispatch is implemented.
Lesson must cover:
- vptr/vtable layout, cost of virtual calls, multiple inheritance thunks, RTTI, `sizeof` of polymorphic objects
Existing: cpp-manual-vtable (keep last).
Problems to add (3):
1. sizeof Predictor [Medium]: compute expected `sizeof` for described class layouts (padding + vptr); verify against real classes.
2. Devirtualization by Hand [Medium]: replace a hot virtual loop by type-sorted batches; must beat a time limit.
3. Type-ID Registry [Hard]: hand-rolled RTTI with per-class ids and `is_a` checks across a hierarchy.

## Module 04: STL

### cpp-vector-array | vector, array and Sequence Containers | Beginner | status: existing-thin
Summary: vector, array, deque, list, forward_list and their complexity.
Lesson must cover:
- capacity vs size, reallocation and iterator invalidation, reserve, erase-remove, deque/list trade-offs
Existing: cpp-merge-slots (keep last).
Problems to add (4):
1. Erase-Remove Filter [Easy]: remove elements by predicate in O(n).
2. Invalidation Bug Hunt [Medium]: fix code that pushes while iterating; driver checks under ASan.
3. Deque Rolling Buffer [Medium]: keep last K readings with push_back/pop_front and stats.
4. list::splice Playlist [Medium]: move song ranges within/between lists in O(1).

### cpp-strings | string and string_view | Beginner | status: existing-thin
Summary: std::string operations, string_view, conversions.
Lesson must cover:
- find/substr/replace, SSO, `string_view` lifetime pitfalls, `to_string`/`stoi`/`from_chars`
Existing: cpp-text-justify (keep last).
Problems to add (4):
1. Word Capitalizer [Easy]: title-case words preserving punctuation.
2. Split with string_view [Medium]: zero-copy split and field extraction from log lines.
3. from_chars Parser [Medium]: parse numbers fast with error reporting per token.
4. Template Expander [Hard]: replace `${name}` placeholders with nested defaults `${a:-b}`.

### cpp-associative | map, set and multimap | Intermediate | status: existing-thin
Summary: Ordered associative containers.
Lesson must cover:
- red-black tree guarantees, lower/upper_bound, equal_range, custom comparators, transparent comparators, node extract/merge
Existing: cpp-booking-calendar (keep last).
Problems to add (4):
1. Word Index [Easy]: `map<string, set<int>>` of words to line numbers.
2. Floor/Ceil Queries [Medium]: dynamic set with insert/erase/floor/ceil.
3. Leaderboard multimap [Medium]: score → names with rank queries and updates.
4. Interval Map [Hard]: assign value to ranges `[l,r)` keeping a canonical `map` (the classic interval_map task).

### cpp-unordered | Unordered Containers and Hashing | Intermediate | status: existing-thin
Summary: Hash tables, custom hashes, load factor.
Lesson must cover:
- buckets, load factor, rehash, custom `hash` specialization, `hash_combine`, anti-hack seeds
Existing: cpp-visited-cells (keep last).
Problems to add (3):
1. Pair-Key Hash [Easy]: count points via `unordered_map<pair<int,int>,int>` with custom hash.
2. Reserve vs Rehash [Medium]: meet a time limit by reserving; count bucket stats.
3. Anti-Hash Defense [Hard]: survive adversarial keys using a splitmix64 seeded hash.

### cpp-adaptors | stack, queue and priority_queue | Intermediate | status: existing-thin
Summary: Container adaptors and custom comparators.
Lesson must cover:
- underlying containers, `priority_queue` with lambda comparators, min-heap tricks, lazy deletion
Existing: cpp-grid-dijkstra (keep last).
Problems to add (3):
1. Bracket Checker [Easy]: stack-based validation with error position.
2. Printer Queue [Medium]: queue simulation with priorities.
3. Lazy-Delete Heap [Medium]: priority queue supporting erase via a second heap.

### cpp-iterators | Iterators | Intermediate | status: existing-thin
Summary: Iterator categories and writing custom iterators.
Lesson must cover:
- categories, iterator traits, `std::advance/distance`, insert iterators, sentinel, writing an iterator for a custom container
Existing: cpp-step-range (keep last).
Problems to add (3):
1. Back Inserter Merge [Easy]: merge sorted sequences with `back_inserter`.
2. Tree In-Order Iterator [Medium]: iterator over a BST using an explicit stack.
3. Zip Iterator [Hard]: iterate two containers in lockstep, compatible with STL algorithms.

### cpp-algorithms | STL Algorithms | Intermediate | status: existing-thin
Summary: `<algorithm>` and `<numeric>` as a vocabulary.
Lesson must cover:
- sort/stable_sort/partial_sort/nth_element, partition, unique, accumulate/transform_reduce, binary search family, permutations
Existing: cpp-leaderboard (keep last).
Problems to add (4):
1. No Raw Loops [Easy]: compute stats using only algorithms (driver greps nothing; tests output).
2. Top-K with nth_element [Medium]: k smallest in O(n) average.
3. next_permutation Scheduler [Medium]: enumerate valid task orders lexicographically.
4. Stable Partition Gather [Hard]: gather selected items to a position preserving order (Sean Parent's gather).

### cpp-lambdas | Lambdas and std::function | Intermediate | status: existing-thin
Summary: Closures, captures, generic lambdas and type erasure via std::function.
Lesson must cover:
- capture by value/ref/init-capture, mutable, generic and template lambdas, `std::function` cost, recursion via Y-combinator style
Existing: cpp-event-bus (keep last).
Problems to add (3):
1. Counter Factory [Easy]: lambdas with mutable captured state.
2. Comparator Builder [Medium]: compose multi-key sort comparators from a spec.
3. Recursive Lambda Memo [Medium]: memoized recursive lambda for grid paths.

### cpp-utilities | pair, tuple, optional, variant, any | Intermediate | status: existing-thin
Summary: Vocabulary types.
Lesson must cover:
- tuple/tie/structured bindings, `optional` semantics, `variant` + `visit` + overloaded pattern, `any`
Existing: cpp-typed-config (keep last).
Problems to add (3):
1. Optional Lookup [Easy]: dictionary returning `optional<int>` with defaulting.
2. Variant Shapes [Medium]: area/perimeter via `std::visit` with an overloaded lambda set.
3. JSON-ish Value [Hard]: recursive variant for a tiny JSON value with printer.

### cpp-ranges | Ranges (C++20) | Advanced | status: existing-thin
Summary: Range algorithms, views and pipelines.
Lesson must cover:
- `std::ranges` algorithms with projections, views (filter/transform/take/drop/split/join), laziness, dangling, writing a view
Existing: cpp-sensor-pipeline (keep last).
Problems to add (3):
1. Projections Sort [Easy]: sort records by member with `ranges::sort(v, {}, &R::key)`.
2. Lazy Pipeline [Medium]: filter/transform/take over an infinite `iota` view.
3. Chunked Statistics [Medium]: `views::chunk`/`slide` (or hand-rolled) moving averages.

### cpp-chrono-random | Time and Randomness: chrono and random | Intermediate | status: new
Summary: Durations, clocks, calendars and reproducible random numbers.
Lesson must cover:
- `duration`, `time_point`, clocks, `duration_cast`, C++20 calendar basics
- engines vs distributions, seeding, reproducibility, why `rand()` is bad
Problems (4):
1. Duration Arithmetic [Easy]: add/subtract mixed-unit durations and print in h:m:s.
2. Calendar Days Between [Medium]: days between dates and weekday with `<chrono>` calendar types.
3. Seeded Simulation [Medium]: deterministic Monte Carlo with `mt19937_64` and a given seed, output must match.
4. Weighted Sampler [Hard]: alias-method sampler checked against `discrete_distribution` statistics.

### cpp-filesystem-files | Files and std::filesystem | Intermediate | status: new
Summary: Reading/writing files and walking directories.
Lesson must cover:
- `fstream` modes, binary I/O, error handling, `std::filesystem` paths and iteration
Problems (4):
1. Binary Record File [Easy]: write fixed-size records to a temp file and read back by index.
2. Path Normalizer [Medium]: lexically normalize/relative paths with `std::filesystem::path`.
3. Directory Size Report [Medium]: build a temp tree from stdin spec, then report sizes per directory.
4. Log Rotator [Hard]: append with size-based rotation (`app.log.1..N`) and verify file contents.

## Module 05: Templates

### cpp-function-templates | Function Templates | Intermediate | status: existing-thin
Summary: Generic functions, deduction and overloading with templates.
Lesson must cover:
- template argument deduction, explicit args, non-type params, overloading vs specialization
Existing: cpp-generic-stats (keep last).
Problems to add (3):
1. Generic Max/Clamp [Easy]: templates working for ints, doubles, strings.
2. Array Size Deduction [Medium]: `template<class T, size_t N>` helpers on raw arrays.
3. Generic Binary Search [Medium]: iterator + comparator template matching `lower_bound` semantics.

### cpp-class-templates | Class Templates | Intermediate | status: existing-thin
Summary: Generic classes, member templates, CTAD.
Lesson must cover:
- class templates, member function definitions, CTAD and deduction guides, dependent names (`typename`, `template`)
Existing: cpp-static-vector (keep last).
Problems to add (3):
1. Generic Stack [Easy]: `Stack<T>` with exceptions on underflow.
2. Matrix<T, R, C> [Medium]: fixed-size matrix with compile-time dimension checks on multiply.
3. Ring Buffer Template [Medium]: `RingBuffer<T, N>` with iterators.

### cpp-template-specialization | Template Specialization | Advanced | status: existing-thin
Summary: Full and partial specialization.
Lesson must cover:
- full vs partial specialization, function template specialization pitfalls, tag dispatch
Existing: cpp-serializer (keep last).
Problems to add (3):
1. Type Name Printer [Easy]: specialized `type_name<T>` for common types and pointers.
2. Partial Specialization for Pointers [Medium]: `Storage<T*>` behaves differently from `Storage<T>`.
3. Tag Dispatch Advance [Medium]: implement `my_advance` choosing random-access vs bidirectional by tag.

### cpp-variadic-templates | Variadic Templates and Fold Expressions | Advanced | status: existing-thin
Summary: Parameter packs and folds.
Lesson must cover:
- packs, `sizeof...`, recursion vs folds, index sequences, tuple iteration
Existing: cpp-mini-format (keep last).
Problems to add (3):
1. Variadic Sum/All/Any [Easy]: fold expressions.
2. Tuple Printer [Medium]: print any tuple with `index_sequence`.
3. Typed Event Dispatcher [Hard]: register handlers with variadic signatures and dispatch by type list.

### cpp-sfinae-traits | SFINAE and Type Traits | Expert | status: existing-thin
Summary: Compile-time introspection.
Lesson must cover:
- `enable_if`, detection idiom, `void_t`, standard traits, writing traits, `if constexpr` as a modern replacement
Existing: cpp-universal-printer (keep last).
Problems to add (3):
1. has_size Detector [Medium]: detect `.size()` and choose behaviour.
2. Custom is_container [Medium]: trait detecting begin/end; printer dispatches.
3. Overload by Capability [Hard]: serialize via `to_string`, `operator<<`, or iterable fallback by priority.

### cpp-concepts | Concepts (C++20) | Advanced | status: existing-thin
Summary: Constraining templates with concepts.
Lesson must cover:
- requires clauses/expressions, standard concepts, subsumption, concept-based overloading, error messages
Existing: cpp-sensor-concepts (keep last).
Problems to add (3):
1. Numeric Concept [Easy]: constrain `mean()` to arithmetic types.
2. Subsumption Overloads [Medium]: `Sortable` vs `RandomAccessSortable` choose algorithm.
3. Container Concept Library [Hard]: define and use `Container`, `SequenceContainer` concepts for generic utilities.

### cpp-crtp-tmp | CRTP and Template Metaprogramming | Expert | status: existing-thin
Summary: Static polymorphism and compile-time computation.
Lesson must cover:
- CRTP mixins, static interfaces, type lists, compile-time recursion, `constexpr` vs TMP
Existing: cpp-crtp-units (keep last).
Problems to add (3):
1. Comparable Mixin [Medium]: derive all comparison ops from `less()` via CRTP.
2. Type List Ops [Hard]: `contains`, `index_of`, `unique` over a type list.
3. Expression Templates [Hard]: lazy vector expressions avoiding temporaries; check numeric result and copy count.

## Module 06: Error Handling

### cpp-exceptions | Exceptions and Exception Safety | Intermediate | status: existing-thin
Summary: Throwing, catching and exception guarantees.
Lesson must cover:
- exception hierarchy, catching by reference, rethrow, nested exceptions, basic/strong/nothrow guarantees, `noexcept`
Existing: cpp-transactional-store (keep last).
Problems to add (4):
1. Parse or Throw [Easy]: number parser throwing typed exceptions; driver prints messages.
2. Custom Exception Hierarchy [Medium]: bank errors with catch ordering.
3. Strong Guarantee Push [Medium]: container insert that leaves state unchanged on throw (throwing copy driver).
4. Nested Exception Trace [Hard]: `throw_with_nested` across layers and print the full chain.

### cpp-expected | std::expected, error codes and assertions | Advanced | status: existing-thin
Summary: Error handling without exceptions.
Lesson must cover:
- `std::expected`, monadic ops (`and_then`, `transform`, `or_else`), `error_code`, assertions and contracts
Existing: cpp-mission-parser (keep last).
Problems to add (3):
1. Safe Division Chain [Easy]: `expected<double, Err>` pipeline.
2. Config Validation with and_then [Medium]: chained validation with first-error reporting.
3. error_code Category [Hard]: custom `error_category` for a device library and mapping to conditions.

## Module 07: Modern C++

### cpp-modern-11-14 | C++11/14 Essentials | Intermediate | status: existing-thin
Summary: The features that define modern C++.
Lesson must cover:
- auto, range-for, nullptr, smart pointers, lambdas, move, `override`, uniform init, `make_unique`
Existing: cpp-modernize-legacy (keep last).
Problems to add (3):
1. Modernize a Loop [Easy]: convert index loops/raw new to modern idioms (behaviour checked).
2. Generic Lambda Utilities [Medium]: C++14 generic lambdas for map/filter helpers.
3. Return Type Deduction [Medium]: `auto` return and `decltype(auto)` forwarding wrapper.

### cpp-modern-17 | C++17 | Advanced | status: existing-thin
Summary: Structured bindings, optional/variant, if constexpr, fold, filesystem.
Lesson must cover:
- structured bindings, if/switch init, `if constexpr`, CTAD, inline variables, `string_view`, parallel algorithms overview
Existing: cpp-disk-report (keep last).
Problems to add (3):
1. Structured Bindings Map [Easy]: iterate maps with bindings and if-init lookups.
2. if constexpr Serializer [Medium]: one function serializing ints, strings, vectors.
3. Aggregate CTAD [Medium]: deduction guides for a `Pair`-like type.

### cpp-modern-20 | C++20: Modules, Coroutines, Spaceship | Expert | status: existing-thin
Summary: Major C++20 features.
Lesson must cover:
- concepts recap, ranges, `<=>`, coroutines (promise types, generators, tasks), modules concepts, `std::format`, `span`
Existing: cpp-coroutine-generator (keep last).
Problems to add (3):
1. std::format Report [Easy]: format a table with widths/precision.
2. Coroutine Task Scheduler [Hard]: cooperative scheduler resuming coroutines in round-robin.
3. Lazy Coroutine Parser [Hard]: coroutine tokenizer that yields tokens on demand.

### cpp-modern-23 | C++23 and Beyond | Expert | status: existing-thin
Summary: Newest standard features.
Lesson must cover:
- `std::expected`, `deducing this`, `std::print`, `mdspan`, `ranges::to`, `flat_map` (where available)
Existing: cpp-grid-cpp23 (keep last).
Problems to add (3):
1. ranges::to Collect [Easy]: build containers from views.
2. Deducing this Builder [Medium]: fluent builder with explicit object parameter.
3. mdspan Matrix Ops [Medium]: 2D/3D views over a flat buffer (fallback implementation allowed).

## Module 08: Concurrency

### cpp-threads | std::thread | Advanced | status: existing-thin
Summary: Creating, joining and partitioning work across threads.
Lesson must cover:
- thread lifecycle, join/detach, `jthread` and stop tokens, passing args, data partitioning, hardware_concurrency
Existing: cpp-parallel-stats (keep last).
Problems to add (3):
1. Parallel Sum [Easy]: split array across threads, combine results deterministically.
2. jthread Cancellation [Medium]: workers stop cleanly on `stop_token`.
3. Parallel Prime Count [Medium]: dynamic chunking to balance uneven work, deterministic output.

### cpp-mutex-locks | Mutexes and Locks | Advanced | status: existing-thin
Summary: Mutual exclusion and lock management.
Lesson must cover:
- data races, `mutex`, `lock_guard`, `unique_lock`, `scoped_lock` for multiple locks, `shared_mutex`, deadlocks
Existing: cpp-concurrent-ledger (keep last).
Problems to add (3):
1. Thread-Safe Counter Map [Easy]: mutex-protected word counts from many threads.
2. Deadlock-Free Transfers [Medium]: `scoped_lock` for account pairs; TSan clean.
3. Reader-Writer Cache [Medium]: `shared_mutex` cache with concurrent reads.

### cpp-condition-variables | Condition Variables | Advanced | status: existing-thin
Summary: Waiting for conditions.
Lesson must cover:
- wait with predicate, spurious wakeups, notify_one vs all, producer-consumer, shutdown protocols
Existing: cpp-bounded-queue (keep last).
Problems to add (3):
1. Ping-Pong Threads [Easy]: two threads alternate printing strictly.
2. Countdown Latch [Medium]: implement latch/barrier with cv.
3. Ordered Printing [Medium]: N threads print in round-robin order using one cv.

### cpp-atomics-memory-model | Atomics and the Memory Model | Expert | status: existing-thin
Summary: Atomic operations and memory orderings.
Lesson must cover:
- `atomic<T>`, happens-before, seq_cst/acquire/release/relaxed, CAS loops, false sharing
Existing: cpp-atomic-telemetry (keep last).
Problems to add (3):
1. Atomic Stats [Easy]: relaxed counters vs mutex; correct totals.
2. Spinlock [Medium]: `atomic_flag` spinlock with backoff.
3. Release-Acquire Publication [Hard]: publish a struct to readers with correct ordering (checked under TSan).

### cpp-async-futures | Futures, Promises and async | Advanced | status: existing-thin
Summary: Task-based concurrency.
Lesson must cover:
- `async` launch policies, `future/promise`, `packaged_task`, `shared_future`, exception propagation
Existing: cpp-task-pool (keep last).
Problems to add (3):
1. Async Map-Reduce [Easy]: `std::async` chunks summed via futures.
2. Promise Fulfilment [Medium]: worker sets values or exceptions; main prints in order.
3. Futures Dependency Chain [Medium]: run a DAG of tasks with `shared_future` dependencies.

### cpp-lock-free | Lock-Free Programming | Research | status: existing-thin
Summary: Non-blocking data structures.
Lesson must cover:
- lock-free vs wait-free, CAS, ABA, hazard pointers/epochs overview, SPSC/MPMC queues
Existing: cpp-spsc-ring (keep last).
Problems to add (3):
1. Lock-Free Counter Max [Medium]: atomic max update with CAS loop.
2. Treiber Stack [Hard]: lock-free stack with tagged pointers against ABA (deferred reclamation).
3. MPMC Bounded Queue [Hard]: Vyukov-style queue with sequence numbers.

### cpp-thread-pools | Thread Pools and Task Graphs | Advanced | status: new
Summary: Building reusable executors.
Lesson must cover:
- worker loop design, task queues, futures from `submit`, shutdown, work stealing, task graphs and dependencies
Problems (5):
1. Fixed Thread Pool [Medium]: submit returns futures; results printed in submit order.
2. Graceful Shutdown [Medium]: drain vs cancel semantics with counts.
3. Task Graph Executor [Hard]: run a DAG respecting dependencies with maximum parallelism; deterministic output.
4. Work-Stealing Deques [Hard]: per-worker deques, steal from others; verify all tasks run once.
5. Parallel Quicksort on Pool [Hard]: recursive tasks submitted to the pool without deadlock.

### cpp-parallel-patterns | Parallel Algorithms and Patterns | Advanced | status: new
Summary: Data-parallel thinking.
Lesson must cover:
- execution policies, map/reduce/scan, parallel prefix sums, pipeline and fork-join patterns, Amdahl's law
Problems (4):
1. Parallel Transform-Reduce [Easy]: use execution policies or threads for a sum of squares.
2. Parallel Prefix Sum [Medium]: two-pass blocked scan.
3. Pipeline Stages [Medium]: three-stage producer→transform→writer pipeline with bounded queues.
4. Parallel Histogram [Hard]: per-thread local histograms merged; beat the time limit of a single-mutex version.

## Module 09: Advanced C++

### cpp-lifetime-ub | Object Lifetime and Undefined Behavior | Expert | status: existing-thin
Summary: Lifetimes, UB categories and how to avoid them.
Lesson must cover:
- storage duration, lifetime start/end, strict aliasing, `std::launder`, signed overflow, dangling, sanitizers
Existing: cpp-string-interner (keep last).
Problems to add (3):
1. Fix the Dangling View [Medium]: functions returning `string_view` to temporaries.
2. Type Punning Safely [Medium]: use `memcpy`/`bit_cast` to inspect float bits.
3. Placement new Storage [Hard]: manual lifetime management in an aligned buffer (optional-like).

### cpp-memory-performance | Memory Layout, Cache and Performance | Expert | status: existing-thin
Summary: Caches, layout and performance.
Lesson must cover:
- cache lines, locality, AoS vs SoA, padding/alignment, branch prediction, measuring
Existing: cpp-struct-layout (keep last).
Problems to add (3):
1. Loop Interchange [Medium]: matrix sum by rows vs columns; must meet time limit.
2. AoS to SoA Particles [Medium]: refactor particle update to SoA for speed.
3. Blocked Matrix Multiply [Hard]: tiled multiply of 1024² matrices within the time limit.

### cpp-allocators | Custom Allocators and PMR | Expert | status: existing-thin
Summary: Allocator model and polymorphic memory resources.
Lesson must cover:
- allocator requirements, `std::pmr` resources (monotonic, pool), arenas, alignment
Existing: cpp-arena-resource (keep last).
Problems to add (3):
1. Counting Allocator [Medium]: allocator that counts allocations of a `vector`.
2. Monotonic Buffer Parse [Medium]: use `pmr::monotonic_buffer_resource` for per-request strings.
3. Pool Allocator for Nodes [Hard]: fixed-size pool used by `std::list` / map nodes; beat time limit.

### cpp-pimpl-abi | PIMPL, ABI and Linking | Expert | status: existing-thin
Summary: Stable interfaces and binary compatibility.
Lesson must cover:
- PIMPL with `unique_ptr`, ABI breakers, symbol visibility, static vs dynamic linking, name mangling
Existing: cpp-pimpl-motor (keep last).
Problems to add (3):
1. Fast PIMPL [Medium]: in-place storage PIMPL with size/alignment static_asserts.
2. Name Demangler Lite [Hard]: demangle a subset of Itanium mangled names.
3. ABI Change Classifier [Medium]: given before/after struct/class declarations, classify changes as ABI-safe or breaking.

---

# DSA in C++ (Modules 10–21): complete, from zero

Every DSA topic: lesson with dry runs, a reusable template, recognition cues, variations, pitfalls and interview Q&A; 6–10 problems, each a different pattern, stress-tested against a brute force.

## Module 10: DSA Foundations (done)

### cpp-complexity-cp | Complexity Analysis and Problem-Solving Setup | Beginner | status: existing-ok
Existing: 7 problems. No changes.

### cpp-dsa-recursion | Recursion from Zero | Beginner | status: existing-ok
Existing: 8 problems. No changes.

### cpp-dsa-arrays-basics | Arrays, Vectors and Matrices | Beginner | status: existing-ok
Existing: 8 problems. No changes.

### cpp-dsa-sorting | Sorting Algorithms from Scratch | Intermediate | status: existing-ok
Existing: 9 problems. No changes.

## Module 11: Array and String Patterns (done)

### cpp-arrays-two-pointers | Two Pointers | Intermediate | status: existing-ok
Existing: 9 problems.

### cpp-dsa-sliding-window | Sliding Window | Intermediate | status: existing-ok
Existing: 9 problems.

### cpp-hashing-prefix | Prefix Sums and Difference Arrays | Intermediate | status: existing-ok
Existing: 8 problems.

### cpp-dsa-hashing | Hashing Patterns | Intermediate | status: existing-ok
Existing: 8 problems.

### cpp-dsa-kadane-subarrays | Subarray Techniques: Kadane, Voting and Index Tricks | Intermediate | status: existing-ok
Existing: 8 problems.

### cpp-dsa-intervals-sweep | Intervals and Sweep Line | Intermediate | status: existing-ok
Existing: 8 problems.

### cpp-dsa-strings-basics | String Manipulation Patterns | Intermediate | status: existing-ok
Existing: 8 problems.

## Module 12: Searching (done)

### cpp-binary-search | Binary Search on Indices | Intermediate | status: existing-ok
Existing: 7 problems.

### cpp-dsa-binary-search-answer | Binary Search on the Answer | Advanced | status: existing-ok
Existing: 9 problems.

## Module 13: Linked Lists

### cpp-linked-trees | Singly Linked Lists from Scratch | Intermediate | status: existing-ok
Existing: 8 problems.

### cpp-dsa-doubly-circular | Doubly and Circular Linked Lists | Intermediate | status: existing-ok
Existing: 7 problems.

### cpp-dsa-list-reversal | Linked List Reversal Patterns | Intermediate | status: existing-ok
Existing: 5 problems, one under the 6-problem DSA band. Optional add (1): 6. Swap Nodes in Pairs Recursively [Medium]: recursive pairwise relinking, contrasting with the iterative k-group solution.

### cpp-dsa-fast-slow | Fast and Slow Pointers | Intermediate | status: new (Wave 1, Author A)
Summary: Two pointers moving at different speeds over lists and functional graphs.
Lesson must cover:
- middle node (both conventions), Floyd cycle detection and the proof of the start-of-cycle step, cycle length
- functional graphs on arrays (duplicate number), Brent's algorithm, palindrome list via reverse-half
Problems (8):
1. Middle of the List [Easy]: return first/second middle as requested.
2. Has Cycle [Easy]: Floyd detection on a list built with a tail→pos link.
3. Cycle Start and Length [Medium]: find entry node and loop length in O(1) memory.
4. Happy Number [Easy]: cycle detection on an implicit sequence.
5. Find the Duplicate Number [Medium]: array as a functional graph, read-only, O(1) memory.
6. Palindrome Linked List [Medium]: reverse second half, compare, restore the list.
7. Remove N-th From End [Medium]: gap pointers, one pass.
8. Intersection of Two Lists [Medium]: pointer switching trick, also with cycles absent proof.
9. Circular Array Loop [Hard]: detect single-direction cycles of length > 1 with marking.

### cpp-dsa-list-merge | Merge and Rearrange Lists | Intermediate | status: new (Wave 1, Author A)
Summary: Merging, partitioning and rearranging nodes by relinking.
Lesson must cover:
- dummy head merging, k-way merge with heap vs divide & conquer, merge sort on lists, partition stability, deep copy with random pointers
Problems (9):
1. Merge Two Sorted Lists [Easy]: dummy head splice.
2. Partition List [Easy]: stable partition around x with two tails.
3. Odd-Even Rearrange [Easy]: group by position parity in place.
4. Add Two Numbers [Medium]: digits in reverse order with carry; then forward-order variant via stacks.
5. Reorder List [Medium]: L0→Ln→L1→Ln-1 using middle + reverse + weave.
6. Sort List [Medium]: bottom-up merge sort O(n log n), O(1) extra.
7. Merge k Sorted Lists [Hard]: heap of heads; compare with pairwise D&C.
8. Copy List with Random Pointer [Medium]: interleaving trick without a hash map.
9. Flatten a Multilevel List [Hard]: child pointers flattened depth-first in place.

### cpp-dsa-skip-list | Advanced Lists: Skip, XOR and Unrolled | Advanced | status: new (Wave 1, Author A)
Summary: Linked structures that trade memory/randomness for speed.
Lesson must cover:
- skip list levels, expected O(log n) proof idea, deterministic seeds, XOR linked list, unrolled lists and cache behaviour
Problems (6):
1. XOR Linked List [Medium]: traverse both directions with `prev ^ next`.
2. Skip List Search/Insert [Medium]: seeded levels, ordered set operations.
3. Skip List Erase and Rank [Hard]: width-augmented skip list answering k-th and rank.
4. Unrolled Linked List [Medium]: blocks of B elements with split/merge on insert/erase at index.
5. Rope via Unrolled List [Hard]: text editor with insert/delete substring at position.
6. Sorted Map Benchmark [Hard]: skip list must handle 10⁶ ops within the limit.

## Module 14: Stacks, Queues and Heaps (Wave 1, Author B)

### cpp-stacks-queues | Stacks: Implementation and Classic Uses | Intermediate | status: rebuild
Summary: Stack from scratch and the problems it solves (old broad topic narrowed to stacks).
Lesson must cover:
- array/list stack, LIFO reasoning, balanced brackets, min stack, expression evaluation, shunting-yard, stack-based DFS
Existing: cpp-monotonic-suite (keep last as mixed review).
Problems (8):
1. Array Stack with Growth [Easy]: implement push/pop/top with errors.
2. Valid Brackets with Position [Easy]: report first error index.
3. Min Stack [Easy]: O(1) getMin with pair or diff encoding.
4. Evaluate RPN [Easy]: integer postfix with truncating division.
5. Infix to Postfix [Medium]: shunting-yard with precedence and associativity (`^` right).
6. Basic Calculator [Hard]: `+ - * / ( )` and unary minus evaluated with two stacks.
7. Decode String [Medium]: `3[a2[c]]` nesting via stack of builders.
8. Simplify Unix Path [Medium]: `..`, `.` and repeated slashes.
9. Asteroid Collision [Medium]: stack simulation of collisions.

### cpp-dsa-monotonic-stack | Monotonic Stack | Advanced | status: new
Summary: Stacks kept sorted to find nearest greater/smaller elements in O(n).
Lesson must cover:
- invariant, amortized proof, next/previous greater/smaller, strict vs non-strict ties for counting, contribution technique
Problems (9):
1. Next Greater Element [Easy]: basic pattern.
2. Daily Temperatures [Easy]: distance to next warmer.
3. Next Greater in Circular Array [Medium]: iterate twice.
4. Stock Span [Medium]: online previous-greater counting.
5. Largest Rectangle in Histogram [Hard]: boundaries via stack.
6. Maximal Rectangle in Binary Matrix [Hard]: histogram per row.
7. Trapping Rain Water (stack form) [Medium]: layer-by-layer water.
8. Sum of Subarray Minimums [Hard]: contribution with tie-breaking (mod 1e9+7).
9. Remove K Digits [Medium]: greedy monotonic stack for smallest number.
10. 132 Pattern [Hard]: reverse scan with stack and candidate third.

### cpp-dsa-queues-deques | Queues and Deques | Intermediate | status: new
Summary: FIFO structures, circular buffers and the monotonic deque.
Lesson must cover:
- circular array queue, queue via two stacks (amortized), deque, monotonic deque window max/min, 0-1 BFS preview
Problems (8):
1. Circular Queue [Easy]: fixed capacity with full/empty detection.
2. Queue via Two Stacks [Easy]: amortized O(1).
3. Stack via Queues [Easy]: single-queue rotation.
4. Recent Calls Counter [Easy]: sliding time window queue.
5. Sliding Window Maximum [Medium]: monotonic deque.
6. Shortest Subarray with Sum ≥ K [Hard]: deque over prefix sums with negatives.
7. Longest Subarray with |max−min| ≤ L [Medium]: two deques.
8. Jump Game with Window Max DP [Hard]: dp[i] = a[i] + max(dp[i−k..i−1]) via deque.

### cpp-dsa-heaps | Heaps and Priority Queues | Intermediate | status: new
Summary: Binary heaps from scratch and heap patterns.
Lesson must cover:
- array heap, sift up/down, O(n) heapify proof, top-K, k-way merge, two-heaps median, lazy deletion, indexed heap with decrease-key
Problems (9):
1. Binary Heap from Scratch [Easy]: push/pop/top on array.
2. Kth Largest in Stream [Easy]: size-k min-heap.
3. Top K Frequent [Medium]: count + heap (vs bucket).
4. K Closest Points [Medium]: max-heap of size k.
5. Merge K Sorted Arrays [Medium]: heap of (value, array, index).
6. Median of Data Stream [Hard]: two heaps rebalance.
7. Task Scheduler with Cooldown [Medium]: heap + waiting queue simulation.
8. Sliding Window Median [Hard]: two heaps with lazy deletion.
9. Indexed Min-Heap [Hard]: decrease-key and erase by id; used for Dijkstra-like updates.
10. IPO / Maximize Capital [Hard]: sorted projects + max-heap greedy.

## Module 15: Trees

### cpp-dsa-tree-traversals | Binary Tree Basics and Traversals | Intermediate | status: new (Wave 1, Author C)
Summary: Building trees and visiting nodes in every order.
Lesson must cover:
- recursive pre/in/post, iterative with stacks, Morris traversal, level order, zigzag, vertical and boundary order
Problems (9):
1. Three Traversals Recursive [Easy]: from level-order input with nulls.
2. Iterative In-Order and Post-Order [Medium]: explicit stack, one-stack post-order.
3. Level Order by Levels [Easy]: BFS by layer.
4. Zigzag Level Order [Medium]: deque alternation.
5. Right Side View [Medium]: last of each level / DFS depth trick.
6. Vertical Order [Medium]: column, row, value tie-break.
7. Boundary Traversal [Hard]: left boundary, leaves, reversed right boundary.
8. Morris In-Order [Hard]: O(1) memory traversal, tree restored.
9. Maximum Width of Tree [Medium]: index positions per level with overflow normalization.

### cpp-dsa-tree-construction | Building and Serializing Trees | Intermediate | status: new (Wave 1, Author C)
Summary: Reconstructing trees from traversals and encoding them.
Lesson must cover:
- uniqueness conditions, pre+in, post+in, pre+post (full trees), serialize/deserialize formats, BST from preorder
Problems (7):
1. Tree from Preorder and Inorder [Medium]: hash map of positions.
2. Tree from Inorder and Postorder [Medium].
3. Full Tree from Preorder and Postorder [Medium].
4. BST from Preorder in O(n) [Medium]: bounds recursion.
5. Serialize/Deserialize Binary Tree [Hard]: codec round trip.
6. Tree from Parenthesis String [Medium]: `4(2(3)(1))(6(5))`.
7. Find Duplicate Subtrees [Hard]: serialization ids via hashing.

### cpp-dsa-tree-paths | Tree Properties and Paths | Intermediate | status: new (Wave 1, Author C)
Summary: Postorder computations: heights, diameters, path sums and LCA.
Lesson must cover:
- return-value design for tree recursion, global vs returned answers, root-to-leaf vs any-path sums, LCA by recursion and parent pointers
Problems (9):
1. Max Depth and Min Depth [Easy].
2. Balanced Tree Check [Easy]: height with early exit.
3. Diameter of Binary Tree [Medium].
4. Path Sum II [Medium]: all root-to-leaf paths with target.
5. Path Sum III [Medium]: any downward path with prefix-sum hashing.
6. Binary Tree Max Path Sum [Hard].
7. Lowest Common Ancestor [Medium]: recursion without parent pointers.
8. All Nodes at Distance K [Medium]: parent map + BFS.
9. Burn the Tree / Time to Infect [Medium]: from a start node.
10. Count Good Nodes [Easy]: max along path.

### cpp-dsa-bst | Binary Search Trees | Intermediate | status: new (Wave 1, Author C)
Summary: Ordered binary trees and their operations.
Lesson must cover:
- search/insert/delete (three cases), validate with bounds, in-order = sorted, kth smallest, successor/predecessor, BST iterator, balanced BST from sorted array
Problems (9):
1. BST Insert and Search [Easy].
2. Validate BST [Medium]: bounds with 64-bit edges.
3. Delete Node in BST [Medium].
4. Kth Smallest [Medium]: in-order with early stop; follow-up with subtree sizes.
5. Inorder Successor [Medium]: without parent pointers.
6. BST Iterator [Medium]: O(h) memory.
7. Sorted Array to Balanced BST [Easy].
8. Recover Swapped BST [Hard]: two misplaced nodes via in-order.
9. Two Sum in BST [Medium]: forward and reverse iterators.
10. Trim BST and Range Sum [Medium].

### cpp-dsa-balanced-bst | Self-Balancing Trees | Advanced | status: new
Summary: Keeping BSTs at O(log n) height: AVL, red-black and treaps.
Lesson must cover:
- rotations, AVL balance factors and the four cases, red-black invariants (and how std::map uses them), treaps and implicit treaps, order-statistics via sizes, `__gnu_pbds` tree
Problems (8):
1. Rotation Practice [Easy]: apply given rotations and print the tree.
2. AVL Insert [Medium]: maintain balance; print heights after each insert.
3. AVL Delete [Hard]: rebalancing on the way up.
4. Order-Statistic Tree [Medium]: size-augmented AVL/treap for rank/select.
5. Red-Black Validator [Medium]: check all RB properties on a given colored tree.
6. Treap Split/Merge [Hard]: ordered set with range erase.
7. Implicit Treap Array [Hard]: insert at position, reverse range, range sum.
8. Count Smaller After Self [Medium]: using pbds or the order-statistic tree.

### cpp-dsa-tries | Tries | Advanced | status: new
Summary: Prefix trees for strings and bits.
Lesson must cover:
- array vs map children, insert/search/prefix, counting via node counters, deletion, trie + DFS for word search, binary (XOR) trie, memory estimation
Problems (8):
1. Implement Trie [Easy]: insert/search/startsWith.
2. Prefix Count and Erase [Medium]: counters per node.
3. Autocomplete Top-3 [Medium]: lexicographic suggestions per typed prefix.
4. Replace Words by Roots [Medium].
5. Word Search II [Hard]: trie-guided backtracking on a grid with pruning.
6. Maximum XOR of Two Numbers [Medium]: bitwise trie.
7. Max XOR with Limit Queries [Hard]: offline sorted queries into XOR trie.
8. Wildcard Dictionary [Medium]: `.` matches any char via DFS.
9. Longest Word Buildable Letter by Letter [Medium].

### cpp-advanced-ds | Segment Trees | Expert | status: rebuild
Summary: Segment trees from point updates to lazy propagation (old broad topic narrowed).
Lesson must cover:
- recursive and iterative segment trees, combine functions/monoids, lazy propagation (add, assign, both), descending the tree (first index ≥ x), merge sort tree, dynamic/sparse trees
Existing: cpp-range-query-engine (keep last).
Problems (9):
1. Range Sum, Point Update [Easy]: iterative bottom-up tree.
2. Range Min with Index [Easy]: pair combine.
3. Max Subarray Sum on Segment [Hard]: four-field node merge.
4. Range Add, Range Sum [Medium]: lazy propagation.
5. Range Assign + Range Add [Hard]: composing lazy tags.
6. First Element ≥ X [Medium]: tree descent.
7. Count ≤ K in Range [Hard]: merge sort tree with binary search.
8. Dynamic Segment Tree [Hard]: coordinates up to 1e9 with node creation on demand.
9. Rectangle Union Area [Hard]: sweep + segment tree of covered length.

### cpp-dsa-fenwick | Fenwick Trees | Advanced | status: new
Summary: Binary indexed trees for prefix aggregates.
Lesson must cover:
- lowbit, update/query proof, building in O(n), range update/point query, range-range with two BITs, 2D BIT, k-th via binary lifting, inversions
Problems (8):
1. BIT Point Update Prefix Sum [Easy].
2. Range Update, Point Query [Easy]: difference BIT.
3. Range Update, Range Query [Medium]: two BITs.
4. Count Inversions [Medium]: coordinate compression + BIT.
5. K-th Smallest in Multiset [Medium]: binary lifting over BIT.
6. 2D BIT Matrix Sum [Medium].
7. Distinct Values in Range Offline [Hard]: sort queries by right end, last occurrence.
8. Longest Increasing Subsequence Count via BIT [Hard]: (length, count) pairs.

### cpp-dsa-range-queries | Static Range Queries | Advanced | status: new
Summary: Precomputation tricks for queries on immutable arrays.
Lesson must cover:
- sparse table for idempotent ops, O(1) RMQ, disjoint sparse table, sqrt decomposition, Mo's algorithm and ordering, Mo with updates overview
Problems (7):
1. Sparse Table RMQ [Easy].
2. Range GCD Queries [Medium]: sparse table with gcd.
3. Count Subarrays with GCD = g [Hard]: sparse table + binary search.
4. Sqrt Decomposition Point Update / Range Sum [Medium].
5. Block Range Add + Count ≥ x [Hard]: sorted blocks.
6. Mo's Distinct Count [Hard].
7. Mo's Pair Count (equal pairs in range) [Hard]: incremental add/remove.

### cpp-dsa-tree-advanced | Advanced Tree Techniques | Expert | status: new
Summary: Techniques for queries on (general) trees.
Lesson must cover:
- binary lifting (k-th ancestor, LCA), Euler tour + RMQ LCA, subtree queries via tin/tout, tree DP and rerooting, small-to-large merging, heavy-light decomposition, centroid decomposition
Problems (9):
1. K-th Ancestor [Easy]: binary lifting.
2. LCA and Distance Queries [Medium]: binary lifting.
3. Subtree Sum with Updates [Medium]: Euler tour + BIT.
4. Sum of Distances to All Nodes [Hard]: rerooting DP.
5. Distinct Colors in Subtrees [Hard]: small-to-large set merging.
6. Path Max Query with Updates [Hard]: HLD + segment tree.
7. Path Add, Path Sum [Expert]: HLD with lazy segment tree.
8. Count Paths of Length K [Hard]: centroid decomposition.
9. Nearest Marked Node [Hard]: centroid tree with updates.

### cpp-dsa-persistent-offline | Persistent and Offline Techniques | Expert | status: new
Summary: Querying history and answering queries out of order.
Lesson must cover:
- path copying, persistent segment tree (k-th smallest in range), persistent arrays, offline processing, DSU rollback, parallel binary search, CDQ divide & conquer overview
Problems (6):
1. Persistent Array Versions [Medium]: set/get in any version.
2. K-th Smallest in Range [Hard]: persistent segment tree on values.
3. Count Distinct in Range Online [Hard]: persistent tree on next occurrence.
4. Offline Connectivity with Rollback DSU [Expert]: edges added/removed over time (segment tree on time).
5. Parallel Binary Search: Meteors-style [Expert]: when does each member reach its target.
6. 3D Dominance Counting [Expert]: CDQ divide and conquer.

## Module 16: Graphs

### cpp-graphs | Graph Representation, BFS and DFS | Intermediate | status: rebuild (Wave 1, Author D)
Summary: Storing graphs and the two fundamental traversals (old broad topic narrowed).
Lesson must cover:
- adjacency list/matrix/edge list, directed vs undirected, BFS levels and shortest unweighted paths, DFS recursive/iterative, components, grid graphs, multi-source BFS, path reconstruction
Existing: cpp-graph-engine (keep last).
Problems (9):
1. Count Connected Components [Easy].
2. Number of Islands [Easy]: grid DFS/BFS.
3. Shortest Path in Unweighted Graph with Path [Medium]: parent array reconstruction.
4. Rotting Oranges [Medium]: multi-source BFS.
5. Walls and Gates / Distance to Nearest Exit [Medium]: multi-source BFS.
6. Clone Graph [Medium]: map old→new.
7. Word Ladder [Hard]: implicit graph with wildcard buckets.
8. Knight Minimum Moves [Medium]: BFS on implicit board.
9. Shortest Path Visiting Keys (BFS with state) [Hard]: (cell, keymask) states.

### cpp-dsa-cycles-bipartite | Cycles and Bipartiteness | Intermediate | status: new (Wave 1, Author D)
Summary: Detecting cycles and two-colorings.
Lesson must cover:
- undirected cycle via parent tracking/DSU, directed cycle with colors, recovering the cycle, bipartite check by BFS coloring, odd cycles
Problems (7):
1. Undirected Cycle Exists [Easy].
2. Directed Cycle with Witness [Medium]: print one cycle.
3. Is Graph Bipartite [Easy].
4. Possible Bipartition (dislikes) [Medium].
5. Find Eventual Safe States [Medium]: reverse graph or colors.
6. Shortest Cycle in Undirected Graph [Hard]: BFS from each node.
7. Redundant Connection II [Hard]: directed tree with one extra edge.

### cpp-dsa-topo-sort | Topological Sort and DAGs | Intermediate | status: new (Wave 1, Author D)
Summary: Ordering DAGs and DP over them.
Lesson must cover:
- Kahn's algorithm, DFS post-order, cycle detection by count, lexicographically smallest order, DAG longest path, counting paths, parallel scheduling
Problems (8):
1. Course Schedule Order [Easy]: Kahn.
2. Lexicographically Smallest Topo Order [Medium]: min-heap Kahn.
3. Alien Dictionary [Hard]: build edges from adjacent words, detect invalid prefix.
4. Minimum Semesters (parallel courses) [Medium]: BFS layers.
5. Longest Path in DAG [Medium]: topo + DP with weights.
6. Count Paths mod p [Medium].
7. Job Scheduling with Durations [Hard]: earliest finish time (critical path).
8. Unique Topological Order Check [Medium]: queue size always 1.

### cpp-dsa-shortest-paths | Shortest Paths | Advanced | status: new (Wave 1, Author D)
Summary: Weighted shortest paths in all their forms.
Lesson must cover:
- relaxation, 0-1 BFS, Dijkstra with heap and proof, Bellman–Ford and negative cycle detection, SPFA caveats, Floyd–Warshall, A* with admissible heuristics, multi-criteria states
Problems (10):
1. Dijkstra Single Source [Easy].
2. 0-1 BFS Minimum Flips [Medium].
3. Network Delay Time [Easy].
4. Cheapest Flight within K Stops [Medium]: Bellman–Ford layers.
5. Negative Cycle Detection with Cycle Output [Hard].
6. Floyd–Warshall All Pairs with Path [Medium].
7. Path with Minimum Effort [Medium]: Dijkstra on max-edge metric.
8. Dijkstra on State Graph (fuel/charges) [Hard].
9. Number of Shortest Paths mod p [Medium].
10. A* Grid Pathfinding [Medium]: Manhattan heuristic, node expansion counts compared.

### cpp-dsa-dsu-mst | Union-Find and Minimum Spanning Trees | Advanced | status: new
Summary: Disjoint sets and spanning trees.
Lesson must cover:
- union by rank/size, path compression, inverse Ackermann intuition, weighted/parity DSU, Kruskal proof (cut property), Prim with heap, second-best MST, DSU on offline problems
Problems (9):
1. DSU Basics [Easy]: union/find/same with component sizes.
2. Accounts Merge [Medium].
3. Satisfiability of Equations [Medium]: `==` then `!=`.
4. Weighted DSU: Evaluate Division [Hard]: ratios on edges.
5. Parity DSU: Bipartite Online [Hard].
6. Kruskal MST [Easy].
7. Prim on Dense Graph [Medium]: O(V²) version.
8. Min Cost to Connect Points [Medium].
9. Second-Best MST [Hard]: max edge on path via binary lifting.
10. Critical and Pseudo-Critical MST Edges [Hard].

### cpp-dsa-graph-connectivity | Connectivity: SCC, Bridges, 2-SAT | Expert | status: new
Summary: Structure of connectivity in directed and undirected graphs.
Lesson must cover:
- Tarjan low-link, bridges and articulation points, 2-edge/biconnected components, Kosaraju, condensation DAG, 2-SAT via SCC
Problems (8):
1. Find Bridges [Medium].
2. Articulation Points [Medium].
3. Strongly Connected Components (Kosaraju) [Medium].
4. Tarjan SCC with Condensation DAG [Hard]: count sources/sinks.
5. Minimum Edges to Make Strongly Connected [Hard]: max(sources, sinks).
6. 2-SAT Feasibility and Assignment [Hard].
7. Biconnected Components (blocks) [Hard].
8. Critical Connections in a Network [Medium]: bridge application with large input.

### cpp-dsa-euler-paths | Euler and Hamilton Paths | Advanced | status: new
Summary: Traversing every edge or every vertex.
Lesson must cover:
- Euler conditions directed/undirected, Hierholzer iterative, lexicographic itineraries, de Bruijn sequences, Hamiltonian path via bitmask DP
Problems (6):
1. Euler Path Existence [Easy]: degree conditions + connectivity.
2. Reconstruct Itinerary [Medium]: lexicographically smallest Euler path.
3. Valid Arrangement of Pairs [Hard]: directed Euler path at scale.
4. De Bruijn Cracking the Safe [Hard].
5. Hamiltonian Path in Small Graph [Medium]: bitmask DP.
6. Shortest Superstring Order [Hard]: Hamiltonian path DP with overlaps.

### cpp-dsa-flows | Flows and Matching | Expert | status: new
Summary: Max flow, min cut and bipartite matching.
Lesson must cover:
- residual graphs, augmenting paths, Edmonds–Karp, Dinic with level graph, max-flow min-cut theorem, recovering the cut, bipartite matching (Kuhn, Hopcroft–Karp), min-cost flow, modeling tricks (node splitting, supersource)
Problems (8):
1. Max Flow Edmonds–Karp [Medium].
2. Dinic on Large Graph [Hard].
3. Min Cut Edges [Hard]: reachable set from source in residual graph.
4. Bipartite Matching (Kuhn) [Medium].
5. Hopcroft–Karp Large Matching [Hard].
6. Edge-Disjoint / Vertex-Disjoint Paths [Hard]: node splitting.
7. Project Selection (max closure) [Expert].
8. Min-Cost Max-Flow Assignment [Expert]: SPFA/Dijkstra with potentials.

## Module 17: Recursion, Backtracking and Divide & Conquer

### cpp-dsa-backtracking | Backtracking | Advanced | status: new
Summary: Exhaustive search with choose–explore–unchoose and pruning.
Lesson must cover:
- decision trees, state restore, duplicates handling with sorting, pruning by bounds, constraint propagation, complexity estimates
Problems (10):
1. Subsets [Easy].
2. Subsets with Duplicates [Medium].
3. Permutations with Duplicates [Medium].
4. Combination Sum (reuse) [Medium].
5. Generate Parentheses [Medium].
6. Palindrome Partitioning [Medium].
7. N-Queens Count with Bitmasks [Hard].
8. Sudoku Solver [Hard]: MRV heuristic.
9. Word Search on Grid [Medium].
10. Partition into K Equal Subsets [Hard]: pruning with sorting and memo.

### cpp-dsa-divide-conquer | Divide and Conquer | Advanced | status: new
Summary: Split, solve, combine.
Lesson must cover:
- recurrence analysis in practice, merge-sort based counting, quickselect expected time, closest pair, Karatsuba, D&C on arrays (max subarray), Strassen idea
Problems (7):
1. Count Inversions via Merge Sort [Easy].
2. Quickselect K-th Element [Medium]: randomized, worst-case discussion.
3. Count Range Sums [Hard]: merge sort on prefix sums.
4. Reverse Pairs [Hard]: `a[i] > 2a[j]`.
5. Closest Pair of Points [Hard].
6. Karatsuba Big Multiplication [Hard].
7. Skyline Problem [Hard]: merging skylines.

### cpp-dsa-bits | Bit Manipulation | Intermediate | status: new
Summary: Thinking in bits.
Lesson must cover:
- two's complement, masks and shifts, lowbit, popcount/clz/ctz builtins and `<bit>`, subset enumeration and submask loops, XOR properties, Gray code, bitsets for speed
Problems (9):
1. Count Set Bits 0..n [Easy]: DP on bits.
2. Single Number II [Medium]: bit counting mod 3.
3. Two Single Numbers [Medium]: split by lowbit.
4. Reverse Bits and Power of Two Checks [Easy].
5. Gray Code Sequence [Medium].
6. Enumerate Submasks [Medium]: sum over all submasks in O(3ⁿ).
7. Maximum AND Pair [Medium]: greedy bit by bit.
8. Sum of XOR over All Pairs [Medium]: per-bit counting.
9. Bitset Subset Sum [Hard]: `bitset` shift-or for speed.

### cpp-dsa-search-techniques | Meet in the Middle and State-Space Search | Advanced | status: new
Summary: Smarter exhaustive search.
Lesson must cover:
- meet in the middle, bidirectional BFS, iterative deepening (IDA*), branch and bound, state encoding/hashing
Problems (6):
1. Subset Sum Count Meet in the Middle [Medium]: n = 40.
2. Closest Subsequence Sum [Hard].
3. Bidirectional BFS Word Ladder [Medium].
4. 8-Puzzle Minimum Moves [Hard]: BFS with encoded states.
5. 15-Puzzle with IDA* [Expert]: Manhattan + linear conflict.
6. Branch and Bound Knapsack [Hard]: fractional bound.

## Module 18: Greedy

### cpp-greedy-math | Greedy Algorithms and Proofs | Advanced | status: rebuild
Summary: Locally optimal choices and how to prove them (old "Greedy, Math and Bits" narrowed; math and bits moved to Modules 17 and 20).
Lesson must cover:
- greedy-choice property, exchange argument, stays-ahead proof, counterexamples, sorting by ratio/deadline, Huffman coding
Existing: cpp-greedy-math-suite (keep last).
Problems (9):
1. Activity Selection [Easy]: earliest finish.
2. Minimum Platforms / Arrows to Burst Balloons [Easy].
3. Jump Game II [Medium]: BFS-like greedy.
4. Gas Station [Medium].
5. Candy Distribution [Hard]: two passes.
6. Huffman Code Length [Medium]: total encoded bits.
7. Minimize Lateness Scheduling [Medium]: earliest deadline first.
8. Fractional Knapsack [Easy]: ratio sort, exact fractions.
9. Queue Reconstruction by Height [Medium].

### cpp-dsa-greedy-advanced | Advanced Greedy: Heaps, Regret and Exchange | Expert | status: new
Summary: Greedy with data structures and undo.
Lesson must cover:
- greedy + heap (deadline scheduling), regret greedy (take then undo), greedy on strings, matroid intuition
Problems (7):
1. Job Sequencing with Deadlines [Medium]: heap or DSU slots.
2. Course Schedule III [Hard]: regret with max-heap.
3. Minimum Refueling Stops [Hard].
4. Smallest Subsequence of Distinct Characters [Medium].
5. Buy Low Sell High Unlimited (regret heap) [Hard].
6. Reorganize String [Medium]: heap of counts.
7. Minimum Cost to Hire K Workers [Hard]: sort by ratio + heap.

## Module 19: Dynamic Programming

### cpp-dp | DP Foundations: 1D DP | Advanced | status: rebuild
Summary: From recursion to memoization to tabulation (old broad topic narrowed to foundations).
Lesson must cover:
- overlapping subproblems, optimal substructure, state/transition/base/order/answer recipe, memo vs table, space optimization, reconstructing choices, counting vs optimization DP
Existing: cpp-dp-engine (keep last).
Problems (9):
1. Climbing Stairs with Steps Set [Easy].
2. House Robber I and II [Easy].
3. Min Cost Climbing [Easy].
4. Decode Ways [Medium].
5. Word Break with Reconstruction [Medium].
6. Longest Increasing Subsequence O(n²) with Path [Medium].
7. Max Product Subarray via DP [Medium].
8. Best Time to Buy/Sell with Cooldown and Fee [Medium]: state machine DP.
9. Perfect Squares / Min Coins with Path [Medium].

### cpp-dsa-dp-grid | Grid and 2D DP | Advanced | status: new
Summary: DP over 2D state spaces.
Lesson must cover:
- grid paths, obstacles, rolling arrays, max square, multi-agent DP (cherry pickup), DP with direction states
Problems (8):
1. Unique Paths with Obstacles [Easy].
2. Minimum Path Sum with Path [Easy].
3. Maximal Square [Medium].
4. Triangle Minimum Path [Easy].
5. Dungeon Game [Hard]: backward DP.
6. Count Square Submatrices [Medium].
7. Cherry Pickup II (two robots) [Hard].
8. Longest Increasing Path in Matrix [Hard]: memo DFS.

### cpp-dsa-dp-knapsack | Knapsack Family | Advanced | status: new
Summary: Choosing items under capacity.
Lesson must cover:
- 0/1 vs unbounded loop order, bounded via binary splitting, subset sum and partition, counting combinations vs permutations, multi-dimensional knapsack, item reconstruction
Problems (9):
1. 0/1 Knapsack with Items [Easy].
2. Unbounded Knapsack [Easy].
3. Coin Change Minimum [Easy].
4. Coin Change Ways (combinations vs permutations) [Medium].
5. Partition Equal Subset Sum [Medium].
6. Target Sum (signs) [Medium].
7. Bounded Knapsack Binary Splitting [Hard].
8. Ones and Zeroes (2D capacity) [Medium].
9. Profitable Schemes [Hard]: capped dimension.

### cpp-dsa-dp-strings | String DP and LIS | Advanced | status: new
Summary: DP over one or two sequences.
Lesson must cover:
- LCS with reconstruction, edit distance with operations, LIS in O(n log n) with path, palindromic subsequence/substring DP, wildcard and regex matching, distinct subsequences
Problems (10):
1. LCS with Reconstruction [Medium].
2. Edit Distance with Operations [Medium].
3. LIS n log n with Path [Medium].
4. Russian Doll Envelopes [Hard].
5. Longest Palindromic Subsequence [Medium].
6. Min Insertions to Palindrome [Medium].
7. Distinct Subsequences Count [Hard].
8. Wildcard Matching [Hard].
9. Regular Expression Matching [Hard].
10. Shortest Common Supersequence [Hard].

### cpp-dsa-dp-interval | Interval DP | Expert | status: new
Summary: DP on subarrays [i, j].
Lesson must cover:
- length-ordered iteration, split point enumeration, matrix chain with parenthesization, burst balloons "last" trick, palindrome partitioning, optimal BST
Problems (7):
1. Matrix Chain Multiplication with Parentheses [Medium].
2. Burst Balloons [Hard].
3. Palindrome Partitioning Min Cuts [Medium].
4. Minimum Cost to Cut a Stick [Medium].
5. Optimal BST [Hard].
6. Remove Boxes [Expert]: extra dimension.
7. Stone Merging (adjacent piles) [Hard].

### cpp-dsa-dp-trees-graphs | DP on Trees and DAGs | Expert | status: new
Summary: DP following tree and DAG structure.
Lesson must cover:
- post-order tree DP, include/exclude states, tree knapsack (O(n²) merging), DAG DP via topo order, path counting, rerooting pointer to Module 15
Problems (8):
1. Max Independent Set in Tree [Medium].
2. House Robber III [Medium].
3. Minimum Vertex Cover in Tree [Medium].
4. Binary Tree Cameras [Hard].
5. Tree Knapsack: Choose K Nodes Connected to Root [Hard].
6. Longest Path in DAG with Count [Medium].
7. Count Paths in Grid DAG with Blocked Cells mod p [Medium].
8. Tree Coloring Count with Constraints [Hard].

### cpp-dsa-dp-bitmask | Bitmask DP | Expert | status: new
Summary: DP over subsets.
Lesson must cover:
- subset states, TSP Held–Karp, assignment DP, profile DP (broken profile tiling), SOS DP, iterating submasks complexity
Problems (8):
1. Travelling Salesman (Held–Karp) [Hard].
2. Assignment Problem by Bitmask [Medium].
3. Minimum Number of Work Sessions [Medium].
4. Domino Tiling Broken Profile [Hard].
5. SOS DP: Count Submasks in Array [Hard].
6. Shortest Path Visiting All Nodes [Hard]: BFS over (node, mask).
7. Partition into Teams with Compatibility [Hard].
8. Maximum Students Seating [Hard]: row masks.

### cpp-dsa-dp-digit | Digit DP and Counting | Expert | status: new
Summary: Counting numbers in ranges with digit constraints.
Lesson must cover:
- tight/leading-zero flags, memo dimensions, f(R) − f(L−1), states for sums, remainders, previous digit
Problems (6):
1. Count Numbers with Digit Sum S [Medium].
2. Numbers Without Consecutive Equal Digits [Medium].
3. Count of Numbers with Unique Digits up to N [Medium].
4. Numbers Divisible by K with Digit Sum Divisible by K [Hard].
5. Count of 1s in All Numbers ≤ N [Medium].
6. K-th Number with Property [Hard]: digit DP + walking.

### cpp-dsa-dp-games-prob | Game Theory and Probability DP | Expert | status: new
Summary: Optimal play and expected values.
Lesson must cover:
- minimax as DP, win/lose states, Nim and Sprague–Grundy, probability DP vs expected value DP, linearity of expectation, Markov chains
Problems (8):
1. Stone Game (take from ends) [Medium].
2. Can I Win (bitmask game) [Hard].
3. Nim and Misère Nim [Easy].
4. Grundy Numbers for Subtraction Game [Medium].
5. Sum of Games on Graph [Hard].
6. Knight Probability on Board [Medium].
7. Expected Dice Rolls to Reach N [Medium].
8. New 21 Game [Hard]: sliding window probability.

### cpp-dsa-dp-optimizations | DP Optimizations | Research | status: new
Summary: Making slow DPs fast.
Lesson must cover:
- prefix-sum transitions, monotonic deque optimization, convex hull trick and Li Chao tree, divide-and-conquer optimization, Knuth optimization, alien trick (Lagrangian), conditions for each
Problems (7):
1. Prefix-Sum Transition: Count Ways with Ranged Steps [Medium].
2. Deque Optimization: Constrained Subsequence Sum [Hard].
3. Convex Hull Trick: Frog Jumps with Square Cost [Hard].
4. Li Chao Tree: Arbitrary Line Queries [Hard].
5. Divide-and-Conquer Opt: Partition into K Groups [Expert].
6. Knuth Optimization: Optimal Merging [Expert].
7. Aliens Trick: Exactly K Segments [Research].

## Module 20: String Algorithms and Math

### cpp-dsa-string-matching | Pattern Matching | Advanced | status: new
Summary: Linear-time string matching.
Lesson must cover:
- naive O(nm), prefix function (KMP), Z-function, rolling hash with double mod and anti-collision, Manacher, applications (period, borders)
Problems (9):
1. Find All Occurrences (KMP) [Easy].
2. Shortest Period of a String [Medium]: prefix function.
3. Z-Function Matching with Wildcard-Free Concatenation [Medium].
4. Shortest Palindrome by Prefix Addition [Hard].
5. Longest Palindromic Substring (Manacher) [Medium].
6. Count Palindromic Substrings [Medium].
7. Rabin–Karp Multiple Pattern Lengths [Medium].
8. Longest Duplicate Substring [Hard]: binary search + hashing.
9. Distinct Substrings Count via Hashing [Hard].

### cpp-dsa-string-advanced | Advanced Strings | Research | status: new
Summary: Multi-pattern and suffix structures.
Lesson must cover:
- Aho–Corasick automaton and output links, suffix array O(n log n), Kasai LCP, suffix automaton construction and uses, comparison of structures
Problems (7):
1. Aho–Corasick Count Matches [Hard].
2. Stream of Characters Queries [Hard].
3. Suffix Array Construction [Hard].
4. Longest Common Substring of Two Strings (SA + LCP) [Hard].
5. Number of Distinct Substrings (SA + LCP) [Hard].
6. Suffix Automaton: Occurrences of Each Query [Expert].
7. K-th Lexicographic Substring [Expert].

### cpp-dsa-number-theory | Number Theory | Advanced | status: new
Summary: Integers, primes and modular arithmetic.
Lesson must cover:
- Euclid and extended Euclid, sieve and linear sieve, smallest prime factor factorization, modular exponentiation, inverses (Fermat/extended), CRT, Euler phi, Miller–Rabin and Pollard rho overview
Problems (9):
1. GCD/LCM of Array with Overflow Care [Easy].
2. Sieve Prime Counting up to 10⁷ [Easy].
3. Factorization Queries with SPF [Medium].
4. Modular Exponentiation and Inverse [Easy].
5. Linear Diophantine Equation [Medium]: extended Euclid.
6. Chinese Remainder Theorem (non-coprime) [Hard].
7. Euler Totient Sum [Medium].
8. Miller–Rabin for 64-bit [Hard].
9. Count Divisors of n! [Medium]: Legendre's formula.

### cpp-dsa-combinatorics | Combinatorics and Matrix Methods | Advanced | status: new
Summary: Counting with factorials, inclusion–exclusion and matrices.
Lesson must cover:
- nCr mod p with factorial tables, Lucas theorem, stars and bars, Catalan numbers, inclusion–exclusion, derangements, matrix exponentiation for linear recurrences, Burnside basics
Problems (8):
1. nCr Queries mod 1e9+7 [Easy].
2. Lucas Theorem nCr mod small p [Medium].
3. Stars and Bars with Bounds [Medium]: inclusion–exclusion.
4. Catalan: Count Valid Bracket Sequences with Prefix [Medium].
5. Derangements [Easy].
6. Fibonacci 10¹⁸ by Matrix Power [Medium].
7. Count Walks of Length K in Graph [Hard].
8. Necklace Counting (Burnside) [Hard].

### cpp-dsa-math-advanced | Algebra Algorithms: FFT, Gaussian Elimination, XOR Basis | Research | status: new
Summary: Polynomial and linear-algebra tools for contests and engineering.
Lesson must cover:
- FFT/NTT for polynomial multiplication, Gaussian elimination (real and mod p), rank and XOR basis, Möbius inversion intro
Problems (6):
1. Polynomial Multiplication via NTT [Hard].
2. Big Integer Multiply via FFT [Hard].
3. Gaussian Elimination over Reals [Medium]: unique/none/infinite.
4. Linear System mod p [Hard].
5. Maximum XOR Subset (linear basis) [Hard].
6. Count Coprime Pairs (Möbius) [Expert].

### cpp-dsa-geometry | Computational Geometry | Advanced | status: new
Summary: Exact 2D geometry with integers and careful floats.
Lesson must cover:
- vectors, dot/cross, orientation, segment intersection, polygon area (shoelace), point in polygon, convex hull (monotone chain), rotating calipers, Pick's theorem, precision strategy
Problems (8):
1. Orientation of Triplets [Easy].
2. Segment Intersection Test [Medium]: collinear cases.
3. Polygon Area and Lattice Points (Pick) [Medium].
4. Point in Polygon (ray casting, boundary) [Medium].
5. Convex Hull Monotone Chain [Medium].
6. Diameter of Point Set (rotating calipers) [Hard].
7. Closest Pair via Sweep [Hard].
8. Minimum Enclosing Circle (Welzl) [Hard].

## Module 21: Interview Mastery

### cpp-dsa-design-ds | Designing Data Structures | Advanced | status: new
Summary: Combining structures to meet operation complexities.
Lesson must cover:
- requirements → structure mapping, hash + list combos, timestamps, amortization, randomization
Problems (8):
1. LRU Cache [Medium].
2. LFU Cache [Hard].
3. Insert/Delete/GetRandom O(1) with Duplicates [Medium].
4. Time-Based Key-Value Store [Medium].
5. Hit Counter / Sliding Rate Limiter [Medium].
6. All O(1) Data Structure [Hard].
7. Design Twitter Feed [Medium]: k-way merge of timelines.
8. Snapshot Array [Medium].

### cpp-dsa-interview-patterns | Pattern Recognition and Mock Rounds | Expert | status: new
Summary: Identify the pattern from the statement, then solve under time pressure.
Lesson must cover:
- constraints → complexity table, keyword → pattern map, decision flowchart, communication script, testing strategy, worked mock interviews
Problems (10, mixed, each from a different module):
1. Product of Array Except Self [Medium]: prefix/suffix.
2. Minimum Window Substring [Hard]: sliding window.
3. Koko Eating Bananas [Medium]: binary search on answer.
4. Course Schedule II [Medium]: topo sort.
5. Swim in Rising Water [Hard]: Dijkstra or binary search + BFS.
6. Serialize N-ary Tree [Hard]: tree codec.
7. Longest Valid Parentheses [Hard]: stack or DP.
8. Number of Islands II [Hard]: online DSU.
9. Count of Smaller Numbers After Self [Hard]: BIT/merge sort.
10. Edit Distance Variant: One Edit Away Stream [Medium]: string two pointers.

---

# Beyond DSA

## Module 22: Robotics

All robotics problems use Eigen where natural; outputs are numbers compared with `compare: float`. Sensor data comes from generators with fixed seeds.

### cpp-rob-transforms | 2D/3D Transforms | Advanced | status: new
Summary: Representing position and orientation.
Lesson must cover:
- rotation matrices (SO(2)/SO(3)), Euler angles and gimbal lock, axis-angle, quaternions (composition, slerp, normalization), homogeneous transforms SE(3), frame conventions, transform trees
Problems (6):
1. 2D Pose Composition [Easy]: compose and invert (x, y, θ) poses.
2. Euler ↔ Rotation Matrix [Medium]: ZYX convention both ways, gimbal-lock case.
3. Quaternion Toolkit [Medium]: multiply, rotate vector, to/from matrix, normalize.
4. Slerp Interpolation [Medium]: shortest-path slerp with sign flip.
5. TF Tree Lookup [Hard]: frames as a tree; answer transform between any two frames at query time.
6. Hand-Eye Style Averaging [Hard]: average rotations via quaternion eigenvector method.

### cpp-rob-kinematics-mobile | Mobile Robot Kinematics | Advanced | status: new
Summary: How wheeled robots move.
Lesson must cover:
- differential drive forward/inverse kinematics, unicycle model, Ackermann/bicycle model, odometry integration (Euler vs exact arc), error accumulation
Problems (5):
1. Diff-Drive Wheel Speeds [Easy]: (v, ω) ↔ wheel speeds.
2. Odometry from Encoders [Medium]: integrate ticks with exact arc update.
3. Bicycle Model Simulation [Medium]: steering angle limits, path output.
4. Mecanum Drive Inverse Kinematics [Medium].
5. Odometry Calibration [Hard]: least-squares fit of wheel radius/baseline from logged runs.

### cpp-rob-kinematics-arm | Manipulator Kinematics | Expert | status: new
Summary: Forward/inverse kinematics of serial arms.
Lesson must cover:
- DH parameters, forward kinematics chain, geometric and analytic Jacobians, singularities, numerical IK (Jacobian transpose, pseudo-inverse, damped least squares), joint limits
Problems (6):
1. Planar 2-Link FK and Analytic IK [Easy]: both elbow solutions.
2. DH Forward Kinematics [Medium]: n-joint chain end-effector pose.
3. Geometric Jacobian [Medium]: verify against finite differences.
4. Damped Least Squares IK [Hard]: converge within tolerance, respect joint limits.
5. Manipulability and Singularity Detection [Medium].
6. Workspace Sampling [Medium]: reachability grid for a 3-link arm.

### cpp-rob-control | Control | Advanced | status: new
Summary: Making systems follow references.
Lesson must cover:
- open vs closed loop, PID with discrete implementation, anti-windup, derivative filtering, feedforward, state-space and LQR (Riccati iteration), pure pursuit, Stanley controller, stability intuition
Problems (6):
1. Discrete PID on First-Order Plant [Easy]: simulate and print response.
2. Anti-Windup and Derivative Filter [Medium]: saturation behaviour.
3. Cascade Control Position/Velocity [Medium].
4. LQR via Discrete Riccati Iteration [Hard]: gain matrix for cart-pole linearization.
5. Pure Pursuit Path Tracking [Medium]: lookahead point selection.
6. Stanley Controller [Hard]: cross-track error and heading correction on a curved path.

### cpp-rob-estimation | State Estimation | Expert | status: new
Summary: Combining models and noisy sensors.
Lesson must cover:
- Bayes filter, Kalman filter derivation intuition, EKF linearization, UKF sigma points, particle filter with resampling, complementary filter, sensor fusion and tuning
Problems (6):
1. 1D Kalman Filter [Easy].
2. Constant-Velocity KF Tracking [Medium]: 2D position measurements.
3. Complementary Filter IMU Tilt [Medium].
4. EKF Range-Bearing Localization [Hard].
5. UKF Nonlinear Tracking [Hard].
6. Particle Filter with Low-Variance Resampling [Hard]: seeded, deterministic output.

### cpp-rob-planning-graph | Path Planning on Grids and Graphs | Advanced | status: new
Summary: Planning on discretized maps.
Lesson must cover:
- occupancy grids, costmaps and inflation, Dijkstra vs A* vs weighted A*, heuristics and consistency, D* Lite idea for replanning, path smoothing, Jump Point Search
Problems (6):
1. Costmap Inflation [Easy]: distance transform with radius.
2. A* 8-Connected with Diagonal Costs [Medium].
3. Weighted A* Trade-off [Medium]: report path cost and expansions.
4. Jump Point Search [Hard].
5. Incremental Replanning [Hard]: obstacles appear; replan efficiently (LPA*/D* Lite).
6. Path Shortcutting with Line-of-Sight [Medium]: Bresenham collision checks.

### cpp-rob-planning-sampling | Sampling-Based Planning | Expert | status: new
Summary: Planning in continuous spaces.
Lesson must cover:
- configuration space, collision checking (circles, polygons), RRT, RRT-Connect, RRT* rewiring, PRM, seeded determinism, nearest-neighbour structures
Problems (5):
1. Collision Checker for Circle Robot [Easy]: segment vs polygon obstacles.
2. RRT in 2D [Medium]: seeded, fixed step; check path validity and length bound.
3. RRT-Connect [Hard].
4. RRT* with Rewiring [Hard]: cost improves with iterations.
5. PRM with k-NN Graph [Hard]: multiple queries on one roadmap.

### cpp-rob-trajectories | Trajectory Generation | Advanced | status: new
Summary: Turning paths into time-parameterized motion.
Lesson must cover:
- polynomial trajectories (cubic, quintic), minimum-jerk, trapezoidal and S-curve velocity profiles, cubic splines through waypoints, time scaling under velocity/acceleration limits
Problems (5):
1. Cubic Point-to-Point [Easy].
2. Trapezoidal Velocity Profile [Medium]: triangular fallback.
3. Quintic Minimum-Jerk [Medium].
4. Natural Cubic Spline through Waypoints [Hard]: tridiagonal solve.
5. Time-Optimal Scaling with Limits [Hard]: forward/backward pass on a path.

### cpp-rob-perception | Point-Cloud Perception | Expert | status: new
Summary: Processing 3D point clouds.
Lesson must cover:
- voxel-grid downsampling, k-d tree neighbours, normal estimation via PCA, RANSAC plane fitting, Euclidean clustering, ICP (point-to-point), outlier removal
Problems (6):
1. Voxel Grid Downsample [Easy]: centroid per voxel.
2. Statistical Outlier Removal [Medium].
3. Normal Estimation via PCA [Medium].
4. RANSAC Plane Fit [Medium]: seeded, inlier count.
5. Euclidean Clustering [Hard]: k-d tree + BFS.
6. Point-to-Point ICP [Hard]: SVD alignment until convergence.

### cpp-rob-vision | Camera Geometry | Expert | status: new
Summary: Pinhole cameras and multi-view geometry.
Lesson must cover:
- intrinsics/extrinsics, projection, lens distortion, calibration idea, homography via DLT, epipolar geometry, triangulation, feature matching with ratio test, PnP overview
Problems (5):
1. Project Points with Distortion [Easy].
2. Homography by DLT [Medium]: normalized DLT with Eigen SVD.
3. Triangulate from Two Views [Medium].
4. Fundamental Matrix 8-Point [Hard].
5. Descriptor Matching with Ratio Test and Cross-Check [Medium].

### cpp-rob-slam | SLAM Foundations | Research | status: new
Summary: Building maps while localizing.
Lesson must cover:
- occupancy grid mapping (log-odds), scan matching, pose graphs, Gauss–Newton and Levenberg–Marquardt, sparse normal equations, loop closures
Problems (5):
1. Log-Odds Occupancy Mapping [Medium]: ray casting with Bresenham.
2. Correlative Scan Matching [Hard]: brute-force search over a small window.
3. 1D Pose Graph Least Squares [Medium].
4. 2D Pose Graph with Gauss–Newton [Hard]: loop closure reduces error.
5. Levenberg–Marquardt Curve/Pose Fit [Hard].

### cpp-rob-realtime | Real-Time C++ for Robots | Expert | status: new
Summary: Deterministic timing in control loops.
Lesson must cover:
- WCET thinking, no allocation/locks/exceptions in the loop, preallocated pools, lock-free SPSC handoff, fixed-rate scheduling and jitter measurement, priority inversion, triple buffering
Problems (5):
1. Fixed-Rate Loop Scheduler Simulation [Easy]: drift-free next-deadline computation.
2. Allocation-Free Control Loop [Medium]: driver counts `operator new` calls; must be zero in loop.
3. Triple Buffer [Medium]: latest-value handoff between threads.
4. Rate-Monotonic Schedulability [Medium]: utilization bound and response-time analysis.
5. Priority Inversion Simulator [Hard]: simulate with/without priority inheritance.

## Module 23: OOP Mastery and Design Patterns

### cpp-oop-thinking | Thinking in Objects in C++ | Intermediate | status: existing-thin
Summary: From requirements to classes.
Lesson must cover:
- nouns/verbs, responsibilities, CRC cards, cohesion/coupling, value vs entity objects
Existing: cpp-dimensional-units (keep last).
Problems to add (3):
1. Library Domain Model [Easy]: books, members, loans from command list.
2. Value Object Money [Medium]: currency-safe arithmetic with rounding.
3. Tell-Don't-Ask Refactor [Medium]: move logic into objects; behaviour preserved.

### cpp-oop-relationships | Relationships and Ownership in C++ | Intermediate | status: existing-thin
Summary: Association, aggregation, composition expressed with C++ ownership.
Lesson must cover:
- members vs `unique_ptr` vs raw observer pointers vs `shared_ptr`, lifetime diagrams
Existing: cpp-fleet-ownership (keep last).
Problems to add (3):
1. Car Has Engine [Easy]: composition with lifetime trace.
2. Department/Employees Aggregation [Medium]: non-owning references; removal semantics.
3. Graph of Friends [Medium]: association with `weak_ptr`, no leaks.

### cpp-oop-solid | SOLID in C++ | Advanced | status: existing-thin
Summary: The five SOLID principles in C++.
Lesson must cover:
- SRP, OCP, LSP (with the square/rectangle trap), ISP, DIP; how templates and virtuals realize each
Existing: cpp-pricing-engine (keep last).
Problems to add (3):
1. SRP Report Split [Easy]: separate parsing, computing and formatting.
2. LSP Violation Fix [Medium]: redesign a hierarchy so all substitutions pass the driver's contract tests.
3. DIP Notification Service [Medium]: inject senders; fake sender in driver.

### cpp-oop-multifile | Header/Source Organization | Advanced | status: existing-thin
Summary: Structuring C++ libraries across files.
Lesson must cover:
- interface headers, include hygiene, forward declarations, templates in headers, compile-time dependencies
Existing: cpp-geometry-library (keep last).
Problems to add (3):
1. Split a Class into Header and Source [Easy]: multi-TU driver links only when declarations/definitions are placed correctly (inline, static members, templates in headers).
2. Include Graph Analyzer [Medium]: from include lists, find cycles and minimal rebuild set after a change.
3. Forward Declaration Fixer [Medium]: decide which includes can become forward declarations given usage facts.

### cpp-oop-value-semantics | Value Types and Regular Types | Advanced | status: new
Summary: Designing types that behave like `int`.
Lesson must cover:
- regular types, equality and copy consistency, invariants, immutability, strong typedefs, `[[nodiscard]]`, comparison via `<=>`
Problems (4):
1. Strong Typedef IDs [Easy]: prevent mixing `UserId` and `OrderId`.
2. Immutable Date Range [Medium]: operations return new values.
3. Regular Polygon Type [Medium]: equality/hash consistent with copy; use in sets.
4. Copy-on-Write String [Hard]: value semantics with shared buffer.

### cpp-oop-polymorphism-forms | Forms of Polymorphism | Expert | status: new
Summary: Virtual vs CRTP vs type erasure vs `std::variant`.
Lesson must cover:
- open vs closed sets of types, performance, binary boundaries, Sean Parent type erasure, variant visitation, concept-based interfaces
Problems (5):
1. Same Shapes, Four Ways [Medium]: implement area via virtual, CRTP, variant and type erasure; same output.
2. Type-Erased Callable [Hard]: small `function`-like with SBO.
3. Type-Erased Drawable Document [Hard]: value-semantic polymorphism with undo.
4. Variant State Machine [Medium]: states as variant alternatives.
5. Choose the Right Form [Medium]: benchmark-driven; the hot loop must meet time limit with a closed set.

### cpp-oop-testing-design | Designing for Testability | Advanced | status: new
Summary: Seams, injection and test doubles in C++.
Lesson must cover:
- dependency injection (constructor, template, link-time), interfaces for I/O and time, fakes vs mocks, gmock overview, deterministic clocks
Problems (4):
1. Injectable Clock [Easy]: token bucket tested with a fake clock.
2. Fake Filesystem [Medium]: interface + in-memory fake; driver exercises edge cases.
3. Hand-Rolled Mock Expectations [Medium]: record calls and verify sequences.
4. Template-Injected Repository [Hard]: policy-based storage swapped at compile time.

### cpp-patterns-creational | Creational Patterns | Advanced | status: existing-thin
Summary: Factory Method, Abstract Factory, Builder, Prototype, Singleton.
Lesson must cover:
- each pattern: intent, UML-ish picture, C++ implementation, modern alternatives, when not to use
Existing: cpp-sensor-factory-builder (keep last).
Problems to add (5, one per pattern):
1. Factory Method Document Exporters [Easy]: create exporter by format string with a registry.
2. Abstract Factory UI Themes [Medium]: families of widgets rendered as text.
3. Builder for HTTP Requests [Medium]: fluent builder with validation at `build()`.
4. Prototype Shape Cloning [Medium]: deep `clone()` into a registry of templates.
5. Thread-Safe Singleton Config [Medium]: Meyers singleton with reset hook for tests.

### cpp-patterns-structural | Structural Patterns I: Adapter, Bridge, Composite, Decorator | Advanced | status: existing-thin
Summary: Composing objects into larger structures.
Lesson must cover:
- Adapter (object/class), Bridge, Composite, Decorator; templates vs virtual implementations
Existing: cpp-sensor-decorator-pipeline (keep last).
Problems to add (4):
1. Adapter for Legacy Sensor API [Easy].
2. Bridge Shapes × Renderers [Medium]: avoid class explosion.
3. Composite File System Sizes [Medium].
4. Decorator Stream Pipeline [Medium]: compress/encrypt/checksum layers on byte streams.

### cpp-patterns-structural-2 | Structural Patterns II: Facade, Flyweight, Proxy | Advanced | status: new
Summary: Simplifying, sharing and controlling access.
Lesson must cover:
- Facade, Flyweight (intrinsic vs extrinsic state), Proxy (virtual, protection, caching, remote)
Problems (4):
1. Home Theater Facade [Easy]: one call orchestrates subsystems.
2. Flyweight Glyphs [Medium]: shared glyph objects for a large document; memory count checked.
3. Caching Proxy [Medium]: memoize expensive service calls with invalidation.
4. Protection Proxy with Roles [Medium]: access control around a repository.

### cpp-patterns-behavioral | Behavioral Patterns I: Observer, Strategy, Command, State, Template Method | Advanced | status: existing-thin
Summary: Communication and responsibility between objects.
Lesson must cover:
- each pattern with classic and modern (lambda/variant) forms
Existing: cpp-signals-undo (keep last).
Problems to add (5):
1. Strategy Route Planner [Easy]: fastest/shortest/scenic strategies.
2. Observer Stock Ticker [Medium]: subscribe/unsubscribe during notification.
3. Command Undo/Redo Editor [Medium]: macro commands.
4. State Vending Machine [Medium]: state objects with transitions.
5. Template Method Data Import [Medium]: fixed algorithm skeleton with hooks.

### cpp-patterns-behavioral-2 | Behavioral Patterns II: Chain, Iterator, Mediator, Memento, Visitor, Interpreter | Advanced | status: new
Summary: The remaining six GoF behavioral patterns.
Lesson must cover:
- Chain of Responsibility, Iterator, Mediator, Memento, Visitor (incl. double dispatch and variant alternative), Interpreter
Problems (6):
1. Chain of Responsibility Support Tickets [Easy].
2. Custom Iterator over Composite Tree [Medium].
3. Mediator Chat Room [Medium].
4. Memento Game Save Slots [Medium].
5. Visitor AST Pretty-Printer and Evaluator [Hard].
6. Interpreter Boolean Rules Engine [Hard]: parse and evaluate rules.

### cpp-patterns-modern | Modern C++ Idioms as Patterns | Expert | status: new
Summary: Patterns specific to C++.
Lesson must cover:
- policy-based design, type erasure, CRTP mixins, RAII, PIMPL, null object, object pool, dependency injection with templates, curiously recurring registration
Problems (5):
1. Policy-Based Logger [Medium]: formatting and sink policies.
2. Object Pool with RAII Handles [Medium].
3. Null Object Logger [Easy].
4. Self-Registering Plugins [Hard]: static registration before main.
5. Policy-Based Smart Pointer [Hard]: checking and ownership policies.

## Module 24: Low-Level Design Case Studies

Each case study is built in stages; each problem adds a different design concern (domain model → rules → concurrency/scale → extension).

### cpp-oop-case-parking | Case Study: Parking Lot in C++ | Advanced | status: existing-thin
Existing: cpp-parking-lot (keep last).
Lesson must cover: requirements gathering, class diagram, pricing strategies, extensibility review.
Problems to add (3):
1. Spot Allocation by Vehicle Size [Easy].
2. Pricing Strategies and Receipts [Medium].
3. Multi-Level Lot with Nearest-Spot Queries [Hard]: heaps per level.

### cpp-oop-case-robot | Case Study: Robot Software Architecture | Expert | status: existing-thin
Existing: cpp-behavior-tree (keep last).
Lesson must cover: layered architecture (HAL, drivers, control, mission), component interfaces, message passing.
Problems to add (3):
1. Driver Interface and Fake Hardware [Medium].
2. Pub/Sub Message Bus with Typed Topics [Hard].
3. Mission Planner State Machine [Hard].

### cpp-oop-case-engine | Case Study: Event-Driven Simulation Engine | Expert | status: existing-thin
Existing: cpp-des-kernel (keep last).
Problems to add (3):
1. Event Queue with Stable Ordering [Medium].
2. Bank Queue Simulation [Medium]: entities and resources.
3. Pluggable Statistics Collectors [Hard].

### cpp-lld-elevator | Case Study: Elevator System | Advanced | status: new
Summary: Designing a multi-elevator controller.
Lesson must cover: requirements, states, scheduling algorithms (FCFS, SCAN/LOOK), dispatcher strategy, simulation clock.
Problems (4):
1. Single Elevator State Machine [Easy].
2. LOOK Scheduling [Medium].
3. Multi-Elevator Dispatcher [Hard]: cost-based assignment.
4. Maintenance Mode and Capacity Limits [Medium]: extension without modification.

### cpp-lld-chess | Case Study: Chess and Board Games | Advanced | status: new
Summary: Modeling pieces, moves and rules.
Lesson must cover: board representation, piece polymorphism vs tables, move generation, game state, undo.
Problems (5):
1. Board and Piece Model with FEN Parse [Easy].
2. Pseudo-Legal Move Generation [Medium].
3. Check and Legal Moves [Hard].
4. Castling, En Passant, Promotion [Hard].
5. Perft Move Counting [Hard]: validate generator at depth 3–4.

### cpp-lld-splitwise | Case Study: Expense Sharing | Advanced | status: new
Summary: Splitwise-style balances and settlements.
Lesson must cover: entities (users, groups, expenses), split strategies (equal, exact, percent), rounding, debt simplification.
Problems (4):
1. Equal/Exact/Percent Splits [Easy].
2. Balances per User and Group [Medium].
3. Minimize Transactions [Hard]: greedy settlement + exact backtracking for small n.
4. Audit Log and Undo of Expenses [Medium].

### cpp-lld-vending-atm | Case Study: Vending Machine and ATM | Advanced | status: new
Summary: State-driven machines with money.
Lesson must cover: state pattern, inventory, change-making, transactions, failure handling.
Problems (4):
1. Vending Machine States [Easy].
2. Change Making with Limited Coins [Medium].
3. ATM Withdrawal with Note Dispensing Chain [Medium].
4. ATM Sessions with PIN Lockout and Daily Limits [Hard].

### cpp-lld-booking | Case Study: Booking Systems (Movies, Hotels) | Expert | status: new
Summary: BookMyShow and hotel reservations.
Lesson must cover: inventory of seats/rooms, holds with expiry, concurrency on the same seat, pricing, cancellation.
Problems (5):
1. Seat Map and Booking [Easy].
2. Temporary Holds with Expiry [Medium].
3. Concurrent Booking without Double Sell [Hard]: threads contend; exactly one wins.
4. Hotel Room Availability by Date Ranges [Medium]: interval queries.
5. Dynamic Pricing and Cancellation Refunds [Medium].

### cpp-lld-infra-components | Case Study: Rate Limiter and Logging Framework | Expert | status: new
Summary: Reusable infrastructure components.
Lesson must cover: token bucket, sliding window log/counter, per-key limiters, logger hierarchy, appenders, formatters, async logging.
Problems (5):
1. Token Bucket Limiter [Easy].
2. Sliding Window Counter per User [Medium].
3. Logger Hierarchy with Levels [Medium].
4. Async Logger with Bounded Queue [Hard].
5. Distributed-Style Limiter Simulation [Hard]: shared counters across nodes with sync intervals.

### cpp-lld-games | Case Study: Snake & Ladders, Tic-Tac-Toe, Snake | Intermediate | status: new
Summary: Small games as design practice.
Lesson must cover: game loop, players, rules engine, extensibility (n×n boards, more players), deterministic dice.
Problems (4):
1. Snake & Ladders Simulator [Easy]: seeded dice.
2. N×N Tic-Tac-Toe O(1) Win Check [Medium].
3. Snake Game Engine [Medium]: deque body, food spawn.
4. Pluggable Rules Variant [Medium]: add rules without editing core classes.

## Module 25: Tooling and Libraries

### cpp-cmake | CMake in Depth | Intermediate | status: existing-thin
Summary: Modern target-based CMake.
Lesson must cover:
- targets, PUBLIC/PRIVATE/INTERFACE, find_package, FetchContent, presets, generator expressions, install/export, vcpkg/Conan overview
Existing: cpp-target-resolver (keep last).
Problems to add (3):
1. Usage Requirement Propagation [Medium]: compute final include dirs/defines per target.
2. Build Order and Cycles [Medium]: topological build plan from target graph.
3. Generator Expression Evaluator [Hard]: evaluate `$<CONFIG:Debug>`-style expressions.

### cpp-gtest | Unit Testing with GoogleTest | Intermediate | status: existing-thin
Summary: Writing effective tests in C++.
Lesson must cover:
- TEST/TEST_F, fixtures, parameterized tests, death tests, gmock matchers, test design (boundaries, properties)
Existing: cpp-gtest-mutants (keep last).
Problems to add (3):
1. Parameterized Boundary Tests [Medium]: tests must kill given mutants.
2. Fixture-Based Bank Tests [Medium].
3. Property-Based Testing by Hand [Hard]: random generator + shrinking for a sort function.

### cpp-sanitizers-debugging | Sanitizers, Debugging and Static Analysis | Advanced | status: new
Summary: Finding bugs with tools.
Lesson must cover:
- ASan/UBSan/TSan/MSan, reading reports, gdb/lldb basics, valgrind, clang-tidy, warnings as errors, fuzzing with libFuzzer
Problems (4):
1. Fix the Heap Overflow [Easy]: code fails under ASan; fix.
2. Fix the UB [Medium]: shifts, overflow, misaligned access caught by UBSan.
3. Fix the Data Race [Medium]: TSan-reported race.
4. Mini Fuzzer [Hard]: write a mutation fuzzer that finds the crashing input of a given parser.

### cpp-libs-json-fmt-log | JSON, fmt and spdlog | Intermediate | status: new
Summary: Everyday libraries.
Lesson must cover:
- nlohmann/json parse/serialize/custom types, fmt formatting, spdlog loggers and sinks
Problems (4):
1. JSON Config Merge [Easy]: deep merge with overrides.
2. Custom Type to/from JSON [Medium]: `to_json`/`from_json` for nested structs.
3. JSON Patch Apply [Hard]: RFC 6902 subset.
4. fmt Table Formatter [Medium]: aligned report with dynamic widths.

### cpp-eigen | Linear Algebra with Eigen | Advanced | status: existing-thin
Summary: Dense linear algebra.
Lesson must cover:
- matrices/vectors, fixed vs dynamic, expression templates and aliasing, decompositions (LU, QR, LLT, SVD), geometry module
Existing: cpp-eigen-geometry (keep last).
Problems to add (3):
1. Solve Linear Systems Robustly [Easy]: choose decomposition, report residual.
2. Least Squares Line/Plane Fit [Medium].
3. PCA via SVD [Medium].

### cpp-opencv | OpenCV in C++ | Advanced | status: existing-thin
Summary: Image processing with OpenCV (headless).
Lesson must cover:
- `cv::Mat`, types, ROI, filtering, thresholding, morphology, contours, transforms
Existing: cpp-marker-tracker (keep last).
Problems to add (3):
1. Grayscale and Histogram [Easy]: image from stdin as numbers.
2. Blob Counting with Morphology [Medium].
3. Perspective Warp of a Document [Hard].

### cpp-ros2 | ROS 2 with rclcpp | Expert | status: existing-thin
Summary: ROS 2 concepts (judged with a simulated middleware).
Lesson must cover:
- nodes, topics, services, actions, QoS, executors, parameters, lifecycle nodes
Existing: cpp-rclcpp-safety-node (keep last).
Problems to add (3):
1. Simulated Pub/Sub Node Graph [Medium].
2. QoS Compatibility Checker [Medium].
3. Action Server State Machine [Hard]: goal/feedback/cancel.

### cpp-boost-overview | Boost and the Ecosystem | Advanced | status: existing-thin
Summary: High-value Boost libraries.
Lesson must cover:
- Boost.Graph, Geometry, Asio overview, Container, Program Options, Multiprecision
Existing: cpp-mission-config (keep last).
Problems to add (3):
1. Boost.Graph Dijkstra [Medium].
2. Boost.Geometry Polygon Ops [Medium]: area, intersection.
3. Multiprecision Factorials [Easy].

## Module 26: Performance Engineering

### cpp-perf-measure | Profiling and Benchmarking | Advanced | status: new
Summary: Measuring before optimizing.
Lesson must cover:
- timers, warmup, variance, microbenchmark pitfalls (DCE, `DoNotOptimize`), perf/gprof, flame graphs, complexity vs constants
Problems (4):
1. Benchmark Harness [Easy]: median-of-N timing with statistics output (deterministic parts checked).
2. Find the Hot Spot [Medium]: optimize the slow function identified from a provided profile.
3. Constant Factor Wins [Medium]: replace `map` by sorted vector + binary search to meet limit.
4. Amortization Audit [Hard]: fix accidental quadratic behaviour (string concat, erase-front).

### cpp-perf-data-oriented | Cache-Aware and Data-Oriented Design | Expert | status: new
Summary: Designing data for the hardware.
Lesson must cover:
- cache hierarchy numbers, prefetching, SoA, hot/cold splitting, false sharing, branchless code
Problems (4):
1. Branchless Filtering [Medium].
2. Hot/Cold Split Entities [Medium].
3. Cache-Oblivious Transpose [Hard].
4. Open Addressing vs Chaining [Hard]: build a flat hash map that beats `unordered_map`.

### cpp-perf-simd | SIMD and Vectorization | Expert | status: new
Summary: Doing more per instruction.
Lesson must cover:
- auto-vectorization requirements, alignment, intrinsics (SSE/AVX2 basics), reductions, gather/scatter limits, portability
Problems (4):
1. Vectorizable Loop Rewrite [Medium].
2. SIMD Sum and Max [Medium]: intrinsics with scalar tail.
3. SIMD Byte Search [Hard]: find character positions.
4. 8-bit Image Blend [Hard]: saturating arithmetic.

### cpp-perf-case-studies | Optimization Case Studies | Expert | status: new
Summary: End-to-end optimization stories.
Lesson must cover:
- methodology, algorithmic then memory then micro, allocation reduction, I/O, parallelism last
Problems (4):
1. Fast CSV Aggregation [Medium].
2. N-Body Step Optimization [Hard].
3. String Interning for Log Analytics [Hard].
4. Parallel Image Convolution [Hard].

## Module 27: Systems and Networking

### cpp-sys-posix | POSIX from C++ | Advanced | status: new
Summary: Files, processes and pipes wrapped in RAII.
Lesson must cover:
- file descriptors, `open/read/write`, errno → exceptions/expected, `fork/exec/pipe`, `mmap`, signals, RAII wrappers
Problems (4):
1. RAII File Descriptor [Easy]: copy file via `read/write` with partial-write handling.
2. Pipe to Child Process [Medium]: run a child that transforms input.
3. mmap Word Count [Medium].
4. Mini Shell Pipeline [Hard]: `a | b | c` with redirections.

### cpp-net-sockets | Sockets and TCP | Advanced | status: new
Summary: TCP/UDP sockets in C++.
Lesson must cover:
- addresses, TCP lifecycle, `socket/bind/listen/accept/connect`, partial reads and framing, nonblocking sockets, UDP, byte order (tested over loopback/socketpair in-process)
Problems (5):
1. Echo over socketpair [Easy].
2. Length-Prefixed Framing [Medium]: reassemble messages from arbitrary chunking.
3. Loopback TCP Echo Server [Medium]: server and client threads in one process.
4. Binary Protocol Codec [Medium]: endianness and versioned headers.
5. Chat Room Broadcast [Hard]: multiple clients via `poll`.

### cpp-net-event-loop | Event Loops and Reactors | Expert | status: new
Summary: Handling many connections.
Lesson must cover:
- blocking vs nonblocking, select/poll/epoll, reactor vs proactor, timers (timer wheel/heap), backpressure
Problems (4):
1. Timer Heap Scheduler [Medium].
2. Hierarchical Timer Wheel [Hard].
3. Reactor Simulation [Hard]: events from stdin dispatched to handlers with write buffers.
4. Backpressure Pipeline [Hard]: pause reads when write buffers exceed thresholds.

### cpp-net-http-server | HTTP Server from Scratch | Expert | status: new
Summary: Implementing HTTP/1.1 pieces.
Lesson must cover:
- request line/headers/body, parsing incrementally, keep-alive, chunked encoding, routing, status codes, static files, security limits
Problems (6):
1. HTTP Request Parser [Medium]: incremental, header limits.
2. Response Builder [Easy]: headers, content-length, date format.
3. Chunked Transfer Decoder [Medium].
4. Router with Path Params [Medium]: `/users/:id` with method matching.
5. URL Decoding and Query Parsing [Easy].
6. Keep-Alive Server over Loopback [Expert]: pipelined requests on one connection.

### cpp-net-asio | Boost.Asio Async I/O | Expert | status: new
Summary: Asynchronous programming with Asio.
Lesson must cover:
- io_context, handlers, timers, strands, coroutines with Asio, error handling (no external network: timers and loopback)
Problems (4):
1. Steady Timer Sequencing [Easy].
2. Strand-Serialized Counters [Medium].
3. Async Loopback Echo [Hard].
4. Coroutine Timeout Wrapper [Hard].

### cpp-net-protocols | Protocol Design and Serialization | Advanced | status: new
Summary: Designing wire formats.
Lesson must cover:
- text vs binary, varints, TLV, protobuf-style encoding, checksums/CRC, versioning, fuzz-safety
Problems (4):
1. Varint Encode/Decode [Easy].
2. TLV Parser with Nested Messages [Medium].
3. Protobuf Wire Format Subset [Hard].
4. Simple RPC Codec with Request IDs [Hard].

## Module 28: Engineering and Scientific Computing

### cpp-num-floating-point | Floating Point and Numerical Error | Advanced | status: new
Summary: Why numerical code goes wrong.
Lesson must cover:
- IEEE 754, rounding, cancellation, condition number, Kahan summation, stable formulas, NaN/Inf handling
Problems (4):
1. Kahan vs Naive Sum [Easy].
2. Stable Quadratic Roots [Medium].
3. Stable Variance (Welford) [Medium].
4. Condition Number Estimation [Hard].

### cpp-num-linear-systems | Linear Systems and Decompositions | Advanced | status: new
Summary: Solving Ax = b by hand and with Eigen.
Lesson must cover:
- Gaussian elimination with partial pivoting, LU, Cholesky, QR, tridiagonal (Thomas), iterative methods (Jacobi, Gauss–Seidel, CG), eigenvalues (power iteration)
Problems (6):
1. Gaussian Elimination with Pivoting [Medium].
2. Thomas Algorithm [Easy].
3. Cholesky Solver [Medium].
4. Conjugate Gradient [Hard].
5. Power Iteration and Inverse Iteration [Medium].
6. QR Least Squares via Householder [Hard].

### cpp-num-calculus | Roots, Interpolation and Integration | Advanced | status: new
Summary: Core numerical methods.
Lesson must cover:
- bisection, Newton, secant, Brent; Lagrange/Newton interpolation, splines; finite differences; trapezoid, Simpson, Gauss quadrature, adaptive integration
Problems (5):
1. Bisection and Newton Roots [Easy].
2. Brent's Method [Medium].
3. Cubic Spline Interpolation [Medium].
4. Adaptive Simpson Integration [Medium].
5. Gauss–Legendre Quadrature [Hard].

### cpp-num-odes | ODE Solvers and Simulation | Advanced | status: new
Summary: Simulating dynamic systems.
Lesson must cover:
- Euler, RK4, adaptive RK45 with error control, stiffness and implicit Euler, symplectic integrators, mass-spring-damper, pendulum
Problems (5):
1. Euler vs RK4 on Exponential Decay [Easy].
2. Mass-Spring-Damper Response [Medium].
3. Adaptive RK45 [Hard].
4. Implicit Euler for Stiff System [Hard]: Newton inner solve.
5. Velocity Verlet Orbit Energy Drift [Medium].

### cpp-num-sparse | Sparse Matrices | Expert | status: new
Summary: Large sparse linear algebra.
Lesson must cover:
- COO/CSR/CSC formats, SpMV, assembly, Eigen::SparseMatrix, sparse solvers, fill-in and reordering (RCM)
Problems (4):
1. COO to CSR and SpMV [Easy].
2. Sparse Transpose and Multiply [Medium].
3. 2D Poisson with Sparse CG [Hard].
4. Reverse Cuthill–McKee Bandwidth Reduction [Hard].

### cpp-num-fem | Finite Element Method from Scratch | Research | status: new
Summary: FEM for structural and heat problems.
Lesson must cover:
- weak form intuition, 1D bar elements, stiffness assembly, boundary conditions, 2D trusses, CST triangles for heat/plane stress, mesh input, post-processing
Problems (5):
1. 1D Bar Element Displacements [Medium].
2. 2D Truss Analysis [Hard]: member forces.
3. 1D Steady Heat Conduction FEM [Medium].
4. 2D Poisson on Triangle Mesh [Hard].
5. Plane Stress CST Element [Expert].

### cpp-num-optimization | Numerical Optimization | Expert | status: new
Summary: Minimizing functions.
Lesson must cover:
- gradient descent and line search, Newton, BFGS, Nelder–Mead, Gauss–Newton/LM for least squares, constraints via penalty
Problems (5):
1. Golden Section Search [Easy].
2. Gradient Descent with Armijo Line Search [Medium].
3. Nelder–Mead [Medium].
4. BFGS on Rosenbrock [Hard].
5. Levenberg–Marquardt Curve Fit [Hard].

### cpp-num-signal | Signal Processing | Advanced | status: new
Summary: Discrete signals and filters.
Lesson must cover:
- sampling and aliasing, DFT/FFT (radix-2), convolution, FIR/IIR filters, windowing, moving averages
Problems (5):
1. Moving Average and Exponential Smoothing [Easy].
2. Radix-2 FFT [Medium].
3. Dominant Frequency Detection [Medium].
4. FIR Filter Design by Windowing [Hard].
5. Biquad IIR Filter Cascade [Hard].

## Module 29: Geometry and CAD Kernels

### cpp-geo-vectors-transforms | Vectors, Planes and Transforms for CAD | Intermediate | status: new
Summary: Geometric primitives.
Lesson must cover:
- points vs vectors, dot/cross, lines/planes, projections, distances, affine transforms and composition, robust predicates (epsilon strategy)
Problems (4):
1. Point-Line-Plane Distances [Easy].
2. Line–Plane and Plane–Plane Intersection [Medium].
3. Transform Stack Composition [Medium].
4. Closest Points Between Two Segments in 3D [Hard].

### cpp-geo-polygons | Polygons and Boolean Operations | Advanced | status: new
Summary: 2D shapes for CAD and GIS.
Lesson must cover:
- orientation, simple polygon tests, triangulation by ear clipping, convex clipping (Sutherland–Hodgman), polygon offsetting ideas, booleans overview
Problems (5):
1. Polygon Orientation and Simplicity [Easy].
2. Ear-Clipping Triangulation [Medium].
3. Sutherland–Hodgman Clipping [Medium].
4. Convex Polygon Intersection Area [Hard].
5. Polygon with Holes Area and Containment [Medium].

### cpp-geo-curves | Bézier and B-Spline Curves | Advanced | status: new
Summary: Parametric curves.
Lesson must cover:
- Bézier basics, de Casteljau, subdivision, B-spline basis (Cox–de Boor), knot vectors, knot insertion, arc length
Problems (5):
1. de Casteljau Evaluation [Easy].
2. Bézier Subdivision and Bounding Box [Medium].
3. B-Spline Basis and Evaluation [Medium].
4. Knot Insertion (Boehm) [Hard].
5. Arc Length and Uniform Resampling [Hard].

### cpp-geo-nurbs-surfaces | NURBS and Surfaces | Expert | status: new
Summary: Rational curves and tensor-product surfaces.
Lesson must cover:
- homogeneous weights, exact circles, NURBS evaluation, derivatives, tensor-product surfaces, surface normals, tessellation
Problems (4):
1. NURBS Curve Evaluation [Medium].
2. Exact Circle by NURBS [Medium].
3. Bézier Surface Evaluation and Normals [Hard].
4. Adaptive Curve Tessellation by Tolerance [Hard].

### cpp-geo-meshes | Meshes and Mesh File Formats | Advanced | status: new
Summary: Triangle meshes and their I/O.
Lesson must cover:
- indexed meshes, half-edge structure, ASCII/binary STL, OBJ, vertex welding, normals, manifoldness, volume and surface area
Problems (5):
1. Parse ASCII STL and Compute Area/Volume [Easy].
2. Binary STL Reader [Medium]: little-endian floats from a byte dump.
3. Vertex Welding and OBJ Export [Medium].
4. Half-Edge Construction and Boundary Loops [Hard].
5. Watertight and Manifold Check [Hard].

### cpp-geo-spatial | Spatial Data Structures | Advanced | status: new
Summary: Accelerating geometric queries.
Lesson must cover:
- uniform grids, quadtrees/octrees, k-d trees, BVH construction (SAH), R-trees overview
Problems (5):
1. Uniform Grid Neighbour Queries [Easy].
2. Quadtree Point Range Query [Medium].
3. k-d Tree Nearest Neighbour [Medium].
4. BVH Ray Intersection [Hard].
5. Octree Voxelization of a Mesh [Hard].

### cpp-geo-collision | Collision Detection | Expert | status: new
Summary: Do two shapes intersect, and how deep?
Lesson must cover:
- AABB/OBB/sphere tests, separating axis theorem, GJK and EPA, broad phase (sweep and prune), continuous collision basics
Problems (5):
1. AABB and Sphere Tests [Easy].
2. SAT for Convex Polygons with MTV [Medium].
3. Sweep and Prune Broad Phase [Medium].
4. GJK Distance/Intersection [Hard].
5. Ray–Triangle (Möller–Trumbore) Batch [Medium].

## Module 30: Graphics and Games

### cpp-gfx-math | Math for Graphics | Intermediate | status: new
Summary: The pipeline math.
Lesson must cover:
- homogeneous coordinates, model/view/projection matrices, perspective divide, viewport, normals transform, color spaces and gamma
Problems (4):
1. Look-At View Matrix [Easy].
2. Perspective Projection to Pixels [Medium].
3. Normal Matrix Transformation [Medium].
4. sRGB ↔ Linear Color Conversion [Easy].

### cpp-gfx-rasterizer | Software Rasterizer | Advanced | status: new
Summary: Drawing triangles on a framebuffer.
Lesson must cover:
- Bresenham lines, edge functions, barycentric interpolation, top-left rule, z-buffer, back-face culling, texture mapping with perspective correction (output as PPM hash/ASCII)
Problems (5):
1. Bresenham Line Drawing [Easy].
2. Triangle Fill with Edge Functions and Top-Left Rule [Medium].
3. Z-Buffer Scene [Medium].
4. Perspective-Correct Texture Mapping [Hard].
5. Clipping Against the Near Plane [Hard].

### cpp-gfx-raytracer | Ray Tracing | Advanced | status: new
Summary: Rendering by tracing rays.
Lesson must cover:
- rays, sphere/plane/triangle intersection, Phong shading, shadows, reflection/refraction, seeded sampling, BVH acceleration
Problems (5):
1. Ray–Sphere Hits [Easy].
2. Phong Shading with Shadows [Medium].
3. Recursive Reflections [Medium].
4. Refraction with Fresnel (Schlick) [Hard].
5. Monte Carlo Diffuse with Seeded RNG [Hard]: image checksum within tolerance.

### cpp-game-loop-ecs | Game Loop and Entity-Component-System | Advanced | status: new
Summary: Architecture of real-time games.
Lesson must cover:
- fixed timestep with interpolation, input handling, ECS (sparse sets, archetypes), systems ordering, event queues
Problems (5):
1. Fixed Timestep Accumulator [Easy].
2. Sparse-Set Component Storage [Medium].
3. ECS Query Iteration [Medium].
4. Archetype Storage [Hard].
5. Deterministic Replay [Hard]: record inputs, reproduce state hash.

### cpp-game-physics | Game Physics Engine | Expert | status: new
Summary: Rigid bodies and collisions.
Lesson must cover:
- integration (semi-implicit Euler), forces/impulses, collision response with restitution and friction, contact resolution, sleeping, constraints overview
Problems (5):
1. Particle Physics with Gravity and Drag [Easy].
2. Circle–Circle Impulse Resolution [Medium].
3. Box Stacking Stability [Hard].
4. Spring–Mass Cloth [Medium].
5. Distance Constraints (Verlet/PBD Rope) [Hard].

### cpp-game-ai | Game AI | Advanced | status: new
Summary: Making agents behave.
Lesson must cover:
- FSMs, behavior trees, steering behaviours (seek, flee, arrive, flocking), grid pathfinding reuse, minimax with alpha-beta, utility AI
Problems (5):
1. Enemy FSM [Easy].
2. Steering: Seek and Arrive [Medium].
3. Boids Flocking Step [Medium].
4. Alpha-Beta Connect Four [Hard].
5. Utility AI Action Selection [Medium].

## Module 31: Embedded C++

### cpp-emb-fixed-point | Fixed-Point Arithmetic in C++ | Advanced | status: new
Summary: Real numbers without an FPU.
Lesson must cover:
- Q formats, templated fixed-point type, rounding, saturation, multiply/divide scaling, lookup tables, CORDIC
Problems (4):
1. Q15 Template Type [Medium].
2. Saturating Arithmetic [Easy].
3. Sine via LUT with Interpolation [Medium].
4. CORDIC atan2 [Hard].

### cpp-emb-no-heap | Memory-Constrained Design | Advanced | status: new
Summary: C++ without dynamic allocation.
Lesson must cover:
- static containers (ETL-style), placement new, compile-time sizing, `-fno-exceptions -fno-rtti` design, stack usage
Problems (4):
1. Static Vector [Easy].
2. Fixed-Capacity Map [Medium].
3. Pool-Backed Message Queue [Medium].
4. Intrusive List Scheduler [Hard].

### cpp-emb-hal-registers | Register Access and HAL Design | Advanced | status: new
Summary: Talking to hardware safely.
Lesson must cover:
- volatile, memory-mapped registers, bit-field templates, type-safe register access, HAL layering, simulated peripherals
Problems (4):
1. Bit Manipulation Helpers [Easy].
2. Type-Safe Register Fields [Medium].
3. Simulated GPIO Driver [Medium].
4. Simulated UART Driver with Interrupt Callbacks [Hard].

### cpp-emb-isr-concurrency | Interrupts and Concurrency on MCUs | Expert | status: new
Summary: Sharing data with ISRs.
Lesson must cover:
- ISR rules, critical sections, atomics on MCUs, SPSC ring buffers, double buffering, debouncing
Problems (4):
1. Lock-Free ISR Ring Buffer [Medium].
2. Button Debouncer [Easy].
3. Double-Buffered ADC Sampling [Medium].
4. Event Flags and Cooperative Scheduler [Hard].

### cpp-emb-state-machines | State Machines for Embedded | Advanced | status: new
Summary: Event-driven firmware.
Lesson must cover:
- table-driven FSMs, hierarchical state machines, guards and actions, timeouts
Problems (4):
1. Table-Driven FSM [Easy].
2. Hierarchical State Machine [Hard].
3. Protocol Handshake FSM with Timeouts [Medium].
4. Battery Charger Controller [Medium].

### cpp-emb-protocols | Communication Protocols | Advanced | status: new
Summary: Serial protocols and integrity.
Lesson must cover:
- UART framing, SLIP/COBS, CRC-8/16/32, CAN frames and signals, Modbus RTU, I2C/SPI transaction modeling
Problems (5):
1. CRC-16 CCITT [Easy].
2. COBS Encode/Decode [Medium].
3. CAN Signal Packing [Medium].
4. Modbus RTU Request Parser [Medium].
5. Robust Framing with Resync [Hard].

## Module 32: Interop: C, Python, WebAssembly

### cpp-interop-c-abi | C++ and C Interop | Advanced | status: new
Summary: Exposing C++ through C APIs.
Lesson must cover:
- `extern "C"`, opaque handles, error codes across the boundary, exceptions must not cross, callbacks with `void*` user data
Problems (4):
1. C API over a C++ Class [Medium].
2. Callback Trampolines [Medium].
3. Exception Firewall [Medium].
4. Versioned Struct ABI [Hard].

### cpp-interop-python | C++ for Python (pybind11 concepts) | Expert | status: new
Summary: Designing C++ libraries consumed from Python.
Lesson must cover:
- pybind11 modules, classes, ownership policies, buffer protocol/NumPy arrays, GIL release, building with CMake/scikit-build (judged via C++ simulation of the binding layer)
Problems (4):
1. Buffer Protocol View [Medium]: strided buffer descriptor and safe element access.
2. Ownership Policy Simulator [Medium]: take_ownership vs reference semantics.
3. Batch API Design [Medium]: vectorized interface to avoid per-call overhead.
4. GIL-Release Worker [Hard]: thread-safe compute while "GIL" lock is released.

### cpp-interop-wasm | C++ to WebAssembly | Expert | status: new
Summary: Running C++ in the browser with Emscripten.
Lesson must cover:
- Emscripten toolchain, linear memory, exporting functions, embind, passing strings/arrays, size optimization (judged via linear-memory simulations)
Problems (4):
1. Linear Memory String Passing [Medium].
2. Arena for JS Interop [Medium].
3. Typed Array Image Filter API [Medium].
4. Serialization Boundary Codec [Hard].

## Module 33: Interview Theory

### cpp-interview-core | C++ Interview Deep Dive I | Advanced | status: existing-thin
Existing: cpp-mini-vector (keep last).
Lesson must cover: top 50 C++ questions (references vs pointers, virtual, RAII, smart pointers, move, templates, STL complexity).
Problems to add (3):
1. Implement std::unique_ptr [Medium].
2. Implement string with SSO [Hard].
3. Implement std::function-like [Hard].

### cpp-interview-advanced | C++ Interview Deep Dive II | Expert | status: existing-thin
Existing: cpp-shared-weak-ptr (keep last).
Lesson must cover: memory model, UB, ABI, templates, concurrency, performance questions.
Problems to add (3):
1. Implement std::optional [Hard].
2. Implement std::variant (2 types) [Hard].
3. Thread-Safe Lazy Init [Medium].
