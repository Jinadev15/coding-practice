# Virtual Functions and Polymorphism

**Runtime polymorphism** means calling one function through a base-class reference or pointer and running the version for the object's **actual (dynamic) type**. In Python every method works this way. In C++ you opt in per function with **`virtual`**. This is the core mechanism of object-oriented design in C++: plug-in sensors, interchangeable controllers, strategy objects, GUI widgets and game entities are all built on it. This lesson covers `virtual`, `override`, `final`, abstract classes, virtual destructors, and the traps.

## 1. Static vs dynamic binding

```cpp
struct Shape {
    double area_static() const { return 0; }          // non-virtual: bound at compile time
    virtual double area() const { return 0; }         // virtual: bound at run time
    virtual ~Shape() = default;
};
struct Circle : Shape {
    double r;
    explicit Circle(double r) : r(r) {}
    double area_static() const { return 3.14159 * r * r; }        // HIDES: not an override
    double area() const override { return 3.14159 * r * r; }      // OVERRIDES
};

Circle c(1.0);
Shape& s = c;
std::cout << s.area_static() << ' ' << s.area();      // 0 3.14159
```

| | Non-virtual | Virtual |
|---|---|---|
| Chosen by | **static** type (the reference's type) | **dynamic** type (the object's actual type) |
| Decided | at compile time | at run time (through the vtable) |
| Inlinable | yes | only when the compiler can devirtualise |

Dispatch happens only through **references and pointers**. Calling on an object by value (`c.area()`) always uses its own type. There's nothing to dispatch.

## 2. `override` and `final`

```cpp
struct Controller {
    virtual double update(double error, double dt) = 0;
    virtual ~Controller() = default;
};
struct PID : Controller {
    double update(double error, double dt) override;     // compiler CHECKS that it overrides
    // double update(double error, float dt) override;   // error: doesn't override anything
};
struct TunedPID final : PID { };                         // nobody can derive from TunedPID
struct Pi : Controller {
    double update(double e, double dt) final;            // derived classes can't override this
};
```

> [!KEY]
> Always write `override`. Without it, a typo in the signature (a different parameter type, a missing `const`) silently creates a **new** function that hides the base one, and dispatch quietly goes to the base. With `override` it's a compile error. `final` documents and enforces "no further overriding", and it lets the compiler devirtualise calls.

## 3. Abstract classes and interfaces

A **pure virtual** function (`= 0`) has no implementation in the base and makes the class **abstract**: it can't be instantiated, and concrete derived classes must override every pure virtual function.

```cpp
class ISensor {                                // an "interface": only pure virtuals + virtual dtor
public:
    virtual ~ISensor() = default;
    virtual std::string name() const = 0;
    virtual double read() = 0;
};

class FakeImu : public ISensor {
public:
    std::string name() const override { return "imu"; }
    double read() override { return 9.81; }
};

// ISensor s;                                  // error: abstract
std::vector<std::unique_ptr<ISensor>> sensors;
sensors.push_back(std::make_unique<FakeImu>());
for (auto& s : sensors) std::cout << s->name() << '=' << s->read() << '\n';
```

The caller depends only on `ISensor`, so you can swap a real IMU for a fake in tests and add new sensors without touching the loop. That's the Open/Closed and Dependency Inversion principles in action.

## 4. Virtual destructors

> [!DANGER]
> Deleting a derived object through a base pointer whose destructor is **not virtual** is **undefined behaviour**. In practice the derived destructor doesn't run, and its resources leak:
> ```cpp
> struct Base { ~Base() {} };                 // NOT virtual
> struct Der : Base { std::vector<int> big = std::vector<int>(1'000'000); };
> Base* p = new Der;
> delete p;                                   // UB: ~Der never runs, the vector leaks
> std::unique_ptr<Base> u = std::make_unique<Der>();   // same problem when u is destroyed
> ```
> **Rule:** a class with any virtual function, or one meant to be deleted polymorphically, needs a `public virtual` destructor. Otherwise, make the destructor `protected` and non-virtual, so deleting through the base won't compile.

## 5. Traps

### Virtual calls in constructors and destructors

```cpp
struct Base {
    Base() { hello(); }                        // calls Base::hello, NOT the override
    virtual void hello() { std::cout << "Base::hello\n"; }
    virtual ~Base() = default;
};
struct Der : Base { void hello() override { std::cout << "Der::hello\n"; } };
Der d;                                         // prints "Base::hello"
```

While `Base`'s constructor runs, the `Der` part doesn't exist yet. The object's dynamic type **is** `Base` during that time, so it dispatches to `Base`. The same applies in destructors. A pure virtual called this way crashes ("pure virtual method called").

### Default arguments are bound statically

```cpp
struct P { virtual void f(int x = 1) { std::cout << "P " << x; } virtual ~P() = default; };
struct Q : P { void f(int x = 2) override { std::cout << "Q " << x; } };
P* p = new Q;
p->f();                                        // "Q 1": Q's body with P's default!
```

The function is chosen dynamically, but the default argument comes from the **static** type. Never redefine default arguments in overrides.

### Covariant return types

An override may return a pointer or reference to a **more derived** type than the base's version: `Shape* clone()` in the base, `Circle* clone() override` in the derived. That's the basis of the **virtual clone** idiom (copying an object you only know through a base pointer).

## 6. Polymorphism without inheritance (preview)

| Technique | When the binding happens | Example |
|---|---|---|
| virtual functions | run time | `unique_ptr<ISensor>` |
| templates / concepts | compile time | `template <Sensor S> void poll(S&)` |
| `std::variant` + `std::visit` | run time, closed set of types | `variant<Lidar, Imu>` |
| type erasure | run time, no common base | `std::function` |

Templates are covered in their own module. Virtual dispatch is the right default when the set of types is open and chosen at run time.

## 7. Exam-ready answers

> [!EXAM]
> **Virtual functions and runtime polymorphism.** A virtual function is a member function declared with `virtual` that can be overridden in derived classes; when it is called through a base-class pointer or reference, the version corresponding to the object's dynamic type is executed (dynamic binding), whereas non-virtual functions are bound statically by the type of the expression. The `override` specifier asks the compiler to verify that a function overrides a base virtual function, and `final` prevents further overriding or derivation. A pure virtual function (`= 0`) makes its class abstract, so it cannot be instantiated; abstract classes define interfaces. A base class used polymorphically must have a virtual destructor; otherwise, deleting a derived object through a base pointer is undefined behaviour. During construction and destruction, virtual calls resolve to the class whose constructor or destructor is currently running.

## 8. Cheat sheet

| Need | Code |
|---|---|
| overridable | `virtual R f(args);` |
| override | `R f(args) override;` |
| interface method | `virtual R f(args) = 0;` |
| polymorphic base | `virtual ~Base() = default;` |
| stop overriding | `R f() final;` / `class X final` |
| polymorphic container | `std::vector<std::unique_ptr<Base>>` |
| polymorphic copy | `virtual std::unique_ptr<Base> clone() const = 0;` |

> [!INTERVIEW]
> **"Why should a base class destructor be virtual? When should it not be?"** If code deletes a derived object through a base pointer (including through `unique_ptr<Base>`), a non-virtual destructor makes that undefined behaviour, typically skipping the derived destructor and leaking resources. So any class with virtual functions, or meant for polymorphic ownership, gets a public virtual destructor. Classes not meant to be polymorphic bases (value types like `std::string`, or `final` classes) shouldn't pay for a vptr. A base used only for code reuse gets a **protected non-virtual** destructor, so polymorphic deletion fails to compile.
