# string and string_view

`std::string` is C++'s owning, growable, contiguous character container. It manages its own memory (no `strcpy` overflows, no manual `free`) and has small-string optimisation. `std::string_view` (C++17) is a **non-owning view** of characters: a pointer plus a length. It makes read-only string parameters cheap, but it brings a new class of lifetime bugs. Text processing is in every program: config files, protocol messages, logs and command parsing.

## 1. `std::string` essentials

```cpp
#include <string>
using namespace std::string_literals;

std::string s = "hello world";
s.size();  s.empty();  s[0];  s.at(0);  s.front();  s.back();
s += "!";                          // append
s.append(3, '.');                  // "hello world!..."
s.substr(6, 5);                    // "world": a NEW string (copies)
s.find("o");                       // 4
s.rfind("o");                      // 7
s.find("z") == std::string::npos;  // not found
s.replace(0, 5, "HELLO");
s.insert(0, ">> ");
s.erase(0, 3);
s.starts_with("HE"); s.ends_with("...");   // C++20
s.contains("wor");                          // C++23
auto lit = "text"s;                // a std::string literal (not const char*)
const char* c = s.c_str();         // NUL-terminated view for C APIs (valid until s changes)
```

`std::string` is a `basic_string<char>`: it holds bytes, not Unicode characters. `size()` counts bytes, so `"é"` in UTF-8 has size 2.

### Small-string optimisation (SSO)

With gcc, `sizeof(std::string) == 32` and strings of up to **15 characters** live inside the object with no heap allocation (`std::string().capacity() == 15`). Longer strings allocate. That's why short strings are cheap to create and copy. You implemented exactly this in the SSO milestone.

## 2. Conversions

```cpp
int n = std::stoi("42");           // also stol, stoll, stoul, stod; throws std::invalid_argument / out_of_range
std::stoi("42abc");                // 42: parsing stops at the first invalid character (no error!)
std::string t = std::to_string(3.5);   // "3.500000": fixed 6 decimals

#include <charconv>
int v;
auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), v);   // no exceptions, no locale, no allocation
if (ec == std::errc{} && ptr == s.data() + s.size()) { /* the whole string was a number */ }
```

> [!TIP]
> For performance-critical parsing (log processing, protocols, competitive programming), `std::from_chars` and `std::to_chars` are the fastest standard conversions and report exactly where parsing stopped. `std::format` / `std::print` (C++20/23) replace `printf` and stream manipulators: `std::format("{:>8.3f}", x)`.

## 3. Splitting and joining

There's no `split` member. Common idioms:

```cpp
std::vector<std::string> split(const std::string& s, char delim) {
    std::vector<std::string> out;
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, delim)) out.push_back(item);
    return out;
}

// C++20 ranges version: lazy, no stream
for (auto part : s | std::views::split(',')) {
    std::string_view piece(part.begin(), part.end());
}
```

## 4. `std::string_view`: a non-owning view

```cpp
#include <string_view>
void log_line(std::string_view msg);   // accepts std::string, const char*, literals, and substrings: no copies

std::string s = "hello world";
std::string_view sv = s;               // pointer + length: 16 bytes
sv.remove_prefix(6);                   // "world": O(1), nothing copied
sv.substr(0, 3);                       // "wor": also a view, O(1)
```

| | `const std::string&` parameter | `std::string_view` parameter |
|---|---|---|
| Pass a `std::string` | free | free |
| Pass `"literal"` or `const char*` | **constructs a temporary string** (may allocate) | free |
| Substrings | `substr` copies | `substr` is O(1) |
| NUL-terminated? | yes (`c_str()`) | **not necessarily** |

> [!DANGER]
> A `string_view` doesn't own its characters. It must not outlive them:
> ```cpp
> std::string_view bad() {
>     std::string s = "temporary";
>     return s;                       // view into a destroyed string: dangling
> }
> std::string_view sv = std::string("abc") + "def";   // the temporary dies at the semicolon: dangling
> ```
> Rules: use `string_view` for **parameters** (read-only, used during the call), and be very careful returning or storing it. Never pass `sv.data()` to a C function expecting a NUL-terminated string, because the view may end mid-string.

## 5. Performance notes

- `s += x` in a loop is amortised O(1) per character (geometric growth). `s = s + x` creates a new string every time, which is O(n²).
- `reserve` when the final length is known.
- `std::string` comparisons are lexicographic by `char` value (`"Z" < "a"`).
- Pass strings you'll **store** by value and `std::move` them into place (the sink-argument idiom): `Robot(std::string name) : name_(std::move(name)) {}`.

## 6. Exam-ready answers

> [!EXAM]
> **`std::string` and `std::string_view`.** `std::string` is an owning, dynamically sized, contiguous sequence of characters that manages its own storage, typically with a small-string optimisation that stores short strings inside the object; it provides searching (`find`, `rfind`), substring extraction (`substr`, which copies), modification (`append`, `insert`, `erase`, `replace`) and access to a NUL-terminated buffer through `c_str`. `std::string_view` is a non-owning, read-only view consisting of a pointer and a length; it can refer to any contiguous character sequence without copying, and its `substr` is constant-time, making it efficient for function parameters. Because it does not own its data, a `string_view` must not outlive the characters it refers to, and its data is not guaranteed to be NUL-terminated.

## 7. Cheat sheet

| Need | Code |
|---|---|
| read-only parameter | `std::string_view` |
| parameter to store | `std::string` by value + `std::move` |
| find | `s.find(x)` vs `std::string::npos` |
| prefix / suffix | `starts_with` / `ends_with` |
| number → text | `std::to_string`, `std::format`, `std::to_chars` |
| text → number | `std::stoi` (throws), `std::from_chars` (no throw) |
| read a line | `std::getline(std::cin, s)` |
| split | `getline(ss, item, ',')` or `views::split` |

> [!INTERVIEW]
> **"When would you use `std::string_view` instead of `const std::string&`, and what is the danger?"** For read-only parameters: `string_view` accepts literals, C strings and substrings without allocating a temporary `std::string`, and slicing is O(1). The danger is lifetime: a view doesn't keep its characters alive, so returning a view of a local, storing a view of a temporary, or keeping a view into a `std::string` that later reallocates all create dangling views. Also, `data()` isn't NUL-terminated, so it can't be passed directly to C APIs.
