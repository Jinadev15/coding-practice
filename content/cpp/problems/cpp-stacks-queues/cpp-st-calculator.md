---
id: cpp-st-calculator
title: Two-Stack Calculator with Unary Minus
difficulty: Hard
order: 6
tags: stack, expression evaluation, unary operators, modular arithmetic
time_limit: 1
---
## Statement
```cpp
long long calculate(const std::string& s);   // value of s modulo 1'000'000'007, in [0, 1e9+7)
```

Evaluate an infix expression **directly** (no postfix string in between) with:

- non-negative integer literals (at most 9 digits),
- binary `+`, `-`, `*` with the usual precedence (`*` before `+ -`, all left-associative),
- **unary minus**: a `-` is unary when it starts the expression, follows `(`, or follows another operator: `-3`, `2*-3`, `--4`, `-(1+2)`,
- parentheses, and **spaces** anywhere between tokens.

Values grow without bound, so compute everything modulo M = 10⁹ + 7 and print a result in `[0, M)`. (With only `+ - *`, the order of reductions does not change the result.)

Examples: `1 + 2 * 3` → 7. `-(2+3)*4` → 1000000007 − 20 = 999999987. `2*-3 - -1` → 999999993 (that is −5).

**Input:** one expression per line until the end of input (total length ≤ 10⁶). Lines are not empty.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long calculate(const string& s) {
    return 0;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string s;
    while (getline(cin, s)) cout << calculate(s) << '\n';
}
```

## Tests
=== sample
1 + 2 * 3
-(2+3)*4
2*-3 - -1
---
7
999999987
1000000002
=== hidden
0
--4
999999999*999999999
(((7)))
- 5 * - 5
10 - 2 - 3 * (4 - -6) * -1
123456789*987654321+-(1-2)*3
---
0
4
64
7
25
38
259106862
=== hidden
0*(11 *--19) *(((3 + 18)*2) -13)
1+13*((3*(16)))*1+ 5+(10)
-7-11 -(- 0 *8)-9*(12 - 8)
(18 *- 5 *19-20)
10-(-6-(13))
19 *1
- (- 1+(2))+((19+2)) +(14)
20* 12+(3)
---
0
640
999999953
999998277
29
19
34
243
=== hidden
4
(-(-14 *12*15* 10)-(- 13 -(4))+(-6))
20
2
((15+-7)-19* (11-(4)*(9)))
(10+ ((9- (9)))+9*(8)* - 15)
0*15- 13
(19*((7*19) -(20-5))-(-20* 14))
---
4
25211
20
2
483
999998937
999999994
2522
=== hidden
15 *(15) -(15) * (-(14+ 8)* 16)
8+ (16)*7-14
(-5* (- 13- 5*7+(6 +--15)))
(8+7) +1*20-17+((18--1))
(-9 +10 +-18--12+ 6)
15
(7+17)+(13- 5)+-7+4+(18)
((12 * (0)) - 19)+ (15)
---
5505
106
135
37
1
15
47
1000000003
=== hidden
@gen 4171975603 big
=== hidden
@gen 4171975604 big
=== hidden
@gen 4171975605 big

## Generator
```python
import random, sys
sys.setrecursionlimit(100000)
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
def sp(out):
    if r.random() < 0.3: out.append(" ")
def build(n, out):                      # appends an expression with n literals to out
    while r.random() < 0.12:
        out.append("-"); sp(out)
    if n == 1:
        out.append(str(r.randint(0, 20) if not big else r.randint(0, 999999999))); return
    k = r.randint(1, n - 1)
    paren = r.random() < 0.3
    if paren: out.append("(")
    build(k, out); sp(out); out.append(r.choice("+-*")); sp(out)
    rp = r.random() < 0.3
    if rp: out.append("(")
    build(n - k, out)
    if rp: out.append(")")
    if paren: out.append(")")
for _ in range(8 if not big else 1):
    out = []
    build(r.randint(1, 7) if not big else 100000, out)
    print("".join(out).strip())
```

## Hints
- Use two stacks: values and pending operators. Applying an operator pops two values and pushes one.
- A `-` is unary exactly when you are expecting an operand: at the start, after `(`, or after another operator.
- Give unary minus the highest precedence and do not pop anything when you push it. Reduce modulo M after every step.

## Solution
This is the shunting-yard algorithm with the output queue replaced by a **value stack**: instead of emitting an operator, you *apply* it to the top two values right away.

**Unary minus** is the same character as binary minus, so the parser tracks one bit of state, `expect_operand`. It is true at the start, after `(` and after any operator. A `-` seen while expecting an operand is unary; it is pushed as a separate operator `n` with the highest precedence. A prefix operator never pops anything when pushed (its operand has not appeared yet), and it is applied once its operand is complete, when a lower-precedence operator, a `)` or the end arrives. `--4` pushes `n` twice and correctly gives 4.

```text
2*-3 - -1
2      vals [2]
*      ops [*]               expect operand
-      unary: ops [* n]
3      vals [2 3]
-      binary: apply n (3 -> -3), apply * (-6); ops [-]
-      unary: ops [- n]
1      vals [-6 1]
end    apply n (-1), apply - : -6 - (-1) = -5  ->  999999993
```

Keeping every value in `[0, M)` and adding `M` before subtracting avoids negative remainders; products of two values below M fit in `long long`.

Complexity: O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

static const long long MOD = 1'000'000'007;

long long calculate(const string& s) {
    vector<long long> vals;
    vector<char> ops;                    // '(', '+', '-', '*', and 'n' = unary minus
    auto prec = [](char o) { return o == 'n' ? 3 : o == '*' ? 2 : o == '(' ? 0 : 1; };
    auto apply = [&]() {
        char o = ops.back(); ops.pop_back();
        if (o == 'n') { vals.back() = (MOD - vals.back()) % MOD; return; }
        long long b = vals.back(); vals.pop_back();
        long long& a = vals.back();
        if (o == '+') a = (a + b) % MOD;
        else if (o == '-') a = (a - b + MOD) % MOD;
        else a = a * b % MOD;
    };
    bool expect_operand = true;          // true at the start, after '(' and after an operator
    for (size_t i = 0; i < s.size(); ++i) {
        char c = s[i];
        if (c == ' ') continue;
        if (isdigit((unsigned char)c)) {
            long long v = 0;
            while (i < s.size() && isdigit((unsigned char)s[i])) v = v * 10 + (s[i++] - '0');
            --i;
            vals.push_back(v % MOD);
            expect_operand = false;
        } else if (c == '(') {
            ops.push_back('('); expect_operand = true;
        } else if (c == ')') {
            while (ops.back() != '(') apply();
            ops.pop_back(); expect_operand = false;
        } else if (c == '-' && expect_operand) {
            ops.push_back('n');          // unary: right-associative prefix, nothing to pop
        } else {
            while (!ops.empty() && prec(ops.back()) >= prec(c)) apply();
            ops.push_back(c); expect_operand = true;
        }
    }
    while (!ops.empty()) apply();
    return vals.back();
}
```
