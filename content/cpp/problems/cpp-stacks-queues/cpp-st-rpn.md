---
id: cpp-st-rpn
title: Evaluate Reverse Polish Notation
difficulty: Medium
order: 4
tags: stack, postfix, expression evaluation
time_limit: 1
---
## Statement
```cpp
long long eval_rpn(const std::vector<std::string>& tokens);
```

Each token is an integer (possibly negative, like `-3`) or one of the operators `+ - * /`. An operator applies to the two most recent values: in `a b -` the result is `a − b`, **not** `b − a`. Division truncates toward zero, as C++ `/` does (`-7 2 /` is `-3`).

The expression is valid, no division by zero happens, and every intermediate value fits in |v| ≤ 10¹⁸.

Example: `2 1 + 3 *` = (2 + 1) · 3 = 9. `4 13 5 / +` = 4 + 2 = 6.

**Input:** cases until the end of input: `n`, then a line with `n` tokens (n ≤ 10⁶ in total).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long eval_rpn(const vector<string>& tokens) {
    return 0;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<string> t(n);
        for (auto& x : t) cin >> x;
        cout << eval_rpn(t) << '\n';
    }
}
```

## Tests
=== sample
5
2 1 + 3 *
5
4 13 5 / +
3
-7 2 /
---
9
6
-3
=== hidden
1
-42
3
3 10 -
13
10 6 9 3 + -11 * / * 17 + 5 +
3
1000000000 1000000000 *
---
-42
-7
22
1000000000000000000
=== hidden
9
-2 -5 -7 * + -2 -6 + +
9
-4 8 9 + -2 / - 1 /
15
-1 3 + 7 + 1 -9 6 * / + -1 -8 - /
15
2 -4 1 -5 5 -8 - / 0 + + 7 - - *
15
5 -1 - -6 9 -9 -6 7 - / + 4 - / *
3
-8 9 -
---
25
4
1
4
-6
-17
=== hidden
3
9 -4 /
3
4 -9 -
3
1 -8 +
13
8 8 - 7 + 1 / 1 / 6 5 / +
3
-5 -2 +
9
8 -6 - 8 -3 3 * - *
---
-2
13
-7
8
-7
238
=== hidden
9
-8 -1 / -5 6 + -3 - +
13
6 2 -2 3 4 * * / -2 * -2 + /
5
2 -9 * 1 +
7
-9 9 3 5 + * *
1
7
9
9 4 -8 3 + + -3 * *
---
12
-3
-17
-648
7
27
=== hidden
@gen 2723312379 big
=== hidden
@gen 2723312380 big
=== hidden
@gen 2723312381 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
LIM = 10**18
def trunc(a, b):
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q
cases = 6 if not big else 1
for _ in range(cases):
    n_nums = r.randint(1, 8) if not big else 400000
    toks, st, pushed = [], [], 0
    while pushed < n_nums or len(st) > 1:
        if pushed < n_nums and (len(st) < 2 or r.random() < 0.5):
            v = r.randint(-9, 9) if not big else r.randint(-1000, 1000)
            toks.append(str(v)); st.append(v); pushed += 1
            continue
        b = st.pop(); a = st.pop()
        ops = ["+", "-"]
        if abs(a * b) <= LIM: ops.append("*")
        if b != 0: ops.append("/")
        op = r.choice(ops)
        res = a + b if op == "+" else a - b if op == "-" else a * b if op == "*" else trunc(a, b)
        if abs(res) > LIM:
            op, res = "/" if b != 0 else "-", trunc(a, b) if b != 0 else a - b
        toks.append(op); st.append(res)
    print(len(toks)); print(*toks)
```

## Hints
- Read tokens left to right. Numbers wait somewhere until an operator needs them. Which ones does an operator use?
- Pop twice: the first pop is the right operand `b`, the second is the left operand `a`.
- `-3` is a number. Treat a token as an operator only when its length is 1.

## Solution
Postfix needs no parentheses and no precedence: an operator always applies to the two values produced most recently, so a stack of values is all the state you need.

```text
4 13 5 / +
4        [4]
13       [4 13]
5        [4 13 5]
/        pop 5 (b), pop 13 (a) -> 13/5 = 2      [4 2]
+        pop 2, pop 4 -> 6                      [6]
```

Two traps:

- **Operand order.** The top of the stack is the *right* operand. Pop `b` first, then `a`, and compute `a op b`. Getting this backwards breaks `-` and `/` only, so tests with just `+` and `*` will not catch it.
- **Negative numbers.** `-3` starts with `-` but is a number. A token is an operator only if its length is 1.

At the end exactly one value remains: the answer.

Complexity: O(n) time, O(n) stack in the worst case (all numbers first).

```cpp
#include <bits/stdc++.h>
using namespace std;

long long eval_rpn(const vector<string>& tokens) {
    vector<long long> st;
    st.reserve(tokens.size());
    for (const string& t : tokens) {
        bool is_op = t.size() == 1 && (t[0] == '+' || t[0] == '-' || t[0] == '*' || t[0] == '/');
        if (!is_op) { st.push_back(stoll(t)); continue; }   // "-3" is a number: length > 1
        long long b = st.back(); st.pop_back();               // the RIGHT operand is on top
        long long a = st.back(); st.pop_back();
        switch (t[0]) {
            case '+': st.push_back(a + b); break;
            case '-': st.push_back(a - b); break;
            case '*': st.push_back(a * b); break;
            default:  st.push_back(a / b); break;             // truncates toward zero
        }
    }
    return st.back();
}
```
