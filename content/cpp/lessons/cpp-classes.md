# Classes and Objects

A C++ class bundles data (**data members**) and behaviour (**member functions**) and, unlike Python, **enforces** encapsulation through `public`, `private` and `protected`. Objects can live on the stack, as members of other objects, or in containers, with **no heap allocation and no per-object overhead** beyond their data. That's why C++ classes are used even in tiny embedded systems. This lesson covers the anatomy of a class, access control, `this`, const member functions, and the header/source split.

## 1. Anatomy of a class

```cpp
#include <string>

class Motor {
public:                                         // the interface: usable by anyone
    Motor(std::string name, int max_rpm)        // constructor (next lesson)
        : name_(std::move(name)), max_rpm_(max_rpm) {}

    void set_speed(int rpm) {                   // member function (method)
        rpm_ = std::clamp(rpm, -max_rpm_, max_rpm_);
    }
    int speed() const { return rpm_; }          // const: doesn't modify the object
    const std::string& name() const { return name_; }

private:                                        // the implementation: only members can touch it
    std::string name_;
    int max_rpm_;
    int rpm_ = 0;                               // default member initialiser
};

Motor left("left", 3000);       // an object on the stack: no new, no heap
left.set_speed(5000);
std::cout << left.speed();      // 3000
// left.rpm_ = 99999;           // error: 'int Motor::rpm_' is private
```

> [!KEY]
> - Members are **private by default** in a `class` and **public by default** in a `struct`. That's the only difference between the two keywords. Convention: `struct` for plain data aggregates, `class` for types with invariants.
> - The compiler enforces access, so it's impossible (without hacks) to break invariants from outside. Python's `_name` convention becomes a real wall here.
> - The trailing underscore (`rpm_`) is a common naming convention for data members.

## 2. `this`

Inside a member function, `this` is a pointer to the object the function was called on:

```cpp
class Counter {
    int count_ = 0;
public:
    Counter& increment() { ++count_; return *this; }   // return a reference to enable chaining
    int value() const { return count_; }
};

Counter c;
c.increment().increment().increment();   // fluent interface
std::cout << c.value();                  // 3
```

`left.set_speed(5000)` is conceptually `Motor::set_speed(&left, 5000)`. That's C++'s `self`, made implicit.

## 3. const member functions

```cpp
int speed() const { return rpm_; }     // `this` is `const Motor*` inside
```

> [!KEY]
> Mark every member function that doesn't modify the object `const`. Only const member functions can be called on `const` objects and through `const&` parameters, and that's how objects are normally passed (`void log(const Motor& m)` can only call `m.speed()` if `speed()` is const). The compiler checks the promise: assigning a member inside a const function is an error. `mutable` members (e.g. a cache or a mutex) are exempt.

## 4. Classes in headers and sources

```cpp
// motor.hpp: the class definition (the interface)
#pragma once
#include <string>
class Motor {
public:
    Motor(std::string name, int max_rpm);
    void set_speed(int rpm);
    int speed() const;
private:
    std::string name_;
    int max_rpm_;
    int rpm_ = 0;
};
```

```cpp
// motor.cpp: member function definitions (the implementation)
#include "motor.hpp"
#include <algorithm>
Motor::Motor(std::string name, int max_rpm) : name_(std::move(name)), max_rpm_(max_rpm) {}
void Motor::set_speed(int rpm) { rpm_ = std::clamp(rpm, -max_rpm_, max_rpm_); }
int Motor::speed() const { return rpm_; }
```

`Motor::` qualifies the names. Functions defined **inside** the class body are implicitly `inline` (fine for short ones). Unlike C's opaque pointers, the private members are visible in the header, though not accessible. The PIMPL idiom hides them completely (Advanced module).

## 5. Objects are values

```cpp
Motor a("a", 100);
Motor b = a;            // COPIES all members (Python would alias!)
b.set_speed(50);        // a is unchanged
std::vector<Motor> motors{a, b};   // stored inline, contiguously in the vector
```

C++ objects have **value semantics** by default: assignment and passing by value copy. For reference semantics you use references, pointers or smart pointers explicitly. That's the biggest mental shift coming from Python.

## 6. Memory layout

A class object occupies exactly the space of its data members, plus alignment padding, plus one hidden pointer if it has virtual functions. Member functions take **no** space in objects: there's one copy of the code, shared by every object.

```cpp
struct Point { double x, y; };
static_assert(sizeof(Point) == 16);    // just the two doubles
```

## 7. Exam-ready answers

> [!EXAM]
> **Classes in C++.** A class is a user-defined type that encapsulates data members and member functions. Access specifiers control visibility: `public` members form the interface accessible to all code, `private` members are accessible only to the class's own members and friends, and `protected` members are additionally accessible to derived classes. Members of a `class` are private by default and those of a `struct` public. Each non-static member function receives an implicit `this` pointer to the object on which it is called; a `const` member function cannot modify the object's non-mutable members and is the only kind callable on const objects. Objects have value semantics: they can be created on the stack, embedded in other objects and copied.

## 8. Cheat sheet

| Need | Code |
|---|---|
| hide data | `private:` members |
| interface | `public:` member functions |
| read-only method | `int get() const;` |
| define out of class | `int Motor::speed() const { ... }` |
| chaining | `return *this;` from a `T&` function |
| plain data | `struct Pose { double x, y, theta; };` |

> [!INTERVIEW]
> **"What's the difference between `struct` and `class` in C++?"** Only the default access, for members and for inheritance: public for `struct`, private for `class`. Everything else is identical (both can have constructors, virtual functions, templates…). By convention, `struct` is used for passive aggregates without invariants, and `class` for types that maintain invariants behind a private implementation.
