---
id: cpp-shape-zoo
title: Polymorphic Shape Zoo
difficulty: Medium
order: 1
tags: virtual functions, abstract classes, clone, unique_ptr
---
## Statement
Design an abstract base class `Shape` and four concrete shapes, then write a factory that reads shapes from a stream.

```cpp
class Shape {
public:
    virtual ~Shape();                                   // must be virtual
    virtual double area() const = 0;
    virtual double perimeter() const = 0;
    virtual std::string name() const = 0;
    virtual std::unique_ptr<Shape> clone() const = 0;   // polymorphic copy
    virtual void scale(double k) = 0;                   // multiply every length by k
    static int live();                                  // number of Shape objects currently alive
};

std::unique_ptr<Shape> make_shape(std::istream& in);    // reads one shape; nullptr on bad input
```

| Input | Shape | name() |
|---|---|---|
| `circle R` | circle with radius R | `circle` |
| `rect W H` | rectangle | `rect` (or `square` if W == H) |
| `tri A B C` | triangle with these sides (Heron's formula); if they violate the triangle inequality (including degenerate ones), `make_shape` returns `nullptr` | `triangle` |
| `poly N S` | regular N-gon (N ≥ 3) with side S: area = N·S² / (4·tan(π/N)) | `N-gon`, e.g. `6-gon` |

Use `π = std::numbers::pi`. Unknown keywords return `nullptr` (the driver prints `bad shape`). The driver reads shapes, clones and scales the whole collection by 2, sorts both collections by area, and prints them with 3 decimals. It also checks that `live()` is correct, which only works if destruction through `unique_ptr<Shape>` reaches the derived destructors.

## Starter
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <cmath>
#include <numbers>

class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
    virtual double perimeter() const = 0;
    virtual std::string name() const = 0;
    virtual std::unique_ptr<Shape> clone() const = 0;
    virtual void scale(double k) = 0;
    static int live() { return 0; }
};

std::unique_ptr<Shape> make_shape(std::istream& in) {
    std::string kind;
    in >> kind;
    return nullptr;
}
```

## Driver
```cpp
#include <vector>
#include <algorithm>
#include <iomanip>
#include <type_traits>

static_assert(std::is_abstract_v<Shape>, "Shape must be abstract");
static_assert(std::has_virtual_destructor_v<Shape>, "Shape needs a virtual destructor");

void print(const std::vector<std::unique_ptr<Shape>>& v) {
    for (const auto& s : v)
        std::cout << "  " << s->name() << " area=" << s->area() << " perim=" << s->perimeter() << '\n';
}

int main() {
    std::cout << std::fixed << std::setprecision(3);
    int n; std::cin >> n;
    std::vector<std::unique_ptr<Shape>> shapes;
    for (int i = 0; i < n; ++i) {
        auto s = make_shape(std::cin);
        if (s) shapes.push_back(std::move(s));
        else std::cout << "bad shape\n";
    }
    std::cout << "live " << Shape::live() << '\n';
    std::vector<std::unique_ptr<Shape>> big;
    for (const auto& s : shapes) { big.push_back(s->clone()); big.back()->scale(2); }
    std::cout << "live " << Shape::live() << '\n';
    auto by_area = [](const auto& a, const auto& b) { return a->area() < b->area(); };
    std::stable_sort(shapes.begin(), shapes.end(), by_area);
    std::stable_sort(big.begin(), big.end(), by_area);
    std::cout << "original:\n"; print(shapes);
    std::cout << "scaled x2:\n"; print(big);
    double total = 0;
    for (const auto& s : shapes) total += s->area();
    std::cout << "total area " << total << '\n';
    big.clear();
    std::cout << "live " << Shape::live() << '\n';
}
```

## Tests
=== sample
5
circle 1
rect 2 3
tri 3 4 5
poly 6 1
hexagon 2
---
bad shape
live 4
live 8
original:
  6-gon area=2.598 perim=6.000
  circle area=3.142 perim=6.283
  rect area=6.000 perim=10.000
  triangle area=6.000 perim=12.000
scaled x2:
  6-gon area=10.392 perim=12.000
  circle area=12.566 perim=12.566
  rect area=24.000 perim=20.000
  triangle area=24.000 perim=24.000
total area 17.740
live 4
=== hidden
6
rect 4 4
tri 1 2 3
tri 1 1 5
tri 2 2 2
poly 5 2
circle 0.5
---
bad shape
bad shape
live 4
live 8
original:
  circle area=0.785 perim=3.142
  triangle area=1.732 perim=6.000
  5-gon area=6.882 perim=10.000
  square area=16.000 perim=16.000
scaled x2:
  circle area=3.142 perim=6.283
  triangle area=6.928 perim=12.000
  5-gon area=27.528 perim=20.000
  square area=64.000 perim=32.000
total area 25.399
live 4
=== hidden
4
poly 4 3
rect 3 2.5
poly 100 0.1
circle 10
---
live 4
live 8
original:
  rect area=7.500 perim=11.000
  100-gon area=7.955 perim=10.000
  4-gon area=9.000 perim=12.000
  circle area=314.159 perim=62.832
scaled x2:
  rect area=30.000 perim=22.000
  100-gon area=31.821 perim=20.000
  4-gon area=36.000 perim=24.000
  circle area=1256.637 perim=125.664
total area 338.614
live 4
=== hidden
1
blob 1 2 3
---
bad shape
live 0
live 0
original:
scaled x2:
total area 0.000
live 0

## Hints
- Put the live counter in `Shape` itself: `Shape() { ++live_; }`, `Shape(const Shape&) { ++live_; }`, and decrement in `~Shape()`. Every derived constructor runs a `Shape` constructor first.
- `clone()` in each concrete class is one line: `return std::make_unique<Circle>(*this);`.
- With the triangle check `a + b <= c` (in any order), the degenerate triangle `1 2 3` is rejected.
- Read the numbers for a shape even if you're going to reject it, so the stream stays in sync.

## Solution
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <cmath>
#include <numbers>

class Shape {
public:
    Shape() { ++live_; }
    Shape(const Shape&) { ++live_; }
    Shape& operator=(const Shape&) = default;
    virtual ~Shape() { --live_; }
    virtual double area() const = 0;
    virtual double perimeter() const = 0;
    virtual std::string name() const = 0;
    virtual std::unique_ptr<Shape> clone() const = 0;
    virtual void scale(double k) = 0;
    static int live() { return live_; }
private:
    static inline int live_ = 0;
};

class Circle final : public Shape {
public:
    explicit Circle(double r) : r_(r) {}
    double area() const override { return std::numbers::pi * r_ * r_; }
    double perimeter() const override { return 2 * std::numbers::pi * r_; }
    std::string name() const override { return "circle"; }
    std::unique_ptr<Shape> clone() const override { return std::make_unique<Circle>(*this); }
    void scale(double k) override { r_ *= k; }
private:
    double r_;
};

class Rect final : public Shape {
public:
    Rect(double w, double h) : w_(w), h_(h) {}
    double area() const override { return w_ * h_; }
    double perimeter() const override { return 2 * (w_ + h_); }
    std::string name() const override { return w_ == h_ ? "square" : "rect"; }
    std::unique_ptr<Shape> clone() const override { return std::make_unique<Rect>(*this); }
    void scale(double k) override { w_ *= k; h_ *= k; }
private:
    double w_, h_;
};

class Triangle final : public Shape {
public:
    Triangle(double a, double b, double c) : a_(a), b_(b), c_(c) {}
    double area() const override {
        double s = perimeter() / 2;
        return std::sqrt(s * (s - a_) * (s - b_) * (s - c_));
    }
    double perimeter() const override { return a_ + b_ + c_; }
    std::string name() const override { return "triangle"; }
    std::unique_ptr<Shape> clone() const override { return std::make_unique<Triangle>(*this); }
    void scale(double k) override { a_ *= k; b_ *= k; c_ *= k; }
private:
    double a_, b_, c_;
};

class RegularPolygon final : public Shape {
public:
    RegularPolygon(int n, double s) : n_(n), s_(s) {}
    double area() const override { return n_ * s_ * s_ / (4 * std::tan(std::numbers::pi / n_)); }
    double perimeter() const override { return n_ * s_; }
    std::string name() const override { return std::to_string(n_) + "-gon"; }
    std::unique_ptr<Shape> clone() const override { return std::make_unique<RegularPolygon>(*this); }
    void scale(double k) override { s_ *= k; }
private:
    int n_;
    double s_;
};

std::unique_ptr<Shape> make_shape(std::istream& in) {
    std::string kind;
    in >> kind;
    if (kind == "circle") { double r; in >> r; return std::make_unique<Circle>(r); }
    if (kind == "rect") { double w, h; in >> w >> h; return std::make_unique<Rect>(w, h); }
    if (kind == "tri") {
        double a, b, c; in >> a >> b >> c;
        if (a + b <= c || a + c <= b || b + c <= a) return nullptr;
        return std::make_unique<Triangle>(a, b, c);
    }
    if (kind == "poly") {
        int n; double s; in >> n >> s;
        if (n < 3) return nullptr;
        return std::make_unique<RegularPolygon>(n, s);
    }
    std::string rest;
    std::getline(in, rest);    // skip the arguments of an unknown shape
    return nullptr;
}
```

- The driver only ever sees `Shape`. Adding a fifth shape means adding one class and one branch in the factory; `print`, sorting and cloning don't change (Open/Closed).
- **`clone()` is the virtual constructor idiom.** You can't copy an object you know only through `Shape*` with `Shape copy = *p;`, which wouldn't compile here (abstract) and would slice anyway. The object copies itself, because only it knows its dynamic type.
- **The live counter** proves the virtual destructor works: `big.clear()` destroys each object through `unique_ptr<Shape>`, the call dispatches to `~Circle` and friends, and they chain to `~Shape`, which decrements. Note that the copy constructor of `Shape` must also count, since `clone` uses it.
- `final` on the leaf classes documents that they aren't meant to be extended, and allows devirtualisation.
