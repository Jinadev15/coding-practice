# I/O Streams

C++ replaces `printf`/`scanf` with **streams**: `std::cout` for output and `std::cin` for input, with the `<<` and `>>` operators. Streams are **type-safe**: the compiler picks the right formatting for each type, so there are no format-string mismatches. They're extensible (you can teach them to print your own classes) and work uniformly for the console, files (`fstream`) and strings (`stringstream`). You also need to know how to make them fast for judges, and how their formatting state works.

## 1. Output with `<<`

```cpp
#include <iostream>

int main() {
    int n = 42;
    double pi = 3.14159;
    std::cout << "n = " << n << ", pi = " << pi << '\n';   // n = 42, pi = 3.14159
    std::cerr << "debug info\n";                            // standard error (unbuffered)
}
```

`<<` returns the stream itself, which is why the calls chain. Each operand is formatted by the overload for its type: no `%d`/`%f` to get wrong.

> [!TIP]
> Use `'\n'` rather than `std::endl`. `std::endl` writes a newline **and flushes** the buffer, which is very slow in loops with lots of output. Flush explicitly only when needed (`std::flush`).

## 2. Input with `>>`

```cpp
int a, b;
std::cin >> a >> b;                    // skips whitespace, reads two ints
if (!std::cin) { /* parse failure or EOF */ }

long long sum = 0;
int x;
while (std::cin >> x)                  // read until EOF or bad input
    sum += x;
```

`>>` skips leading whitespace and reads a value of the variable's type. The stream converts to `false` when a read fails: the **fail state**. After a failure, every later read does nothing until you call `std::cin.clear()` and discard the bad input.

### Reading lines and words

```cpp
#include <string>
std::string word, line;
std::cin >> word;                      // one whitespace-delimited word
std::getline(std::cin, line);          // the REST of the current line (often empty here!)
std::getline(std::cin, line);          // a whole line
```

> [!DANGER]
> Mixing `>>` with `getline`: `std::cin >> n;` leaves the `'\n'` in the buffer, so the next `getline` returns an empty string. Fix it with `std::cin >> std::ws;` (skip whitespace) before `getline`, or read every line with `getline` and parse it.

## 3. Formatting with manipulators (`<iomanip>`)

```cpp
#include <iomanip>
std::cout << std::fixed << std::setprecision(2) << 3.14159 << '\n';   // 3.14
std::cout << std::setw(6) << 42 << '|' << '\n';                        // "    42|"
std::cout << std::left << std::setw(6) << 42 << '|' << '\n';           // "42    |"
std::cout << std::setfill('0') << std::setw(5) << 7 << '\n';           // 00007
std::cout << std::hex << 255 << std::dec << '\n';                      // ff
std::cout << std::boolalpha << true << '\n';                           // true
```

> [!WARNING]
> Most manipulators are **sticky**: `fixed`, `setprecision`, `hex`, `left` and `setfill` stay in effect until changed. Only `setw` resets after the next output. A forgotten `std::hex` turns every later number into hex.

### `std::format` and `std::print` (C++20/23)

The modern alternative, with Python-like format specs:

```cpp
#include <format>
#include <print>
std::string s = std::format("{:>8.2f}|{:04d}", 3.14159, 7);   // "    3.14|0007"
std::println("x={} y={:.3f}", 3, 2.5);                         // C++23: prints with a newline
```

## 4. Fast I/O for competitive programming

```cpp
int main() {
    std::ios::sync_with_stdio(false);   // stop syncing with C stdio (big speedup)
    std::cin.tie(nullptr);              // don't flush cout before each cin read
    // ... read and write lots of data ...
}
```

With these two lines, `cin`/`cout` are as fast as `scanf`/`printf`. Afterwards, don't mix C and C++ I/O in the same program.

## 5. String streams and file streams

```cpp
#include <sstream>
#include <fstream>

std::istringstream in("10 20 30");
int v, total = 0;
while (in >> v) total += v;                 // parse from a string: 60

std::ostringstream out;
out << "id=" << 7 << ";";                   // build a string
std::string text = out.str();

std::ifstream file("data.txt");             // closes automatically (RAII)
for (std::string line; std::getline(file, line); )
    std::cout << line << '\n';
```

## 6. Printing your own types

```cpp
struct Point { double x, y; };

std::ostream& operator<<(std::ostream& os, const Point& p) {
    return os << '(' << p.x << ", " << p.y << ')';
}

std::cout << Point{1, 2} << '\n';   // (1, 2)
```

The Operator Overloading lesson covers this properly.

## 7. Exam-ready answers

> [!EXAM]
> **C++ streams.** C++ performs I/O through stream objects of the `<iostream>` library: `std::cin` (standard input), `std::cout` (standard output), `std::cerr` (unbuffered standard error) and `std::clog`. The insertion operator `<<` writes values to an output stream and the extraction operator `>>` reads whitespace-separated values from an input stream; both are overloaded for each type, making stream I/O type-safe and extensible to user-defined types. Stream state flags record failures, and a stream evaluates as false after a failed operation, which allows loops such as `while (std::cin >> x)`. Manipulators from `<iomanip>` such as `setw`, `setprecision`, `fixed` and `setfill` control formatting, and `getline` reads whole lines. String streams (`std::stringstream`) and file streams (`std::fstream`) provide the same interface for strings and files.

## 8. Cheat sheet

| Need | Code |
|---|---|
| print | `std::cout << a << ' ' << b << '\n';` |
| read until EOF | `while (std::cin >> x)` |
| a line | `std::getline(std::cin, s);` (after `>> std::ws` if mixing) |
| 2 decimals | `std::cout << std::fixed << std::setprecision(2) << x;` |
| width | `std::setw(8)` (applies once) |
| fast | `std::ios::sync_with_stdio(false); std::cin.tie(nullptr);` |
| parse a string | `std::istringstream in(s); in >> a >> b;` |
| modern format | `std::format("{:.2f}", x)` / `std::println(...)` |

> [!INTERVIEW]
> **"Why is my C++ solution with `cin`/`cout` slower than the C version with `scanf`?"** By default, C++ streams stay synchronised with C stdio, and `cin` is tied to `cout` (a flush before every input). Add `std::ios::sync_with_stdio(false); std::cin.tie(nullptr);`, and replace `std::endl` with `'\n'` to avoid flushing on every line. Then streams match or beat stdio.
