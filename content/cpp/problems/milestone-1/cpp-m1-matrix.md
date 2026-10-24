---
id: cpp-m1-matrix
title: Integer Matrix Library
difficulty: Hard
order: 3
tags: RAII, rule of five, operator overloading, exceptions, algorithms
---
## Statement
Implement an exact integer matrix class that owns its storage **manually** (`std::unique_ptr<long long[]>` or a raw `new[]`; **no `std::vector`**, so you practise the Rule of Five):

```cpp
class Matrix {
public:
    Matrix(std::size_t rows, std::size_t cols);               // zero-filled; throws std::invalid_argument if either is 0
    static Matrix identity(std::size_t n);
    Matrix(const Matrix&); Matrix(Matrix&&) noexcept;
    Matrix& operator=(const Matrix&); Matrix& operator=(Matrix&&) noexcept;
    ~Matrix();

    std::size_t rows() const; std::size_t cols() const;
    long long& operator()(std::size_t r, std::size_t c);       // bounds-checked: std::out_of_range
    long long operator()(std::size_t r, std::size_t c) const;

    Matrix& operator+=(const Matrix&); Matrix& operator-=(const Matrix&);   // std::invalid_argument on a shape mismatch
    friend Matrix operator+(Matrix, const Matrix&);
    friend Matrix operator-(Matrix, const Matrix&);
    friend Matrix operator*(const Matrix&, const Matrix&);     // matrix product; invalid_argument if inner dims differ
    friend Matrix operator*(long long k, Matrix m);            // scalar
    friend bool operator==(const Matrix&, const Matrix&);      // same shape and elements
    Matrix transposed() const;
    long long det() const;              // exact (the Bareiss algorithm); invalid_argument if not square
    Matrix pow_mod(unsigned long long e, long long mod) const; // square only; fast exponentiation, entries reduced into [0, mod)
    friend std::ostream& operator<<(std::ostream&, const Matrix&);   // rows on lines, elements separated by single spaces
};
```

The driver reads named matrices and evaluates commands: `let NAME R C v11 v12 ...`, `add A B`, `sub A B`, `mul A B`, `scale K A`, `T A`, `det A`, `pow A E MOD`, `eq A B`, `at A r c`, and `copytest A`, which checks copy/move semantics and independence. Errors print `error: invalid_argument` or `error: out_of_range`.

Determinants in the tests fit in `long long`, and so do the intermediate values of the Bareiss algorithm (but they wouldn't with naive cofactor expansion on a 12×12 matrix, which is also far too slow).

## Starter
```cpp
#include <cstddef>
#include <memory>
#include <ostream>
#include <stdexcept>

class Matrix {
public:
    Matrix(std::size_t rows, std::size_t cols) : r_(rows), c_(cols) {}
    static Matrix identity(std::size_t n) { return Matrix(n, n); }
    std::size_t rows() const { return r_; }
    std::size_t cols() const { return c_; }
    long long& operator()(std::size_t, std::size_t) { static long long x; return x; }
    long long operator()(std::size_t, std::size_t) const { return 0; }
    Matrix& operator+=(const Matrix&) { return *this; }
    Matrix& operator-=(const Matrix&) { return *this; }
    friend Matrix operator+(Matrix a, const Matrix&) { return a; }
    friend Matrix operator-(Matrix a, const Matrix&) { return a; }
    friend Matrix operator*(const Matrix& a, const Matrix&) { return a; }
    friend Matrix operator*(long long, Matrix m) { return m; }
    friend bool operator==(const Matrix&, const Matrix&) { return true; }
    Matrix transposed() const { return *this; }
    long long det() const { return 0; }
    Matrix pow_mod(unsigned long long, long long) const { return *this; }
    friend std::ostream& operator<<(std::ostream& os, const Matrix&) { return os; }
private:
    std::size_t r_, c_;
};
```

## Driver
```cpp
#include <iostream>
#include <map>
#include <string>
#include <type_traits>
#include <utility>

static_assert(std::is_nothrow_move_constructible_v<Matrix>);
static_assert(!std::is_default_constructible_v<Matrix>, "a Matrix always has a shape");

int main() {
    std::map<std::string, Matrix> env;
    std::string cmd;
    auto get = [&](const std::string& n) -> const Matrix& { return env.at(n); };
    while (std::cin >> cmd) {
        try {
            if (cmd == "let") {
                std::string n; std::size_t r, c; std::cin >> n >> r >> c;
                Matrix m(r, c);
                for (std::size_t i = 0; i < r; ++i)
                    for (std::size_t j = 0; j < c; ++j) std::cin >> m(i, j);
                env.insert_or_assign(n, std::move(m));
            } else if (cmd == "add" || cmd == "sub" || cmd == "mul" || cmd == "eq") {
                std::string a, b; std::cin >> a >> b;
                if (cmd == "eq") { std::cout << (get(a) == get(b) ? "equal" : "different") << '\n'; continue; }
                Matrix r = cmd == "add" ? get(a) + get(b) : cmd == "sub" ? get(a) - get(b) : get(a) * get(b);
                std::cout << r << '\n';
            } else if (cmd == "scale") {
                long long k; std::string a; std::cin >> k >> a;
                std::cout << k * get(a) << '\n';
            } else if (cmd == "T") {
                std::string a; std::cin >> a;
                std::cout << get(a).transposed() << '\n';
            } else if (cmd == "det") {
                std::string a; std::cin >> a;
                std::cout << get(a).det() << '\n';
            } else if (cmd == "pow") {
                std::string a; unsigned long long e; long long mod; std::cin >> a >> e >> mod;
                std::cout << get(a).pow_mod(e, mod) << '\n';
            } else if (cmd == "at") {
                std::string a; std::size_t r, c; std::cin >> a >> r >> c;
                std::cout << get(a)(r, c) << '\n';
            } else if (cmd == "zero") {
                std::size_t r, c; std::cin >> r >> c;
                Matrix z(r, c);
                std::cout << z << '\n';
            } else if (cmd == "copytest") {
                std::string a; std::cin >> a;
                Matrix c = get(a);
                c(0, 0) += 100;
                Matrix m = std::move(c);
                Matrix d = Matrix::identity(m.rows());
                d = m;
                d = d;
                d(0, 0) -= 100;
                std::cout << "original " << (get(a)(0, 0)) << " moved " << m(0, 0) << " assigned-back-equal " << (d == get(a)) << '\n';
            }
        } catch (const std::invalid_argument&) {
            std::cout << "error: invalid_argument\n";
        } catch (const std::out_of_range&) {
            std::cout << "error: out_of_range\n";
        }
    }
}
```

## Tests
=== sample
let A 2 2 1 2 3 4
let B 2 2 5 6 7 8
let V 2 1 1 -1
add A B
mul A B
mul A V
mul V A
scale -2 A
T V
det A
pow A 10 1000000007
eq A A
at A 1 1
at A 2 0
copytest A
---
6 8
10 12
19 22
43 50
-1
-1
error: invalid_argument
-2 -4
-6 -8
1 -1
-2
4783807 6972050
10458075 15241882
equal
4
error: out_of_range
original 1 moved 101 assigned-back-equal 1
=== hidden
let I 3 3 1 0 0 0 1 0 0 0 1
det I
let S 3 3 2 -3 1 2 0 -1 1 4 5
det S
let Z 3 3 1 2 3 4 5 6 7 8 9
det Z
let R 2 3 1 2 3 4 5 6
det R
mul R R
T R
mul R I
add R I
zero 0 3
let F 2 2 1 1 1 0
pow F 90 1000000007
pow F 0 7
pow F 1 7
let N 1 1 -5
pow N 3 7
scale 0 R
copytest S
---
1
49
0
error: invalid_argument
error: invalid_argument
1 4
2 5
3 6
1 2 3
4 5 6
error: invalid_argument
error: invalid_argument
755204270 210345902
210345902 544858368
1 0
0 1
1 1
1 0
1
0 0 0
0 0 0
original 2 moved 102 assigned-back-equal 1
=== hidden
let H 12 12 2 1 0 0 0 0 0 0 0 0 0 1 1 2 1 0 0 0 0 0 0 0 0 0 0 1 2 1 0 0 0 0 0 0 0 0 0 0 1 2 1 0 0 0 0 0 0 0 0 0 0 1 2 1 0 0 0 0 0 0 0 0 0 0 1 2 1 0 0 0 0 0 0 0 0 0 0 1 2 1 0 0 0 0 0 0 0 0 0 0 1 2 1 0 0 0 0 0 0 0 0 0 0 1 2 1 0 0 0 0 0 0 0 0 0 0 1 2 1 0 0 0 0 0 0 0 0 0 0 1 2 1 1 0 0 0 0 0 0 0 0 0 1 2
det H
let P 4 4 0 0 0 1 0 0 1 0 0 1 0 0 1 0 0 0
det P
let Q 4 4 3 1 4 1 5 9 2 6 5 3 5 8 9 7 9 3
det Q
pow Q 1000000000000 998244353
eq Q P
let G 12 12 0 -1 2 1 2 -1 -2 0 -3 -1 0 -1 2 3 0 2 3 1 -2 1 -3 2 1 -2 0 -1 -2 -1 -2 -3 1 3 -2 -3 1 2 3 -1 2 0 3 3 -3 -3 -3 3 2 1 -2 -3 0 0 -3 2 0 -2 1 -1 1 1 -2 2 -3 1 -2 1 3 -3 0 1 0 2 1 0 0 1 0 1 -3 2 2 -3 -2 3 2 -1 -1 -1 3 2 0 2 -1 -3 -1 -2 -1 -1 -1 1 1 3 3 1 -2 -3 0 3 3 0 -3 1 -3 -2 2 0 -3 0 -2 3 1 -3 3 1 -2 -2 -3 2 -1 -3 0 -1 0 -1 1 2 2 -3 1 0 -1 -2 -1 -1
det G
---
0
1
98
22752176 500247288 802965500 504920132
688651649 925858105 376595419 424371080
11024570 92715490 16044615 47355598
345151669 683142792 811475471 848211608
different
33825001

## Hints
- Store `std::unique_ptr<long long[]> data_` with element `(r, c)` at `data_[r * cols + c]` (row-major). Copy construction allocates and copies; moves just transfer the pointer and the shape.
- Moved-from objects only need to be destructible and assignable. With `unique_ptr`, the defaulted move operations are already correct and `noexcept`.
- Bareiss algorithm (fraction-free Gaussian elimination): with `prev = 1`, for each pivot k, swap in a non-zero pivot row if needed (flipping the sign), then for i, j > k: `a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) / prev`. The division is **exact**. Set `prev = a[k][k]`. The determinant is `sign * a[n-1][n-1]`.
- `pow_mod`: square-and-multiply on matrices, reducing every entry with `((x % m) + m) % m`. Use `__int128` for the products inside the multiplication to avoid overflow before reducing.

## Solution
```cpp
#include <cstddef>
#include <memory>
#include <ostream>
#include <stdexcept>
#include <algorithm>
#include <utility>

class Matrix {
public:
    Matrix(std::size_t rows, std::size_t cols) : r_(rows), c_(cols) {
        if (rows == 0 || cols == 0) throw std::invalid_argument("empty matrix");
        data_ = std::make_unique<long long[]>(rows * cols);   // value-initialised: zeros
    }
    static Matrix identity(std::size_t n) {
        Matrix m(n, n);
        for (std::size_t i = 0; i < n; ++i) m.at(i, i) = 1;
        return m;
    }
    Matrix(const Matrix& o) : r_(o.r_), c_(o.c_), data_(std::make_unique<long long[]>(o.r_ * o.c_)) {
        std::copy_n(o.data_.get(), r_ * c_, data_.get());
    }
    Matrix(Matrix&&) noexcept = default;
    Matrix& operator=(const Matrix& o) {
        if (this != &o) { Matrix tmp(o); *this = std::move(tmp); }   // strong guarantee
        return *this;
    }
    Matrix& operator=(Matrix&&) noexcept = default;
    ~Matrix() = default;

    std::size_t rows() const { return r_; }
    std::size_t cols() const { return c_; }
    long long& operator()(std::size_t r, std::size_t c) { check(r, c); return at(r, c); }
    long long operator()(std::size_t r, std::size_t c) const { check(r, c); return at(r, c); }

    Matrix& operator+=(const Matrix& o) { same_shape(o); for (std::size_t i = 0; i < r_ * c_; ++i) data_[i] += o.data_[i]; return *this; }
    Matrix& operator-=(const Matrix& o) { same_shape(o); for (std::size_t i = 0; i < r_ * c_; ++i) data_[i] -= o.data_[i]; return *this; }
    friend Matrix operator+(Matrix a, const Matrix& b) { a += b; return a; }
    friend Matrix operator-(Matrix a, const Matrix& b) { a -= b; return a; }
    friend Matrix operator*(const Matrix& a, const Matrix& b) {
        if (a.c_ != b.r_) throw std::invalid_argument("inner dimensions differ");
        Matrix r(a.r_, b.c_);
        for (std::size_t i = 0; i < a.r_; ++i)
            for (std::size_t k = 0; k < a.c_; ++k) {          // i-k-j order: cache-friendly
                long long aik = a.at(i, k);
                for (std::size_t j = 0; j < b.c_; ++j) r.at(i, j) += aik * b.at(k, j);
            }
        return r;
    }
    friend Matrix operator*(long long k, Matrix m) {
        for (std::size_t i = 0; i < m.r_ * m.c_; ++i) m.data_[i] *= k;
        return m;
    }
    friend bool operator==(const Matrix& a, const Matrix& b) {
        return a.r_ == b.r_ && a.c_ == b.c_ && std::equal(a.data_.get(), a.data_.get() + a.r_ * a.c_, b.data_.get());
    }
    Matrix transposed() const {
        Matrix t(c_, r_);
        for (std::size_t i = 0; i < r_; ++i)
            for (std::size_t j = 0; j < c_; ++j) t.at(j, i) = at(i, j);
        return t;
    }
    long long det() const {
        if (r_ != c_) throw std::invalid_argument("not square");
        Matrix a(*this);
        std::size_t n = r_;
        long long sign = 1, prev = 1;
        for (std::size_t k = 0; k + 1 < n; ++k) {
            if (a.at(k, k) == 0) {                             // find a non-zero pivot
                std::size_t p = k + 1;
                while (p < n && a.at(p, k) == 0) ++p;
                if (p == n) return 0;
                for (std::size_t j = 0; j < n; ++j) std::swap(a.at(k, j), a.at(p, j));
                sign = -sign;
            }
            for (std::size_t i = k + 1; i < n; ++i)
                for (std::size_t j = k + 1; j < n; ++j) {
                    __int128 v = static_cast<__int128>(a.at(i, j)) * a.at(k, k)
                               - static_cast<__int128>(a.at(i, k)) * a.at(k, j);
                    a.at(i, j) = static_cast<long long>(v / prev);   // exact division (Bareiss)
                }
            prev = a.at(k, k);
        }
        return sign * a.at(n - 1, n - 1);
    }
    Matrix pow_mod(unsigned long long e, long long mod) const {
        if (r_ != c_) throw std::invalid_argument("not square");
        Matrix base(*this), result = identity(r_);
        for (std::size_t i = 0; i < r_ * c_; ++i) base.data_[i] = ((base.data_[i] % mod) + mod) % mod;
        for (std::size_t i = 0; i < r_ * c_; ++i) result.data_[i] %= mod;   // handles mod == 1
        while (e) {
            if (e & 1) result = mul_mod(result, base, mod);
            base = mul_mod(base, base, mod);
            e >>= 1;
        }
        return result;
    }
    friend std::ostream& operator<<(std::ostream& os, const Matrix& m) {
        for (std::size_t i = 0; i < m.r_; ++i) {
            if (i) os << '\n';
            for (std::size_t j = 0; j < m.c_; ++j) os << (j ? " " : "") << m.at(i, j);
        }
        return os;
    }

private:
    long long& at(std::size_t r, std::size_t c) { return data_[r * c_ + c]; }
    long long at(std::size_t r, std::size_t c) const { return data_[r * c_ + c]; }
    void check(std::size_t r, std::size_t c) const { if (r >= r_ || c >= c_) throw std::out_of_range("index"); }
    void same_shape(const Matrix& o) const { if (r_ != o.r_ || c_ != o.c_) throw std::invalid_argument("shape"); }
    static Matrix mul_mod(const Matrix& a, const Matrix& b, long long mod) {
        Matrix r(a.r_, b.c_);
        for (std::size_t i = 0; i < a.r_; ++i)
            for (std::size_t j = 0; j < b.c_; ++j) {
                __int128 s = 0;
                for (std::size_t k = 0; k < a.c_; ++k) s += static_cast<__int128>(a.at(i, k)) * b.at(k, j);
                r.at(i, j) = static_cast<long long>(s % mod);
            }
        return r;
    }

    std::size_t r_, c_;
    std::unique_ptr<long long[]> data_;
};
```

**Highlights:**
- **The Rule of Five, mostly for free:** with `unique_ptr<long long[]>` as the owner, the defaulted moves are correct and `noexcept`, and the destructor is trivial to get right. Only the copy operations need writing: a deep copy, plus copy-then-move assignment for the strong guarantee and self-assignment safety.
- **Operators follow the canonical forms:** compound operators are members, binary ones are friends built on them, and `k * m` takes `m` by value so it can modify the copy (moved in when the argument is a temporary).
- **Two levels of access:** the public `operator()` checks bounds (it's an API boundary), and the private `at()` doesn't (it's used in hot loops already known to be in range).
- **The Bareiss algorithm** keeps everything integral: each division is exact because the dividend is a multiple of the previous pivot (Sylvester's identity), so the determinant is exact in O(n³). Cofactor expansion would be O(n!).
- **`pow_mod`** uses square-and-multiply: 10¹² as the exponent takes about 40 squarings instead of 10¹² multiplications. That's the same idea as integer fast power, and it's how linear recurrences (Fibonacci in O(log n)) are computed.
