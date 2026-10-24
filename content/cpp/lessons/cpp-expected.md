# std::expected, Error Codes and Assertions

Exceptions aren't the only, or always the best, error-handling tool. **`std::expected<T, E>`** (C++23) returns *either* a value *or* an error, explicitly in the type: callers can't forget that failure is possible, there's no hidden control flow, and it costs no more than returning a struct. This lesson compares the strategies (exceptions, `std::expected`, `std::optional`, `std::error_code`, assertions and `static_assert`) and teaches how to choose between them.

## 1. `std::expected<T, E>`

```cpp
#include <expected>
#include <charconv>

enum class ParseError { empty, not_a_number, out_of_range };

std::expected<int, ParseError> parse_port(std::string_view s) {
    if (s.empty()) return std::unexpected(ParseError::empty);
    int v;
    auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || p != s.data() + s.size()) return std::unexpected(ParseError::not_a_number);
    if (v < 1 || v > 65535) return std::unexpected(ParseError::out_of_range);
    return v;                                        // the success value converts implicitly
}

auto r = parse_port("8080");
if (r) std::cout << *r;                              // has_value(), operator*, value()
else  handle(r.error());                             // the error, typed
int port = parse_port(arg).value_or(80);
```

`value()` on an error throws `std::bad_expected_access<E>`, and `*r` on an error is undefined behaviour, just like `optional`.

### Monadic chaining

```cpp
std::expected<Config, std::string> load_config(const std::string& path);

auto port = read_file(path)                          // expected<std::string, std::string>
    .and_then(parse_json)                            // runs only on success; returns another expected
    .and_then(extract_port)
    .transform([](int p) { return p + 1000; })       // maps the value
    .transform_error([](std::string e) { return "config: " + e; });   // maps the error
```

The error short-circuits through the chain like an exception, but **visibly**, with no unwinding and no hidden control flow. Rust's `Result<T, E>` and `?` operator express the same idea.

## 2. The alternatives

| Mechanism | Communicates | Cost | Can be ignored? | Best for |
|---|---|---|---|---|
| exceptions | any failure, propagating through many layers | free if not thrown, slow if thrown | no (an uncaught one terminates) | rare failures, constructors, deep stacks |
| `std::expected<T, E>` | a value or a typed error | like returning a struct | harder (`[[nodiscard]]`) | expected failures: parsing, I/O, validation |
| `std::optional<T>` | a value or "nothing" (no reason) | small | harder | lookups, "not found" |
| `std::error_code` | an OS or library error (category + value) | small | yes (it's an out-parameter) | system calls, networking (`std::filesystem` and Asio overloads) |
| bool / int return codes | success or failure | none | **easily** | C interfaces |
| `assert` | a broken invariant: a **bug** | none in release | n/a | internal consistency checks |
| `static_assert` | a compile-time fact | none | no (it fails the build) | type sizes, trait requirements |

```cpp
std::error_code ec;
auto size = std::filesystem::file_size(path, ec);   // the non-throwing overload
if (ec) std::cerr << ec.message() << '\n';          // "No such file or directory"
```

## 3. Bugs vs errors

> [!KEY]
> Distinguish **errors** (the environment or input misbehaves: a missing file, a malformed packet, a disconnected sensor), which must be **handled**, from **bugs** (the program's own logic is wrong: an out-of-range index, a violated invariant), which must be **found and fixed**. Handle errors with `expected`, exceptions or codes. Detect bugs with `assert`, sanitizers and contracts, and fail fast, because continuing with corrupted state is worse.

```cpp
#include <cassert>
void set_wheel_speed(std::size_t wheel, double rpm) {
    assert(wheel < wheels_.size() && "wheel index out of range");   // a bug if violated
    wheels_[wheel].set(rpm);
}
static_assert(sizeof(Packet) == 32, "wire format must stay 32 bytes");
static_assert(std::is_trivially_copyable_v<Packet>);
```

C++26 adds **contracts** (`pre(...)`, `post(...)`, `contract_assert`) as language-level preconditions and postconditions with configurable checking.

## 4. Designing error types

- Use a small `enum class` for errors callers branch on, and wrap it in a struct when context is needed (`{code, line, message}`).
- Mark error-returning functions `[[nodiscard]]` so ignoring the result triggers a warning. (`std::expected` itself is `[[nodiscard]]` in practice.)
- At module boundaries, convert between strategies deliberately: the parser returns `expected`, and the top-level command handler turns errors into user messages or exceptions.
- Real-time control loops: preallocate, never throw, return status, and enter a **safe state** on failure.

## 5. Exam-ready answers

> [!EXAM]
> **Error-handling strategies.** C++ supports several mechanisms. Exceptions propagate failures automatically through the call stack with destructor-based cleanup, suitable for rare errors and constructors but with a slow throw path. `std::expected<T, E>` (C++23) holds either a value of type T or an error of type E, making failure explicit in the function's return type; it is inspected with `has_value`, `operator*`, `value` and `error`, and composed with the monadic operations `and_then`, `transform`, `or_else` and `transform_error`. `std::optional` represents an absent value without a reason, and `std::error_code` represents system errors by category and value. Assertions (`assert`) check internal invariants and are removed when `NDEBUG` is defined, while `static_assert` verifies conditions at compile time. Errors arising from the environment should be handled; violations of invariants indicate bugs and should be detected early.

## 6. Cheat sheet

| Need | Code |
|---|---|
| return a value or an error | `std::expected<T, E> f();` / `return std::unexpected(e);` |
| check and use | `if (r) use(*r); else log(r.error());` |
| default on error | `r.value_or(def)` |
| chain fallible steps | `.and_then(f).transform(g)` |
| system error, no throw | `std::error_code ec; f(args, ec); if (ec) ec.message();` |
| internal bug check | `assert(cond && "message")` |
| compile-time check | `static_assert(cond, "message")` |
| force callers to look | `[[nodiscard]]` |

> [!INTERVIEW]
> **"Exceptions or `std::expected`: how do you choose?"** Use `expected` when failure is a normal, anticipated outcome the immediate caller should handle (parsing user input, opening optional files, validating messages): it's explicit in the signature, cheap, and composes without hidden control flow. Use exceptions for truly exceptional conditions that must propagate across many layers to a handler (out of memory, a corrupted invariant reported from deep inside a library, constructor failure), where threading `expected` through every layer would be noise. Also consider the environment: hard real-time and `-fno-exceptions` codebases require `expected` or codes, and many teams use `expected` inside modules and exceptions at boundaries.
