# Rule of 0, 3 and 5

A class can define up to six **special member functions**: the default constructor, destructor, copy constructor, copy assignment, move constructor and move assignment. The compiler generates them when it can, but the generated versions do **member-wise** copying, which is wrong for a class that owns a raw resource. The Rule of Three, Rule of Five and Rule of Zero tell you exactly when to write them yourself, and the answer in modern C++ is usually **never**.

## 1. The special members

| Function | Signature | Called when |
|---|---|---|
| default constructor | `T()` | `T x;`, `T x{};` |
| destructor | `~T()` | an object's lifetime ends |
| copy constructor | `T(const T&)` | `T b = a;`, pass or return by value from an lvalue |
| copy assignment | `T& operator=(const T&)` | `b = a;` |
| move constructor | `T(T&&) noexcept` | `T b = std::move(a);`, from temporaries |
| move assignment | `T& operator=(T&&) noexcept` | `b = std::move(a);` |

The compiler-generated versions apply the operation to each base and member in order. For `int`s, `std::string`s and `std::vector`s, that's exactly right.

## 2. Why member-wise copying breaks a raw-pointer owner

```cpp
class BadBuffer {
    double* data_;
public:
    BadBuffer(std::size_t n) : data_(new double[n]) {}
    ~BadBuffer() { delete[] data_; }
    // no copy operations written → the compiler copies the POINTER
};

BadBuffer a(10);
BadBuffer b = a;    // b.data_ == a.data_ (a shallow copy)
// end of scope: both destructors delete[] the same block → double free (UB)
```

## 3. The Rule of Three (C++98) and Five (C++11)

> [!KEY]
> **Rule of Three**: if a class needs a user-defined **destructor**, **copy constructor** or **copy assignment**, it almost certainly needs all three, because it manages a resource.
> **Rule of Five**: in C++11 and later, add the **move constructor** and **move assignment** too. Otherwise moves fall back to (expensive) copies.

A correct Rule-of-Five class, using the copy-and-swap idiom:

```cpp
#include <algorithm>
#include <utility>

class Buffer {
    std::size_t size_ = 0;
    double* data_ = nullptr;
public:
    explicit Buffer(std::size_t n) : size_(n), data_(new double[n]{}) {}
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& o) : size_(o.size_), data_(new double[o.size_]) {     // deep copy
        std::copy(o.data_, o.data_ + size_, data_);
    }
    Buffer(Buffer&& o) noexcept                                                // steal
        : size_(std::exchange(o.size_, 0)), data_(std::exchange(o.data_, nullptr)) {}

    Buffer& operator=(Buffer o) noexcept {      // takes BY VALUE: copy or move happens at the call
        swap(*this, o);                          // swap with the parameter…
        return *this;                            // …whose destructor frees our old data
    }
    friend void swap(Buffer& a, Buffer& b) noexcept {
        using std::swap;
        swap(a.size_, b.size_);
        swap(a.data_, b.data_);
    }
};
```

Copy-and-swap gives one assignment operator that handles both copy and move, is safe against self-assignment, and has the **strong exception guarantee**: if the copy throws, `*this` is untouched.

## 4. The Rule of Zero: the modern default

> [!KEY]
> **Rule of Zero**: design classes so they need **none** of the special members. Hold resources through RAII members (`std::vector`, `std::string`, `std::unique_ptr`) whose own special members already do the right thing. Then the compiler-generated versions are correct automatically.

```cpp
class Buffer {                      // Rule of Zero: no destructor, no copy or move code
    std::vector<double> data_;
public:
    explicit Buffer(std::size_t n) : data_(n) {}
};

class Robot {
    std::string name_;
    std::unique_ptr<Controller> ctrl_;    // makes Robot move-only automatically (that's correct!)
};
```

Only the small set of low-level resource classes (and you'll rarely write those, because the standard library already has them) need the Rule of Five.

## 5. `= default` and `= delete`

```cpp
class Sensor {
public:
    Sensor() = default;                         // request the compiler-generated version
    Sensor(const Sensor&) = delete;             // forbid copying (a unique hardware handle)
    Sensor& operator=(const Sensor&) = delete;
    Sensor(Sensor&&) noexcept = default;        // allow moving
    Sensor& operator=(Sensor&&) noexcept = default;
    virtual ~Sensor() = default;                // polymorphic base: virtual destructor
};
```

## 6. When does the compiler generate what?

The suppression rules are a classic interview question:

| You declare… | Then… |
|---|---|
| any constructor | no implicit default constructor |
| a destructor, or a copy operation | moves are **not** generated (moves fall back to copies) |
| a move operation | copies are **deleted** |

So declaring even an empty destructor `~T() {}` silently disables moves, which is a performance bug. Either don't declare it, or declare all five (`= default` where appropriate).

## 7. Exam-ready answers

> [!EXAM]
> **Rule of three, five and zero.** The compiler can implicitly generate a class's destructor, copy constructor, copy assignment operator, and (since C++11) move constructor and move assignment operator, performing member-wise operations. The rule of three states that if a class requires a user-defined destructor, copy constructor or copy assignment operator, which typically indicates that it manages a resource such as raw heap memory, it requires all three to avoid shallow copies and double deletion. The rule of five extends this to the move operations, so that resources can be transferred efficiently. The rule of zero recommends that classes avoid defining any of these functions by delegating resource management to RAII members such as containers and smart pointers, so the implicitly generated operations are correct.

## 8. Cheat sheet

| Situation | Do |
|---|---|
| ordinary class | Rule of Zero: use `vector`, `string`, `unique_ptr` members |
| owns a raw resource | Rule of Five (copy-and-swap) |
| non-copyable handle | `T(const T&) = delete;` + defaulted moves |
| polymorphic base | `virtual ~Base() = default;` |
| want the generated version | `= default` |
| debugging copies | print in the copy constructor and move constructor |

> [!INTERVIEW]
> **"I added `~Widget() {}` for logging and my program got slower. Why?"** A user-declared destructor suppresses the implicit move constructor and move assignment, so every "move" of a `Widget`, such as inside `std::vector` growth or when returning it, became a copy. Either remove the destructor (Rule of Zero), or explicitly default the moves (`Widget(Widget&&) noexcept = default;` and the assignment, plus the copies if wanted).
