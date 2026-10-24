# Move Semantics and Perfect Forwarding

Before C++11, returning a `std::vector` from a function or inserting a string into a container meant **deep copies**: allocate new memory and copy every element. **Move semantics** lets an object *steal* the resources of a temporary instead: three pointer copies instead of a million element copies. It's why modern C++ can return big objects by value, why `std::vector<std::string>` grows cheaply, and how move-only types like `std::unique_ptr` and `std::thread` exist.

## 1. Copy vs move, concretely

```cpp
class Buffer {
    std::size_t size_;
    double* data_;
public:
    explicit Buffer(std::size_t n) : size_(n), data_(new double[n]{}) {}
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& other)                    // COPY constructor: deep copy
        : size_(other.size_), data_(new double[other.size_]) {
        std::copy(other.data_, other.data_ + size_, data_);
    }

    Buffer(Buffer&& other) noexcept                // MOVE constructor: steal
        : size_(other.size_), data_(other.data_) {
        other.size_ = 0;
        other.data_ = nullptr;                     // leave the source valid (its destructor must be safe)
    }
};
```

<div class="figure">
<svg viewBox="0 0 600 170" width="600" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="12">
  <defs><marker id="mva" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text x="20" y="18" fill="currentColor" font-family="sans-serif" font-size="13" font-weight="bold">copy: allocate + copy N elements</text>
  <rect x="20" y="30" width="80" height="30" fill="none" stroke="#2f81f7"/><text x="30" y="50" fill="currentColor">src</text>
  <rect x="160" y="30" width="120" height="30" fill="none" stroke="#3fb950"/><text x="170" y="50" fill="currentColor">heap [N]</text>
  <rect x="20" y="75" width="80" height="30" fill="none" stroke="#2f81f7"/><text x="30" y="95" fill="currentColor">dst</text>
  <rect x="160" y="75" width="120" height="30" fill="none" stroke="#d29922"/><text x="170" y="95" fill="currentColor">NEW heap [N]</text>
  <line x1="100" y1="45" x2="156" y2="45" stroke="currentColor" marker-end="url(#mva)"/><line x1="100" y1="90" x2="156" y2="90" stroke="currentColor" marker-end="url(#mva)"/>
  <text x="320" y="18" fill="currentColor" font-family="sans-serif" font-size="13" font-weight="bold">move: steal the pointer, O(1)</text>
  <rect x="320" y="30" width="80" height="30" fill="none" stroke="#2f81f7"/><text x="328" y="50" fill="currentColor">src=null</text>
  <rect x="320" y="75" width="80" height="30" fill="none" stroke="#2f81f7"/><text x="330" y="95" fill="currentColor">dst</text>
  <rect x="460" y="55" width="120" height="30" fill="none" stroke="#3fb950"/><text x="470" y="75" fill="currentColor">heap [N]</text>
  <line x1="400" y1="90" x2="456" y2="74" stroke="currentColor" marker-end="url(#mva)"/>
</svg>
<figcaption>Moving transfers ownership of the existing heap block; nothing is allocated or copied.</figcaption>
</div>

## 2. When does the compiler move?

A move happens when the source is an **rvalue**:

```cpp
Buffer make();
Buffer a = make();               // a temporary → move (or elided entirely)
Buffer b = std::move(a);         // you cast a to an rvalue → move; don't use a's value afterwards
std::vector<Buffer> v;
v.push_back(Buffer(100));        // temporary → move into the vector
v.push_back(b);                  // lvalue → COPY
v.push_back(std::move(b));       // explicit → move
```

## 3. Copy elision and RVO

```cpp
Buffer make() {
    Buffer local(1000);
    return local;                // NRVO: usually constructed directly in the caller's storage
}
Buffer c = make();               // usually neither copy nor move happens
```

- Returning a **prvalue** (`return Buffer(1000);`) has **guaranteed** elision since C++17: no copy or move constructor is called at all.
- Returning a **named local** (NRVO) is elided by every major compiler in practice. If not, it's **moved** automatically.

> [!DANGER]
> Don't write `return std::move(local);`. It *prevents* NRVO (forcing a move instead of nothing), and compilers warn about it (`-Wpessimizing-move`). Plain `return local;` is optimal.

## 4. `noexcept` on move operations matters

When `std::vector` grows, it must transfer its elements to new storage. If your move constructor **might throw**, the vector **copies** instead, to keep its strong exception guarantee. Mark move constructors and move assignment `noexcept` (they rarely can throw), or vector growth gets much slower.

## 5. Move assignment

```cpp
Buffer& operator=(Buffer&& other) noexcept {
    if (this != &other) {
        delete[] data_;             // release our own resource
        data_ = other.data_;        // steal
        size_ = other.size_;
        other.data_ = nullptr;
        other.size_ = 0;
    }
    return *this;
}
```

The Rule of Five lesson shows how the copy-and-swap idiom implements both assignments compactly and safely.

## 6. Moving into members: the sink-parameter idiom

```cpp
class Robot {
    std::string name_;
public:
    explicit Robot(std::string name) : name_(std::move(name)) {}   // take by value, then move
};

std::string n = "rover";
Robot r1(n);                    // one copy (into the parameter), then a move
Robot r2("arm");                // a temporary is built straight into the parameter, then a move
Robot r3(std::move(n));         // two moves, no copies
```

Taking a parameter **by value and moving it** into the member serves both lvalue and rvalue callers optimally with one function.

## 7. Perfect forwarding

A factory or wrapper should pass arguments on **exactly as received**, lvalues as lvalues and rvalues as rvalues:

```cpp
template <typename T, typename... Args>
std::unique_ptr<T> make(Args&&... args) {                 // forwarding references
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}
```

- `Args&&` with a **deduced** `Args` is a **forwarding reference**: it binds to anything, thanks to **reference collapsing** (`T& &&` → `T&`, `T&& &&` → `T&&`).
- `std::forward<Args>(args)` casts back to an rvalue **only if** the original argument was an rvalue.

That's how `std::make_unique`, `emplace_back` and `std::thread`'s constructor work.

```cpp
std::vector<Robot> fleet;
fleet.emplace_back("rover");     // constructs the Robot in place inside the vector: no temporary at all
```

## 8. Exam-ready answers

> [!EXAM]
> **Move semantics.** Move semantics allow the resources of an object that is no longer needed, typically a temporary (an rvalue), to be transferred to another object instead of being copied. A move constructor `T(T&& other)` and move assignment operator `T& operator=(T&& other)` take an rvalue reference, take over the source's resources (for example its heap pointer), and leave the source in a valid but unspecified state. The compiler selects them automatically for rvalues; `std::move` casts an lvalue to an rvalue to request a move explicitly. Move operations should be `noexcept` so that containers such as `std::vector` use them during reallocation. Combined with copy elision, move semantics make returning and passing large objects by value efficient.

> [!EXAM]
> **Perfect forwarding.** In a function template, a parameter of the form `T&&` where `T` is deduced is a forwarding reference that can bind to both lvalues and rvalues through reference collapsing. `std::forward<T>(arg)` forwards the argument to another function preserving its original value category, so that rvalues are moved and lvalues copied. This is used by factory and wrapper functions such as `std::make_unique` and `emplace_back`.

## 9. Cheat sheet

| Need | Code |
|---|---|
| move constructor | `T(T&& o) noexcept : res(o.res) { o.res = nullptr; }` |
| request a move | `auto b = std::move(a);` |
| return a big object | `return local;` (never `return std::move(local);`) |
| store a parameter | `T(std::string s) : s_(std::move(s)) {}` |
| construct in place | `v.emplace_back(args...)` |
| forward arguments | `f(std::forward<Args>(args)...)` |

> [!INTERVIEW]
> **"Why must move constructors be `noexcept` for good `std::vector` performance?"** When a vector reallocates, it promises the strong exception guarantee: if something throws, the original vector is unchanged. A move that might throw could leave elements half-transferred, so the vector uses `std::move_if_noexcept` and falls back to copying unless the move constructor is `noexcept`. Forgetting `noexcept` silently turns O(1) element transfers into deep copies.
