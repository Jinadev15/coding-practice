# Thinking in Objects in C++

Object-oriented design isn't about using `class`. It's about **finding the right abstractions**: objects that own their data, protect their invariants, and expose behaviour in the vocabulary of the problem. C++ adds its own dimension: every type is either a **value** (copyable, comparable, often immutable) or an **entity** (identity, usually non-copyable, owned through pointers), and that choice drives the whole design. This lesson covers going from requirements to classes, invariants and class responsibilities, value types versus entity types, **strong types** that make unit errors impossible at compile time, and "tell, don't ask".

## 1. From requirements to classes

Requirement: *"A delivery robot follows a route of waypoints at a speed limited by its configuration. It must never exceed its battery's remaining range."*

1. **Nouns** become candidate classes: Robot, Route, Waypoint, Speed, Configuration, Battery, Range.
2. **Verbs** become responsibilities: follow (Robot), limit (Configuration), estimate the range (Battery).
3. **Invariants** are what must always be true: a route is non-empty, speed is in [0, v_max], battery charge is in [0, 1]. Each invariant belongs to exactly one class, which enforces it.
4. Decide **value or entity** for each class (§3).

| Class | Kind | Invariant it owns |
|---|---|---|
| `Waypoint` | value | coordinates finite |
| `Route` | value | at least one waypoint |
| `Battery` | entity | 0 ≤ charge ≤ capacity |
| `Robot` | entity | never commanded beyond its range |

## 2. Invariants and the class boundary

```cpp
class Battery {
public:
    explicit Battery(double capacity_wh) : capacity_(capacity_wh), charge_(capacity_wh) {
        if (!(capacity_wh > 0)) throw std::invalid_argument("capacity must be > 0");
    }
    double charge() const noexcept { return charge_; }
    double fraction() const noexcept { return charge_ / capacity_; }
    bool draw(double wh) noexcept {                 // can't go negative: the invariant is protected
        if (wh < 0 || wh > charge_) return false;
        charge_ -= wh;
        return true;
    }
private:
    double capacity_, charge_;                      // private: only Battery can break the invariant
};
```

> [!KEY]
> A class is a **boundary around an invariant**. Constructors establish it (or throw), member functions preserve it, and private data means nothing else can violate it. If a class has no invariant, it may just be a `struct` of public data, and that's fine.

**Tell, don't ask**: instead of `if (battery.charge() > need) battery.set_charge(battery.charge() - need);` (asking for data and deciding outside), write `battery.draw(need)`. The logic lives next to the data it protects.

## 3. Value types and entity types

| | Value type | Entity type |
|---|---|---|
| Identity | none: two equal values are interchangeable | yes: *this* robot |
| Copy | cheap and meaningful | usually deleted (`= delete`) or explicit `clone()` |
| Equality | compares contents (`operator==`, often defaulted) | identity, or none at all |
| Mutability | often immutable | stateful |
| Storage | by value, in containers | `unique_ptr`/`shared_ptr`, references |
| Examples | `Pose`, `Meters`, `Color`, `std::string` | `Robot`, `Socket`, `Mission`, `std::thread` |

```cpp
struct Pose {                                      // value: aggregate, comparable, cheap to copy
    double x, y, theta;
    friend bool operator==(const Pose&, const Pose&) = default;   // C++20
};

class Robot {                                      // entity: unique identity and resources
public:
    explicit Robot(std::string id);
    Robot(const Robot&) = delete;                  // two copies of "rover-7" make no sense
    Robot& operator=(const Robot&) = delete;
    Robot(Robot&&) noexcept = default;
};
```

## 4. Strong types: let the compiler check units

The Mars Climate Orbiter was lost in 1999 because one module produced pound-force seconds and another expected newton-seconds. With raw `double`s, `move(distance, time)` and `move(time, distance)` both compile. **Strong types** make such bugs compile errors:

```cpp
template <int L, int T>                           // dimensions: length^L * time^T
struct Quantity {
    double v;
    constexpr explicit Quantity(double x) : v(x) {}
    constexpr Quantity operator+(Quantity o) const { return Quantity(v + o.v); }   // same dims only
    constexpr auto operator<=>(const Quantity&) const = default;
};
template <int L1, int T1, int L2, int T2>
constexpr Quantity<L1 + L2, T1 + T2> operator*(Quantity<L1, T1> a, Quantity<L2, T2> b) { return Quantity<L1 + L2, T1 + T2>(a.v * b.v); }
template <int L1, int T1, int L2, int T2>
constexpr Quantity<L1 - L2, T1 - T2> operator/(Quantity<L1, T1> a, Quantity<L2, T2> b) { return Quantity<L1 - L2, T1 - T2>(a.v / b.v); }

using Meters = Quantity<1, 0>;
using Seconds = Quantity<0, 1>;
using MetersPerSecond = Quantity<1, -1>;

constexpr MetersPerSecond v = Meters(10) / Seconds(4);    // ok: 2.5 m/s
// Meters(1) + Seconds(1);                                 // compile error: different types
template <class A, class B> concept Addable = requires(A a, B b) { a + b; };
static_assert(!Addable<Meters, Seconds>);                  // and we can test that it doesn't compile
```

Zero runtime cost (it's still one `double`), and the dimensional analysis happens at compile time. Libraries such as **mp-units** (proposed for standardisation) and Boost.Units generalise this, and the C++ standard's `std::chrono` uses exactly this technique for durations.

## 5. Responsibility heuristics

- **Single responsibility**: one reason to change. A `Robot` that also parses YAML and renders graphics has three.
- **High cohesion**: a class's members are used together.
- **Low coupling**: a class knows few others, and those mostly through interfaces.
- **Prefer free functions** for operations that need only the public interface (`distance(Pose, Pose)`). That keeps classes small, and it's what the standard library does (`std::begin`, `std::size`).
- **Make illegal states unrepresentable**: use `std::optional` for "maybe", `std::variant` for "one of", enums instead of booleans, and constructors that refuse invalid input.

> [!EXAM]
> **What distinguishes a value type from an entity type, and how does that affect a C++ class's design?**
> A value type is defined entirely by its contents: two objects with equal contents are interchangeable, so it's freely copyable, has content-based equality, is often immutable, and is stored by value. Examples are `Pose`, `Meters` and `std::string`. An entity has an identity independent of its attributes (this robot, this socket) and usually owns resources, so copying is disabled or replaced by an explicit `clone`. Equality, if defined at all, means identity, and entities are held through owning or non-owning pointers. In C++ this decides the special member functions (defaulted copy and `==` for values, deleted copy for entities), the storage and ownership model, and how the objects are passed around.
