---
id: cpp-str-parsing
title: Robust atoi and Version Comparison
difficulty: Medium
order: 3
tags: strings, parsing, overflow, cursor
time_limit: 1
---
## Statement
```cpp
int my_atoi(const std::string& s);
    // skip leading spaces; optional '+' or '-'; then digits until the first non-digit;
    // no digits -> 0; clamp the result to [INT_MIN, INT_MAX]
int compare_versions(const std::string& a, const std::string& b);
    // dot-separated revisions compared numerically ("1.01" == "1.001", "1.0" == "1"); return -1, 0 or 1
```

Examples: `"   -42"` gives −42, `"4193 with words"` gives 4193, `"words 987"` gives 0, and `"-91283472332"` gives −2147483648.

For atoi, detect overflow **before** it happens, because signed overflow is undefined behaviour. Accumulate in `long long` and clamp once the value exceeds the `int` range (stop reading digits after that). For versions, parse each revision as a number (leading zeros don't matter) and treat missing revisions as 0. Revisions can have up to 50 digits, so compare them as strings after stripping leading zeros: longer means bigger, and equal length means compare lexicographically.

**Input:** lines `atoi <text>` (the text may contain spaces) or `ver a b`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int my_atoi(const string& s) { try { return stoi(s); } catch (...) { return 0; } }
int compare_versions(const string& a, const string& b) { return a < b ? -1 : a > b ? 1 : 0; }
```

## Driver
```cpp
int main() {
    string line;
    while (getline(cin, line)) {
        if (line.rfind("atoi ", 0) == 0) cout << my_atoi(line.substr(5)) << '\n';
        else if (line.rfind("ver ", 0) == 0) {
            istringstream in(line.substr(4)); string a, b; in >> a >> b;
            cout << compare_versions(a, b) << '\n';
        }
    }
}
```

## Tests
=== sample
atoi 42
atoi    -42
atoi 4193 with words
atoi words and 987
atoi -91283472332
ver 1.01 1.001
ver 1.0 1.0.0
ver 0.1 1.1
---
42
-42
4193
0
-2147483648
0
0
-1
=== hidden
atoi x
atoi +
atoi +-12
atoi 2147483647
atoi 2147483648
atoi -2147483648
atoi 00000000000000000000123
atoi   +0 123
ver 1 1.0.0.0.1
ver 7.5.2.4 7.5.3
ver 1.000000000000000000000000000000000000002 1.2
ver 99999999999999999999 100000000000000000000
---
0
0
0
2147483647
2147483647
-2147483648
123
0
-1
-1
0
-1
=== hidden
atoi -024500.
atoi +7782893202
ver 1.001.0.02 02.1
ver 000.00.02.00 03
ver 02 002.3.000
atoi   +3052315424 7
atoi -8999356.
ver 00.1.02.3 02.0
ver 0 02.002.0.00
atoi   -88814944691135x9
atoi 339 7
atoi  +-07462259685183 7
atoi   +-52x9
atoi   9807945.
atoi   +-1926420581462x9
atoi -7188982x9
atoi -56201045975058 7
ver 002.003.003 003
atoi   9x9
ver 02 000.0.01.001
atoi  +-930
ver 1 03.001.001
ver 001 3.03.03
atoi 0776853679 7
ver 02.003.00.003 01.002
---
-24500
2147483647
-1
-1
-1
2147483647
-8999356
-1
-1
-2147483648
339
0
0
9807945
0
-7188982
-2147483648
-1
9
1
0
-1
-1
776853679
1
=== hidden
ver 00.03.03.00 02.02
ver 000 001.02.00
ver 01.01.02.1 002.2
atoi  +71730124041143
atoi +-5x9
ver 00 2
atoi +-04782.
atoi   +125381
atoi  -82037279110400.
atoi +-11215952473127x9
atoi   8284257227650
ver 02.1.1 00.2.001
atoi   -
ver 03.003.00 001.000
atoi   +870.
ver 1.02.3 0.002
atoi   +-3774x9
atoi  +0x9
ver 2.2.001.003 00.2
ver 2.003.003.001 01
ver 1.02.3 2.0.000
atoi   +-8526608633x9
atoi   -x9
atoi   -70396 7
ver 003 0.002.3.0
---
-1
-1
-1
2147483647
0
-1
0
125381
-2147483648
0
2147483647
1
0
1
870
1
0
0
1
1
-1
0
0
-70396
1
=== hidden
atoi +-315133
atoi  +7182731107 7
ver 1 1
ver 01.001.2 02.00.00
ver 2.001 02.001
atoi -18238009196818.
atoi +2927858689612x9
ver 0.01 003.01.002.0
atoi +-561x9
atoi   -05870720439
atoi   +1268421.
atoi +1742645627 7
atoi   -84
atoi  -0233x9
atoi  -870076196560
atoi  +84x9
ver 01.02 01
atoi -98
atoi  09751704007332x9
atoi   +-607 7
atoi 83598186666
atoi  4116759068.
atoi  +-11440538741100
ver 0.002 2
atoi   -6051x9
---
0
2147483647
0
-1
0
-2147483648
2147483647
-1
0
-2147483648
1268421
1742645627
-84
-233
-2147483648
84
1
-98
2147483647
0
2147483647
2147483647
0
-1
-6051
=== hidden
ver 02.1.1.2 002.003.01.003
atoi   +-5214134455691x9
ver 000 0
atoi  8760924134
atoi   -64327058x9
atoi   -5403353.
atoi   -
atoi   4427204593.
ver 000.3.00 001.03
atoi  +-356771 7
ver 0.000 01.00
atoi   +-91080607375 7
ver 0.3.000 01.01.000.1
ver 2.0.003.01 03.003
atoi   +7164930310086.
ver 002.003 003
atoi   +50652789898714 7
ver 02.00.3 02.003
atoi  502124x9
atoi   +21293941323300 7
ver 0 03.002.001
atoi  +5.
ver 1.2 001.3.03
ver 3 1
atoi 12408073.
---
-1
0
0
2147483647
-64327058
-5403353
0
2147483647
-1
0
-1
0
-1
-1
2147483647
-1
2147483647
-1
502124
2147483647
-1
5
-1
1
12408073
=== hidden
ver 002.0.02 3
atoi -275181x9
atoi  530864.
atoi  +3324 7
ver 2 002
ver 1 1.3.02
ver 003 00.00.2.001
atoi 22182238x9
ver 2.02.3.003 002
atoi  +-556455
atoi   +x9
atoi -4x9
ver 002.002.01.001 02
ver 1.1.2.01 003
atoi  -2593489323
atoi   458573211667x9
ver 00 02.02.001
ver 0.1.2.03 3
atoi +-0.
atoi   -2955x9
ver 0.2.00.02 00.3.00.002
atoi 12720112413166.
ver 2.000.000 000.02.01.2
atoi -48674230571211
atoi   -x9
---
-1
-275181
530864
3324
0
-1
1
22182238
1
0
0
-4
1
-1
-2147483648
2147483647
-1
-1
0
-2955
-1
2147483647
1
-2147483648
0
=== hidden
atoi  +7499217
atoi   +-64363733257x9
atoi  +-7.
atoi -6x9
ver 00 002.00.01
ver 000.3.000.1 2.00.00.03
atoi +93
atoi  +7
ver 3.0.001.03 2.000.003
atoi -2245849.
ver 01.02.02 003
ver 02 2.01.1
atoi -711.
ver 1.2 01
atoi   +-87615998609649
atoi   +51287132056417 7
atoi 929238.
atoi   +-88126093x9
atoi -214736612553 7
ver 02.2.0.000 0.02.001.1
atoi  601410604858x9
ver 3 3.00.2.002
ver 1 02.02.0.003
atoi +-3732
atoi  386868236.
---
7499217
0
0
-6
-1
-1
93
7
1
-2245849
-1
-1
-711
1
0
2147483647
929238
0
-2147483648
1
2147483647
-1
-1
0
386868236

## Hints
- atoi: skip spaces, read an optional sign, then read digits. Stop at the first non-digit.
- Accumulate in a wider type and stop as soon as the value leaves the `int` range, then clamp.
- Versions: walk both strings revision by revision. Compare after stripping leading zeros (longer = bigger), and treat missing revisions as "0".

## Solution
**atoi** is a tiny state machine: spaces → sign → digits → stop. The cursor `i` only moves forward. Overflow is the real trap. Accumulating in `long long` and stopping once the magnitude passes `INT_MAX + 1` keeps the arithmetic far from 64-bit overflow, even for 1000-digit inputs, and the clamp then gives the saturated answer. (Without a wider type, check `v > (INT_MAX − d) / 10` before each step.)

**Versions** are split at dots with a cursor. Each revision is compared **numerically**. Revisions may be longer than any integer type, so strip the leading zeros and compare the lengths first, then the digits. Missing trailing revisions behave like `0`, so `1.0.0 == 1`.

Complexity: O(n) for both.

```cpp
#include <bits/stdc++.h>
using namespace std;

int my_atoi(const string& s) {
    size_t i = 0;
    while (i < s.size() && s[i] == ' ') ++i;                         // leading spaces only
    bool neg = false;
    if (i < s.size() && (s[i] == '+' || s[i] == '-')) neg = s[i++] == '-';
    long long v = 0;
    while (i < s.size() && isdigit((unsigned char)s[i])) {
        v = v * 10 + (s[i++] - '0');
        if (v > (long long)INT_MAX + 1) break;                       // already out of range: stop early
    }
    if (neg) v = -v;
    if (v > INT_MAX) return INT_MAX;
    if (v < INT_MIN) return INT_MIN;
    return (int)v;
}

static int cmp_num(string x, string y) {                             // compare decimal strings numerically
    auto strip = [](string& t) { size_t k = t.find_first_not_of('0'); t = k == string::npos ? "0" : t.substr(k); };
    strip(x); strip(y);
    if (x.size() != y.size()) return x.size() < y.size() ? -1 : 1;
    return x < y ? -1 : x > y ? 1 : 0;
}

int compare_versions(const string& a, const string& b) {
    size_t i = 0, j = 0;
    while (i < a.size() || j < b.size()) {
        size_t ni = a.find('.', i), nj = b.find('.', j);
        if (ni == string::npos) ni = a.size();
        if (nj == string::npos) nj = b.size();
        string x = i < a.size() ? a.substr(i, ni - i) : "0";         // missing revision counts as 0
        string y = j < b.size() ? b.substr(j, nj - j) : "0";
        if (int c = cmp_num(x, y)) return c;
        i = ni + 1; j = nj + 1;
    }
    return 0;
}
```
