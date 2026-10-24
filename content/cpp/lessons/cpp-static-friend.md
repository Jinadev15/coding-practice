# Static Members and friend

Most members belong to each object. **Static members** belong to the **class itself**: one copy shared by all instances, like Python's class attributes and `@staticmethod`/`@classmethod`. **`friend`** grants a specific function or class access to private members. That's a controlled exception to encapsulation, used mainly for operators and tightly coupled helpers.

## 1. Static data members

```cpp
class Robot {
public:
    Robot() : id_(next_id_++) { ++count_; }
    ~Robot() { --count_; }
    static int count() { return count_; }      // static member function
    int id() const { return id_; }
private:
    int id_;
    static inline int next_id_ = 1;            // C++17 inline static: defined right here
    static inline int count_ = 0;
};

Robot a, b;
{
    Robot c;
    std::cout << Robot::count();   // 3
}
std::cout << Robot::count() << ' ' << b.id();   // 2 2
```

- One instance of the static member exists for the whole program (static storage duration), no matter how many objects there are, even zero.
- Access it through the class: `Robot::count()` (also legal through an object, but misleading).
- **Before C++17**, a non-const static data member had to be **defined** in exactly one `.cpp` file: `int Robot::count_ = 0;`. With `static inline` the definition can live in the header. `static constexpr` members are implicitly inline.

```cpp
class Limits {
public:
    static constexpr double max_speed = 2.0;   // a compile-time class constant
};
```

## 2. Static member functions

```cpp
class Temperature {
public:
    static Temperature from_fahrenheit(double f) { return Temperature((f - 32) * 5 / 9); }  // named constructor
    double celsius() const { return c_; }
private:
    explicit Temperature(double c) : c_(c) {}
    double c_;
};

auto t = Temperature::from_fahrenheit(212);
```

A static member function has **no `this`**. It can't access non-static members directly, but it **can** access private members of objects passed to it, and the class's private constructors, which is what makes named constructors and factories possible.

| | Non-static member function | Static member function |
|---|---|---|
| has `this` | yes | no |
| call syntax | `obj.f()` | `Cls::f()` |
| accesses instance data | directly | only through an object parameter |
| can be `const`/`virtual` | yes | no |
| uses | object behaviour | factories, class-wide state, utilities |

## 3. `friend`

```cpp
class Vec2 {
public:
    Vec2(double x, double y) : x_(x), y_(y) {}
    friend std::ostream& operator<<(std::ostream& os, const Vec2& v);   // grants access
    friend class VecTester;                                             // a whole class
private:
    double x_, y_;
};

std::ostream& operator<<(std::ostream& os, const Vec2& v) {
    return os << '(' << v.x_ << ", " << v.y_ << ')';     // OK: friend can read private members
}
```

- Friendship is **granted** by the class (you can't claim it from outside), it's **not inherited**, and it's **not transitive**.
- Typical legitimate uses: **operator overloads** that need private data but must be non-members (`operator<<`, symmetric `operator+`), unit tests, and tightly paired classes (a container and its iterator).
- Overusing friends is a design smell: it's breaking encapsulation. Prefer a public accessor when one is natural.

### Hidden friends

Defining the friend **inside** the class body makes it a "hidden friend", found only through ADL. This is the modern recommended style for operators:

```cpp
class Money {
    long long cents_;
public:
    explicit Money(long long c) : cents_(c) {}
    friend Money operator+(Money a, Money b) { return Money(a.cents_ + b.cents_); }
    friend bool operator==(Money a, Money b) = default;
};
```

## 4. Static locals and the Meyers singleton

```cpp
Config& config() {
    static Config instance;     // constructed on first call, thread-safe since C++11, destroyed at exit
    return instance;
}
```

This is the safest way to have one shared object. Use it sparingly: global state hurts testability. Dependency injection (Master OOP) is usually better.

## 5. Exam-ready answers

> [!EXAM]
> **Static members.** A static data member is shared by all objects of a class and exists independently of any object, with static storage duration; it is accessed through the class name, and (before C++17 `inline` variables) must be defined in exactly one translation unit. A static member function has no `this` pointer, cannot access non-static members directly, and is called through the class name; it is used for class-wide operations such as factories, counters and utility functions.

> [!EXAM]
> **Friend functions and classes.** A `friend` declaration inside a class grants a non-member function or another class access to the class's private and protected members. Friendship is granted only by the class itself and is neither inherited nor transitive. It is commonly used for operator overloads that must be non-members, such as `operator<<`, and for tightly coupled helper classes, but should be used sparingly because it weakens encapsulation.

## 6. Cheat sheet

| Need | Code |
|---|---|
| shared counter | `static inline int count_ = 0;` |
| class constant | `static constexpr int N = 8;` |
| factory | `static T create(args);` |
| call | `T::create(...)` |
| stream output | `friend std::ostream& operator<<(std::ostream&, const T&);` |
| one global instance | a function returning a reference to a `static` local |

> [!INTERVIEW]
> **"Can a static member function be virtual or const? Why not?"** No. `virtual` dispatches on the object's dynamic type, and `const` qualifies the `this` pointer, but a static member function has no object and no `this` to dispatch on or qualify. To get polymorphic behaviour from a factory-like function, use a virtual member function, or a registry of factory functions.
