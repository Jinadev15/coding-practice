---
id: cpp-vehicle-chain
title: Vehicle Hierarchy and Construction Order
difficulty: Medium
order: 1
tags: inheritance, constructors, name hiding, inheriting constructors
---
## Statement
Build a three-level hierarchy `Vehicle` → `Car` → `ElectricCar`. The provided `Tag` struct prints a line when it's constructed and destroyed, which lets the tests check your **construction and destruction order** exactly. Don't modify `Tag`.

**`Vehicle`**
- Data member `Tag tag_` named `"chassis"`.
- Constructor `Vehicle(std::string id, int wheels)`: its body prints `Vehicle(ID, WHEELS)`. Destructor prints `~Vehicle(ID)`.
- `const std::string& id() const`, `int wheels() const`.
- A **protected** helper `void log(const std::string& msg) const` that prints `ID: msg`.

**`Car : public Vehicle`**
- Data member `Tag tag_` named `"engine"`.
- Constructor `explicit Car(std::string id)`: a car has 4 wheels. Its body prints `Car(ID)`. Destructor prints `~Car(ID)`.
- `void set(int kmh)` logs `speed KMH km/h`. `void set(double ms)` logs `speed MS m/s` (print the double with `<<`).

**`ElectricCar : public Car`**
- Data member `Tag tag_` named `"battery"`.
- Gets **all of `Car`'s constructors by inheriting them** (`using`). Write no constructor of your own.
- Destructor prints `~ElectricCar(ID)`.
- `void set(const std::string& mode)` logs `mode MODE`. `set(int)` and `set(double)` from `Car` must **still work** on an `ElectricCar`.

The driver processes commands `car ID`, `ev ID`, `set ID 30`, `set ID 2.5`, `set ID eco` and `drop ID`, then destroys everything left in reverse creation order.

## Starter
```cpp
#include <iostream>
#include <string>

// provided: do not modify
struct Tag {
    std::string name;
    explicit Tag(std::string n) : name(std::move(n)) { std::cout << "  +" << name << '\n'; }
    ~Tag() { std::cout << "  -" << name << '\n'; }
};

class Vehicle {
public:
    Vehicle(std::string id, int wheels) : id_(id), wheels_(wheels) {}
    const std::string& id() const { return id_; }
    int wheels() const { return wheels_; }
protected:
    void log(const std::string& msg) const { std::cout << id_ << ": " << msg << '\n'; }
private:
    std::string id_;
    int wheels_;
};

class Car : public Vehicle {
public:
    explicit Car(std::string id) : Vehicle(id, 4) {}
};

class ElectricCar : public Car {
public:
    using Car::Car;
};
```

## Driver
```cpp
#include <map>
#include <memory>
#include <vector>
#include <type_traits>
#include <algorithm>
#include <cctype>

static_assert(std::is_base_of_v<Vehicle, ElectricCar>);
static_assert(!std::is_convertible_v<std::string, Car>, "Car(string) must be explicit");

int main() {
    // separate owners: these classes have non-virtual destructors, so never delete through a base pointer
    std::map<std::string, std::unique_ptr<Car>> cars;
    std::map<std::string, std::unique_ptr<ElectricCar>> evs;
    std::vector<std::string> order;
    std::string cmd, id;
    while (std::cin >> cmd >> id) {
        if (cmd == "car") {
            cars[id] = std::make_unique<Car>(id);
            order.push_back(id);
        } else if (cmd == "ev") {
            evs[id] = std::make_unique<ElectricCar>(id);
            order.push_back(id);
        } else if (cmd == "set") {
            std::string v; std::cin >> v;
            bool is_num = !v.empty() && (std::isdigit(static_cast<unsigned char>(v[0])) != 0);
            bool is_real = v.find('.') != std::string::npos;
            if (cars.count(id)) {
                Car& c = *cars[id];
                if (is_real) c.set(std::stod(v)); else if (is_num) c.set(std::stoi(v));
                else std::cout << id << ": cars have no modes\n";
            } else {
                ElectricCar& e = *evs[id];
                if (is_real) e.set(std::stod(v)); else if (is_num) e.set(std::stoi(v)); else e.set(v);
                const Vehicle& base = e;      // derived-to-base reference: no copy, no slicing
                std::cout << "  (" << base.id() << " has " << base.wheels() << " wheels)\n";
            }
        } else if (cmd == "drop") {
            std::cout << "drop " << id << '\n';
            cars.erase(id);
            evs.erase(id);
            order.erase(std::find(order.begin(), order.end(), id));
        }
    }
    std::cout << "shutdown\n";
    for (auto it = order.rbegin(); it != order.rend(); ++it) {
        cars.erase(*it);
        evs.erase(*it);
    }
}
```

## Tests
=== sample
car c1
ev e1
set c1 30
set e1 eco
set e1 2.5
drop c1
---
  +chassis
Vehicle(c1, 4)
  +engine
Car(c1)
  +chassis
Vehicle(e1, 4)
  +engine
Car(e1)
  +battery
c1: speed 30 km/h
e1: mode eco
  (e1 has 4 wheels)
e1: speed 2.5 m/s
  (e1 has 4 wheels)
drop c1
~Car(c1)
  -engine
~Vehicle(c1)
  -chassis
shutdown
~ElectricCar(e1)
  -battery
~Car(e1)
  -engine
~Vehicle(e1)
  -chassis
=== hidden
ev a
ev b
set a 100
set b 0.5
set a sport
drop a
car z
set z eco
set z 7
---
  +chassis
Vehicle(a, 4)
  +engine
Car(a)
  +battery
  +chassis
Vehicle(b, 4)
  +engine
Car(b)
  +battery
a: speed 100 km/h
  (a has 4 wheels)
b: speed 0.5 m/s
  (b has 4 wheels)
a: mode sport
  (a has 4 wheels)
drop a
~ElectricCar(a)
  -battery
~Car(a)
  -engine
~Vehicle(a)
  -chassis
  +chassis
Vehicle(z, 4)
  +engine
Car(z)
z: cars have no modes
z: speed 7 km/h
shutdown
~Car(z)
  -engine
~Vehicle(z)
  -chassis
~ElectricCar(b)
  -battery
~Car(b)
  -engine
~Vehicle(b)
  -chassis
=== hidden
car only
set only 1.25
---
  +chassis
Vehicle(only, 4)
  +engine
Car(only)
only: speed 1.25 m/s
shutdown
~Car(only)
  -engine
~Vehicle(only)
  -chassis

## Hints
- Construction order: base class, then members, then your constructor body. So for an `ElectricCar` you'll see `+chassis`, `Vehicle(...)`, `+engine`, `Car(...)`, `+battery`, and nothing more, because inherited constructors have no body of their own.
- Each class can have its own member called `tag_`. They're different members (the derived one hides the base one's name).
- Declaring `set(const std::string&)` in `ElectricCar` hides **both** `Car::set` overloads. Bring them back with `using Car::set;`.

## Solution
```cpp
#include <iostream>
#include <string>
#include <utility>

// provided: do not modify
struct Tag {
    std::string name;
    explicit Tag(std::string n) : name(std::move(n)) { std::cout << "  +" << name << '\n'; }
    ~Tag() { std::cout << "  -" << name << '\n'; }
};

class Vehicle {
public:
    Vehicle(std::string id, int wheels) : id_(std::move(id)), wheels_(wheels) {
        std::cout << "Vehicle(" << id_ << ", " << wheels_ << ")\n";
    }
    ~Vehicle() { std::cout << "~Vehicle(" << id_ << ")\n"; }
    const std::string& id() const { return id_; }
    int wheels() const { return wheels_; }
protected:
    void log(const std::string& msg) const { std::cout << id_ << ": " << msg << '\n'; }
private:
    std::string id_;
    int wheels_;
    Tag tag_{"chassis"};
};

class Car : public Vehicle {
public:
    explicit Car(std::string id) : Vehicle(std::move(id), 4) { std::cout << "Car(" << this->id() << ")\n"; }
    ~Car() { std::cout << "~Car(" << id() << ")\n"; }
    void set(int kmh) { log("speed " + std::to_string(kmh) + " km/h"); }
    void set(double ms) {
        std::cout << id() << ": speed " << ms << " m/s\n";
    }
private:
    Tag tag_{"engine"};
};

class ElectricCar : public Car {
public:
    using Car::Car;     // inherit Car's constructors
    using Car::set;     // un-hide set(int) and set(double)
    ~ElectricCar() { std::cout << "~ElectricCar(" << id() << ")\n"; }
    void set(const std::string& mode) { log("mode " + mode); }
private:
    Tag tag_{"battery"};
};
```

**What the output shows:**
- **Construction:** base subobject first (`+chassis`, then the `Vehicle` body), then `Car`'s members and body, then `ElectricCar`'s member `+battery`. The inherited constructor has no body, so nothing more is printed.
- **Destruction is the exact mirror image:** derived destructor body, derived members, then the base, all the way down. RAII cleanup composes automatically through a hierarchy.
- **Name hiding:** without `using Car::set;`, the call `e.set(30)` doesn't compile, because name lookup finds `ElectricCar::set(const std::string&)` and stops there, and `int` doesn't convert to `std::string`.
- **No slicing:** the driver views the `ElectricCar` as `const Vehicle&`, a reference to the base subobject inside the same object.
- **Why the driver keeps separate owners:** none of these destructors is virtual, so destroying an `ElectricCar` through a `unique_ptr<Car>` would be undefined behaviour (next lesson).
