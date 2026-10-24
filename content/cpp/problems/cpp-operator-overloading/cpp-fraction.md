---
id: cpp-fraction
title: Exact Fraction Arithmetic
difficulty: Medium
order: 1
tags: operator overloading, spaceship operator, streams, hidden friends
time_limit: 2
---
## Statement
Floating point can't represent 1/3 exactly. Implement a `Fraction` type with exact rational arithmetic, used like a built-in number:

```cpp
class Fraction {
public:
    Fraction(long long num = 0, long long den = 1);   // implicit from integers is intended; den == 0 throws std::domain_error
    long long num() const;
    long long den() const;
    // + - * /  (binary, symmetric: 1 + f and f + 1 both work), unary -, and += -= *= /=
    // == and <=> (all six comparisons)
    // operator<< prints "n/d", or just "n" when d == 1
    // operator>> reads "n/d" or "n" (no spaces inside a fraction)
};
```

The value is **always stored normalised**: `gcd(|num|, den) == 1` and `den > 0` (so `2/-4` is stored as `-1/2`, and zero as `0/1`). Division by a zero fraction throws `std::domain_error`.

Inputs have numerators and denominators with absolute value ≤ 10⁹. Intermediate products fit in `long long` if you normalise after every operation. Comparisons need 128-bit products (`__int128`) or another overflow-free method.

The driver reads `Q` lines of the form `A OP B`, with OP one of `+ - * / < ==`, then a list of fractions to sort.

## Starter
```cpp
#include <iostream>
#include <compare>
#include <numeric>
#include <stdexcept>

class Fraction {
public:
    Fraction(long long num = 0, long long den = 1) : n_(num), d_(den) {}
    long long num() const { return n_; }
    long long den() const { return d_; }

    friend Fraction operator+(Fraction a, const Fraction& b) { return a; }
    friend Fraction operator-(Fraction a, const Fraction& b) { return a; }
    friend Fraction operator*(Fraction a, const Fraction& b) { return a; }
    friend Fraction operator/(Fraction a, const Fraction& b) { return a; }
    Fraction operator-() const { return *this; }
    friend bool operator==(const Fraction&, const Fraction&) = default;
    friend std::strong_ordering operator<=>(const Fraction& a, const Fraction& b) {
        return std::strong_ordering::equal;
    }
    friend std::ostream& operator<<(std::ostream& os, const Fraction& f) { return os << f.n_ << '/' << f.d_; }
    friend std::istream& operator>>(std::istream& is, Fraction& f) { return is >> f.n_; }
private:
    long long n_, d_;
};
```

## Driver
```cpp
#include <vector>
#include <algorithm>
#include <string>

int main() {
    // symmetry and mixed arithmetic must compile
    Fraction half(1, 2);
    std::cout << "check " << 1 + half << ' ' << half * 4 << ' ' << -half << ' ' << (half += Fraction(1, 3)) << '\n';
    std::cout << "norm " << Fraction(2, -4) << ' ' << Fraction(0, -7) << ' ' << Fraction(10, 5) << '\n';
    try { Fraction bad(1, 0); std::cout << "no throw\n"; }
    catch (const std::domain_error&) { std::cout << "zero den rejected\n"; }

    int q; std::cin >> q;
    while (q--) {
        Fraction a, b; std::string op;
        std::cin >> a >> op >> b;
        try {
            if (op == "+") std::cout << a + b;
            else if (op == "-") std::cout << a - b;
            else if (op == "*") std::cout << a * b;
            else if (op == "/") std::cout << a / b;
            else if (op == "<") std::cout << (a < b ? "true" : "false");
            else if (op == "==") std::cout << (a == b ? "true" : "false");
        } catch (const std::domain_error&) { std::cout << "undefined"; }
        std::cout << '\n';
    }
    int k; std::cin >> k;
    std::vector<Fraction> v(k);
    for (auto& f : v) std::cin >> f;
    std::sort(v.begin(), v.end());
    Fraction sum;
    for (const auto& f : v) sum += f;
    std::cout << "sorted";
    for (const auto& f : v) std::cout << ' ' << f;
    std::cout << "\nsum " << sum << '\n';
}
```

## Tests
=== sample
6
1/2 + 1/3
3/4 - 3/4
2/3 * 9/4
1/2 / 0
-1/3 < -1/4
2/4 == 1/2
4
1/2 -3 7/8 2/3
---
check 3/2 2 -1/2 5/6
norm -1/2 0 2
zero den rejected
5/6
0
3/2
undefined
true
true
sorted -3 1/2 2/3 7/8
sum -23/24
=== hidden
8
1000000000/999999999 - 999999999/1000000000
999999937/1000000000 < 999999938/1000000001
1000000000/1 * 1000000000/1
-5 / -10/4
0 == 0/5
7/-14 + 1/2
1/1000000000 < 1/999999999
-1000000000/3 * 3/-1000000000
5
1000000000/999999999 999999999/1000000000 1 -7 0
---
check 3/2 2 -1/2 5/6
norm -1/2 0 2
zero den rejected
1999999999/999999999000000000
true
1000000000000000000
2
true
0
true
1
sorted -7 0 999999999/1000000000 1 1000000000/999999999
sum -3999999995999999999/999999999000000000
=== hidden
3
3/9 + 2/6
1/6 - 1/2
1/2 / 1/2
6
1/2 2/4 -1/2 3/6 0/9 -0/3
---
check 3/2 2 -1/2 5/6
norm -1/2 0 2
zero den rejected
2/3
-1/3
1
sorted -1/2 0 0 1/2 1/2 1/2
sum 1

## Hints
- Normalise in the constructor: divide by `std::gcd(|n|, |d|)`, and flip both signs if `d < 0`. Every operator returns a value built through that constructor.
- `a/b + c/d = (a·d + c·b) / (b·d)`. With each part ≤ 10⁹, these products fit in `long long`.
- `a/b < c/d` is equivalent to `a·d < c·b` because both denominators are positive. Compute the products in `__int128`, since numerators can grow past 10⁹ in the running sum.
- Implement `+=` and friends, then write `+` as `a += b; return a;`.
- For `>>`: read a `long long`, then `if (is.peek() == '/') { is.get(); is >> d; }`.

## Solution
```cpp
#include <iostream>
#include <compare>
#include <numeric>
#include <stdexcept>

class Fraction {
public:
    Fraction(long long num = 0, long long den = 1) : n_(num), d_(den) {
        if (d_ == 0) throw std::domain_error("zero denominator");
        normalise();
    }
    long long num() const { return n_; }
    long long den() const { return d_; }

    Fraction& operator+=(const Fraction& o) { return *this = Fraction(n_ * o.d_ + o.n_ * d_, d_ * o.d_); }
    Fraction& operator-=(const Fraction& o) { return *this = Fraction(n_ * o.d_ - o.n_ * d_, d_ * o.d_); }
    Fraction& operator*=(const Fraction& o) {
        // cross-cancel first so the products stay small
        long long g1 = std::gcd(n_, o.d_), g2 = std::gcd(o.n_, d_);
        if (g1 == 0) g1 = 1;
        if (g2 == 0) g2 = 1;
        return *this = Fraction((n_ / g1) * (o.n_ / g2), (d_ / g2) * (o.d_ / g1));
    }
    Fraction& operator/=(const Fraction& o) {
        if (o.n_ == 0) throw std::domain_error("division by zero");
        return *this *= Fraction(o.d_, o.n_);
    }

    friend Fraction operator+(Fraction a, const Fraction& b) { return a += b; }
    friend Fraction operator-(Fraction a, const Fraction& b) { return a -= b; }
    friend Fraction operator*(Fraction a, const Fraction& b) { return a *= b; }
    friend Fraction operator/(Fraction a, const Fraction& b) { return a /= b; }
    Fraction operator-() const { return Fraction(-n_, d_); }

    friend bool operator==(const Fraction&, const Fraction&) = default;   // valid: always normalised
    friend std::strong_ordering operator<=>(const Fraction& a, const Fraction& b) {
        __int128 l = static_cast<__int128>(a.n_) * b.d_, r = static_cast<__int128>(b.n_) * a.d_;
        return l < r ? std::strong_ordering::less
             : l > r ? std::strong_ordering::greater : std::strong_ordering::equal;
    }

    friend std::ostream& operator<<(std::ostream& os, const Fraction& f) {
        os << f.n_;
        if (f.d_ != 1) os << '/' << f.d_;
        return os;
    }
    friend std::istream& operator>>(std::istream& is, Fraction& f) {
        long long n, d = 1;
        if (!(is >> n)) return is;
        if (is.peek() == '/') { is.get(); is >> d; }
        f = Fraction(n, d);
        return is;
    }

private:
    void normalise() {
        long long g = std::gcd(n_, d_);   // std::gcd works on absolute values
        n_ /= g;
        d_ /= g;
        if (d_ < 0) { n_ = -n_; d_ = -d_; }
    }
    long long n_, d_;
};
```

**Design notes:**
- **One normalising constructor.** Every operation produces its result by constructing a new `Fraction`, so the invariant (lowest terms, positive denominator) can't be broken. Because the representation is canonical, the defaulted member-wise `==` is correct: equal values have identical members.
- **Hidden friends for symmetric operators.** `operator+` takes its left operand by value (a copy it can modify), applies `+=`, and returns it. Because it's a non-member, the implicit `Fraction(long long)` conversion applies to *either* side, so `1 + half` works. A member `operator+` would reject `1 + half`.
- **`<=>` returns `strong_ordering`.** This defines `<`, `<=`, `>` and `>=`, which `std::sort` uses. Cross-multiplying in `__int128` avoids overflow, and the positive denominators keep the inequality direction correct.
- **Cross-cancellation in `*=`** keeps intermediate values small, so `1e9/1 * 1e9/1` is the only case that produces a large result, and that fits in `long long`.
