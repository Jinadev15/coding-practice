# Study guide: Special quiz 1

Quiz 1 checks that you can build **value types** and **class hierarchies** that manage resources correctly.

## 1. Polymorphic JSON document model — Composite and clone

The **Composite pattern** treats leaves (numbers, strings) and containers (arrays, objects) through one interface:

```cpp
struct Value {
    virtual ~Value() = default;                         // ALWAYS virtual in a base class
    virtual std::string dump() const = 0;
    virtual std::unique_ptr<Value> clone() const = 0;   // "virtual copy constructor"
};
struct Number : Value {
    double v;
    explicit Number(double v) : v(v) {}
    std::string dump() const override { /* format v */ }
    std::unique_ptr<Value> clone() const override { return std::make_unique<Number>(*this); }
};
struct Array : Value {
    std::vector<std::unique_ptr<Value>> items;
    std::unique_ptr<Value> clone() const override {
        auto a = std::make_unique<Array>();
        for (auto& it : items) a->items.push_back(it->clone());   // deep copy
        return a;
    }
};
```

- **Why `clone`?** A copy constructor can't be virtual. Given a `Value&`, you don't know the concrete type, but `clone()` does.
- **Why `unique_ptr`?** Each child has exactly one owner, its container. Destroying the root frees the whole tree automatically.
- **Why a virtual destructor?** Deleting a `Derived` through a `Base*` without one is undefined behaviour.

Parse the input with recursive descent, as in the other milestones, returning `std::unique_ptr<Value>`.

## 2. Integer matrix library — rule of five and operators

A class that owns a raw resource needs all five special members, or none of them (the **rule of zero**: use `std::vector` and let the compiler write them).

```cpp
class Matrix {
    std::size_t r_{}, c_{};
    std::vector<long long> a_;            // rule of zero: vector handles copying/moving
public:
    Matrix(std::size_t r, std::size_t c) : r_(r), c_(c), a_(r * c) {}
    long long& operator()(std::size_t i, std::size_t j)       { return a_[i * c_ + j]; }
    long long  operator()(std::size_t i, std::size_t j) const { return a_[i * c_ + j]; }
    Matrix& operator+=(const Matrix& o) {
        if (r_ != o.r_ || c_ != o.c_) throw std::invalid_argument("shape mismatch");
        for (std::size_t k = 0; k < a_.size(); ++k) a_[k] += o.a_[k];
        return *this;
    }
    friend Matrix operator+(Matrix a, const Matrix& b) { return a += b; }   // reuse +=
};
```

Idioms to learn:

- Implement `+` in terms of `+=`, taking the left operand **by value**.
- Provide `const` and non-`const` versions of `operator()`.
- Throw a standard exception on a shape mismatch.
- Matrix multiplication runs `i-k-j` loop order for cache friendliness.
- Fast exponentiation by repeated squaring needs O(log n) multiplies.

## 3. String class with small-string optimisation (SSO)

`std::string` avoids `new` for short strings. It stores them **inside the object**, reusing the bytes that would otherwise hold the heap pointer and capacity.

```cpp
class Str {
    static constexpr std::size_t SSO = 15;
    std::size_t size_ = 0;
    bool heap_ = false;
    union { char small_[SSO + 1]; struct { char* ptr; std::size_t cap; } big_; };
    char* data() { return heap_ ? big_.ptr : small_; }
    // ...
};
```

Getting the **rule of five** right is the core of this problem:

| Member | Must do |
|---|---|
| destructor | `delete[]` only if `heap_` |
| copy ctor | allocate a fresh buffer if the source is big; copy the bytes |
| copy assign | handle `a = a`; the copy-and-swap idiom does this for free |
| move ctor | **steal** the pointer if big (leave the source empty and small); copy bytes if small |
| move assign | free your own buffer first, then steal; mark it `noexcept` |

> [!KEY]
> Mark the move operations `noexcept`. `std::vector<Str>` will only *move* elements when it grows if moving can't throw. Otherwise it copies them.
