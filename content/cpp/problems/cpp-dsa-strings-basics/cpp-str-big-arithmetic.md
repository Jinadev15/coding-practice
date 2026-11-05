---
id: cpp-str-big-arithmetic
title: Adding and Multiplying Huge Numbers as Strings
difficulty: Medium
order: 7
tags: strings, big integers, schoolbook arithmetic, carries
time_limit: 1
---
## Statement
Non-negative integers are given as decimal strings (no leading zeros, except `"0"` itself), with up to 5000 digits:

```cpp
std::string add_strings(const std::string& a, const std::string& b);
std::string multiply_strings(const std::string& a, const std::string& b);
```

You must not convert the whole number to a built-in type. It doesn't fit.

- **Addition:** go right to left, digit plus digit plus carry.
- **Multiplication:** digit `i` of `a` times digit `j` of `b` contributes to position `i + j + 1` of an `(n + m)`-digit result. Add all the products into an array first, then propagate the carries in one right-to-left pass. Strip leading zeros, but keep `"0"`.

**Input:** lines `add a b` or `mul a b`. Print the result if it has at most 80 digits, otherwise its length plus its first and last 20 digits.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string add_strings(const string& a, const string& b) { return to_string(stoll(a) + stoll(b)); }
string multiply_strings(const string& a, const string& b) { return to_string(stoll(a) * stoll(b)); }
```

## Driver
```cpp
static void show(const string& s) {
    if (s.size() <= 80) cout << s << '\n';
    else cout << s.size() << " digits " << s.substr(0, 20) << "..." << s.substr(s.size() - 20) << '\n';
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd, a, b;
    while (cin >> cmd >> a >> b) show(cmd == "add" ? add_strings(a, b) : multiply_strings(a, b));
}
```

## Tests
=== sample
add 11 123
add 456 77
mul 2 3
mul 123 456
mul 0 98765
---
134
533
6
56088
0
=== hidden
add 0 0
add 999 1
mul 1 1
mul 99 99
mul 123456789123456789 987654321987654321
---
0
1000
1
9801
121932631356500531347203169112635269
=== hidden
mul 0 661585
mul 4 43885913
mul 53 769
mul 591840 33586516
add 4 5
add 6575 66757
mul 95 523898
add 48 15
add 92 49746250
add 16669492 455715
---
0
175543652
40757
19877843629440
9
73332
49770310
63
49746342
17125207
=== hidden
mul 878973 323743
add 28534 397
mul 78185 614375
mul 73485750 638823
mul 99482379 46
mul 786 304
add 19802618 5110
add 715 749065
add 702630 9104
mul 361 65377
---
284561355939
28931
48034909375
46944387272250
4576189434
238944
19807728
749780
711734
23601097
=== hidden
mul 30 12
mul 62 692956
mul 5587338 7
add 4018553 4983893
add 483 4431674
mul 37317715 2
add 333983 40031179
add 485727 92489
mul 42812 788
mul 16571103 5
---
360
42963272
39111366
9002446
4432157
74635430
40365162
578216
33735856
82855515
=== hidden
@gen 295048040 big
=== hidden
@gen 295048041 big
=== hidden
@gen 295048042 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
def num(d): return str(r.randint(1, 9)) + "".join(r.choice("0123456789") for _ in range(d - 1)) if d > 1 else str(r.randint(0, 9))
out = []
for _ in range(10 if not big else 2):
    if big: out.append(f"{r.choice(['add','mul'])} {num(5000)} {num(5000)}")
    else: out.append(f"{r.choice(['add','mul'])} {num(r.randint(1, 8))} {num(r.randint(1, 8))}")
print("\n".join(out))
```

## Hints
- Add from the rightmost digits with a carry. Keep going while either number or the carry is left. Append, then reverse.
- For multiplication, the product of digits `a[i]` and `b[j]` belongs at index `i + j + 1` of an array of size `n + m`.
- Sum all products first, then do one right-to-left carry pass, and strip leading zeros (but leave a single "0").

## Solution
**Addition** is the schoolbook method: the carry is at most 1, and the loop continues while either number has digits left or a carry remains. Building by appending and reversing once keeps it linear.

**Multiplication.** In the product, the digit at position `i` of `a` (from the left) times the digit at position `j` of `b` lands at position `i + j + 1` of the `n + m`-digit result (the extra position at the front absorbs the final carry). Accumulating all `n·m` products **before** normalising lets one carry pass at the end do all the work. Each cell receives at most `min(n, m) × 81` before carrying, which is small.

O(n·m) is fine for 5000 digits (2.5·10⁷ operations). Karatsuba (Divide and Conquer topic) and FFT-based multiplication beat it for huge inputs.

Complexity: O(n + m) for addition, O(n·m) for multiplication.

```cpp
#include <bits/stdc++.h>
using namespace std;

string add_strings(const string& a, const string& b) {
    string out;
    int i = (int)a.size() - 1, j = (int)b.size() - 1, carry = 0;
    while (i >= 0 || j >= 0 || carry) {
        int d = carry + (i >= 0 ? a[i--] - '0' : 0) + (j >= 0 ? b[j--] - '0' : 0);
        out += char('0' + d % 10);
        carry = d / 10;
    }
    reverse(out.begin(), out.end());              // built backwards by appending: reverse once
    return out;
}

string multiply_strings(const string& a, const string& b) {
    int n = a.size(), m = b.size();
    vector<long long> acc(n + m, 0);
    for (int i = n - 1; i >= 0; --i)
        for (int j = m - 1; j >= 0; --j)
            acc[i + j + 1] += (a[i] - '0') * (b[j] - '0');       // at most 81 * 5000 per cell: fits easily
    for (int k = n + m - 1; k > 0; --k) { acc[k - 1] += acc[k] / 10; acc[k] %= 10; }   // one carry pass
    string out;
    int k = 0;
    while (k < n + m - 1 && acc[k] == 0) ++k;                    // strip leading zeros, keep one digit
    for (; k < n + m; ++k) out += char('0' + acc[k]);
    return out;
}
```
