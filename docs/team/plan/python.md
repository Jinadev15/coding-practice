# Python plan: everything except expanding DSA

Planner: Agent 1. Format follows `HEAD_PLAYBOOK.md`. Python DSA (Module 13) stays exactly as it is.

## How to read this plan

- **existing-ok**: meets the bar (≥ 4 problems) or is DSA (left as is by CEO decision). Do not touch.
- **existing-thin**: fewer than 4 problems. Bring the lesson to the CEO bar and **add** the listed problems; target total is 5 (4–6). Existing problems are kept; an old broad "suite"/case problem goes last.
- **new**: new topic id.
- Judge: stdin/stdout, a hidden driver appended to the user's file (no `if __name__ == "__main__"`, no `from __future__`). Available: numpy, pandas, scipy, scikit-learn, torch (CPU), opencv, fastapi, flask, django, sqlalchemy, pydantic, httpx/requests (no network). Not available (teach the concept, implement a small version by hand): pint, hypothesis, alembic, celery, redis, DRF, matplotlib is assumed present for `py-matplotlib` (Agg backend; judge by inspecting Figure/Axes objects, never images). No internet: HTTP clients are tested against in-process apps (`fastapi.testclient.TestClient`, `flask.test_client()`, `django.test.Client`, `httpx.MockTransport`).
- ML problems must be deterministic: fixed seeds, small synthetic data from generators, metrics compared with tolerance (`compare: float`) or thresholds checked by the driver ("accuracy ≥ 0.9 on hidden split").
- Time limits: torch problems use tiny models (CPU, < 1 s training).

## Priority: what authors build first

1. **Foundations top-ups (Modules 01–12)** — every learner passes through these; most need +2 problems. Cheap and high value. Parallelize across 2 authors.
2. **Web and backend (Module 17)** in order: HTTP → Flask → FastAPI → SQL → SQLAlchemy → auth/security → Django → real-time/caching/queues → API testing → deployment → projects.
3. **Scientific stack (Module 19)** NumPy → pandas → visualization → statistics/SciPy, then **ML (20)** and **deep learning (21)**, then NLP/CV (22), ML engineering (23), LLM apps (24).
4. **Engineering and scientific computing (Module 25)** (mechanical, civil, electrical).
5. **OOP, all GoF patterns, LLD case studies (Modules 14–15)**.
6. **Data engineering & automation (18)**, packaging/tooling (16), software engineering & system design (27), robotics (26).

## Module map (proposed order)

| # | Module | Topics |
|---|---|---|
| 01 | Foundations | 10 (9 thin, 1 ok) |
| 02 | Core Data Structures | 10 (7 thin, 3 ok) |
| 03 | Functions | 7 (6 thin, 1 ok) |
| 04 | Iteration | 4 thin |
| 05 | Errors and Files | 6 thin |
| 06 | Modules and Packaging | 3 thin |
| 07 | OOP Basics | 7 thin |
| 08 | Standard Library Essentials | 8 (7 thin, 1 new) |
| 09 | Advanced Python | 9 (8 thin, 1 new) |
| 10 | Internals and Performance | 6 (5 thin, 1 new) |
| 11 | Concurrency | 7 (6 thin, 1 new) |
| 12 | Testing and Quality | 6 (4 thin, 2 new) |
| 13 | DSA Patterns | 27 existing-ok (unchanged) |
| 14 | OOP Mastery and Design Patterns | 12 (9 thin, 3 new) |
| 15 | Low-Level Design Case Studies | 11 (5 thin, 6 new) |
| 16 | Packaging, Tooling and CLI | 4 (1 thin, 3 new) |
| 17 | Web and Backend Engineering | 19 (5 thin, 14 new) |
| 18 | Data Engineering and Automation | 6 new |
| 19 | Scientific Python: NumPy, pandas, Visualization, Statistics | 11 (5 thin, 6 new) |
| 20 | Machine Learning | 9 (2 thin, 7 new) |
| 21 | Deep Learning with PyTorch | 8 (3 thin, 5 new) |
| 22 | NLP and Computer Vision | 5 (1 thin, 4 new) |
| 23 | Applied ML Engineering | 4 new |
| 24 | LLM Application Engineering (offline) | 5 new |
| 25 | Engineering and Scientific Computing | 13 new |
| 26 | Robotics with Python | 2 thin |
| 27 | Software Engineering, System Design and Interviews | 7 (3 thin, 4 new) |

---

## Module 01: Foundations

### py-how-python-runs | How Python Runs Your Code | Beginner | status: existing-thin
Summary: Interpreter, bytecode, REPL vs scripts, stdin/stdout judging.
Lesson must cover:
- source → bytecode → CPython VM, `.pyc`, modules executed top to bottom, `sys.argv`, `sys.stdin` reading idioms
Existing: py-hello-judge, py-sum-two-lines, py-three-numbers-one-line.
Problems to add (2):
4. Read Until EOF Stats [Easy]: `sys.stdin.read().split()` vs line loops; count/sum/max of all numbers.
5. Fast Input for 10⁶ Lines [Medium]: `sys.stdin.buffer` and `'\n'.join` output to meet the time limit.

### py-syntax-basics | Syntax, Indentation and Comments | Beginner | status: existing-thin
Summary: Blocks, statements, line continuation, naming.
Lesson must cover:
- indentation rules, `IndentationError`, implicit/explicit line joining, comments/docstrings, PEP 8 naming
Existing: py-long-expression, py-sign-report.
Problems to add (3):
3. Nested Block Router [Easy]: nested if/for blocks producing a routing table.
4. Docstring Extractor [Medium]: read a function's `__doc__` and print its first line and parameter list.
5. Indentation Checker [Medium]: given source lines, report the first line with inconsistent indentation (spaces vs tabs, dedent to unknown level).

### py-variables-objects | Variables and the Object Model | Beginner | status: existing-thin
Existing: py-alias-detective, py-rotate-three, py-swap-names.
Lesson must cover: names vs objects, identity/type/value, `is` vs `==`, small int caching caveats, rebinding vs mutation.
Problems to add (2):
4. Rebind or Mutate [Medium]: predict and then reproduce final states after a list of operations on aliased lists.
5. Reference Graph Counter [Medium]: count distinct objects reachable from given names (use `id()` with care).

### py-numbers | Numbers: int, float, complex | Beginner | status: existing-thin
Existing: py-ceiling-boxes, py-digit-stats, py-python-vs-c-division.
Lesson must cover: arbitrary precision ints, float representation, `round` banker's rounding, `decimal`, `fractions`, `complex`, `math.isclose`.
Problems to add (2):
4. Money with Decimal [Medium]: invoice totals with `ROUND_HALF_UP` per line.
5. Exact Fractions Calculator [Medium]: evaluate fraction expressions with `Fraction`.

### py-strings-basics | String Basics | Beginner | status: existing-thin
Existing: py-caesar-cipher, py-first-last-middle, py-palindrome-check.
Lesson must cover: immutability, indexing, methods, `join` vs `+=`, f-strings, `in`.
Problems to add (2):
4. Word Stats [Easy]: longest word, vowels count, title-case output.
5. Run-Length Decode with Validation [Medium].

### py-io-formatting | Input/Output and f-strings | Beginner | status: existing-thin
Existing: py-number-formats, py-receipt, py-sum-until-eof.
Lesson must cover: `print` args, format spec mini-language, alignment, `!r`, `=` specifier, `sys.stdout.write`.
Problems to add (2):
4. Aligned Table Printer [Easy]: compute widths dynamically.
5. Format Spec Implementer [Hard]: implement a subset of `format(value, spec)` (fill, align, width, precision, type d/f/x/%) and compare.

### py-operators | Operators and Precedence | Beginner | status: existing-thin
Existing: py-bit-toolkit, py-single-number, py-triangle-type.
Lesson must cover: arithmetic incl. `//` and `%` with negatives, comparison chaining, boolean short circuit, walrus, precedence table.
Problems to add (2):
4. Chained Comparisons Validator [Easy].
5. Precedence-Aware Evaluator [Hard]: evaluate expressions with Python's precedence (incl. `**` right-assoc and unary minus) and compare with `eval` semantics.

### py-booleans-truthiness | Booleans and Truthiness | Beginner | status: existing-thin
Existing: py-default-names, py-leap-years, py-sign-counts.
Lesson must cover: truthy/falsy values, `and`/`or` return operands, `any`/`all`, `__bool__`/`__len__`.
Problems to add (2):
4. Config Fallback Chain [Easy]: `a or b or default` with care for valid zeros.
5. Custom Truthiness [Medium]: classes implementing `__bool__`/`__len__`; filter objects accordingly.

### py-conditionals | Conditionals | Beginner | status: existing-thin
Existing: py-max-of-three, py-quadrant, py-shipping-cost.
Lesson must cover: if/elif/else, conditional expressions, guard clauses, dict dispatch instead of long chains.
Problems to add (2):
4. Tax Bracket Calculator [Medium]: progressive brackets.
5. Dispatch Table Calculator [Medium]: replace if-chains with dict of functions.

### py-loops | Loops: while and for | Beginner | status: existing-ok
Existing: 4 problems. No changes.

## Module 02: Core Data Structures

### py-lists | Lists | Beginner | status: existing-ok
Existing: 4 problems.

### py-tuples | Tuples | Beginner | status: existing-thin
Existing: py-distinct-points, py-leaderboard, py-min-max-pair.
Lesson must cover: immutability (shallow), packing/unpacking, tuples as keys, `namedtuple`.
Problems to add (2):
4. Lexicographic Record Sort [Easy]: multi-key sort via tuple keys.
5. Namedtuple CSV Parser [Medium].

### py-dicts | Dictionaries | Beginner | status: existing-ok
Existing: 4 problems.

### py-sets | Sets and Frozensets | Beginner | status: existing-thin
Existing: py-contains-duplicate, py-longest-consecutive, py-pangram.
Lesson must cover: hashing, set algebra, frozenset as keys, set comprehension, complexity.
Problems to add (2):
4. Course Overlap Report [Easy]: intersections/differences of enrolments.
5. Group Equal Sets [Medium]: frozensets as dict keys.

### py-slicing | Slicing in Depth | Intermediate | status: existing-thin
Existing: py-implement-slice, py-is-rotation, py-reverse-chunks.
Lesson must cover: start/stop/step, negative steps, slice objects, `slice.indices`, slice assignment, `__getitem__` with slices.
Problems to add (2):
4. Slice Assignment Editor [Medium]: apply edit commands using slice assignment.
5. Sliceable Custom Sequence [Hard]: class supporting int and slice indexing with negative steps.

### py-comprehensions | Comprehensions | Intermediate | status: existing-thin
Existing: py-inverted-index, py-pythagorean-triples, py-transpose-flatten.
Lesson must cover: list/dict/set/generator comprehensions, nested, conditionals, scope rules, readability limits.
Problems to add (2):
4. Matrix Ops in Comprehensions [Easy].
5. Grouping with Dict Comprehension [Medium].

### py-unpacking | Unpacking and Star Expressions | Intermediate | status: existing-thin
Existing: py-grade-records, py-merge-config, py-rotate-matrix.
Lesson must cover: starred assignment, `*`/`**` in calls and literals, nested unpacking.
Problems to add (2):
4. Head/Tail Parser [Easy].
5. Nested Record Unpacker [Medium].

### py-strings-advanced | Strings Advanced: Methods, Unicode, Bytes | Intermediate | status: existing-thin
Existing: py-log-parser, py-run-length, py-utf8-stats.
Lesson must cover: Unicode code points, normalization (NFC/NFD), casefold, encode/decode errors, bytes vs str.
Problems to add (2):
4. Unicode Normalizer Compare [Medium].
5. Manual UTF-8 Encoder/Decoder [Hard].

### py-mutability-copying | Mutability and Copying | Intermediate | status: existing-thin
Existing: py-fix-default, py-my-deepcopy, py-undo-grid.
Lesson must cover: shallow vs deep copy, `copy` module, `__copy__`/`__deepcopy__`, mutable defaults.
Problems to add (2):
4. Grid Aliasing Bug [Easy]: `[[0]*n]*m` fix.
5. Custom __deepcopy__ with Shared References [Hard].

### py-sorting | Sorting and Key Functions | Intermediate | status: existing-ok
Existing: 4 problems.

## Module 03: Functions

### py-functions-basics | Defining and Calling Functions | Beginner | status: existing-thin
Existing: py-next-prime, py-stats-functions, py-temperature.
Problems to add (2):
4. Pure vs Impure Refactor [Medium]: rewrite side-effecting functions to pure.
5. Function as Value Pipeline [Medium].

### py-parameters | Parameters: defaults, *args, **kwargs | Intermediate | status: existing-thin
Existing: py-flexible-stats, py-signature-binder, py-tag-builder.
Lesson must cover: positional-only `/`, keyword-only `*`, defaults evaluated once, `inspect.signature`.
Problems to add (2):
4. Keyword-Only API [Easy].
5. Argument Forwarding Wrapper [Medium].

### py-scope-closures | Scope (LEGB), global, nonlocal and Closures | Intermediate | status: existing-thin
Existing: py-counter-factory, py-memoize-closure, py-moving-average.
Problems to add (2):
4. Late Binding Loop Bug [Medium]: fix lambdas capturing loop variable.
5. Closure-Based Rate Limiter [Medium].

### py-lambda-functional | Lambdas and Functional Tools | Intermediate | status: existing-thin
Existing: py-my-reduce, py-pipeline, py-word-transforms.
Problems to add (2):
4. Compose and Pipe [Easy].
5. Point-Free Data Processing [Medium]: map/filter/reduce over records with `operator` module.

### py-recursion | Recursion | Intermediate | status: existing-ok
Existing: 4 problems.

### py-decorators | Decorators | Advanced | status: existing-thin
Existing: py-call-logger, py-retry-decorator, py-type-check-decorator.
Problems to add (2):
4. Timing Decorator with Fake Clock [Medium].
5. Decorator with Arguments and functools.wraps [Medium]: `@cache_for(seconds)`.

### py-type-hints | Type Hints | Intermediate | status: existing-thin
Existing: py-mini-typechecker, py-typed-functions.
Lesson must cover: annotations, Optional/Union `|`, collections generics, `TypedDict`, `Literal`, `get_type_hints`.
Problems to add (3):
3. Annotate and Validate [Easy]: runtime validation using `get_type_hints`.
4. TypedDict Payload Checker [Medium].
5. Literal-Based Dispatcher [Medium].

## Module 04: Iteration

### py-iterators | Iterables and Iterators | Intermediate | status: existing-thin
Existing: py-my-range, py-peeking-iterator, py-round-robin.
Problems to add (2):
4. Iterator Protocol for Tree [Medium].
5. Resettable Chunked Reader [Medium].

### py-generators | Generators and yield | Advanced | status: existing-thin
Existing: py-batched, py-deep-flatten, py-prime-stream.
Lesson must cover: `send`, `throw`, `close`, `yield from`, generator pipelines, coroutine-style generators.
Problems to add (2):
4. Generator Pipeline for Logs [Medium].
5. send()-Driven Running Average [Hard].

### py-itertools | itertools | Advanced | status: existing-thin
Existing: py-k-subset-sum, py-longest-run, py-phone-letters.
Problems to add (2):
4. groupby Sessionizer [Medium].
5. Pairwise and Accumulate Analytics [Medium].

### py-functools | functools | Advanced | status: existing-thin
Existing: py-decode-ways, py-lru-cache, py-singledispatch-render.
Problems to add (2):
4. partial and reduce Config Pipeline [Easy].
5. cached_property and total_ordering Models [Medium].

## Module 05: Errors and Files

### py-exceptions | Exceptions | Intermediate | status: existing-thin
Existing: py-bank-exceptions, py-config-chain, py-safe-calculator.
Lesson must cover: hierarchy, `raise from`, exception groups and `except*`, `finally`, `add_note`.
Problems to add (2):
4. Exception Groups Validation [Medium]: collect all errors.
5. Retry Policy Classifier [Medium].

### py-context-managers | Context Managers | Advanced | status: existing-thin
Existing: py-indenter, py-resource-log, py-transaction.
Problems to add (2):
4. contextlib Tools [Medium]: `suppress`, `redirect_stdout`, `ExitStack`.
5. Async Context Manager [Medium].

### py-file-io | File I/O | Intermediate | status: existing-thin
Existing: py-binary-records, py-file-tail, py-numbered-copy.
Problems to add (2):
4. Atomic File Write [Medium]: temp + rename.
5. Chunked Large File Checksum [Medium].

### py-pathlib-os | pathlib, os and shutil | Intermediate | status: existing-thin
Existing: py-duplicate-files, py-extension-report, py-tree-printer.
Problems to add (2):
4. Organize Files by Date [Medium]: within a temp dir.
5. Glob-Based Cleanup Dry Run [Medium].

### py-json-csv | JSON, CSV and Serialization | Intermediate | status: existing-thin
Existing: py-csv-to-json, py-json-query, py-sales-report.
Problems to add (2):
4. Custom JSON Encoder/Decoder [Medium]: dates, Decimals, dataclasses.
5. Pickle vs JSON Safety [Medium]: safe deserializer allowing a whitelist.

### py-logging | Logging | Intermediate | status: existing-thin
Existing: py-log-analyzer-levels, py-log-levels.
Problems to add (3):
3. Handler and Formatter Setup [Easy].
4. Logger Hierarchy and Propagation [Medium].
5. Structured JSON Logging with Context [Medium].

## Module 06: Modules and Packaging

### py-modules-imports | Modules and Imports | Intermediate | status: existing-thin
Existing: py-fix-circular, py-two-module-app.
Problems to add (3):
3. Import Resolution Order [Medium]: simulate `sys.path` lookup.
4. importlib Dynamic Loading [Medium].
5. Module Reload and Caching [Medium].

### py-packages | Packages and Project Structure | Intermediate | status: existing-thin
Existing: py-sensor-package.
Problems to add (4):
2. __init__ Exports and __all__ [Easy].
3. Relative Imports in Subpackages [Medium].
4. Namespace Packages [Medium].
5. Plugin Discovery via Entry-Point-Like Registry [Hard].

### py-venv-packaging | Virtual Environments, pip, uv and pyproject | Intermediate | status: existing-thin
Existing: py-version-specifiers.
Problems to add (4):
2. pyproject Parser [Easy]: `tomllib` read and validate metadata.
3. Dependency Resolver [Hard]: pick versions satisfying constraints (backtracking).
4. Lock File Diff [Medium].
5. Wheel Filename Parser [Medium]: tags compatibility.

## Module 07: OOP Basics

### py-classes-objects | Classes and Objects | Beginner | status: existing-thin
Existing: py-bank-account-class, py-robot-composition.
Problems to add (3):
3. Rectangle with Validation [Easy].
4. Stack and Queue Classes [Easy].
5. Matrix Class [Medium].

### py-class-vs-instance | Class vs Instance Attributes | Intermediate | status: existing-thin
Existing: py-sensor-registry.
Problems to add (4):
2. Shared Mutable Class Attribute Bug [Easy].
3. Instance Counter and IDs [Easy].
4. Attribute Lookup Order Tracer [Medium].
5. Class-Level Config with Overrides [Medium].

### py-method-types | Instance, Class and Static Methods | Intermediate | status: existing-thin
Existing: py-alt-constructors.
Problems to add (4):
2. Static Utility vs Instance Method [Easy].
3. classmethod Factories in Subclasses [Medium].
4. Registry via __init_subclass__ [Medium].
5. Unit Conversion Classmethods [Medium].

### py-encapsulation-properties | Encapsulation and Properties | Intermediate | status: existing-thin
Existing: py-validated-motor.
Problems to add (4):
2. Read-Only Properties [Easy].
3. Computed Properties with Caching [Medium].
4. Name Mangling Explained [Medium].
5. Temperature with Unit Setters [Medium].

### py-inheritance | Inheritance and super() | Intermediate | status: existing-thin
Existing: py-shape-hierarchy.
Problems to add (4):
2. Employee Payroll Hierarchy [Easy].
3. MRO and Cooperative super() [Medium].
4. Mixins for Serialization [Medium].
5. C3 Linearization Implementer [Hard].

### py-polymorphism | Polymorphism and Duck Typing | Intermediate | status: existing-thin
Existing: py-shape-areas.
Problems to add (4):
2. Duck-Typed File-Likes [Easy].
3. Operator Polymorphism for Vectors [Medium].
4. EAFP vs LBYL Handlers [Medium].
5. Plugin Polymorphism via Protocol [Medium].

### py-dunder-basics | Special Methods: __str__, __repr__, __eq__ | Intermediate | status: existing-thin
Existing: py-money-value.
Problems to add (4):
2. repr Round-Trip [Easy].
3. __eq__ and __hash__ Consistency [Medium].
4. Ordering with total_ordering [Medium].
5. Container Dunders [Medium]: `__len__`, `__contains__`, `__iter__`.

## Module 08: Standard Library Essentials

### py-collections | collections Module | Intermediate | status: existing-thin
Existing: py-access-log-stats, py-sliding-window-max.
Problems to add (3):
3. Counter Arithmetic [Easy].
4. ChainMap Config Layers [Medium].
5. OrderedDict LRU [Medium].

### py-heapq-bisect | heapq and bisect | Intermediate | status: existing-thin
Existing: py-cpu-scheduler, py-range-queries, py-running-median.
Problems to add (2):
4. heapq.merge Sorted Logs [Easy].
5. bisect Grade Mapper and Insort [Easy].

### py-datetime | datetime and time | Intermediate | status: existing-thin
Existing: py-shift-hours.
Lesson must cover: naive vs aware, `zoneinfo`, timedelta arithmetic, parsing/formatting, DST pitfalls, monotonic time.
Problems to add (4):
2. Age and Day Differences [Easy].
3. Timezone Meeting Planner [Medium]: `zoneinfo`.
4. DST-Safe Scheduling [Hard].
5. ISO Week Reports [Medium].

### py-math-random | math, random, statistics | Intermediate | status: existing-thin
Existing: py-number-toolkit.
Problems to add (4):
2. Seeded Shuffle and Sample [Easy].
3. statistics Module Summary [Easy].
4. Monte Carlo π with Error Bound [Medium].
5. Reservoir Sampling [Medium].

### py-regex | Regular Expressions | Advanced | status: existing-thin
Existing: py-kv-log-parser, py-tokenizer.
Problems to add (3):
3. Named Groups Date Extractor [Easy].
4. Lookarounds Password Rules [Medium].
5. Regex Substitution with Callbacks [Medium].

### py-dataclasses | Dataclasses | Intermediate | status: existing-thin
Existing: py-parts-catalog.
Problems to add (4):
2. Frozen and Ordered Dataclasses [Easy].
3. field(default_factory) and __post_init__ Validation [Medium].
4. slots and kw_only [Medium].
5. Dataclass to/from Dict Serializer [Medium].

### py-enum | Enums | Intermediate | status: existing-thin
Existing: py-robot-fsm.
Problems to add (4):
2. Enum Lookup by Value/Name [Easy].
3. Flag Permissions [Medium].
4. StrEnum Status Codes [Easy].
5. Enum with Behaviour [Medium].

### py-typing-runtime | Runtime Data Validation with Pydantic | Intermediate | status: new
Summary: Validating untrusted data with pydantic v2.
Lesson must cover:
- BaseModel, field types, validators, model_dump/validate_json, nested models, settings-style config
Problems (5):
1. Validate User Payloads [Easy].
2. Field Validators and Constraints [Medium].
3. Nested Models and Errors Report [Medium].
4. Discriminated Unions [Hard].
5. Custom Serializer and Aliases [Medium].

## Module 09: Advanced Python

### py-data-model | The Python Data Model | Advanced | status: existing-thin
Existing: py-matrix-protocols.
Problems to add (4):
2. Numeric Tower Type [Medium]: `__add__`, `__radd__`, `NotImplemented`.
3. Context of __getattr__ vs __getattribute__ [Medium].
4. Callable Objects [Easy].
5. Rich Comparison Protocols [Medium].

### py-descriptors | Descriptors | Expert | status: existing-thin
Existing: py-validated-fields.
Problems to add (4):
2. Lazy Property Descriptor [Medium].
3. Typed Field with __set_name__ [Medium].
4. Non-Data vs Data Descriptor Lookup [Hard].
5. Mini ORM Columns [Hard].

### py-metaclasses | Metaclasses and Class Creation | Expert | status: existing-thin
Existing: py-plugin-framework.
Problems to add (4):
2. type() Class Factory [Medium].
3. __init_subclass__ vs Metaclass [Medium].
4. Enforced Interface Metaclass [Hard].
5. Singleton and Registry Metaclass [Hard].

### py-slots-memory | __slots__ and Object Memory | Advanced | status: existing-thin
Existing: py-weak-sprite-cache.
Problems to add (4):
2. Slots Memory Comparison [Medium].
3. Slots with Inheritance [Medium].
4. WeakValueDictionary Cache [Medium].
5. Flyweight with Slots [Medium].

### py-abc-protocols | Abstract Base Classes and Protocols | Advanced | status: existing-thin
Existing: py-ordered-set.
Problems to add (4):
2. ABC Enforcement [Easy].
3. collections.abc Mixins [Medium].
4. runtime_checkable Protocol [Medium].
5. Virtual Subclass Registration [Medium].

### py-generics-typing | Advanced Typing and Generics | Expert | status: existing-thin
Existing: py-runtime-typecheck.
Lesson must cover: TypeVar bounds/constraints, Generic classes, PEP 695 syntax, ParamSpec, Concatenate, overloads, variance, Self, TypeGuard.
Problems to add (4):
2. Generic Repository [Medium].
3. ParamSpec Decorator [Hard].
4. Overloaded Parse Function [Medium].
5. Variance Checker [Hard]: given type relations, decide assignability for covariant/contravariant generics.

### py-pattern-matching | Structural Pattern Matching | Advanced | status: existing-thin
Existing: py-robot-commands.
Problems to add (4):
2. JSON Shape Router [Medium].
3. AST Evaluator with match [Medium].
4. Class Patterns with __match_args__ [Medium].
5. Guards and Or-Patterns Parser [Medium].

### py-advanced-decorators | Advanced Decorators and Closures | Expert | status: existing-thin
Existing: py-decorator-suite.
Problems to add (4):
2. Class Decorator Adding Methods [Medium].
3. Decorator Preserving Signature [Medium].
4. Method Decorator with Descriptors [Hard].
5. Async-Aware Decorator [Hard].

### py-internals-objects | How Objects Work: Attribute Lookup and Namespaces | Expert | status: new
Summary: The machinery behind attribute access and class creation.
Lesson must cover:
- `__dict__`, MRO, attribute lookup algorithm, bound methods, `__class_getitem__`, `__set_name__`
Problems (4):
1. Attribute Lookup Simulator [Hard].
2. Bound Method Builder [Medium].
3. Dynamic Proxy Object [Medium].
4. Class Creation Pipeline Trace [Hard].

## Module 10: Internals and Performance

### py-memory-gc | Memory Management and Garbage Collection | Expert | status: existing-thin
Existing: py-refcount-simulator.
Problems to add (4):
2. Cycle Detector Simulation [Hard].
3. weakref Finalizers [Medium].
4. Memory Leak Hunt with tracemalloc [Medium].
5. sys.getsizeof Deep Size [Medium].

### py-gil-free-threading | The GIL and Free-Threaded Python | Expert | status: existing-thin
Existing: none (0 problems).
Lesson must cover: what the GIL protects, CPU- vs I/O-bound, switching interval, free-threaded 3.13+ build, thread-safety of builtins.
Problems (4):
1. CPU vs I/O Bound Classifier [Easy]: choose threads/processes per task description.
2. Race on Counter [Medium]: demonstrate and fix with a lock.
3. Release-the-GIL with NumPy [Medium]: threads speed up NumPy work.
4. Thread-Safe Lazy Cache [Hard].

### py-bytecode-dis | Bytecode and dis | Expert | status: existing-thin
Existing: py-expr-compiler.
Problems to add (4):
2. Disassemble and Count Ops [Medium].
3. Stack VM for Subset Bytecode [Hard].
4. Constant Folding Detector [Medium].
5. Code Object Introspection [Medium].

### py-profiling | Profiling and Optimization | Advanced | status: existing-thin
Existing: py-optimize-pipeline.
Problems to add (4):
2. cProfile Hot Spot Report [Medium].
3. Vectorize the Loop [Medium].
4. Algorithmic Fix Beats Micro-Opt [Medium].
5. Memory-Efficient Generators [Medium].

### py-c-extensions | C Extensions, ctypes and Cython | Expert | status: existing-thin
Existing: py-ctypes-libc.
Problems to add (4):
2. ctypes Structures and Arrays [Medium].
3. Callbacks into Python via ctypes [Hard].
4. Buffer Protocol and memoryview [Medium].
5. struct Module Binary Packing [Medium].

### py-performance-patterns | High-Performance Python Patterns | Advanced | status: new
Summary: Making Python fast enough.
Lesson must cover:
- complexity first, built-ins and comprehensions, `array`/`memoryview`, NumPy vectorization, caching, numba-style thinking (typed loops), multiprocessing for CPU work
Problems (5):
1. Built-ins Beat Loops [Easy].
2. String Building at Scale [Medium].
3. NumPy Rolling Window via Strides [Hard].
4. Memoization vs Tabulation Timing [Medium].
5. Batch Processing with Multiprocessing Pool [Hard].

## Module 11: Concurrency

### py-threading | Threading | Advanced | status: existing-thin
Existing: py-threaded-pipeline.
Problems to add (4):
2. Thread-Safe Counter [Easy].
3. Producer-Consumer with queue.Queue [Medium].
4. Timer and Event Coordination [Medium].
5. Thread Pool Crawler (fake I/O) [Medium].

### py-multiprocessing | Multiprocessing | Advanced | status: existing-thin
Existing: py-parallel-sieve.
Problems to add (4):
2. Pool.map Chunking [Easy].
3. Shared Memory Arrays [Medium].
4. Manager Dict Aggregation [Medium].
5. Process Pipeline with Queues [Hard].

### py-concurrent-futures | concurrent.futures | Advanced | status: existing-thin
Existing: py-futures-fetcher.
Problems to add (4):
2. as_completed Ordering [Easy].
3. Timeouts and Cancellation [Medium].
4. Exception Propagation from Workers [Medium].
5. Bounded Submission Window [Hard].

### py-asyncio-basics | asyncio Fundamentals | Advanced | status: existing-thin
Existing: py-async-telemetry.
Problems to add (4):
2. gather vs sequential [Easy].
3. TaskGroup Error Handling [Medium].
4. asyncio.Queue Workers [Medium].
5. Timeouts with asyncio.timeout [Medium].

### py-asyncio-advanced | asyncio Advanced | Expert | status: existing-thin
Existing: py-async-crawler.
Problems to add (4):
2. Semaphore Rate Limiting [Medium].
3. Async Generators and Streams [Medium].
4. Graceful Shutdown with Cancellation [Hard].
5. Custom Event Loop Scheduler Simulation [Hard].

### py-sync-primitives | Synchronization Primitives and Deadlocks | Expert | status: existing-thin
Existing: py-bank-and-buffer.
Problems to add (4):
2. Condition-Based Bounded Buffer [Medium].
3. Dining Philosophers Without Deadlock [Hard].
4. Reader-Writer Lock [Hard].
5. Deadlock Detector from Wait-For Graph [Medium].

### py-async-production | Async Patterns in Production | Expert | status: new
Summary: Real-world async design.
Lesson must cover:
- backpressure, retries with jitter, circuit breakers, structured concurrency, mixing sync and async (`to_thread`), testing async code
Problems (5):
1. Retry with Exponential Backoff and Jitter [Medium].
2. Circuit Breaker [Medium].
3. Bounded Async Pipeline [Hard].
4. Async Cache with Request Coalescing [Hard].
5. to_thread Offloading [Medium].

## Module 12: Testing and Quality

### py-unittest-pytest | unittest and pytest | Intermediate | status: existing-thin
Existing: py-kill-the-mutants, py-unittest-testcase.
Problems to add (3):
3. Parametrized Tests that Kill Mutants [Medium].
4. Fixtures and tmp_path [Medium].
5. Testing Exceptions and Warnings [Medium].

### py-mocking | Mocking and Test Doubles | Advanced | status: existing-thin
Existing: py-mock-interactions.
Problems to add (4):
2. patch the Right Place [Medium].
3. Fake vs Mock vs Stub [Medium].
4. Mocking Time and Randomness [Medium].
5. autospec Catches API Drift [Hard].

### py-tdd-quality | TDD, Linting and Static Typing | Intermediate | status: existing-thin
Existing: py-tdd-token-bucket.
Problems to add (4):
2. Red-Green-Refactor Kata: String Calculator [Medium].
3. Lint Rule Implementer [Medium]: AST-based unused-variable checker.
4. Cyclomatic Complexity Calculator [Medium].
5. Type-Annotation Coverage Report [Medium].

### py-debugging | Debugging | Intermediate | status: existing-thin
Existing: py-debug-telemetry.
Problems to add (4):
2. Traceback Reader [Easy].
3. Bisect the Bad Commit [Medium]: binary search over versions.
4. Off-by-One Hunt [Easy].
5. Heisenbug: Shared State [Medium].

### py-property-testing | Property-Based and Fuzz Testing | Advanced | status: new
Summary: Testing invariants with random inputs (hand-rolled, hypothesis concepts).
Lesson must cover:
- properties vs examples, generators, shrinking, oracles, metamorphic testing, fuzzing parsers
Problems (4):
1. Round-Trip Property [Medium].
2. Shrinking Failing Lists [Hard].
3. Metamorphic Testing of a Sort [Medium].
4. Differential Fuzzing Two Parsers [Hard].

### py-refactoring-clean-code | Clean Code and Refactoring | Intermediate | status: new
Summary: Improving code without changing behaviour.
Lesson must cover:
- code smells, extract function/class, replace conditional with polymorphism, characterization tests, naming
Problems (4):
1. Extract Function Kata [Easy].
2. Replace Conditional with Polymorphism [Medium].
3. Characterization Test then Refactor [Medium].
4. Long Parameter List to Parameter Object [Medium].

## Module 13: DSA Patterns (unchanged by CEO decision)

All status: existing-ok. Do not add problems.

### py-complexity | Complexity Analysis (Big-O) | Intermediate | status: existing-ok
### py-two-pointers | Two Pointers | Intermediate | status: existing-ok
### py-sliding-window | Sliding Window | Intermediate | status: existing-ok
### py-prefix-sums | Prefix Sums and Difference Arrays | Intermediate | status: existing-ok
### py-hashing-patterns | Hashing Patterns | Intermediate | status: existing-ok
### py-binary-search | Binary Search and Search on Answer | Advanced | status: existing-ok
### py-stacks-monotonic | Stacks and Monotonic Stacks | Advanced | status: existing-ok
### py-queues-bfs | Queues and Deques | Intermediate | status: existing-ok
### py-linked-lists | Linked Lists | Intermediate | status: existing-ok
### py-trees | Binary Trees and Traversals | Intermediate | status: existing-ok
### py-bst | Binary Search Trees | Advanced | status: existing-ok
### py-heaps-topk | Heaps and Top-K | Advanced | status: existing-ok
### py-graphs-traversal | Graphs: Representation and BFS/DFS | Advanced | status: existing-ok
### py-topological-sort | Topological Sort | Advanced | status: existing-ok
### py-shortest-paths | Shortest Paths | Expert | status: existing-ok
### py-union-find | Union-Find (Disjoint Set Union) | Advanced | status: existing-ok
### py-backtracking | Backtracking | Advanced | status: existing-ok
### py-dp-1d | Dynamic Programming I: 1D | Advanced | status: existing-ok
### py-dp-2d | Dynamic Programming II: Grids and Knapsack | Expert | status: existing-ok
### py-dp-strings | Dynamic Programming III: Strings | Expert | status: existing-ok
### py-dp-advanced | Dynamic Programming IV: Bitmask, Trees, Intervals | Research | status: existing-ok
### py-greedy-intervals | Greedy Algorithms and Intervals | Advanced | status: existing-ok
### py-tries | Tries | Advanced | status: existing-ok
### py-segment-fenwick | Segment Trees and Fenwick Trees | Expert | status: existing-ok
### py-string-algorithms | String Algorithms | Expert | status: existing-ok
### py-bit-manipulation | Bit Manipulation | Advanced | status: existing-ok
### py-math-number-theory | Math and Number Theory | Advanced | status: existing-ok

## Module 14: OOP Mastery and Design Patterns

### py-oop-thinking | Thinking in Objects: From Problem to Classes | Intermediate | status: existing-thin
Existing: py-money-value-object.
Problems to add (3):
2. Requirements to Classes: Library Loans [Easy].
3. Tell-Don't-Ask Refactor [Medium].
4. Entities vs Value Objects in an Order System [Medium].

### py-oop-relationships | Relationships: Association, Aggregation, Composition | Intermediate | status: existing-thin
Existing: py-university-enrollment.
Problems to add (3):
2. Composition Lifetime: Car and Engine [Easy].
3. Many-to-Many with Association Objects [Medium].
4. Bidirectional Links Kept Consistent [Medium].

### py-oop-solid | SOLID Principles | Advanced | status: existing-thin
Existing: py-report-service.
Problems to add (4):
2. Open/Closed Discount Rules [Medium].
3. Liskov Contract Tests [Medium].
4. Interface Segregation for Devices [Medium].
5. Dependency Inversion Notification [Medium].

### py-oop-composition | Composition over Inheritance and Dependency Injection | Advanced | status: existing-thin
Existing: py-di-container.
Problems to add (3):
2. Replace Inheritance with Strategy Objects [Medium].
3. Constructor Injection and Fakes [Medium].
4. Delegation via __getattr__ [Medium].

### py-oop-multifile | Organizing an OOP Project Across Files | Advanced | status: existing-thin
Existing: py-layered-package.
Problems to add (3):
2. Break a Circular Dependency with Interfaces [Medium].
3. Package Layering Validator [Medium]: forbid imports from domain to infrastructure.
4. Public API Surface via __all__ [Easy].

### py-patterns-creational | Creational Patterns | Advanced | status: existing-thin
Existing: py-plugin-registry.
Lesson must cover: Factory Method, Abstract Factory, Builder, Prototype, Singleton (and the Pythonic module-level alternative).
Problems to add (5, one per pattern):
2. Factory Method Exporters [Easy].
3. Abstract Factory Themes [Medium].
4. Fluent Query Builder [Medium].
5. Prototype Registry with deepcopy [Medium].
6. Singleton Three Ways [Medium]: module, metaclass, decorator; compare behaviours.

### py-patterns-structural | Structural Patterns I: Adapter, Bridge, Composite, Decorator | Advanced | status: existing-thin
Existing: py-decorator-toolkit.
Problems to add (4):
2. Adapter for Third-Party Payment API [Easy].
3. Bridge Shapes × Renderers [Medium].
4. Composite Org Chart [Medium].
5. Decorator Pattern Stream Wrappers [Medium].

### py-patterns-structural-2 | Structural Patterns II: Facade, Flyweight, Proxy | Advanced | status: new
Lesson must cover: Facade, Flyweight, Proxy (lazy, caching, protection, remote).
Problems (4):
1. Video Conversion Facade [Easy].
2. Flyweight Map Tiles [Medium].
3. Lazy Loading Proxy [Medium].
4. Access-Control Proxy [Medium].

### py-patterns-behavioral | Behavioral Patterns I: Observer, Strategy, Command, State, Template Method | Advanced | status: existing-thin
Existing: py-topic-event-bus.
Problems to add (5):
2. Strategy Shipping Costs [Easy].
3. Command Undo/Redo Text Editor [Medium].
4. State Pattern Traffic Controller [Medium].
5. Template Method Report Pipeline [Medium].
6. Observer with Weak References [Medium].

### py-patterns-behavioral-2 | Behavioral Patterns II: Chain, Iterator, Mediator, Memento, Visitor, Interpreter | Advanced | status: new
Problems (6):
1. Middleware Chain of Responsibility [Easy].
2. Iterator over Composite [Medium].
3. Mediator Air Traffic Control [Medium].
4. Memento Editor History [Medium].
5. Visitor over AST with singledispatch [Hard].
6. Interpreter for a Filter DSL [Hard].

### py-clean-architecture | Clean Architecture | Expert | status: existing-thin
Existing: py-hexagonal-fleet.
Problems to add (3):
2. Use Case with Ports and Adapters [Medium].
3. Repository and Unit of Work [Hard].
4. Domain Events and Handlers [Hard].

### py-ddd-modeling | Domain-Driven Design Essentials | Expert | status: new
Summary: Modeling complex domains.
Lesson must cover: ubiquitous language, entities, value objects, aggregates and invariants, domain services, bounded contexts, anti-corruption layers.
Problems (4):
1. Aggregate Invariants: Order Lines [Medium].
2. Value Objects for Money and Address [Easy].
3. Anti-Corruption Layer Translator [Medium].
4. Event-Sourced Bank Account [Hard].

## Module 15: Low-Level Design Case Studies

Each case study: requirements → class model → behaviours → extension. Problems are stages with different design concerns.

### py-oop-case-library | Case Study: Library Management System | Advanced | status: existing-thin
Existing: py-library-system (keep last).
Problems to add (3): 1. Catalog Search with Filters [Easy]. 2. Reservations Queue and Fines [Medium]. 3. Notification Hooks via Observer [Medium].

### py-oop-case-parking | Case Study: Parking Lot | Advanced | status: existing-thin
Existing: py-parking-reservations (keep last).
Problems to add (3): 1. Spot Assignment by Size [Easy]. 2. Pricing Strategies [Medium]. 3. Multi-Gate Concurrency with Locks [Hard].

### py-oop-case-bank | Case Study: Banking System | Advanced | status: existing-thin
Existing: py-banking-ledger (keep last).
Problems to add (3): 1. Accounts and Transactions [Easy]. 2. Double-Entry Ledger Invariants [Medium]. 3. Interest Scheduling and Statements [Medium].

### py-oop-case-robot | Case Study: Robot Controller | Expert | status: existing-thin
Existing: py-mission-executor (keep last).
Problems to add (3): 1. Hardware Abstraction with Fakes [Medium]. 2. Behavior Tree Executor [Hard]. 3. Safety Supervisor Layer [Medium].

### py-oop-case-game | Case Study: Game Engine Entities | Expert | status: existing-thin
Existing: py-ecs-engine (keep last).
Problems to add (3): 1. Component Composition [Medium]. 2. Event Queue Systems [Medium]. 3. Save/Load Game State [Medium].

### py-lld-elevator | Case Study: Elevator System | Advanced | status: new
Problems (4): 1. Single Elevator FSM [Easy]. 2. LOOK Scheduling [Medium]. 3. Multi-Car Dispatcher [Hard]. 4. Emergency Mode Extension [Medium].

### py-lld-splitwise | Case Study: Expense Sharing | Advanced | status: new
Problems (4): 1. Split Strategies [Easy]. 2. Group Balances [Medium]. 3. Debt Simplification [Hard]. 4. Multi-Currency Expenses [Medium].

### py-lld-vending-atm | Case Study: Vending Machine and ATM | Advanced | status: new
Problems (4): 1. Vending States [Easy]. 2. Change with Limited Coins [Medium]. 3. ATM Cash Dispenser Chain [Medium]. 4. ATM Session Security Rules [Hard].

### py-lld-booking | Case Study: Movie and Hotel Booking | Expert | status: new
Problems (5): 1. Seat Map Booking [Easy]. 2. Holds with Expiry [Medium]. 3. Concurrent Booking with Locks [Hard]. 4. Room Availability by Date Ranges [Medium]. 5. Cancellation and Refund Policies [Medium].

### py-lld-infra | Case Study: Rate Limiter, Logger and Cache | Expert | status: new
Problems (5): 1. Token Bucket [Easy]. 2. Sliding Window Log per Key [Medium]. 3. Logging Framework with Handlers [Medium]. 4. LRU/LFU Cache with TTL [Hard]. 5. Pub/Sub Message Broker [Hard].

### py-lld-marketplace | Case Study: E-commerce Cart, Orders and Inventory | Expert | status: new
Problems (5): 1. Cart and Pricing Rules [Easy]. 2. Coupons and Promotions Engine [Medium]. 3. Inventory Reservation [Medium]. 4. Order State Machine [Medium]. 5. Food Delivery Assignment [Hard]: match orders to couriers.

## Module 16: Packaging, Tooling and CLI

### py-cli-apps | Command-Line Applications | Intermediate | status: existing-thin
Existing: py-telemetry-cli.
Problems to add (4):
2. argparse Subcommands [Easy].
3. Config Precedence: Defaults < File < Env < Flags [Medium].
4. Exit Codes and stderr Discipline [Easy].
5. Interactive REPL Tool with cmd [Medium].

### py-project-tooling | Project Tooling: Linters, Formatters, Type Checkers, CI | Intermediate | status: new
Summary: The modern Python toolchain.
Lesson must cover: ruff/black/mypy/pyright concepts, pre-commit, pytest config, CI pipelines, semantic versioning, changelogs.
Problems (4):
1. Semantic Version Bumper [Easy].
2. Conventional Commits to Changelog [Medium].
3. CI Matrix Expander [Medium]: expand a YAML-like matrix spec.
4. Import Sorter [Medium]: isort-like grouping.

### py-config-architecture | Configuration, Logging and App Architecture | Advanced | status: new
Summary: Structuring real applications.
Lesson must cover: 12-factor config, env vars, settings objects, secrets handling, logging config dicts, app factories, plugin architectures.
Problems (4):
1. Env-Based Settings Loader [Easy].
2. dictConfig Logging Setup [Medium].
3. Feature Flags with Rollout Percentages [Medium].
4. Plugin Architecture with Hooks [Hard].

### py-packaging-distribution | Building and Publishing Packages | Advanced | status: new
Summary: From code to installable package.
Lesson must cover: pyproject, build backends, wheels vs sdists, versioning, entry points, `importlib.metadata`, private indexes.
Problems (4):
1. Read Package Metadata [Easy].
2. Entry Point Registry [Medium].
3. Version Constraint Satisfier [Medium].
4. Build Manifest Validator [Medium].

## Module 17: Web and Backend Engineering

All problems run in-process: test clients, `httpx.MockTransport`, or `socket.socketpair()`.

### py-http-requests | HTTP, REST and requests | Intermediate | status: existing-thin
Summary: HTTP from first principles and as a client.
Existing: py-resilient-fleet-client.
Lesson must cover: request/response anatomy, methods and idempotency, status codes, headers, cookies, caching headers, REST vs RPC, content negotiation, httpx clients with mock transports.
Problems to add (4):
2. Raw HTTP Request Parser [Easy].
3. Status Code Router [Easy]: pick correct codes for scenarios.
4. httpx Client against MockTransport [Medium]: retries and pagination.
5. Cache-Control and ETag Logic [Medium].

### py-web-http-server | HTTP Server from Scratch | Advanced | status: new
Summary: Build a tiny HTTP server with sockets.
Lesson must cover: socket lifecycle, parsing requests, routing, keep-alive, WSGI interface, ASGI concept.
Problems (5):
1. Request Line and Header Parser [Easy].
2. Response Serializer [Easy].
3. Mini Router with Path Params [Medium].
4. WSGI App Runner [Medium]: call a WSGI app with an environ built from raw requests.
5. Socketpair HTTP Exchange [Hard]: serve pipelined requests over `socketpair()`.

### py-sockets-networking | Sockets and Networking | Advanced | status: existing-thin
Existing: py-asyncio-kv-server.
Problems to add (3):
2. Length-Prefixed Framing [Medium].
3. UDP-Style Datagram Reassembly [Medium].
4. selectors-Based Echo over socketpairs [Hard].

### py-flask-django | Flask and Django Overview | Intermediate | status: existing-thin
Summary: Comparing web frameworks (overview topic).
Existing: py-flask-maintenance-log.
Problems to add (3):
2. Same Endpoint in Flask and Django [Medium].
3. Request Lifecycle Tracing [Medium].
4. Choose the Framework [Easy]: scenario classifier with rationale codes.

### py-flask | Flask in Depth | Intermediate | status: new
Summary: Building web apps with Flask.
Lesson must cover: routing, request/response, blueprints, app factory, Jinja templates, sessions, error handlers, `test_client`, config.
Problems (6):
1. Hello Routes and Query Params [Easy].
2. JSON CRUD API for Todos [Medium].
3. Blueprints and App Factory [Medium].
4. Jinja Templates with Escaping [Medium].
5. Sessions and Flash Messages [Medium].
6. Error Handlers and Validation [Medium].

### py-fastapi | FastAPI | Advanced | status: existing-thin
Existing: py-fleet-mission-api.
Lesson must cover: path/query/body params, Pydantic models, response models, status codes, dependencies, routers, TestClient.
Problems to add (4):
2. Typed CRUD with Response Models [Easy].
3. Dependency Injection for DB Sessions [Medium].
4. Pagination and Filtering [Medium].
5. Error Handling and Custom Exceptions [Medium].

### py-fastapi-advanced | FastAPI Advanced | Expert | status: new
Summary: Production FastAPI.
Lesson must cover: async endpoints, background tasks, middleware, lifespan events, OpenAPI customization, security dependencies, websockets.
Problems (5):
1. Middleware Request IDs and Timing [Medium].
2. Background Tasks [Medium].
3. OAuth2 Password Flow with JWT (local) [Hard].
4. Lifespan Resources [Medium].
5. OpenAPI Schema Assertions [Medium].

### py-sql-fundamentals | SQL from Zero | Intermediate | status: new
Summary: Relational databases with sqlite3.
Lesson must cover: tables, keys, SELECT/WHERE/ORDER, JOINs, GROUP BY/HAVING, subqueries, window functions, indexes and EXPLAIN, transactions and isolation, normalization (1NF–3NF).
Problems (6):
1. Basic Queries [Easy].
2. Joins Across Three Tables [Medium].
3. Aggregation with HAVING [Medium].
4. Window Functions: Running Totals and Ranks [Hard].
5. Index Choice with EXPLAIN QUERY PLAN [Medium].
6. Transactions and Rollback [Medium].

### py-databases | Databases: sqlite3, SQL and SQLAlchemy | Advanced | status: existing-thin
Summary: Database access from Python (DB-API, parameters, connection management).
Existing: py-fleet-sql-repository.
Problems to add (3):
2. Parameterized Queries vs Injection [Easy].
3. Connection and Transaction Context Managers [Medium].
4. Schema Normalization Exercise [Medium]: split a denormalized table, verify queries.

### py-sqlalchemy | SQLAlchemy 2.0 ORM | Advanced | status: new
Summary: Modern ORM usage.
Lesson must cover: engine/session, declarative mapping, relationships, `select()` API, eager vs lazy loading and N+1, migrations concepts (Alembic-style versioning), unit of work.
Problems (6):
1. Declarative Models and CRUD [Easy].
2. One-to-Many and Many-to-Many [Medium].
3. 2.0-Style Queries with Joins [Medium].
4. Fix the N+1 Query [Hard]: count SQL statements.
5. Hand-Rolled Migration Runner [Medium].
6. Repository + Unit of Work [Hard].

### py-web-auth | Authentication and Authorization | Advanced | status: new
Summary: Who are you and what may you do?
Lesson must cover: password hashing (hashlib.scrypt/pbkdf2), sessions vs tokens, JWT structure and signing (HMAC by hand), OAuth2 flows, RBAC/ABAC, refresh tokens.
Problems (5):
1. Password Hashing and Verify [Easy].
2. HMAC-Signed Tokens (JWT by Hand) [Medium].
3. Session Auth in Flask [Medium].
4. Role-Based Access Control [Medium].
5. OAuth2 Authorization Code Flow Simulator [Hard].

### py-web-security | Web Security and OWASP Top 10 | Advanced | status: new
Summary: Building secure web apps.
Lesson must cover: injection, XSS, CSRF, broken access control (IDOR), SSRF, security headers, rate limiting, input validation, secrets.
Problems (5):
1. Fix SQL Injection [Easy].
2. Escape for XSS Contexts [Medium].
3. CSRF Token Middleware [Medium].
4. IDOR Fix in an API [Medium].
5. SSRF URL Validator [Hard].

### py-django | Django in Depth | Advanced | status: new
Summary: Full-stack framework.
Lesson must cover: project/apps, models and ORM, migrations, admin, views (FBV/CBV), URL routing, templates, forms, auth, test Client (in-memory SQLite settings configured in-file).
Problems (6):
1. Models and QuerySets [Easy].
2. Function Views and URL Routing [Medium].
3. ModelForms and Validation [Medium].
4. Class-Based Views [Medium].
5. Auth and Permissions [Medium].
6. ORM Optimization select/prefetch_related [Hard].

### py-django-api | Building APIs with Django | Expert | status: new
Summary: JSON APIs in Django (DRF concepts implemented with JsonResponse).
Lesson must cover: serializers concept, viewsets, pagination, filtering, throttling, versioning.
Problems (4):
1. JSON CRUD Endpoints [Medium].
2. Serializer Validation Layer [Medium].
3. Cursor Pagination [Hard].
4. Throttling Middleware [Medium].

### py-web-realtime | WebSockets and Server-Sent Events | Advanced | status: new
Summary: Real-time communication.
Lesson must cover: polling vs SSE vs WebSockets, FastAPI websockets with TestClient, rooms/broadcast, heartbeats, SSE format.
Problems (4):
1. Echo WebSocket [Easy].
2. Chat Rooms with Broadcast [Medium].
3. SSE Event Stream Formatter [Medium].
4. Presence and Heartbeat Timeouts [Hard].

### py-web-caching-queues | Caching, Task Queues and Idempotency | Expert | status: new
Summary: Scaling backends.
Lesson must cover: cache-aside, write-through, TTL and invalidation, Redis concepts, task queues (Celery concepts) with retries, idempotency keys, pagination strategies, outbox pattern.
Problems (5):
1. Cache-Aside with TTL [Easy].
2. Idempotency-Key Middleware [Medium].
3. In-Process Task Queue with Retries and DLQ [Hard].
4. Keyset vs Offset Pagination [Medium].
5. Transactional Outbox [Hard].

### py-api-design-testing | API Design and Testing | Advanced | status: new
Summary: Designing and testing APIs.
Lesson must cover: resource modeling, versioning, error models (RFC 7807), contract tests, pytest with test clients, load-testing concepts.
Problems (4):
1. Error Model Standardization [Easy].
2. Versioned Routes [Medium].
3. Contract Test against Schema [Medium].
4. Load Test Result Analyzer [Medium]: percentiles from latency logs.

### py-deployment-ops | Deployment and Operations | Advanced | status: new
Summary: Shipping and running services.
Lesson must cover: 12-factor, gunicorn/uvicorn workers, reverse proxies, Docker basics (Dockerfile layers), CI/CD pipelines, health checks, observability (logs, metrics, traces).
Problems (4):
1. Health Check Endpoints [Easy].
2. Dockerfile Linter [Medium].
3. Metrics Counter and Histogram Exporter [Medium]: Prometheus text format.
4. Trace Span Tree Builder [Hard].

### py-web-projects | Backend Projects | Expert | status: new
Summary: Capstone services built end to end.
Lesson must cover: requirements, data model, endpoints, auth, tests — walkthrough of each project.
Problems (5):
1. URL Shortener [Medium]: base62 ids, redirects, stats.
2. Blog with Auth [Hard].
3. Shop REST API with Orders [Hard].
4. Real-Time Chat Backend [Hard].
5. Job Board with Search and Pagination [Hard].

## Module 18: Data Engineering and Automation

### py-data-etl | ETL Pipelines | Advanced | status: new
Summary: Extract, transform, load.
Lesson must cover: pipeline stages, idempotency, incremental loads, schema evolution, data quality checks, columnar formats (Parquet concepts), SQL analytics.
Problems (5):
1. CSV to SQLite Loader [Easy].
2. Incremental Load with Watermarks [Medium].
3. Deduplication and SCD Type 2 [Hard].
4. Data Quality Rules Engine [Medium].
5. Chunked Processing of Large Files [Medium].

### py-data-validation | Data Validation and Contracts | Intermediate | status: new
Summary: Trusting your data.
Lesson must cover: schemas, pydantic for records, pandas validation, anomaly checks, contracts between producers and consumers.
Problems (4):
1. Row Validator with Error Report [Easy].
2. Schema Drift Detector [Medium].
3. Statistical Anomaly Flags [Medium].
4. Contract Versioning Compatibility [Medium].

### py-automation-files | Automating Files and Reports | Intermediate | status: new
Summary: Everyday automation scripts.
Lesson must cover: batch renaming, archiving (zipfile/tarfile), templated reports (text/HTML/Markdown), email composition (`email` package, no sending).
Problems (4):
1. Batch Renamer with Patterns [Easy].
2. Zip Archive Builder and Verifier [Medium].
3. HTML Report Generator [Medium].
4. MIME Email Composer [Medium].

### py-web-scraping | Web Scraping and Parsing (offline) | Intermediate | status: new
Summary: Extracting data from HTML/XML.
Lesson must cover: html.parser, xml.etree, CSS-selector ideas, robots/ethics, pagination via mock transports.
Problems (4):
1. Link Extractor [Easy].
2. Table to CSV [Medium].
3. Paginated Scrape via MockTransport [Medium].
4. XML Feed Parser [Medium].

### py-api-integration | Working with APIs | Intermediate | status: new
Summary: Consuming third-party APIs robustly.
Lesson must cover: auth headers, rate limits, retries, pagination styles, webhooks (signature verification).
Problems (4):
1. Paginated API Collector [Easy].
2. Rate-Limit-Aware Client [Medium].
3. Webhook Signature Verifier [Medium].
4. Sync Two Systems with Conflict Resolution [Hard].

### py-scheduling-jobs | Scheduling and Job Automation | Intermediate | status: new
Summary: Running tasks on time.
Lesson must cover: cron syntax, sched module, retries, idempotent jobs, locking.
Problems (4):
1. Cron Expression Next-Run Calculator [Medium].
2. Job Scheduler with sched [Medium].
3. Lockfile-Based Single Instance [Medium].
4. Dependency-Aware Job Runner [Hard].

## Module 19: Scientific Python

### py-numpy-basics | NumPy Fundamentals | Intermediate | status: existing-thin
Existing: py-image-array-ops.
Problems to add (4):
2. Array Creation and Dtypes [Easy].
3. Boolean Masking and Fancy Indexing [Easy].
4. Axis Reductions [Medium].
5. Views vs Copies [Medium].

### py-numpy-advanced | NumPy: Broadcasting, Vectorization, Linear Algebra | Advanced | status: existing-thin
Existing: py-vectorized-geometry.
Problems to add (4):
2. Pairwise Distance Matrix via Broadcasting [Medium].
3. einsum Tensor Contractions [Medium].
4. Stride Tricks Sliding Windows [Hard].
5. Vectorize a Simulation Loop [Hard].

### py-numpy-linalg-random | NumPy Linear Algebra and Random | Advanced | status: new
Lesson must cover: solve, lstsq, eig, svd, norms, conditioning, `default_rng`, distributions, reproducibility.
Problems (5):
1. Solve and Check Residual [Easy].
2. Least Squares Polynomial Fit [Medium].
3. SVD Image Compression Error [Medium].
4. Random Walk Statistics with Generator [Medium].
5. Markov Chain Stationary Distribution [Medium].

### py-pandas | Pandas | Intermediate | status: existing-thin
Existing: py-telemetry-analytics.
Lesson must cover: Series/DataFrame, indexing (loc/iloc), missing data, dtypes, apply vs vectorized.
Problems to add (4):
2. Load, Filter, Sort [Easy].
3. Missing Data Strategies [Medium].
4. loc/iloc and Boolean Indexing [Easy].
5. String and Category Columns [Medium].

### py-pandas-advanced | pandas: GroupBy, Merge and Reshape | Advanced | status: new
Lesson must cover: groupby-agg/transform/filter, merges and join types, pivot/melt/stack, MultiIndex, performance.
Problems (6):
1. GroupBy Aggregations [Easy].
2. transform for Group-Normalization [Medium].
3. Merge with Validation and Indicator [Medium].
4. Pivot and Melt [Medium].
5. MultiIndex Slicing [Hard].
6. Vectorize an apply for Speed [Medium].

### py-pandas-timeseries | Time Series with pandas | Advanced | status: new
Lesson must cover: DatetimeIndex, resample, rolling/expanding, shifting/lags, time zones, gaps and interpolation.
Problems (5):
1. Resample to Hourly [Easy].
2. Rolling Statistics and Anomalies [Medium].
3. Lag Features [Medium].
4. Gap Filling and Interpolation [Medium].
5. As-Of Merge of Sensors [Hard].

### py-matplotlib | Data Visualization with Matplotlib | Intermediate | status: existing-thin
Existing: py-plot-builder.
Lesson must cover: Figure/Axes model, line/scatter/bar/hist, subplots, labels and legends, styles, saving; judged by inspecting artists.
Problems to add (4):
2. Labeled Line Plot [Easy].
3. Subplots Grid [Medium].
4. Histogram with Bins Choice [Medium].
5. Engineering Report Figure [Medium]: twin axes, annotations.

### py-statistics-probability | Probability and Statistics with SciPy | Advanced | status: new
Lesson must cover: distributions (pdf/cdf/ppf), sampling, CLT, confidence intervals, bootstrap, MLE.
Problems (5):
1. Distribution Queries [Easy].
2. Confidence Interval for Mean [Medium].
3. Bootstrap CI [Medium].
4. MLE Fit of Exponential/Normal [Medium].
5. Simulate the CLT [Medium].

### py-hypothesis-testing | Hypothesis Testing and A/B Analysis | Advanced | status: new
Lesson must cover: null/alternative, p-values, t-tests, chi-square, Mann–Whitney, multiple testing, power and sample size.
Problems (5):
1. One- and Two-Sample t-tests [Easy].
2. Chi-Square Independence [Medium].
3. A/B Conversion Test [Medium].
4. Bonferroni and Benjamini–Hochberg [Medium].
5. Sample Size for Power [Hard].

### py-scipy | SciPy for Scientific Computing | Advanced | status: existing-thin
Existing: py-scipy-toolkit.
Problems to add (4):
2. scipy.optimize Root and Minimize [Medium].
3. scipy.integrate solve_ivp [Medium].
4. scipy.interpolate Splines [Medium].
5. scipy.sparse Linear Systems [Medium].

### py-regression-analysis | Regression and Statistical Modeling | Advanced | status: new
Lesson must cover: OLS, diagnostics (residuals, R²), multicollinearity, logistic regression interpretation, regularization effects.
Problems (4):
1. OLS with Normal Equations [Easy].
2. Residual Diagnostics [Medium].
3. Multicollinearity via VIF [Medium].
4. Logistic Regression Odds Ratios [Medium].

## Module 20: Machine Learning

### py-sklearn | Machine Learning with scikit-learn | Advanced | status: existing-thin
Existing: py-terrain-classifier.
Lesson must cover: estimator API, fit/predict, train/test split, baseline models.
Problems to add (4):
2. First Classifier with Baseline [Easy].
3. Regression with Metrics [Easy].
4. Preprocessing: Scaling and Encoding [Medium].
5. Pipeline + ColumnTransformer [Medium].

### py-sklearn-model-selection | Model Selection and Evaluation | Advanced | status: new
Lesson must cover: cross-validation strategies (stratified, group, time series), GridSearch/RandomizedSearch, metrics (precision/recall/F1/ROC-AUC/PR), calibration, data leakage.
Problems (6):
1. K-Fold vs Stratified [Easy].
2. Grid Search with Pipelines [Medium].
3. Choose the Right Metric for Imbalance [Medium].
4. Find the Leakage [Hard].
5. Time-Series CV [Medium].
6. Threshold Tuning on PR Curve [Medium].

### py-sklearn-models | The Model Zoo | Advanced | status: new
Lesson must cover: linear models, kNN, Naive Bayes, SVMs, trees, ensembles (RF, GBM), clustering, dimensionality reduction; when to use which.
Problems (6):
1. Regularized Linear Models [Easy].
2. SVM with Kernels [Medium].
3. Random Forest Feature Importance [Medium].
4. Gradient Boosting Tuning [Medium].
5. Clustering with KMeans and DBSCAN [Medium].
6. PCA + Classifier Pipeline [Medium].

### py-ml-from-scratch | ML Algorithms from Scratch | Expert | status: existing-thin
Summary: Linear models and core algorithms in NumPy.
Existing: py-numpy-learners.
Problems to add (4):
2. Linear Regression by Gradient Descent [Easy].
3. Logistic Regression with Regularization [Medium].
4. kNN Classifier [Easy].
5. Gaussian Naive Bayes [Medium].

### py-ml-scratch-trees | Trees and Ensembles from Scratch | Expert | status: new
Problems (5):
1. Gini and Entropy Splits [Easy].
2. Decision Tree Classifier [Hard].
3. Random Forest with Bootstrap [Hard].
4. Gradient Boosting Regression [Hard].
5. AdaBoost Stumps [Medium].

### py-ml-scratch-unsupervised | Unsupervised Learning from Scratch | Expert | status: new
Problems (5):
1. K-Means with k-means++ [Medium].
2. PCA via Eigendecomposition [Medium].
3. GMM with EM [Hard].
4. Hierarchical Clustering [Medium].
5. Linear SVM via Subgradient [Hard].

### py-feature-engineering | Feature Engineering | Advanced | status: new
Lesson must cover: numeric transforms, encodings (one-hot, target with CV), date features, text features, interactions, feature selection.
Problems (4):
1. Date/Time Features [Easy].
2. Target Encoding without Leakage [Hard].
3. Feature Selection by Mutual Information [Medium].
4. Custom sklearn Transformer [Medium].

### py-recommender-systems | Recommender Systems | Expert | status: new
Lesson must cover: popularity baselines, collaborative filtering, matrix factorization, implicit feedback, evaluation (precision@k, NDCG).
Problems (4):
1. Popularity Baseline and Precision@k [Easy].
2. Item-Item Collaborative Filtering [Medium].
3. Matrix Factorization with ALS [Hard].
4. NDCG Evaluation [Medium].

### py-time-series-forecasting | Time Series Forecasting | Advanced | status: new
Lesson must cover: stationarity, decomposition, naive/seasonal baselines, exponential smoothing, AR models, backtesting.
Problems (4):
1. Naive and Seasonal Naive Baselines [Easy].
2. Exponential Smoothing (Holt) [Medium].
3. AR Model by Least Squares [Medium].
4. Rolling-Origin Backtest [Medium].

## Module 21: Deep Learning with PyTorch

### py-pytorch-tensors | PyTorch Tensors and Autograd | Advanced | status: existing-thin
Existing: py-autograd-workbench.
Problems to add (4):
2. Tensor Ops and Broadcasting [Easy].
3. Autograd Gradients Check [Medium].
4. Custom autograd.Function [Hard].
5. Micrograd: Scalar Autograd Engine [Hard].

### py-pytorch-training | PyTorch Models and Training Loops | Expert | status: existing-thin
Existing: py-train-imu-classifier.
Problems to add (4):
2. nn.Module MLP [Easy].
3. Dataset and DataLoader [Medium].
4. Train/Eval Loop with Early Stopping [Medium].
5. Checkpoint Save/Load [Medium].

### py-pytorch-optim | Optimization and Regularization | Expert | status: new
Lesson must cover: SGD/momentum/Adam from scratch, learning-rate schedules, initialization, batch norm, dropout, weight decay, gradient clipping.
Problems (5):
1. SGD with Momentum from Scratch [Medium].
2. Adam from Scratch [Medium].
3. Initialization Effects [Medium].
4. BatchNorm Forward/Backward [Hard].
5. LR Schedule Implementations [Easy].

### py-cnn | Convolutional Neural Networks | Expert | status: new
Lesson must cover: convolution math, padding/stride, pooling, receptive field, CNN architecture patterns, conv from scratch.
Problems (5):
1. Conv2D Output Shapes [Easy].
2. Conv2D from Scratch vs torch [Medium].
3. Tiny CNN on Synthetic Shapes [Medium].
4. Receptive Field Calculator [Medium].
5. Residual Block [Hard].

### py-rnn-sequence | RNNs and Sequence Models | Expert | status: new
Lesson must cover: RNN cell, BPTT, vanishing gradients, LSTM/GRU gates, packing, seq2seq.
Problems (5):
1. RNN Cell Forward [Easy].
2. LSTM Cell from Scratch [Medium].
3. Sequence Classification with GRU [Medium].
4. Next-Character Model [Hard].
5. Padding and Packing [Medium].

### py-deep-learning-arch | Deep Learning Architectures: CNN, RNN, Transformer | Research | status: existing-thin
Summary: Attention and architecture survey.
Existing: py-attention-from-scratch.
Problems to add (3):
2. Multi-Head Attention [Hard].
3. Positional Encodings [Medium].
4. Causal Masking [Medium].

### py-transformer-from-scratch | Transformers from Scratch | Research | status: new
Lesson must cover: transformer block, layer norm, residuals, decoder-only LM, training tiny GPT, sampling strategies.
Problems (5):
1. LayerNorm from Scratch [Easy].
2. Transformer Block Forward [Hard].
3. Tiny Decoder-Only LM Training [Hard].
4. Greedy, Top-k and Temperature Sampling [Medium].
5. KV Cache for Generation [Hard].

### py-dl-practical | Practical Deep Learning | Expert | status: new
Lesson must cover: debugging training (overfit one batch), mixed precision concepts, transfer learning, augmentation, experiment hygiene.
Problems (4):
1. Overfit One Batch Check [Easy].
2. Find the Training Bug [Medium].
3. Transfer Learning with Frozen Backbone [Medium].
4. Learning Rate Finder [Medium].

## Module 22: NLP and Computer Vision

### py-nlp-text | Text Processing and Classic NLP | Advanced | status: new
Lesson must cover: tokenization, normalization, n-grams, TF-IDF, BM25, Naive Bayes text classification, edit distance.
Problems (5):
1. Tokenizer and Normalizer [Easy].
2. TF-IDF from Scratch [Medium].
3. BM25 Ranking [Medium].
4. Spam Classifier [Medium].
5. N-gram Language Model with Smoothing [Hard].

### py-nlp-neural | Neural NLP: Embeddings and Sequence Models | Expert | status: new
Lesson must cover: word2vec (skip-gram), subword tokenization (BPE), embedding layers, text classification with neural nets.
Problems (5):
1. BPE Tokenizer Training [Hard].
2. Skip-Gram Pairs and Negative Sampling [Medium].
3. Embedding Similarity Queries [Easy].
4. Text Classifier with EmbeddingBag [Medium].
5. Named Entity Tagging with BIO [Hard].

### py-opencv | Computer Vision with OpenCV | Advanced | status: existing-thin
Existing: py-cone-detector.
Problems to add (4):
2. Color Spaces and Thresholding [Easy].
3. Edges and Contours [Medium].
4. Geometric Transforms and Homography [Medium].
5. Feature Matching (ORB) [Medium].

### py-cv-deep | Deep Learning for Vision | Expert | status: new
Lesson must cover: augmentation, CNN pipelines, IoU and NMS, detection basics, segmentation metrics.
Problems (5):
1. Augmentation Pipeline [Easy].
2. IoU Calculator [Easy].
3. Non-Maximum Suppression [Medium].
4. mAP Evaluation [Hard].
5. Segmentation Dice/IoU [Medium].

### py-image-processing-classic | Classical Image Processing with NumPy | Advanced | status: new
Lesson must cover: convolution kernels, histograms, equalization, morphology, connected components.
Problems (4):
1. Kernel Convolution [Easy].
2. Histogram Equalization [Medium].
3. Connected Components Labeling [Medium].
4. Otsu Thresholding [Medium].

## Module 23: Applied ML Engineering

### py-mlops-reproducibility | Reproducibility and Experiment Tracking | Advanced | status: new
Lesson must cover: seeds, data versioning (hashing), config-driven experiments, tracking runs, model registries.
Problems (4):
1. Seed Everything [Easy].
2. Dataset Fingerprinting [Medium].
3. Experiment Tracker [Medium].
4. Model Registry with Stages [Medium].

### py-model-serving | Model Serving | Expert | status: new
Lesson must cover: serialization (joblib, torch.save, ONNX concepts), FastAPI inference service, batching, input validation, latency.
Problems (4):
1. Save/Load Pipeline [Easy].
2. FastAPI Predict Endpoint [Medium].
3. Micro-Batching Server [Hard].
4. Input Schema Validation and Versioning [Medium].

### py-ml-monitoring | Monitoring and Data Drift | Expert | status: new
Lesson must cover: drift metrics (PSI, KS), performance decay, alerting, shadow deployments, A/B for models.
Problems (4):
1. Population Stability Index [Medium].
2. KS Drift Test per Feature [Medium].
3. Rolling Performance Alerts [Medium].
4. Shadow Model Comparison [Medium].

### py-ml-system-design | ML System Design | Expert | status: new
Lesson must cover: problem framing, data pipelines, offline/online features, evaluation design, feedback loops, case studies.
Problems (4):
1. Metric Selection Scenarios [Easy].
2. Feature Store Point-in-Time Join [Hard].
3. Offline Evaluation Harness [Medium].
4. Fairness Metrics Report [Medium].

## Module 24: LLM Application Engineering (offline)

No network: embeddings come from deterministic local models (TF-IDF/SVD, hashing, small torch encoders); an LLM is replaced by a deterministic stub where needed.

### py-llm-foundations | LLM Concepts and Tokenization | Advanced | status: new
Lesson must cover: tokens, context windows, sampling, prompting patterns, cost estimation, structured outputs.
Problems (4):
1. Token Budget Calculator [Easy].
2. Prompt Template Engine [Medium].
3. Structured Output Validator with Repair [Medium].
4. Chunking Long Documents by Tokens [Medium].

### py-embeddings-vector-search | Embeddings and Vector Search | Advanced | status: new
Lesson must cover: embeddings, cosine similarity, exact vs approximate search, IVF, HNSW idea, product quantization.
Problems (5):
1. Cosine Top-k [Easy].
2. Local Embeddings via TF-IDF + SVD [Medium].
3. IVF Index [Hard].
4. HNSW-Lite Graph Search [Hard].
5. Product Quantization [Hard].

### py-rag-pipelines | Retrieval-Augmented Generation | Expert | status: new
Lesson must cover: ingestion, chunking strategies, hybrid search (BM25 + vectors), reranking, context assembly, citations.
Problems (5):
1. Chunker with Overlap [Easy].
2. Hybrid Retrieval with Reciprocal Rank Fusion [Medium].
3. Context Assembly under Token Budget [Medium].
4. Citation-Grounded Answer Stub [Medium].
5. End-to-End RAG over a Document Set [Hard].

### py-llm-evaluation | Evaluating LLM Systems | Expert | status: new
Lesson must cover: retrieval metrics (recall@k, MRR), answer metrics (exact match, F1), LLM-as-judge concepts, regression suites.
Problems (4):
1. Recall@k and MRR [Easy].
2. Token-F1 and Exact Match [Easy].
3. Golden-Set Regression Runner [Medium].
4. Pairwise Preference Aggregation (Bradley–Terry) [Hard].

### py-llm-agents-tools | Tool Use and Agent Loops | Expert | status: new
Lesson must cover: function calling schemas, agent loop, tool routing, guardrails, memory (with stubbed model).
Problems (4):
1. Tool Schema Validator [Easy].
2. Agent Loop with Stub Model [Medium].
3. Guardrail Filters [Medium].
4. Conversation Memory Summarizer [Medium].

## Module 25: Engineering and Scientific Computing (mechanical, civil, electrical)

### py-num-methods | Numerical Methods I: Roots, Interpolation, Integration | Advanced | status: new
Lesson must cover: error and stability, bisection/Newton/secant, interpolation (Lagrange, splines), finite differences, trapezoid/Simpson/Gauss quadrature.
Problems (5):
1. Bisection and Newton [Easy].
2. Lagrange vs Spline Interpolation [Medium].
3. Numerical Differentiation Error [Medium].
4. Composite Simpson and Romberg [Medium].
5. Gauss Quadrature [Hard].

### py-num-linear-algebra | Numerical Linear Algebra | Advanced | status: new
Lesson must cover: Gaussian elimination, LU/Cholesky/QR, iterative solvers, conditioning, eigenproblems (power iteration).
Problems (5):
1. LU with Partial Pivoting [Medium].
2. Jacobi and Gauss–Seidel [Medium].
3. Conjugate Gradient [Hard].
4. Condition Number Experiments [Medium].
5. Power Iteration for Natural Frequencies [Medium].

### py-odes-simulation | ODEs and Simulation | Advanced | status: new
Lesson must cover: Euler, RK4, solve_ivp adaptive, stiffness, systems of ODEs, vibrations (mass–spring–damper), event detection.
Problems (5):
1. Euler vs RK4 [Easy].
2. Mass–Spring–Damper Response [Medium].
3. Pendulum with solve_ivp and Events [Medium].
4. Stiff Chemical Kinetics [Hard].
5. Two-DOF Vibration Modes [Hard].

### py-optimization | Optimization for Engineers | Advanced | status: new
Lesson must cover: gradient descent, scipy.optimize (minimize, constraints, linprog), least squares, curve fitting.
Problems (5):
1. Curve Fit Material Data [Easy].
2. Constrained Beam Design [Medium].
3. Linear Programming Production Plan [Medium].
4. Nonlinear Least Squares Calibration [Medium].
5. Gradient Descent from Scratch [Medium].

### py-signal-processing | Signal Processing | Advanced | status: new
Lesson must cover: sampling and aliasing, FFT, spectra, windowing, filters (scipy.signal butter/filtfilt), noise, sensor data.
Problems (5):
1. FFT Dominant Frequency [Easy].
2. Aliasing Predictor [Medium].
3. Butterworth Low-Pass [Medium].
4. Spectrogram Peak Tracking [Hard].
5. Vibration Fault Detection [Medium].

### py-mech-statics-truss | Statics and Truss Analysis | Advanced | status: new
Lesson must cover: equilibrium, free-body diagrams in code, method of joints, matrix stiffness method for trusses, support reactions.
Problems (5):
1. Resultant Force and Moment [Easy].
2. Support Reactions of a Beam [Easy].
3. Method of Joints [Medium].
4. Matrix Stiffness 2D Truss [Hard].
5. Truss Member Stress Check [Medium].

### py-mech-beams-fem | Beams and Finite Elements | Expert | status: new
Lesson must cover: shear/moment diagrams, beam deflection (Euler–Bernoulli), 1D bar FEM, beam elements, 2D CST elements.
Problems (5):
1. Shear and Moment Diagrams [Medium].
2. Beam Deflection by Integration [Medium].
3. 1D Bar FEM [Medium].
4. Beam Element FEM [Hard].
5. 2D Plane Stress CST [Expert].

### py-heat-fluids | Heat Transfer and Fluids Computation | Expert | status: new
Lesson must cover: 1D/2D heat equation (explicit/implicit, stability), steady conduction, pipe flow (Darcy–Weisbach, Colebrook), simple CFD ideas.
Problems (5):
1. Steady 1D Conduction [Easy].
2. Explicit Heat Equation with CFL [Medium].
3. Crank–Nicolson [Hard].
4. Pipe Network Pressure Drop [Medium].
5. 2D Laplace Solver [Medium].

### py-electrical-circuits | Electrical Circuit Computation | Advanced | status: new
Lesson must cover: Ohm/Kirchhoff, nodal analysis (MNA), AC phasors with complex numbers, RC/RLC transients, power.
Problems (5):
1. Series/Parallel Resistance Reducer [Easy].
2. Nodal Analysis Solver [Medium].
3. AC Phasor Circuit [Medium].
4. RC/RLC Transient Simulation [Medium].
5. Three-Phase Power Calculations [Medium].

### py-control-systems | Control Systems | Advanced | status: new
Lesson must cover: transfer functions, step response, PID tuning, stability (poles), Bode, state space.
Problems (4):
1. Step Response of First/Second Order [Easy].
2. PID Simulation and Tuning [Medium].
3. Pole Stability Checker [Medium].
4. Bode Magnitude/Phase [Medium].

### py-units-engineering-data | Units and Engineering Data | Intermediate | status: new
Lesson must cover: unit systems, dimensional analysis (hand-built Quantity class since pint is unavailable), uncertainty propagation, engineering CSV pipelines, report plots.
Problems (4):
1. Quantity Class with Dimensions [Medium].
2. Unit Conversion Parser [Medium].
3. Uncertainty Propagation [Medium].
4. Test-Rig CSV to Summary Report [Medium].

### py-cad-geometry | CAD and Geometry Scripting | Advanced | status: new
Lesson must cover: parametric geometry, 2D/3D transforms, polygons, meshes and STL files, CadQuery/FreeCAD concepts (described, not run).
Problems (5):
1. Parametric Bolt-Hole Pattern [Easy].
2. 3D Transform Chains [Medium].
3. STL Writer and Reader [Medium].
4. Mesh Volume and Surface Area [Medium].
5. Polygon Offset/Buffer (simple convex) [Hard].

### py-civil-structures | Civil Engineering Computations | Advanced | status: new
Lesson must cover: load combinations, frame analysis basics, soil bearing, hydrology (rational method), surveying calculations.
Problems (4):
1. Load Combination Envelope [Easy].
2. Traverse Closure and Area [Medium].
3. Rational Method Runoff [Easy].
4. Portal Frame by Stiffness Method [Hard].

## Module 26: Robotics with Python

### py-ros2 | Robotics with ROS 2 (rclpy) | Expert | status: existing-thin
Existing: py-safety-controller-node.
Problems to add (3):
2. Simulated Topic Graph [Medium].
3. Parameter Server Validation [Medium].
4. Action Client State Machine [Hard].

### py-robotics-math | Robotics Math: Transforms, Kinematics, Control | Research | status: existing-thin
Existing: py-robot-math-suite.
Problems to add (4):
2. Homogeneous Transform Chains [Easy].
3. Diff-Drive Odometry [Medium].
4. 2-Link IK [Medium].
5. Kalman Filter Tracking [Hard].

## Module 27: Software Engineering, System Design and Interviews

### py-system-design-basics | System Design Fundamentals | Expert | status: existing-thin
Existing: py-consistent-hash-ring.
Problems to add (4):
2. Back-of-Envelope Estimator [Easy].
3. Load Balancer Strategies [Medium].
4. Sharding and Rebalancing [Medium].
5. Replication Lag and Read-Your-Writes [Hard].

### py-system-design-components | System Design Building Blocks | Expert | status: new
Lesson must cover: caches, queues, databases (SQL vs NoSQL), consistency models, CAP, rate limiting, CDNs, idempotency.
Problems (5):
1. Bloom Filter [Medium].
2. Distributed Rate Limiter Simulation [Medium].
3. Vector Clocks [Hard].
4. Leader Election (Bully) Simulation [Medium].
5. Write-Ahead Log with Recovery [Hard].

### py-system-design-cases | System Design Case Studies | Expert | status: new
Lesson must cover: URL shortener, news feed, chat, ride sharing, search autocomplete — requirements, estimates, design, trade-offs.
Problems (4):
1. URL Shortener Core [Medium].
2. News Feed Fan-out on Write vs Read [Hard].
3. Geohash Nearby Drivers [Medium].
4. Autocomplete with Top-k per Prefix [Medium].

### py-software-craft | Software Craftsmanship | Intermediate | status: new
Lesson must cover: code review checklists, git workflows (branching, rebasing concepts), documentation, ADRs, reading large codebases.
Problems (4):
1. Diff Parser and Review Stats [Medium].
2. Three-Way Merge [Hard].
3. Commit Graph Queries [Medium].
4. Docstring Coverage Checker [Easy].

### py-interview-core | Python Interview Deep Dive I: Core | Advanced | status: existing-thin
Existing: py-lru-from-scratch.
Problems to add (3):
2. Implement a defaultdict [Medium].
3. Implement a Context-Managed Timer [Easy].
4. Implement functools.partial [Medium].

### py-interview-advanced | Python Interview Deep Dive II: Internals | Expert | status: existing-thin
Existing: py-declarative-models.
Problems to add (3):
2. Implement property [Medium].
3. Implement a Generator-Based Coroutine Scheduler [Hard].
4. Implement dataclass-lite Decorator [Hard].

### py-interview-behavioral-lld | Interview Strategy: LLD and Behavioural | Advanced | status: new
Lesson must cover: LLD interview script, STAR answers, clarifying requirements, trade-off talk.
Problems (4):
1. Requirements Clarifier [Easy]: classify functional vs non-functional from text items.
2. Design a Parking API in 30 Minutes [Medium].
3. Design an In-Memory File System [Hard].
4. Design a Key-Value Store with Transactions [Hard].
