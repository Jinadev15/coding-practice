---
id: cpp-st-shunting-yard
title: Infix to Postfix with the Shunting-Yard Algorithm
difficulty: Medium
order: 5
tags: stack, shunting-yard, precedence, associativity, parsing
time_limit: 1
---
## Statement
```cpp
std::string to_postfix(const std::string& infix);
```

Convert an infix expression to postfix (Reverse Polish) notation. The expression contains:

- operands: non-negative integers (`0`, `42`, …) or single lowercase letters (`x`),
- binary operators, by precedence: `^` (highest, **right**-associative), then `*` `/` (left), then `+` `-` (left),
- parentheses `(` `)`.

There are no spaces, no unary operators, and the expression is valid. Output the postfix tokens separated by single spaces.

| infix | postfix |
|---|---|
| `a+b*c` | `a b c * +` |
| `(a+b)*c` | `a b + c *` |
| `a-b-c` | `a b - c -` (left: `(a−b)−c`) |
| `2^3^2` | `2 3 2 ^ ^` (right: `2^(3^2)`) |

**Input:** one expression per line until the end of input (total length ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string to_postfix(const string& infix) {
    return "";
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string s;
    while (cin >> s) cout << to_postfix(s) << '\n';
}
```

## Tests
=== sample
a+b*c
(a+b)*c
a-b-c
2^3^2
---
a b c * +
a b + c *
a b - c -
2 3 2 ^ ^
=== hidden
x
1234
a*b+c*d-e/f
((a))
(a^b)^c
a^b*c^d^e+f
10/(2-3)*4^(1+x)
---
x
1234
a b * c d * + e f / -
a
a b ^ c ^
a b ^ c d e ^ ^ * f +
10 2 3 - / 4 1 x + ^ *
=== hidden
(c-52)^(y/b)^(z/37*(c))
(95)^((45)/a)+x^90
y-(y-60)^(85*(88/b))^(c)
(81+104^y)*(y+(30)*y)
(69)-(95*c)-(31+4)
(45+31)^(71-(73)/z)
3
21
---
c 52 - y b / z 37 / c * ^ ^
95 45 a / ^ x 90 ^ +
y y 60 - 85 88 b / * c ^ ^ -
81 104 y ^ + y 30 y * + *
69 95 c * - 31 4 + -
45 31 + 71 73 z / - ^
3
21
=== hidden
(b^17^a)^((68)/(z))+2
(b-100-(14-30))*84/118
(28^(b*62))+(b-120)*z
z/101
(10)/a*(x-58)+(30^2-61)
(c*b^a/y-(65)^33)*c
b+((z/50)^(90-(34))-x)
((c)+(z))^a
---
b 17 a ^ ^ 68 z / ^ 2 +
b 100 - 14 30 - - 84 * 118 /
28 b 62 * ^ b 120 - z * +
z 101 /
10 a / x 58 - * 30 2 ^ 61 - +
c b a ^ * y / 65 33 ^ - c *
b z 50 / 90 34 - ^ x - +
c z + a ^
=== hidden
(c+x/36)^c^34
z^2/(115*(c-x*(b))-39)
(b)/b
(85)-z+64
(9)*b
z
(c*c+z)^(((b)^a-31)/c)
38^(b-78)/(50+((112)+77))
---
c x 36 / + c 34 ^ ^
z 2 ^ 115 c x b * - * 39 - /
b b /
85 z - 64 +
9 b *
z
c c * z + b a ^ 31 - c / ^
38 b 78 - ^ 50 112 77 + + /
=== hidden
@gen 3550167859 big
=== hidden
@gen 3550167860 big
=== hidden
@gen 3550167861 big

## Generator
```python
import random, sys
sys.setrecursionlimit(100000)
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
P = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
def build(n, out):                      # appends an expression with n operands; returns its precedence
    if n == 1:
        out.append(r.choice("abcxyz") if r.random() < 0.5 else str(r.randint(0, 120))); return 9
    op = r.choice("+-*/^"); p = P[op]; k = r.randint(1, n - 1)
    left, right = [], []
    lp = build(k, left); rp = build(n - k, right)
    if lp < p or (lp == p and op == "^") or r.random() < 0.1: left = ["("] + left + [")"]
    if rp < p or (rp == p and op != "^") or r.random() < 0.1: right = ["("] + right + [")"]
    out.extend(left); out.append(op); out.extend(right)
    return p
for _ in range(8 if not big else 1):
    out = []
    build(r.randint(1, 7) if not big else 120000, out)
    print("".join(out))
```

## Hints
- Operands go to the output immediately; operators wait on a stack until it is safe to emit them.
- Before pushing `c`, pop operators with higher precedence, and with equal precedence only if `c` is left-associative.
- `(` is a barrier on the stack; `)` pops until the matching `(`. Numbers can have several digits.

## Solution
Operands keep their order in postfix; only operators move. The **operator stack** holds operators that are still waiting for their right operand to finish.

When a new operator `c` arrives, every waiting operator that should be applied **before** `c` is popped to the output first:

- a stacked operator of **higher** precedence binds tighter, so it goes first;
- of **equal** precedence, it goes first only if `c` is **left**-associative (`a-b-c` = `(a-b)-c`). For the right-associative `^`, the stacked `^` must wait (`2^3^2` = `2^(3^2)`).

`(` is pushed as a barrier that nothing pops past; `)` pops down to its `(` and discards both. At the end, the remaining operators are flushed.

```text
a+b*c-d
a        out a
+        ops [+]
b        out a b
*        * > +: push          ops [+ *]
c        out a b c
-        pop * (higher), pop + (equal, left-assoc), push -   out a b c * +
d        out a b c * + d
end      out a b c * + d -
```

Complexity: O(n): each operator is pushed and popped once.

```cpp
#include <bits/stdc++.h>
using namespace std;

static int prec(char op) { return op == '^' ? 3 : (op == '*' || op == '/') ? 2 : 1; }

string to_postfix(const string& s) {
    string out;
    vector<char> ops;                                   // operator stack ('(' acts as a barrier)
    auto emit = [&](const string& tok) { if (!out.empty()) out += ' '; out += tok; };
    for (size_t i = 0; i < s.size();) {
        char c = s[i];
        if (isalnum((unsigned char)c)) {                // operand: goes straight to the output
            size_t j = i;
            if (isdigit((unsigned char)c)) while (j < s.size() && isdigit((unsigned char)s[j])) ++j;
            else j = i + 1;
            emit(s.substr(i, j - i)); i = j; continue;
        }
        if (c == '(') ops.push_back(c);
        else if (c == ')') {
            while (ops.back() != '(') { emit(string(1, ops.back())); ops.pop_back(); }
            ops.pop_back();                             // discard the '('
        } else {
            bool right = (c == '^');
            while (!ops.empty() && ops.back() != '(' &&
                   (prec(ops.back()) > prec(c) || (prec(ops.back()) == prec(c) && !right))) {
                emit(string(1, ops.back())); ops.pop_back();
            }
            ops.push_back(c);
        }
        ++i;
    }
    while (!ops.empty()) { emit(string(1, ops.back())); ops.pop_back(); }
    return out;
}
```
