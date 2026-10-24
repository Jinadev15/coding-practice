---
id: cpp-expr-tree
title: Symbolic Expression Trees
difficulty: Hard
order: 2
tags: polymorphism, composite pattern, recursion, clone, symbolic differentiation
---
## Statement
Build a polymorphic expression tree (the **Composite** pattern) that can be evaluated, printed and **differentiated symbolically**, like a tiny autodiff engine.

```cpp
using Env = std::map<char, double>;

class Expr {
public:
    virtual ~Expr() = default;
    virtual double eval(const Env& env) const = 0;
    virtual std::string str() const = 0;
    virtual std::unique_ptr<Expr> derive(char var) const = 0;
    virtual std::unique_ptr<Expr> clone() const = 0;
};

std::unique_ptr<Expr> parse(std::istream& in);   // reads ONE expression in prefix notation
```

**Prefix input**: tokens separated by spaces. A token is a non-negative integer, a single lowercase letter (a variable), one of the binary operators `+ - * /` followed by its two operands, or `neg` followed by one operand. For example, `* + x 2 y` means `(x + 2) * y`.

**`str()`**: numbers print as integers (`3`), variables as their letter, binary operations fully parenthesised with spaces: `((x + 2) * y)`, and negation as `(-u)`.

**`derive(v)`** must follow **exactly** these rules (no simplification), where `du` means `u.derive(v)`:

| Expression | Derivative |
|---|---|
| number | `0` |
| variable | `1` if it's `v`, else `0` |
| `u + v`, `u - v` | `(du + dv)`, `(du - dv)` |
| `u * v` | `((du * v) + (u * dv))` |
| `u / v` | `(((du * v) - (u * dv)) / (v * v))` |
| `neg u` | `(-du)` |

The input has `Q` queries. Each query is two lines: the expression, then the variable values as `name value` pairs. The driver prints the expression, its value, the derivative with respect to `x`, and the derivative's value.

## Starter
```cpp
#include <iostream>
#include <map>
#include <memory>
#include <string>

using Env = std::map<char, double>;

class Expr {
public:
    virtual ~Expr() = default;
    virtual double eval(const Env& env) const = 0;
    virtual std::string str() const = 0;
    virtual std::unique_ptr<Expr> derive(char var) const = 0;
    virtual std::unique_ptr<Expr> clone() const = 0;
};

std::unique_ptr<Expr> parse(std::istream& in) {
    return nullptr;
}
```

## Driver
```cpp
#include <sstream>

int main() {
    int q; std::cin >> q;
    std::string line;
    std::getline(std::cin, line);
    while (q--) {
        std::getline(std::cin, line);
        std::istringstream ein(line);
        std::unique_ptr<Expr> e = parse(ein);
        std::getline(std::cin, line);
        std::istringstream vin(line);
        Env env; char name; double val;
        while (vin >> name >> val) env[name] = val;
        std::unique_ptr<Expr> d = e->derive('x');
        std::unique_ptr<Expr> copy = e->clone();
        e.reset();                        // the clone must be a deep, independent copy
        std::cout << copy->str() << " = " << copy->eval(env) << '\n';
        std::cout << "d/dx " << d->str() << " = " << d->eval(env) << '\n';
    }
}
```

## Tests
=== sample
3
* + x 2 y
x 3 y 4
/ 1 x
x 2
neg * x x
x 5
---
((x + 2) * y) = 20
d/dx (((1 + 0) * y) + ((x + 2) * 0)) = 4
(1 / x) = 0.5
d/dx (((0 * x) - (1 * 1)) / (x * x)) = -0.25
(-(x * x)) = -25
d/dx (-((1 * x) + (x * 1))) = -10
=== hidden
4
7
x 1
y
x 1 y 9
- * 3 * x x * 2 x
x 4
/ + x 1 - x 1
x 3
---
7 = 7
d/dx 0 = 0
y = 9
d/dx 0 = 0
((3 * (x * x)) - (2 * x)) = 40
d/dx (((0 * (x * x)) + (3 * ((1 * x) + (x * 1)))) - ((0 * x) + (2 * 1))) = 22
((x + 1) / (x - 1)) = 2
d/dx ((((1 + 0) * (x - 1)) - ((x + 1) * (1 - 0))) / ((x - 1) * (x - 1))) = -0.5
=== hidden
2
+ * x * x x neg / y x
x 2 y 8
* * x y * x z
x 1.5 y 2 z -1
---
((x * (x * x)) + (-(y / x))) = 4
d/dx (((1 * (x * x)) + (x * ((1 * x) + (x * 1)))) + (-(((0 * x) - (y * 1)) / (x * x)))) = 14
((x * y) * (x * z)) = -4.5
d/dx ((((1 * y) + (x * 0)) * (x * z)) + ((x * y) * ((1 * z) + (x * 0)))) = -6
=== hidden
1
+ + + + x x x x x
x 0.25
---
((((x + x) + x) + x) + x) = 1.25
d/dx ((((1 + 1) + 1) + 1) + 1) = 5

## Hints
- One class per node kind: `Num`, `Var`, `Neg`, and one class for binary operators, either a single `Bin` holding the operator character, or `Add`/`Sub`/`Mul`/`Div`.
- `parse` is naturally recursive: read a token; if it's an operator, call `parse` for its operands.
- The product rule needs `u` and `v` themselves inside the derivative, but they're owned by the original tree. That's what `clone()` is for.
- Print numbers with `std::to_string(static_cast<long long>(value))` (input numbers are integers).

## Solution
```cpp
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <cctype>

using Env = std::map<char, double>;

class Expr {
public:
    virtual ~Expr() = default;
    virtual double eval(const Env& env) const = 0;
    virtual std::string str() const = 0;
    virtual std::unique_ptr<Expr> derive(char var) const = 0;
    virtual std::unique_ptr<Expr> clone() const = 0;
};
using P = std::unique_ptr<Expr>;

class Num final : public Expr {
public:
    explicit Num(double v) : v_(v) {}
    double eval(const Env&) const override { return v_; }
    std::string str() const override { return std::to_string(static_cast<long long>(v_)); }
    P derive(char) const override { return std::make_unique<Num>(0); }
    P clone() const override { return std::make_unique<Num>(*this); }
private:
    double v_;
};

class Var final : public Expr {
public:
    explicit Var(char n) : n_(n) {}
    double eval(const Env& env) const override { return env.at(n_); }
    std::string str() const override { return std::string(1, n_); }
    P derive(char v) const override { return std::make_unique<Num>(v == n_ ? 1 : 0); }
    P clone() const override { return std::make_unique<Var>(*this); }
private:
    char n_;
};

class Neg final : public Expr {
public:
    explicit Neg(P u) : u_(std::move(u)) {}
    double eval(const Env& env) const override { return -u_->eval(env); }
    std::string str() const override { return "(-" + u_->str() + ")"; }
    P derive(char v) const override { return std::make_unique<Neg>(u_->derive(v)); }
    P clone() const override { return std::make_unique<Neg>(u_->clone()); }
private:
    P u_;
};

class Bin final : public Expr {
public:
    Bin(char op, P l, P r) : op_(op), l_(std::move(l)), r_(std::move(r)) {}
    double eval(const Env& env) const override {
        double a = l_->eval(env), b = r_->eval(env);
        switch (op_) {
            case '+': return a + b;
            case '-': return a - b;
            case '*': return a * b;
            default:  return a / b;
        }
    }
    std::string str() const override {
        return "(" + l_->str() + " " + op_ + " " + r_->str() + ")";
    }
    P derive(char v) const override {
        auto mk = [](char op, P a, P b) { return std::make_unique<Bin>(op, std::move(a), std::move(b)); };
        switch (op_) {
            case '+': case '-':
                return mk(op_, l_->derive(v), r_->derive(v));
            case '*':
                return mk('+', mk('*', l_->derive(v), r_->clone()), mk('*', l_->clone(), r_->derive(v)));
            default:
                return mk('/',
                          mk('-', mk('*', l_->derive(v), r_->clone()), mk('*', l_->clone(), r_->derive(v))),
                          mk('*', r_->clone(), r_->clone()));
        }
    }
    P clone() const override { return std::make_unique<Bin>(op_, l_->clone(), r_->clone()); }
private:
    char op_;
    P l_, r_;
};

P parse(std::istream& in) {
    std::string t;
    in >> t;
    if (t == "neg") return std::make_unique<Neg>(parse(in));
    if (t.size() == 1 && std::string("+-*/").find(t[0]) != std::string::npos) {
        P l = parse(in);
        P r = parse(in);
        return std::make_unique<Bin>(t[0], std::move(l), std::move(r));
    }
    if (std::isalpha(static_cast<unsigned char>(t[0]))) return std::make_unique<Var>(t[0]);
    return std::make_unique<Num>(std::stod(t));
}
```

**How it fits together:**
- **Composite pattern:** a `Bin` *is an* `Expr` and *has* two `Expr` children. Client code (the driver) treats leaves and whole trees uniformly through the `Expr` interface.
- **Ownership:** every node owns its children through `unique_ptr`, so destroying the root frees the whole tree (and the virtual destructor makes this work through `Expr*`). There are no leaks and no manual `delete`.
- **Why `clone()`:** the derivative of `u * v` contains `u` and `v` again, but those subtrees belong to the original tree, and a `unique_ptr` can't have two owners. `clone()` makes a deep copy, polymorphically, because each node knows its own type. The driver checks this by destroying the original before using the copy.
- **Order of evaluation:** in `parse`, `l` and `r` are parsed in separate statements. Writing `make_unique<Bin>(t[0], parse(in), parse(in))` would be a bug, because function arguments may be evaluated in either order.

This is a miniature of how symbolic math libraries (SymPy, CasADi used in robot optimal control) and autodiff frameworks represent computations as polymorphic graphs.
